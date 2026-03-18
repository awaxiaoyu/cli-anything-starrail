"""Version detection for StarRailCopilot compatibility.

This module provides version detection and compatibility checking
between CLI-Anything and the underlying StarRailCopilot project.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class VersionInfo:
    version: str
    major: int
    minor: int
    patch: int
    source: str
    detected_at: datetime

    def __str__(self) -> str:
        return self.version

    def __repr__(self) -> str:
        return f"VersionInfo({self.version}, source={self.source})"

    def is_compatible_with(self, other: "VersionInfo") -> bool:
        if self.major != other.major:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "source": self.source,
            "detected_at": self.detected_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VersionInfo":
        return cls(
            version=data.get("version", "0.0.0"),
            major=data.get("major", 0),
            minor=data.get("minor", 0),
            patch=data.get("patch", 0),
            source=data.get("source", "unknown"),
            detected_at=datetime.fromisoformat(data["detected_at"])
            if "detected_at" in data
            else datetime.now(),
        )


def parse_version(version_str: str) -> Tuple[int, int, int]:
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", version_str)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = re.match(r"v?(\d+)\.(\d+)", version_str)
    if match:
        return int(match.group(1)), int(match.group(2)), 0
    return 0, 0, 0


def get_src_version(repo_root: Path) -> Optional[VersionInfo]:
    version_sources = [
        ("webapp/package.json", lambda p: _extract_npm_version(p)),
        ("pyproject.toml", lambda p: _extract_pyproject_version(p)),
        ("VERSION", lambda p: _extract_file_version(p)),
        ("version.txt", lambda p: _extract_file_version(p)),
    ]

    for source_path, extractor in version_sources:
        full_path = repo_root / source_path
        if full_path.exists():
            version_str = extractor(full_path)
            if version_str:
                major, minor, patch = parse_version(version_str)
                return VersionInfo(
                    version=version_str,
                    major=major,
                    minor=minor,
                    patch=patch,
                    source=source_path,
                    detected_at=datetime.now(),
                )

    return None


def _extract_npm_version(path: Path) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version")
    except (json.JSONDecodeError, KeyError):
        return None


def _extract_pyproject_version(path: Path) -> Optional[str]:
    try:
        content = path.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def _extract_file_version(path: Path) -> Optional[str]:
    try:
        content = path.read_text(encoding="utf-8").strip()
        if content:
            return content
    except Exception:
        pass
    return None


def get_src_config_schema_version(config_path: Path) -> Optional[str]:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "_version" in data:
            return data["_version"]
        if "_schema_version" in data:
            return data["_schema_version"]

        return None
    except (json.JSONDecodeError, KeyError):
        return None


def detect_src_features(repo_root: Path) -> dict:
    features = {
        "tasks": [],
        "dungeons": [],
        "rogue_worlds": [],
        "rogue_paths": [],
    }

    src_path = repo_root / "src.py"
    if src_path.exists():
        content = src_path.read_text(encoding="utf-8")
        task_methods = re.findall(r"def\s+(\w+)\(self\):", content)
        features["tasks"] = [
            t for t in task_methods if t not in ("restart", "start", "stop", "goto_main", "error_postprocess", "loop")
        ]

    template_path = repo_root / "config" / "template.json"
    if template_path.exists():
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "Rogue" in data and "RogueWorld" in data["Rogue"]:
                rogue_world = data["Rogue"]["RogueWorld"]
                if "World" in rogue_world:
                    features["rogue_worlds"].append(rogue_world["World"])
                if "Path" in rogue_world:
                    features["rogue_paths"].append(rogue_world["Path"])

            if "Dungeon" in data and "Dungeon" in data["Dungeon"]:
                dungeon = data["Dungeon"]["Dungeon"]
                if "Name" in dungeon:
                    features["dungeons"].append(dungeon["Name"])

        except (json.JSONDecodeError, KeyError):
            pass

    return features


@dataclass
class CompatibilityReport:
    cli_version: VersionInfo
    src_version: Optional[VersionInfo]
    is_compatible: bool
    warnings: list[str]
    features: dict

    def to_dict(self) -> dict:
        return {
            "cli_version": self.cli_version.to_dict(),
            "src_version": self.src_version.to_dict() if self.src_version else None,
            "is_compatible": self.is_compatible,
            "warnings": self.warnings,
            "features": self.features,
        }


def check_compatibility(repo_root: Path, cli_version: str = "1.0.0") -> CompatibilityReport:
    warnings = []

    major, minor, patch = parse_version(cli_version)
    cli_ver = VersionInfo(
        version=cli_version,
        major=major,
        minor=minor,
        patch=patch,
        source="cli_anything",
        detected_at=datetime.now(),
    )

    src_ver = get_src_version(repo_root)
    features = detect_src_features(repo_root)

    is_compatible = True

    if src_ver is None:
        warnings.append("无法检测 StarRailCopilot 版本，可能需要手动检查兼容性")
    else:
        if src_ver.major != cli_ver.major:
            is_compatible = False
            warnings.append(
                f"主版本不匹配: CLI v{cli_ver.major}.x.x, SRC v{src_ver.major}.x.x"
            )
        elif src_ver.minor > cli_ver.minor:
            warnings.append(
                f"StarRailCopilot 版本较新 (v{src_ver.version})，可能包含新功能"
            )

    expected_tasks = {
        "dungeon", "weekly", "daily_quest", "battle_pass", "assignment",
        "data_update", "freebies", "rogue", "ornament", "benchmark", "daemon"
    }
    detected_tasks = set(features.get("tasks", []))
    missing_tasks = expected_tasks - detected_tasks
    if missing_tasks:
        warnings.append(f"未检测到以下任务: {', '.join(missing_tasks)}")

    return CompatibilityReport(
        cli_version=cli_ver,
        src_version=src_ver,
        is_compatible=is_compatible,
        warnings=warnings,
        features=features,
    )


def get_repo_root() -> Path:
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "src.py").exists() and (current / "config").is_dir():
            return current
        current = current.parent
    return Path(__file__).parent.parent.parent.parent.parent
