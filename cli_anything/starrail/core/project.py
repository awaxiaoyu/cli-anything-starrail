"""Project management for StarRailCopilot CLI.

A project represents a configuration profile with its settings,
task schedule, and execution state.
"""

import copy
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class TaskConfig:
    name: str
    enable: bool = False
    next_run: Optional[datetime] = None
    command: str = ""
    server_update: str = "04:00"
    interval: int = 120
    failure_interval: int = 30

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "enable": self.enable,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "command": self.command,
            "server_update": self.server_update,
            "interval": self.interval,
            "failure_interval": self.failure_interval,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskConfig":
        next_run = data.get("next_run")
        if isinstance(next_run, str):
            next_run = datetime.fromisoformat(next_run)
        return cls(
            name=data.get("name", ""),
            enable=data.get("enable", False),
            next_run=next_run,
            command=data.get("command", data.get("name", "")),
            server_update=data.get("server_update", "04:00"),
            interval=data.get("interval", 120),
            failure_interval=data.get("failure_interval", 30),
        )


@dataclass
class EmulatorConfig:
    serial: str = "auto"
    game_client: str = "android"
    package_name: str = "auto"
    game_language: str = "auto"
    screenshot_method: str = "auto"
    control_method: str = "MaaTouch"

    def to_dict(self) -> dict:
        return {
            "serial": self.serial,
            "game_client": self.game_client,
            "package_name": self.package_name,
            "game_language": self.game_language,
            "screenshot_method": self.screenshot_method,
            "control_method": self.control_method,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmulatorConfig":
        return cls(
            serial=data.get("serial", "auto"),
            game_client=data.get("game_client", "android"),
            package_name=data.get("package_name", "auto"),
            game_language=data.get("game_language", "auto"),
            screenshot_method=data.get("screenshot_method", "auto"),
            control_method=data.get("control_method", "MaaTouch"),
        )


@dataclass
class DungeonConfig:
    name: str = "Calyx_Golden_Treasures"
    team: int = 1
    use_support: bool = False
    support_character: str = ""
    stamina_consume: int = 0
    stamina_fuel: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "team": self.team,
            "use_support": self.use_support,
            "support_character": self.support_character,
            "stamina_consume": self.stamina_consume,
            "stamina_fuel": self.stamina_fuel,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DungeonConfig":
        return cls(
            name=data.get("name", "Calyx_Golden_Treasures"),
            team=data.get("team", 1),
            use_support=data.get("use_support", False),
            support_character=data.get("support_character", ""),
            stamina_consume=data.get("stamina_consume", 0),
            stamina_fuel=data.get("stamina_fuel", False),
        )


@dataclass
class RogueConfig:
    world: str = "Simulated_Universe_World_1"
    path: str = "Preservation"
    team: int = 1
    use_support: bool = False
    support_character: str = ""
    bonus: bool = False

    def to_dict(self) -> dict:
        return {
            "world": self.world,
            "path": self.path,
            "team": self.team,
            "use_support": self.use_support,
            "support_character": self.support_character,
            "bonus": self.bonus,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RogueConfig":
        return cls(
            world=data.get("world", "Simulated_Universe_World_1"),
            path=data.get("path", "Preservation"),
            team=data.get("team", 1),
            use_support=data.get("use_support", False),
            support_character=data.get("support_character", ""),
            bonus=data.get("bonus", False),
        )


@dataclass
class Project:
    name: str
    created_at: datetime
    modified_at: datetime
    emulator: EmulatorConfig = field(default_factory=EmulatorConfig)
    dungeon: DungeonConfig = field(default_factory=DungeonConfig)
    rogue: RogueConfig = field(default_factory=RogueConfig)
    tasks: dict[str, TaskConfig] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.tasks:
            self._init_default_tasks()

    def _init_default_tasks(self):
        default_tasks = [
            "Dungeon", "Daily", "BattlePass", "Assignment",
            "Rogue", "Freebies", "DataUpdate", "Weekly"
        ]
        for task_name in default_tasks:
            self.tasks[task_name] = TaskConfig(name=task_name, command=task_name)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "emulator": self.emulator.to_dict(),
            "dungeon": self.dungeon.to_dict(),
            "rogue": self.rogue.to_dict(),
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        tasks = {}
        for k, v in data.get("tasks", {}).items():
            tasks[k] = TaskConfig.from_dict(v)

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        modified_at = data.get("modified_at")
        if isinstance(modified_at, str):
            modified_at = datetime.fromisoformat(modified_at)
        else:
            modified_at = datetime.now()

        return cls(
            name=data.get("name", "Untitled"),
            created_at=created_at,
            modified_at=modified_at,
            emulator=EmulatorConfig.from_dict(data.get("emulator", {})),
            dungeon=DungeonConfig.from_dict(data.get("dungeon", {})),
            rogue=RogueConfig.from_dict(data.get("rogue", {})),
            tasks=tasks,
            metadata=data.get("metadata", {}),
        )

    def touch(self):
        self.modified_at = datetime.now()


def create_project(name: str = "default") -> Project:
    return Project(
        name=name,
        created_at=datetime.now(),
        modified_at=datetime.now(),
    )


def load_project(path: str) -> Project:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        if path.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)

    return Project.from_dict(data)


def save_project(project: Project, path: str) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    project.touch()

    with open(path, "w", encoding="utf-8") as f:
        if path.suffix in [".yaml", ".yml"]:
            yaml.dump(project.to_dict(), f, default_flow_style=False, allow_unicode=True)
        else:
            json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)

    return str(path)


def project_to_src_config(project: Project) -> dict:
    config = {
        "Alas": {
            "Emulator": {
                "Serial": project.emulator.serial,
                "GameClient": project.emulator.game_client,
                "PackageName": project.emulator.package_name,
                "GameLanguage": project.emulator.game_language,
                "ScreenshotMethod": project.emulator.screenshot_method,
                "ControlMethod": project.emulator.control_method,
            },
            "Optimization": {
                "WhenTaskQueueEmpty": "goto_main",
            },
        },
    }

    for task_name, task_config in project.tasks.items():
        config[task_name] = {
            "Scheduler": {
                "Enable": task_config.enable,
                "NextRun": task_config.next_run.isoformat() if task_config.next_run else "2020-01-01 00:00:00",
                "Command": task_config.command,
                "ServerUpdate": task_config.server_update,
            },
        }

    if "Dungeon" in project.tasks:
        config["Dungeon"].update({
            "Dungeon": {
                "Name": project.dungeon.name,
                "Team": project.dungeon.team,
            },
            "Support": {
                "Use": project.dungeon.use_support,
                "Character": project.dungeon.support_character,
            },
            "Stamina": {
                "Consume": project.dungeon.stamina_consume,
                "UseFuel": project.dungeon.stamina_fuel,
            },
        })

    if "Rogue" in project.tasks:
        config["Rogue"].update({
            "RogueWorld": {
                "World": project.rogue.world,
                "Path": project.rogue.path,
            },
            "Team": {
                "Team": project.rogue.team,
            },
            "Support": {
                "Use": project.rogue.use_support,
                "Character": project.rogue.support_character,
            },
            "Bonus": {
                "Enable": project.rogue.bonus,
            },
        })

    return config
