"""Main CLI entry point for cli-anything-starrail.

Provides both subcommand mode and interactive REPL mode.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from .core import (
    Session,
    Project,
    create_project,
    load_project,
    save_project,
    TaskRunner,
    TaskStatus,
)
from .utils.repl_skin import ReplSkin


def _resolve_project_path(ctx) -> Optional[str]:
    if ctx.parent:
        return ctx.parent.params.get("project")
    return ctx.params.get("project")


def _get_session(ctx) -> Session:
    if not hasattr(ctx, "session"):
        ctx.session = Session()
    return ctx.session


def _output_json(data: dict):
    print(json.dumps(data, indent=2, default=str))


def _format_datetime(dt: Optional[datetime]) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


skin = ReplSkin("starrail", version="1.0.0")


@click.group(invoke_without_command=True)
@click.option("--project", "-p", type=click.Path(), help="Project file path")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.version_option(version="1.0.0", prog_name="cli-anything-starrail")
@click.pass_context
def cli(ctx, project, json_output):
    ctx.ensure_object(dict)
    ctx.obj["project_path"] = project
    ctx.obj["json_output"] = json_output
    ctx.obj["session"] = Session()

    if project and os.path.exists(project):
        try:
            proj = load_project(project)
            ctx.obj["session"].project = proj
        except Exception as e:
            if not ctx.invoked_subcommand:
                skin.error(f"Failed to load project: {e}")

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=project)


@cli.command()
@click.argument("name", default="default")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def new(ctx, name, output):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    session.begin_action("new", f"Create project: {name}")
    project = create_project(name)
    session.project = project

    if output:
        path = save_project(project, output)
        if json_out:
            _output_json({"status": "created", "path": path, "name": name})
        else:
            skin.success(f"Created project: {name}")
            skin.status("Path", path)
    else:
        if json_out:
            _output_json({"status": "created", "name": name, "project": project.to_dict()})
        else:
            skin.success(f"Created project: {name}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def load(ctx, path):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    try:
        project = load_project(path)
        session.project = project
        ctx.obj["project_path"] = path

        if json_out:
            _output_json({"status": "loaded", "path": path, "project": project.to_dict()})
        else:
            skin.success(f"Loaded project: {project.name}")
            skin.status("Path", path)
            skin.status("Created", _format_datetime(project.created_at))
            skin.status("Modified", _format_datetime(project.modified_at))
    except Exception as e:
        if json_out:
            _output_json({"status": "error", "error": str(e)})
        else:
            skin.error(f"Failed to load project: {e}")
        sys.exit(1)


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def save(ctx, output):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    output_path = output or ctx.obj.get("project_path")
    if not output_path:
        if json_out:
            _output_json({"status": "error", "error": "No output path specified"})
        else:
            skin.error("No output path specified. Use -o or load a project first.")
        sys.exit(1)

    session.begin_action("save", f"Save project to: {output_path}")
    path = save_project(session.project, output_path)
    session.clear_history()

    if json_out:
        _output_json({"status": "saved", "path": path})
    else:
        skin.success(f"Saved project: {session.project.name}")
        skin.status("Path", path)


@cli.command()
@click.pass_context
def info(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    project = session.project

    if json_out:
        _output_json(project.to_dict())
    else:
        skin.section(f"Project: {project.name}")
        skin.status("Created", _format_datetime(project.created_at))
        skin.status("Modified", _format_datetime(project.modified_at))

        skin.section("Emulator")
        skin.status("Serial", project.emulator.serial)
        skin.status("Game Client", project.emulator.game_client)
        skin.status("Package", project.emulator.package_name)

        skin.section("Tasks")
        for name, task in project.tasks.items():
            status = "✓" if task.enable else "✗"
            next_run = _format_datetime(task.next_run) if task.next_run else "Not scheduled"
            print(f"  {status} {name}: {next_run}")


@cli.command()
@click.pass_context
def status(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    runner = TaskRunner(session.project)
    results = runner.get_all_results()

    if json_out:
        _output_json({
            "session_state": session.state.value,
            "current_task": session.current_task,
            "modified": session.is_modified,
            "can_undo": session.can_undo,
            "can_redo": session.can_redo,
            "task_results": {k: v.to_dict() for k, v in results.items()},
        })
    else:
        skin.section("Session Status")
        skin.status("State", session.state.value)
        skin.status("Modified", "Yes" if session.is_modified else "No")
        skin.status("Current Task", session.current_task or "None")

        if results:
            skin.section("Task Results")
            for name, result in results.items():
                status_icon = {
                    TaskStatus.SUCCESS: "✓",
                    TaskStatus.FAILED: "✗",
                    TaskStatus.RUNNING: "●",
                    TaskStatus.PENDING: "○",
                    TaskStatus.CANCELLED: "⊘",
                }.get(result.status, "?")
                print(f"  {status_icon} {name}: {result.status.value}")
                if result.message:
                    print(f"      {result.message}")


@cli.group()
@click.pass_context
def emulator(ctx):
    pass


@emulator.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def emulator_set(ctx, key, value):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    valid_keys = ["serial", "game_client", "package_name", "game_language", "screenshot_method", "control_method"]
    if key not in valid_keys:
        if json_out:
            _output_json({"status": "error", "error": f"Invalid key. Valid keys: {', '.join(valid_keys)}"})
        else:
            skin.error(f"Invalid key. Valid keys: {', '.join(valid_keys)}")
        sys.exit(1)

    session.begin_action("emulator_set", f"Set {key} = {value}")
    setattr(session.project.emulator, key, value)

    if json_out:
        _output_json({"status": "updated", "key": key, "value": value})
    else:
        skin.success(f"Set {key} = {value}")


@emulator.command("show")
@click.pass_context
def emulator_show(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    emu = session.project.emulator

    if json_out:
        _output_json(emu.to_dict())
    else:
        skin.section("Emulator Configuration")
        skin.status("Serial", emu.serial)
        skin.status("Game Client", emu.game_client)
        skin.status("Package Name", emu.package_name)
        skin.status("Game Language", emu.game_language)
        skin.status("Screenshot Method", emu.screenshot_method)
        skin.status("Control Method", emu.control_method)


@cli.group()
@click.pass_context
def task(ctx):
    pass


@task.command("list")
@click.pass_context
def task_list(ctx):
    json_out = ctx.obj.get("json_output", False)
    runner = TaskRunner()

    tasks = runner.list_available_tasks()

    if json_out:
        _output_json({"tasks": tasks})
    else:
        skin.section("Available Tasks")
        for t in tasks:
            info = runner.get_task_info(t)
            print(f"  • {t}")
            print(f"      {info['description']}")


@task.command("enable")
@click.argument("name")
@click.pass_context
def task_enable(ctx, name):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    if name not in session.project.tasks:
        if json_out:
            _output_json({"status": "error", "error": f"Unknown task: {name}"})
        else:
            skin.error(f"Unknown task: {name}")
        sys.exit(1)

    session.begin_action("task_enable", f"Enable task: {name}")
    session.project.tasks[name].enable = True

    if json_out:
        _output_json({"status": "enabled", "task": name})
    else:
        skin.success(f"Enabled task: {name}")


@task.command("disable")
@click.argument("name")
@click.pass_context
def task_disable(ctx, name):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    if name not in session.project.tasks:
        if json_out:
            _output_json({"status": "error", "error": f"Unknown task: {name}"})
        else:
            skin.error(f"Unknown task: {name}")
        sys.exit(1)

    session.begin_action("task_disable", f"Disable task: {name}")
    session.project.tasks[name].enable = False

    if json_out:
        _output_json({"status": "disabled", "task": name})
    else:
        skin.success(f"Disabled task: {name}")


@task.command("run")
@click.argument("name")
@click.option("--config", "-c", default="cli_temp", help="Config name to use")
@click.pass_context
def task_run(ctx, name, config):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    runner = TaskRunner(session.project)

    if json_out:
        result = runner.run_task(name, config)
        _output_json(result.to_dict())
    else:
        skin.info(f"Running task: {name}...")
        result = runner.run_task(name, config)

        if result.status == TaskStatus.SUCCESS:
            skin.success(result.message)
        else:
            skin.error(result.message)
            if result.error:
                skin.hint(result.error[:200])


@cli.group()
@click.pass_context
def dungeon(ctx):
    pass


@dungeon.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def dungeon_set(ctx, key, value):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    valid_keys = ["name", "team", "use_support", "support_character", "stamina_consume", "stamina_fuel"]
    if key not in valid_keys:
        if json_out:
            _output_json({"status": "error", "error": f"Invalid key. Valid keys: {', '.join(valid_keys)}"})
        else:
            skin.error(f"Invalid key. Valid keys: {', '.join(valid_keys)}")
        sys.exit(1)

    if key in ["team", "stamina_consume"]:
        try:
            value = int(value)
        except ValueError:
            if json_out:
                _output_json({"status": "error", "error": f"{key} must be an integer"})
            else:
                skin.error(f"{key} must be an integer")
            sys.exit(1)
    elif key in ["use_support", "stamina_fuel"]:
        value = value.lower() in ["true", "yes", "1", "on"]

    session.begin_action("dungeon_set", f"Set {key} = {value}")
    setattr(session.project.dungeon, key, value)

    if json_out:
        _output_json({"status": "updated", "key": key, "value": value})
    else:
        skin.success(f"Set {key} = {value}")


@dungeon.command("show")
@click.pass_context
def dungeon_show(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    dungeon_cfg = session.project.dungeon

    if json_out:
        _output_json(dungeon_cfg.to_dict())
    else:
        skin.section("Dungeon Configuration")
        skin.status("Name", dungeon_cfg.name)
        skin.status("Team", str(dungeon_cfg.team))
        skin.status("Use Support", "Yes" if dungeon_cfg.use_support else "No")
        if dungeon_cfg.support_character:
            skin.status("Support Character", dungeon_cfg.support_character)
        skin.status("Stamina Consume", str(dungeon_cfg.stamina_consume))
        skin.status("Use Fuel", "Yes" if dungeon_cfg.stamina_fuel else "No")


@cli.group()
@click.pass_context
def rogue(ctx):
    pass


@rogue.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def rogue_set(ctx, key, value):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    valid_keys = ["world", "path", "team", "use_support", "support_character", "bonus"]
    if key not in valid_keys:
        if json_out:
            _output_json({"status": "error", "error": f"Invalid key. Valid keys: {', '.join(valid_keys)}"})
        else:
            skin.error(f"Invalid key. Valid keys: {', '.join(valid_keys)}")
        sys.exit(1)

    if key == "team":
        try:
            value = int(value)
        except ValueError:
            if json_out:
                _output_json({"status": "error", "error": "team must be an integer"})
            else:
                skin.error("team must be an integer")
            sys.exit(1)
    elif key in ["use_support", "bonus"]:
        value = value.lower() in ["true", "yes", "1", "on"]

    session.begin_action("rogue_set", f"Set {key} = {value}")
    setattr(session.project.rogue, key, value)

    if json_out:
        _output_json({"status": "updated", "key": key, "value": value})
    else:
        skin.success(f"Set {key} = {value}")


@rogue.command("show")
@click.pass_context
def rogue_show(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if not session.project:
        if json_out:
            _output_json({"status": "error", "error": "No project loaded"})
        else:
            skin.error("No project loaded")
        sys.exit(1)

    rogue_cfg = session.project.rogue

    if json_out:
        _output_json(rogue_cfg.to_dict())
    else:
        skin.section("Rogue Configuration")
        skin.status("World", rogue_cfg.world)
        skin.status("Path", rogue_cfg.path)
        skin.status("Team", str(rogue_cfg.team))
        skin.status("Use Support", "Yes" if rogue_cfg.use_support else "No")
        if rogue_cfg.support_character:
            skin.status("Support Character", rogue_cfg.support_character)
        skin.status("Bonus", "Yes" if rogue_cfg.bonus else "No")


@cli.command()
@click.pass_context
def undo(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if session.undo():
        if json_out:
            _output_json({"status": "undone", "can_redo": session.can_redo})
        else:
            skin.success("Undone last action")
    else:
        if json_out:
            _output_json({"status": "error", "error": "Nothing to undo"})
        else:
            skin.warning("Nothing to undo")


@cli.command()
@click.pass_context
def redo(ctx):
    session = ctx.obj["session"]
    json_out = ctx.obj.get("json_output", False)

    if session.redo():
        if json_out:
            _output_json({"status": "redone", "can_undo": session.can_undo})
        else:
            skin.success("Redone last action")
    else:
        if json_out:
            _output_json({"status": "error", "error": "Nothing to redo"})
        else:
            skin.warning("Nothing to redo")


@cli.command()
@click.option("--project-path", type=click.Path(), help="Project file to load")
@click.pass_context
def repl(ctx, project_path):
    session = ctx.obj["session"]

    if project_path and os.path.exists(project_path):
        try:
            project = load_project(project_path)
            session.project = project
            ctx.obj["project_path"] = project_path
        except Exception as e:
            skin.error(f"Failed to load project: {e}")

    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "new <name>": "Create a new project",
        "load <path>": "Load a project file",
        "save [path]": "Save current project",
        "info": "Show project information",
        "status": "Show session status",
        "emulator show": "Show emulator configuration",
        "emulator set <key> <value>": "Set emulator option",
        "dungeon show": "Show dungeon configuration",
        "dungeon set <key> <value>": "Set dungeon option",
        "rogue show": "Show rogue configuration",
        "rogue set <key> <value>": "Set rogue option",
        "task list": "List available tasks",
        "task enable <name>": "Enable a task",
        "task disable <name>": "Disable a task",
        "task run <name>": "Run a task",
        "undo": "Undo last action",
        "redo": "Redo last action",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        project_name = session.project.name if session.project else ""
        modified = session.is_modified

        try:
            line = skin.get_input(pt_session, project_name, modified)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ["quit", "exit", "q"]:
            if session.is_modified:
                skin.warning("You have unsaved changes. Use 'save' to save or 'quit!' to force quit.")
                continue
            skin.print_goodbye()
            break

        if cmd == "quit!":
            skin.print_goodbye()
            break

        if cmd == "help":
            skin.help(commands)
            continue

        try:
            if cmd == "new":
                name = parts[1] if len(parts) > 1 else "default"
                ctx.invoke(new, name=name)
            elif cmd == "load":
                if len(parts) < 2:
                    skin.error("Usage: load <path>")
                else:
                    ctx.invoke(load, path=parts[1])
            elif cmd == "save":
                output = parts[1] if len(parts) > 1 else None
                ctx.invoke(save, output=output)
            elif cmd == "info":
                ctx.invoke(info)
            elif cmd == "status":
                ctx.invoke(status)
            elif cmd == "undo":
                ctx.invoke(undo)
            elif cmd == "redo":
                ctx.invoke(redo)
            elif cmd == "emulator":
                if len(parts) < 2:
                    skin.error("Usage: emulator <show|set> ...")
                elif parts[1] == "show":
                    ctx.invoke(emulator_show)
                elif parts[1] == "set":
                    if len(parts) < 4:
                        skin.error("Usage: emulator set <key> <value>")
                    else:
                        ctx.invoke(emulator_set, key=parts[2], value=" ".join(parts[3:]))
                else:
                    skin.error(f"Unknown emulator command: {parts[1]}")
            elif cmd == "dungeon":
                if len(parts) < 2:
                    skin.error("Usage: dungeon <show|set> ...")
                elif parts[1] == "show":
                    ctx.invoke(dungeon_show)
                elif parts[1] == "set":
                    if len(parts) < 4:
                        skin.error("Usage: dungeon set <key> <value>")
                    else:
                        ctx.invoke(dungeon_set, key=parts[2], value=" ".join(parts[3:]))
                else:
                    skin.error(f"Unknown dungeon command: {parts[1]}")
            elif cmd == "rogue":
                if len(parts) < 2:
                    skin.error("Usage: rogue <show|set> ...")
                elif parts[1] == "show":
                    ctx.invoke(rogue_show)
                elif parts[1] == "set":
                    if len(parts) < 4:
                        skin.error("Usage: rogue set <key> <value>")
                    else:
                        ctx.invoke(rogue_set, key=parts[2], value=" ".join(parts[3:]))
                else:
                    skin.error(f"Unknown rogue command: {parts[1]}")
            elif cmd == "task":
                if len(parts) < 2:
                    skin.error("Usage: task <list|enable|disable|run> ...")
                elif parts[1] == "list":
                    ctx.invoke(task_list)
                elif parts[1] == "enable":
                    if len(parts) < 3:
                        skin.error("Usage: task enable <name>")
                    else:
                        ctx.invoke(task_enable, name=parts[2])
                elif parts[1] == "disable":
                    if len(parts) < 3:
                        skin.error("Usage: task disable <name>")
                    else:
                        ctx.invoke(task_disable, name=parts[2])
                elif parts[1] == "run":
                    if len(parts) < 3:
                        skin.error("Usage: task run <name>")
                    else:
                        ctx.invoke(task_run, name=parts[2])
                else:
                    skin.error(f"Unknown task command: {parts[1]}")
            else:
                skin.error(f"Unknown command: {cmd}. Type 'help' for available commands.")
        except SystemExit:
            pass
        except Exception as e:
            skin.error(f"Error: {e}")


def main():
    cli()


if __name__ == "__main__":
    main()
