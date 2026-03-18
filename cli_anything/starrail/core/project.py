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

from .mapping import (
    EMULATOR_MAPPINGS,
    DUNGEON_MAPPINGS,
    ROGUE_MAPPINGS,
    WEEKLY_MAPPINGS,
    ORNAMENT_MAPPINGS,
    TASK_SCHEDULER_MAPPINGS,
    DEFAULT_TASKS,
    CONFIG_SCHEMA_VERSION,
    apply_mappings_to_cli,
    apply_mappings_to_src,
    get_nested_value,
    set_nested_value,
    normalize_task_name,
)


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

    @classmethod
    def from_src_config(cls, src_config: dict) -> "EmulatorConfig":
        data = apply_mappings_to_cli(src_config, EMULATOR_MAPPINGS)
        return cls(**data)


@dataclass
class DungeonConfig:
    name: str = "Calyx_Golden_Treasures_Jarilo_VI"
    team: int = 1
    use_support: bool = False
    support_character: str = "FirstCharacter"
    stamina_consume: int = 0
    stamina_fuel: bool = False
    extract_reserved: bool = False
    fuel_reserve: int = 5

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "team": self.team,
            "use_support": self.use_support,
            "support_character": self.support_character,
            "stamina_consume": self.stamina_consume,
            "stamina_fuel": self.stamina_fuel,
            "extract_reserved": self.extract_reserved,
            "fuel_reserve": self.fuel_reserve,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DungeonConfig":
        return cls(
            name=data.get("name", "Calyx_Golden_Treasures_Jarilo_VI"),
            team=data.get("team", 1),
            use_support=data.get("use_support", False),
            support_character=data.get("support_character", "FirstCharacter"),
            stamina_consume=data.get("stamina_consume", 0),
            stamina_fuel=data.get("stamina_fuel", False),
            extract_reserved=data.get("extract_reserved", False),
            fuel_reserve=data.get("fuel_reserve", 5),
        )

    @classmethod
    def from_src_config(cls, src_config: dict) -> "DungeonConfig":
        data = apply_mappings_to_cli(src_config, DUNGEON_MAPPINGS)
        return cls(**data)


@dataclass
class RogueConfig:
    world: str = "Simulated_Universe_World_8"
    path: str = "The_Hunt"
    team: int = 1
    use_support: bool = False
    support_character: str = "FirstCharacter"
    bonus: bool = False
    domain_strategy: str = "combat"

    def to_dict(self) -> dict:
        return {
            "world": self.world,
            "path": self.path,
            "team": self.team,
            "use_support": self.use_support,
            "support_character": self.support_character,
            "bonus": self.bonus,
            "domain_strategy": self.domain_strategy,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RogueConfig":
        return cls(
            world=data.get("world", "Simulated_Universe_World_8"),
            path=data.get("path", "The_Hunt"),
            team=data.get("team", 1),
            use_support=data.get("use_support", False),
            support_character=data.get("support_character", "FirstCharacter"),
            bonus=data.get("bonus", False),
            domain_strategy=data.get("domain_strategy", "combat"),
        )

    @classmethod
    def from_src_config(cls, src_config: dict) -> "RogueConfig":
        data = apply_mappings_to_cli(src_config, ROGUE_MAPPINGS)
        return cls(**data)


@dataclass
class WeeklyConfig:
    name: str = "Echo_of_War_Destruction_Beginning"
    team: int = 1
    use_support: bool = False
    support_character: str = "FirstCharacter"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "team": self.team,
            "use_support": self.use_support,
            "support_character": self.support_character,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WeeklyConfig":
        return cls(
            name=data.get("name", "Echo_of_War_Destruction_Beginning"),
            team=data.get("team", 1),
            use_support=data.get("use_support", False),
            support_character=data.get("support_character", "FirstCharacter"),
        )

    @classmethod
    def from_src_config(cls, src_config: dict) -> "WeeklyConfig":
        data = apply_mappings_to_cli(src_config, WEEKLY_MAPPINGS)
        return cls(**data)


@dataclass
class OrnamentConfig:
    dungeon: str = "Divergent_Universe_Eternal_Comedy"
    team: int = 0
    use_immersifier: bool = True
    double_event: bool = True
    use_stamina: bool = False

    def to_dict(self) -> dict:
        return {
            "dungeon": self.dungeon,
            "team": self.team,
            "use_immersifier": self.use_immersifier,
            "double_event": self.double_event,
            "use_stamina": self.use_stamina,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrnamentConfig":
        return cls(
            dungeon=data.get("dungeon", "Divergent_Universe_Eternal_Comedy"),
            team=data.get("team", 0),
            use_immersifier=data.get("use_immersifier", True),
            double_event=data.get("double_event", True),
            use_stamina=data.get("use_stamina", False),
        )

    @classmethod
    def from_src_config(cls, src_config: dict) -> "OrnamentConfig":
        data = apply_mappings_to_cli(src_config, ORNAMENT_MAPPINGS)
        return cls(**data)


@dataclass
class Project:
    name: str
    created_at: datetime
    modified_at: datetime
    emulator: EmulatorConfig = field(default_factory=EmulatorConfig)
    dungeon: DungeonConfig = field(default_factory=DungeonConfig)
    rogue: RogueConfig = field(default_factory=RogueConfig)
    weekly: WeeklyConfig = field(default_factory=WeeklyConfig)
    ornament: OrnamentConfig = field(default_factory=OrnamentConfig)
    tasks: dict[str, TaskConfig] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.tasks:
            self._init_default_tasks()

    def _init_default_tasks(self):
        for task_name in DEFAULT_TASKS:
            self.tasks[task_name] = TaskConfig(name=task_name, command=task_name)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "emulator": self.emulator.to_dict(),
            "dungeon": self.dungeon.to_dict(),
            "rogue": self.rogue.to_dict(),
            "weekly": self.weekly.to_dict(),
            "ornament": self.ornament.to_dict(),
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
            weekly=WeeklyConfig.from_dict(data.get("weekly", {})),
            ornament=OrnamentConfig.from_dict(data.get("ornament", {})),
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
    config: dict = {
        "_version": CONFIG_SCHEMA_VERSION,
        "Alas": {
            "Emulator": {},
            "Optimization": {
                "WhenTaskQueueEmpty": "goto_main",
            },
        },
    }

    emulator_data = {
        "serial": project.emulator.serial,
        "game_client": project.emulator.game_client,
        "package_name": project.emulator.package_name,
        "game_language": project.emulator.game_language,
        "screenshot_method": project.emulator.screenshot_method,
        "control_method": project.emulator.control_method,
    }
    config = apply_mappings_to_src(emulator_data, EMULATOR_MAPPINGS, config)

    for task_name, task_config in project.tasks.items():
        normalized_name = normalize_task_name(task_name)
        if normalized_name not in config:
            config[normalized_name] = {}
        config[normalized_name]["Scheduler"] = {
            "Enable": task_config.enable,
            "NextRun": task_config.next_run.isoformat() if task_config.next_run else "2020-01-01 00:00:00",
            "Command": task_config.command,
            "ServerUpdate": task_config.server_update,
        }

    dungeon_data = project.dungeon.to_dict()
    config = apply_mappings_to_src(dungeon_data, DUNGEON_MAPPINGS, config)

    rogue_data = project.rogue.to_dict()
    config = apply_mappings_to_src(rogue_data, ROGUE_MAPPINGS, config)

    weekly_data = project.weekly.to_dict()
    config = apply_mappings_to_src(weekly_data, WEEKLY_MAPPINGS, config)

    ornament_data = project.ornament.to_dict()
    config = apply_mappings_to_src(ornament_data, ORNAMENT_MAPPINGS, config)

    return config


def load_src_config(path: str) -> Project:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        if path.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)

    return project_from_src_config(data, path.stem)


def project_from_src_config(data: dict, name: str = "imported") -> Project:
    project = create_project(name)

    project.emulator = EmulatorConfig.from_src_config(data)

    for task_name in DEFAULT_TASKS:
        if task_name in data:
            scheduler = data[task_name].get("Scheduler", {})
            project.tasks[task_name] = TaskConfig(
                name=task_name,
                enable=scheduler.get("Enable", False),
                command=scheduler.get("Command", task_name),
                server_update=scheduler.get("ServerUpdate", "04:00"),
            )

    if "Dungeon" in data:
        project.dungeon = DungeonConfig.from_src_config(data)

    if "Rogue" in data:
        project.rogue = RogueConfig.from_src_config(data)

    if "Weekly" in data:
        project.weekly = WeeklyConfig.from_src_config(data)

    if "Ornament" in data:
        project.ornament = OrnamentConfig.from_src_config(data)

    project.metadata["source"] = "src_config"
    project.metadata["imported_at"] = datetime.now().isoformat()
    project.metadata["src_version"] = data.get("_version", "unknown")

    return project


def save_as_src_config(project: Project, path: str) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    config = project_to_src_config(project)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return str(path)
