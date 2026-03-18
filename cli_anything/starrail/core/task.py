"""Task runner for StarRailCopilot CLI.

Provides task execution, status tracking, and integration with
the underlying StarRailCopilot system.
"""

import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from .project import Project, project_to_src_config
from .mapping import TASK_METHOD_MAPPINGS, get_task_method


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    task_name: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    message: str = ""
    error: Optional[str] = None
    data: dict = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> dict:
        return {
            "task_name": self.task_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "message": self.message,
            "error": self.error,
            "data": self.data,
        }


class TaskRunner:
    AVAILABLE_TASKS = [
        "dungeon",
        "weekly",
        "daily_quest",
        "battle_pass",
        "assignment",
        "data_update",
        "freebies",
        "rogue",
        "ornament",
        "benchmark",
        "daemon",
        "planner_scan",
    ]

    def __init__(self, project: Optional[Project] = None, config_dir: Optional[str] = None):
        self._project = project
        self._config_dir = config_dir or self._get_default_config_dir()
        self._results: dict[str, TaskResult] = {}
        self._running = False
        self._stop_event = threading.Event()
        self._current_process: Optional[subprocess.Popen] = None
        self._on_status_change: Optional[Callable[[str, TaskStatus], None]] = None

    def _get_default_config_dir(self) -> str:
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        return str(repo_root / "config")

    @property
    def project(self) -> Optional[Project]:
        return self._project

    @project.setter
    def project(self, value: Optional[Project]):
        self._project = value

    @property
    def is_running(self) -> bool:
        return self._running

    def set_status_callback(self, callback: Callable[[str, TaskStatus], None]):
        self._on_status_change = callback

    def _notify_status(self, task_name: str, status: TaskStatus):
        if self._on_status_change:
            self._on_status_change(task_name, status)

    def _write_config_file(self, config_name: str) -> str:
        if not self._project:
            raise ValueError("No project loaded")

        config_path = Path(self._config_dir) / f"{config_name}.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = project_to_src_config(self._project)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        return str(config_path)

    def _get_src_path(self) -> str:
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        return str(repo_root / "src.py")

    def run_task(self, task_name: str, config_name: str = "cli_temp") -> TaskResult:
        if task_name.lower() not in [t.lower() for t in self.AVAILABLE_TASKS]:
            return TaskResult(
                task_name=task_name,
                status=TaskStatus.FAILED,
                message=f"Unknown task: {task_name}",
                error=f"Available tasks: {', '.join(self.AVAILABLE_TASKS)}",
            )

        result = TaskResult(
            task_name=task_name,
            status=TaskStatus.PENDING,
            start_time=datetime.now(),
        )

        try:
            config_path = self._write_config_file(config_name)
            repo_root = Path(self._config_dir).parent
            src_path = repo_root / "src.py"

            if not src_path.exists():
                result.status = TaskStatus.FAILED
                result.message = "StarRailCopilot src.py not found"
                result.error = f"Expected at: {src_path}"
                result.end_time = datetime.now()
                return result

            result.status = TaskStatus.RUNNING
            self._notify_status(task_name, TaskStatus.RUNNING)

            task_method = self._task_name_to_method(task_name)

            runner_script = f'''
import sys
sys.path.insert(0, r"{repo_root}")
from src import StarRailCopilot
src = StarRailCopilot("{config_name}")
src.run("{task_method}")
'''

            self._current_process = subprocess.Popen(
                [sys.executable, "-c", runner_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(repo_root),
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )

            stdout, stderr = self._current_process.communicate(timeout=3600)

            if self._current_process.returncode == 0:
                result.status = TaskStatus.SUCCESS
                result.message = f"Task {task_name} completed successfully"
                result.data["stdout"] = stdout[-2000:] if len(stdout) > 2000 else stdout
            else:
                result.status = TaskStatus.FAILED
                result.message = f"Task {task_name} failed"
                error_output = stderr or stdout
                result.error = error_output[-1000:] if len(error_output) > 1000 else error_output

        except subprocess.TimeoutExpired:
            result.status = TaskStatus.FAILED
            result.message = f"Task {task_name} timed out (1 hour limit)"
            result.error = "Process exceeded maximum execution time"
            if self._current_process:
                self._current_process.kill()
        except FileNotFoundError as e:
            result.status = TaskStatus.FAILED
            result.message = f"File not found: {e}"
            result.error = str(e)
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.message = f"Error running task: {e}"
            result.error = str(e)
        finally:
            result.end_time = datetime.now()
            self._results[task_name] = result
            self._notify_status(task_name, result.status)
            self._current_process = None

        return result

    def _task_name_to_method(self, task_name: str) -> str:
        return get_task_method(task_name)

    def run_task_async(self, task_name: str, config_name: str = "cli_temp",
                       callback: Optional[Callable[[TaskResult], None]] = None) -> threading.Thread:
        def _run():
            result = self.run_task(task_name, config_name)
            if callback:
                callback(result)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread

    def stop(self):
        self._stop_event.set()
        if self._current_process:
            self._current_process.terminate()
            self._current_process = None

    def get_result(self, task_name: str) -> Optional[TaskResult]:
        return self._results.get(task_name)

    def get_all_results(self) -> dict[str, TaskResult]:
        return dict(self._results)

    def clear_results(self):
        self._results.clear()

    def list_available_tasks(self) -> list[str]:
        return list(self.AVAILABLE_TASKS)

    def get_task_info(self, task_name: str) -> dict:
        task_info = {
            "dungeon": {
                "description": "Run dungeon farming",
                "requires": ["dungeon.name", "dungeon.team"],
            },
            "weekly": {
                "description": "Run weekly dungeon",
                "requires": ["weekly.name"],
            },
            "daily_quest": {
                "description": "Complete daily quests",
                "requires": [],
            },
            "battle_pass": {
                "description": "Claim battle pass rewards",
                "requires": [],
            },
            "assignment": {
                "description": "Dispatch and claim assignments",
                "requires": [],
            },
            "data_update": {
                "description": "Update character/item data",
                "requires": [],
            },
            "freebies": {
                "description": "Claim mail and redeem codes",
                "requires": [],
            },
            "rogue": {
                "description": "Run Simulated Universe",
                "requires": ["rogue.world", "rogue.path"],
            },
            "ornament": {
                "description": "Run Ornament Extractions",
                "requires": [],
            },
            "benchmark": {
                "description": "Run performance benchmark",
                "requires": [],
            },
            "daemon": {
                "description": "Run daemon mode (continuous)",
                "requires": [],
            },
            "planner_scan": {
                "description": "Scan materials for planner",
                "requires": [],
            },
        }
        return task_info.get(task_name.lower(), {"description": "Unknown task", "requires": []})


def run_single_task(project: Project, task_name: str,
                    config_name: str = "cli_temp") -> TaskResult:
    runner = TaskRunner(project)
    return runner.run_task(task_name, config_name)
