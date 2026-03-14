"""Session management with undo/redo support for StarRailCopilot CLI.

Provides stateful session management for tracking project changes,
execution history, and undo/redo capabilities.
"""

import copy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from .project import Project


class SessionState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class HistoryEntry:
    timestamp: datetime
    action: str
    description: str
    project_snapshot: Optional[dict] = None


class Session:
    MAX_HISTORY = 50

    def __init__(self, project: Optional[Project] = None):
        self._project: Optional[Project] = project
        self._state: SessionState = SessionState.IDLE
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        self._history: list[HistoryEntry] = []
        self._current_task: Optional[str] = None
        self._task_status: dict[str, Any] = {}
        self._metadata: dict[str, Any] = {}

    @property
    def project(self) -> Optional[Project]:
        return self._project

    @project.setter
    def project(self, value: Optional[Project]):
        self._project = value
        self._undo_stack.clear()
        self._redo_stack.clear()

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def current_task(self) -> Optional[str]:
        return self._current_task

    @property
    def is_modified(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def _snapshot_project(self) -> Optional[dict]:
        if self._project is None:
            return None
        return self._project.to_dict()

    def _restore_project(self, snapshot: dict):
        self._project = Project.from_dict(snapshot)

    def begin_action(self, action: str, description: str = ""):
        snapshot = self._snapshot_project()
        if snapshot is not None:
            self._undo_stack.append(snapshot)
            if len(self._undo_stack) > self.MAX_HISTORY:
                self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._add_history(action, description)

    def _add_history(self, action: str, description: str):
        entry = HistoryEntry(
            timestamp=datetime.now(),
            action=action,
            description=description,
            project_snapshot=self._snapshot_project(),
        )
        self._history.append(entry)
        if len(self._history) > self.MAX_HISTORY * 2:
            self._history = self._history[-self.MAX_HISTORY:]

    def undo(self) -> bool:
        if not self.can_undo:
            return False

        current = self._snapshot_project()
        if current is not None:
            self._redo_stack.append(current)

        snapshot = self._undo_stack.pop()
        self._restore_project(snapshot)
        self._add_history("undo", "Undo last action")
        return True

    def redo(self) -> bool:
        if not self.can_redo:
            return False

        current = self._snapshot_project()
        if current is not None:
            self._undo_stack.append(current)

        snapshot = self._redo_stack.pop()
        self._restore_project(snapshot)
        self._add_history("redo", "Redo last action")
        return True

    def clear_history(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def get_history(self, limit: int = 10) -> list[HistoryEntry]:
        return self._history[-limit:]

    def set_state(self, state: SessionState):
        self._state = state

    def set_task(self, task_name: Optional[str]):
        self._current_task = task_name

    def set_task_status(self, task_name: str, status: dict):
        self._task_status[task_name] = {
            **status,
            "updated_at": datetime.now().isoformat(),
        }

    def get_task_status(self, task_name: str) -> Optional[dict]:
        return self._task_status.get(task_name)

    def get_all_task_status(self) -> dict[str, dict]:
        return dict(self._task_status)

    def set_metadata(self, key: str, value: Any):
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def to_dict(self) -> dict:
        return {
            "project": self._project.to_dict() if self._project else None,
            "state": self._state.value,
            "current_task": self._current_task,
            "task_status": self._task_status,
            "metadata": self._metadata,
            "undo_count": len(self._undo_stack),
            "redo_count": len(self._redo_stack),
            "history_count": len(self._history),
        }

    def clone(self) -> "Session":
        new_session = Session()
        if self._project:
            new_session._project = Project.from_dict(self._project.to_dict())
        new_session._state = self._state
        new_session._current_task = self._current_task
        new_session._task_status = copy.deepcopy(self._task_status)
        new_session._metadata = copy.deepcopy(self._metadata)
        return new_session
