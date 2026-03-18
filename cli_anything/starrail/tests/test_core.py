"""Unit tests for cli-anything-starrail core modules."""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from cli_anything.starrail.core.project import (
    Project,
    TaskConfig,
    EmulatorConfig,
    DungeonConfig,
    RogueConfig,
    WeeklyConfig,
    OrnamentConfig,
    create_project,
    load_project,
    save_project,
    project_to_src_config,
    load_src_config,
)
from cli_anything.starrail.core.session import Session, SessionState, HistoryEntry
from cli_anything.starrail.core.task import TaskRunner, TaskStatus, TaskResult
from cli_anything.starrail.core.version import (
    VersionInfo,
    parse_version,
    get_src_version,
    check_compatibility,
    detect_src_features,
    get_repo_root,
)
from cli_anything.starrail.core.mapping import (
    EMULATOR_MAPPINGS,
    DUNGEON_MAPPINGS,
    ROGUE_MAPPINGS,
    TASK_METHOD_MAPPINGS,
    normalize_task_name,
    get_task_method,
    get_nested_value,
    set_nested_value,
    apply_mappings_to_cli,
    apply_mappings_to_src,
)


class TestTaskConfig:
    def test_create_task_config(self):
        config = TaskConfig(name="Dungeon", enable=True)
        assert config.name == "Dungeon"
        assert config.enable is True
        assert config.command == ""
        assert config.interval == 120

    def test_task_config_to_dict(self):
        config = TaskConfig(name="Dungeon", enable=True, command="Dungeon")
        data = config.to_dict()
        assert data["name"] == "Dungeon"
        assert data["enable"] is True
        assert data["command"] == "Dungeon"

    def test_task_config_from_dict(self):
        data = {"name": "Rogue", "enable": False, "interval": 60}
        config = TaskConfig.from_dict(data)
        assert config.name == "Rogue"
        assert config.enable is False
        assert config.interval == 60


class TestEmulatorConfig:
    def test_create_emulator_config(self):
        config = EmulatorConfig(serial="127.0.0.1:5555")
        assert config.serial == "127.0.0.1:5555"
        assert config.game_client == "android"
        assert config.control_method == "MaaTouch"

    def test_emulator_config_to_dict(self):
        config = EmulatorConfig(serial="auto", game_client="cloud_android")
        data = config.to_dict()
        assert data["serial"] == "auto"
        assert data["game_client"] == "cloud_android"

    def test_emulator_config_from_dict(self):
        data = {"serial": "emulator-5554", "screenshot_method": "scrcpy"}
        config = EmulatorConfig.from_dict(data)
        assert config.serial == "emulator-5554"
        assert config.screenshot_method == "scrcpy"


class TestDungeonConfig:
    def test_create_dungeon_config(self):
        config = DungeonConfig(name="Calyx_Crimson", team=2)
        assert config.name == "Calyx_Crimson"
        assert config.team == 2

    def test_dungeon_config_to_dict(self):
        config = DungeonConfig(name="Stagnant_Shadow", use_support=True)
        data = config.to_dict()
        assert data["name"] == "Stagnant_Shadow"
        assert data["use_support"] is True


class TestRogueConfig:
    def test_create_rogue_config(self):
        config = RogueConfig(world="Simulated_Universe_World_3", path="Destruction")
        assert config.world == "Simulated_Universe_World_3"
        assert config.path == "Destruction"

    def test_rogue_config_to_dict(self):
        config = RogueConfig(bonus=True)
        data = config.to_dict()
        assert data["bonus"] is True


class TestProject:
    def test_create_project(self):
        project = create_project("test_config")
        assert project.name == "test_config"
        assert project.emulator is not None
        assert len(project.tasks) > 0

    def test_project_default_tasks(self):
        project = create_project()
        assert "Dungeon" in project.tasks
        assert "DailyQuest" in project.tasks
        assert "Rogue" in project.tasks
        assert "Weekly" in project.tasks
        assert "Ornament" in project.tasks

    def test_project_to_dict(self):
        project = create_project("test")
        data = project.to_dict()
        assert data["name"] == "test"
        assert "emulator" in data
        assert "tasks" in data

    def test_project_from_dict(self):
        data = {
            "name": "restored",
            "created_at": "2024-01-01T00:00:00",
            "modified_at": "2024-01-01T00:00:00",
            "emulator": {"serial": "test_serial"},
            "tasks": {"Dungeon": {"name": "Dungeon", "enable": True}},
        }
        project = Project.from_dict(data)
        assert project.name == "restored"
        assert project.emulator.serial == "test_serial"
        assert "Dungeon" in project.tasks


class TestProjectIO:
    def test_save_and_load_json(self):
        project = create_project("io_test")
        project.emulator.serial = "test_serial"

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            save_project(project, path)
            loaded = load_project(path)
            assert loaded.name == "io_test"
            assert loaded.emulator.serial == "test_serial"
        finally:
            os.unlink(path)

    def test_save_and_load_yaml(self):
        project = create_project("yaml_test")
        project.dungeon.name = "Calyx_Golden"

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = f.name

        try:
            save_project(project, path)
            loaded = load_project(path)
            assert loaded.name == "yaml_test"
            assert loaded.dungeon.name == "Calyx_Golden"
        finally:
            os.unlink(path)

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_project("/nonexistent/path/config.json")


class TestProjectToSrcConfig:
    def test_conversion(self):
        project = create_project("convert_test")
        project.emulator.serial = "127.0.0.1:5555"
        project.tasks["Dungeon"].enable = True

        config = project_to_src_config(project)

        assert "Alas" in config
        assert config["Alas"]["Emulator"]["Serial"] == "127.0.0.1:5555"
        assert "Dungeon" in config
        assert config["Dungeon"]["Scheduler"]["Enable"] is True

    def test_conversion_with_version(self):
        project = create_project("version_test")
        config = project_to_src_config(project)
        assert "_version" in config
        assert config["_version"] == "1.0.0"


class TestMapping:
    def test_get_nested_value(self):
        data = {"a": {"b": {"c": "value"}}}
        assert get_nested_value(data, ("a", "b", "c")) == "value"
        assert get_nested_value(data, ("a", "b", "d"), "default") == "default"
        assert get_nested_value(data, ("x",), "default") == "default"

    def test_set_nested_value(self):
        data = {}
        set_nested_value(data, ("a", "b", "c"), "value")
        assert data["a"]["b"]["c"] == "value"

    def test_apply_mappings_to_cli(self):
        src_config = {
            "Alas": {
                "Emulator": {
                    "Serial": "test_serial",
                    "GameClient": "android",
                }
            }
        }
        result = apply_mappings_to_cli(src_config, EMULATOR_MAPPINGS)
        assert result["serial"] == "test_serial"
        assert result["game_client"] == "android"

    def test_apply_mappings_to_src(self):
        cli_config = {
            "serial": "new_serial",
            "game_client": "cloud_android",
        }
        result = apply_mappings_to_src(cli_config, EMULATOR_MAPPINGS)
        assert result["Alas"]["Emulator"]["Serial"] == "new_serial"
        assert result["Alas"]["Emulator"]["GameClient"] == "cloud_android"

    def test_normalize_task_name(self):
        assert normalize_task_name("Daily") == "DailyQuest"
        assert normalize_task_name("Dungeon") == "Dungeon"
        assert normalize_task_name("Rogue") == "Rogue"

    def test_get_task_method(self):
        assert get_task_method("dungeon") == "dungeon"
        assert get_task_method("daily") == "daily_quest"
        assert get_task_method("daily-quest") == "daily_quest"
        assert get_task_method("battle_pass") == "battle_pass"

    def test_task_method_mappings(self):
        assert "dungeon" in TASK_METHOD_MAPPINGS
        assert "rogue" in TASK_METHOD_MAPPINGS
        assert "daily_quest" in TASK_METHOD_MAPPINGS


class TestVersion:
    def test_parse_version(self):
        assert parse_version("1.0.0") == (1, 0, 0)
        assert parse_version("v2.1.3") == (2, 1, 3)
        assert parse_version("1.0") == (1, 0, 0)
        assert parse_version("invalid") == (0, 0, 0)

    def test_version_info(self):
        ver = VersionInfo("1.2.3", 1, 2, 3, "test", datetime.now())
        assert ver.version == "1.2.3"
        assert ver.major == 1
        assert ver.minor == 2
        assert ver.patch == 3
        assert str(ver) == "1.2.3"

    def test_version_info_comparison(self):
        v1 = VersionInfo("1.0.0", 1, 0, 0, "test", datetime.now())
        v2 = VersionInfo("1.0.0", 1, 0, 0, "test", datetime.now())
        v3 = VersionInfo("2.0.0", 2, 0, 0, "test", datetime.now())

        assert v1.is_compatible_with(v2) is True
        assert v1.is_compatible_with(v3) is False

    def test_get_repo_root(self):
        root = get_repo_root()
        assert root.exists()
        assert (root / "src.py").exists()

    def test_detect_src_features(self):
        root = get_repo_root()
        features = detect_src_features(root)
        assert "tasks" in features
        assert "dungeon" in features["tasks"] or "rogue" in features["tasks"]

    def test_check_compatibility(self):
        root = get_repo_root()
        report = check_compatibility(root, "1.0.0")
        assert report.cli_version.version == "1.0.0"
        assert isinstance(report.warnings, list)
        assert isinstance(report.features, dict)


class TestSession:
    def test_create_session(self):
        session = Session()
        assert session.project is None
        assert session.state == SessionState.IDLE

    def test_session_with_project(self):
        project = create_project("session_test")
        session = Session(project)
        assert session.project is not None
        assert session.project.name == "session_test"

    def test_undo_redo(self):
        project = create_project("undo_test")
        session = Session(project)

        session.begin_action("test", "Test action")
        project.name = "modified"

        assert session.is_modified
        assert session.can_undo

        session.undo()
        assert session.project.name == "undo_test"

        session.redo()
        assert session.project.name == "modified"

    def test_undo_stack_limit(self):
        project = create_project("limit_test")
        session = Session(project)

        for i in range(60):
            session.begin_action(f"action_{i}", f"Action {i}")
            project.name = f"name_{i}"

        assert len(session._undo_stack) <= 50

    def test_session_state(self):
        session = Session()
        session.set_state(SessionState.RUNNING)
        assert session.state == SessionState.RUNNING

    def test_task_status(self):
        session = Session()
        session.set_task_status("Dungeon", {"status": "success", "count": 5})

        status = session.get_task_status("Dungeon")
        assert status["status"] == "success"
        assert status["count"] == 5

    def test_session_to_dict(self):
        project = create_project("dict_test")
        session = Session(project)

        data = session.to_dict()
        assert data["state"] == "idle"
        assert data["project"] is not None


class TestTaskRunner:
    def test_available_tasks(self):
        runner = TaskRunner()
        tasks = runner.list_available_tasks()
        assert "dungeon" in tasks
        assert "rogue" in tasks
        assert "daily_quest" in tasks

    def test_task_info(self):
        runner = TaskRunner()
        info = runner.get_task_info("dungeon")
        assert "description" in info
        assert "requires" in info

    def test_unknown_task(self):
        project = create_project("unknown_test")
        runner = TaskRunner(project)
        result = runner.run_task("unknown_task_xyz")

        assert result.status == TaskStatus.FAILED
        assert "Unknown task" in result.message

    def test_result_to_dict(self):
        result = TaskResult(
            task_name="test",
            status=TaskStatus.SUCCESS,
            message="Completed",
        )
        data = result.to_dict()
        assert data["task_name"] == "test"
        assert data["status"] == "success"
        assert data["message"] == "Completed"


class TestReplSkin:
    def test_skin_creation(self):
        from cli_anything.starrail.utils.repl_skin import ReplSkin

        skin = ReplSkin("starrail", version="1.0.0")
        assert skin.software == "starrail"
        assert skin.version == "1.0.0"

    def test_prompt(self):
        from cli_anything.starrail.utils.repl_skin import ReplSkin

        skin = ReplSkin("starrail")
        prompt = skin.prompt("my_config", modified=True)
        assert "starrail" in prompt
        assert "my_config" in prompt
        assert "*" in prompt
