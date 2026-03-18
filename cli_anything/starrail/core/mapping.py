"""Configuration mapping between CLI-Anything and StarRailCopilot.

This module provides a centralized mapping table for configuration fields,
making it easier to maintain compatibility when StarRailCopilot updates.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class FieldMapping:
    cli_field: str
    src_path: tuple[str, ...]
    default: Any = None
    transformer: Optional[Callable[[Any], Any]] = None
    reverse_transformer: Optional[Callable[[Any], Any]] = None


EMULATOR_MAPPINGS: list[FieldMapping] = [
    FieldMapping(
        cli_field="serial",
        src_path=("Alas", "Emulator", "Serial"),
        default="auto",
    ),
    FieldMapping(
        cli_field="game_client",
        src_path=("Alas", "Emulator", "GameClient"),
        default="android",
    ),
    FieldMapping(
        cli_field="package_name",
        src_path=("Alas", "Emulator", "PackageName"),
        default="auto",
    ),
    FieldMapping(
        cli_field="game_language",
        src_path=("Alas", "Emulator", "GameLanguage"),
        default="auto",
    ),
    FieldMapping(
        cli_field="screenshot_method",
        src_path=("Alas", "Emulator", "ScreenshotMethod"),
        default="auto",
    ),
    FieldMapping(
        cli_field="control_method",
        src_path=("Alas", "Emulator", "ControlMethod"),
        default="MaaTouch",
    ),
]


DUNGEON_MAPPINGS: list[FieldMapping] = [
    FieldMapping(
        cli_field="name",
        src_path=("Dungeon", "Dungeon", "Name"),
        default="Calyx_Golden_Treasures_Jarilo_VI",
    ),
    FieldMapping(
        cli_field="team",
        src_path=("Dungeon", "Dungeon", "Team"),
        default=1,
    ),
    FieldMapping(
        cli_field="use_support",
        src_path=("Dungeon", "DungeonSupport", "Use"),
        default=False,
        transformer=lambda v: v if v else "do_not_use",
        reverse_transformer=lambda v: v != "do_not_use",
    ),
    FieldMapping(
        cli_field="support_character",
        src_path=("Dungeon", "DungeonSupport", "Character"),
        default="FirstCharacter",
    ),
    FieldMapping(
        cli_field="stamina_consume",
        src_path=("Dungeon", "TrailblazePower", "Consume"),
        default=0,
    ),
    FieldMapping(
        cli_field="stamina_fuel",
        src_path=("Dungeon", "TrailblazePower", "UseFuel"),
        default=False,
    ),
    FieldMapping(
        cli_field="extract_reserved",
        src_path=("Dungeon", "TrailblazePower", "ExtractReservedTrailblazePower"),
        default=False,
    ),
    FieldMapping(
        cli_field="fuel_reserve",
        src_path=("Dungeon", "TrailblazePower", "FuelReserve"),
        default=5,
    ),
]


ROGUE_MAPPINGS: list[FieldMapping] = [
    FieldMapping(
        cli_field="world",
        src_path=("Rogue", "RogueWorld", "World"),
        default="Simulated_Universe_World_8",
    ),
    FieldMapping(
        cli_field="path",
        src_path=("Rogue", "RogueWorld", "Path"),
        default="The_Hunt",
    ),
    FieldMapping(
        cli_field="bonus",
        src_path=("Rogue", "RogueWorld", "Bonus"),
        default="",
        transformer=lambda v: "Blessing Universe" if v else "",
        reverse_transformer=lambda v: bool(v),
    ),
    FieldMapping(
        cli_field="domain_strategy",
        src_path=("Rogue", "RogueWorld", "DomainStrategy"),
        default="combat",
    ),
    FieldMapping(
        cli_field="team",
        src_path=("Rogue", "Team", "Team"),
        default=1,
    ),
    FieldMapping(
        cli_field="use_support",
        src_path=("Rogue", "Support", "Use"),
        default=False,
        transformer=lambda v: v if v else "do_not_use",
        reverse_transformer=lambda v: v != "do_not_use",
    ),
    FieldMapping(
        cli_field="support_character",
        src_path=("Rogue", "Support", "Character"),
        default="FirstCharacter",
    ),
]


WEEKLY_MAPPINGS: list[FieldMapping] = [
    FieldMapping(
        cli_field="name",
        src_path=("Weekly", "Weekly", "Name"),
        default="Echo_of_War_Destruction_Beginning",
    ),
    FieldMapping(
        cli_field="team",
        src_path=("Weekly", "Weekly", "Team"),
        default=1,
    ),
    FieldMapping(
        cli_field="use_support",
        src_path=("Weekly", "DungeonSupport", "Use"),
        default=False,
        transformer=lambda v: v if v else "do_not_use",
        reverse_transformer=lambda v: v != "do_not_use",
    ),
    FieldMapping(
        cli_field="support_character",
        src_path=("Weekly", "DungeonSupport", "Character"),
        default="FirstCharacter",
    ),
]


ORNAMENT_MAPPINGS: list[FieldMapping] = [
    FieldMapping(
        cli_field="dungeon",
        src_path=("Ornament", "Ornament", "Dungeon"),
        default="Divergent_Universe_Eternal_Comedy",
    ),
    FieldMapping(
        cli_field="team",
        src_path=("Ornament", "Ornament", "Team40"),
        default=0,
    ),
    FieldMapping(
        cli_field="use_immersifier",
        src_path=("Ornament", "Ornament", "UseImmersifier"),
        default=True,
    ),
    FieldMapping(
        cli_field="double_event",
        src_path=("Ornament", "Ornament", "DoubleEvent"),
        default=True,
    ),
    FieldMapping(
        cli_field="use_stamina",
        src_path=("Ornament", "Ornament", "UseStamina"),
        default=False,
    ),
]


TASK_SCHEDULER_MAPPINGS: dict[str, str] = {
    "Dungeon": "Dungeon",
    "DailyQuest": "DailyQuest",
    "Daily": "DailyQuest",
    "BattlePass": "BattlePass",
    "Assignment": "Assignment",
    "DataUpdate": "DataUpdate",
    "Freebies": "Freebies",
    "Rogue": "Rogue",
    "Weekly": "Weekly",
    "Ornament": "Ornament",
    "Restart": "Restart",
    "Daemon": "Daemon",
    "PlannerScan": "PlannerScan",
}


TASK_METHOD_MAPPINGS: dict[str, str] = {
    "dungeon": "dungeon",
    "weekly": "weekly",
    "daily_quest": "daily_quest",
    "daily": "daily_quest",
    "battle_pass": "battle_pass",
    "assignment": "assignment",
    "data_update": "data_update",
    "freebies": "freebies",
    "rogue": "rogue",
    "ornament": "ornament",
    "benchmark": "benchmark",
    "daemon": "daemon",
    "planner_scan": "planner_scan",
}


DEFAULT_TASKS: list[str] = [
    "Dungeon",
    "DailyQuest",
    "BattlePass",
    "Assignment",
    "DataUpdate",
    "Freebies",
    "Rogue",
    "Weekly",
    "Ornament",
]


def get_nested_value(data: dict, path: tuple[str, ...], default: Any = None) -> Any:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def set_nested_value(data: dict, path: tuple[str, ...], value: Any) -> None:
    current = data
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[path[-1]] = value


def apply_mappings_to_cli(
    src_config: dict, mappings: list[FieldMapping]
) -> dict[str, Any]:
    result = {}
    for mapping in mappings:
        value = get_nested_value(src_config, mapping.src_path, mapping.default)
        if mapping.reverse_transformer and value is not None:
            value = mapping.reverse_transformer(value)
        result[mapping.cli_field] = value
    return result


def apply_mappings_to_src(
    cli_config: dict, mappings: list[FieldMapping], src_config: Optional[dict] = None
) -> dict:
    result = src_config.copy() if src_config else {}
    for mapping in mappings:
        value = cli_config.get(mapping.cli_field, mapping.default)
        if mapping.transformer and value is not None:
            value = mapping.transformer(value)
        set_nested_value(result, mapping.src_path, value)
    return result


def normalize_task_name(task_name: str) -> str:
    return TASK_SCHEDULER_MAPPINGS.get(task_name, task_name)


def get_task_method(task_name: str) -> str:
    normalized = task_name.lower().replace("-", "_")
    return TASK_METHOD_MAPPINGS.get(normalized, normalized)


CONFIG_SCHEMA_VERSION = "1.0.0"


def get_config_schema() -> dict:
    return {
        "_version": CONFIG_SCHEMA_VERSION,
        "_cli_anything_compatible": True,
    }
