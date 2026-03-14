# StarRailCopilot CLI Architecture SOP

## Overview

StarRailCopilot is an automation tool for Honkai: Star Rail that uses computer vision
and ADB control to automate gameplay tasks. This document describes how to build a
CLI interface that allows AI agents to control the automation system.

## Backend Engine

### Core Components

1. **src.py / StarRailCopilot class**: Main entry point that runs the scheduler loop
2. **module/config/config.py**: Configuration management with YAML/JSON persistence
3. **module/device/device.py**: Device control (screenshot, touch, app management)
4. **tasks/**: Individual task implementations (dungeon, rogue, daily, etc.)

### Data Model

The configuration is stored as JSON files in `config/<config_name>.json`:

```json
{
  "Alas": {
    "Emulator": {
      "Serial": "auto",
      "GameClient": "android",
      "PackageName": "auto",
      ...
    },
    "Optimization": {...}
  },
  "Dungeon": {
    "Scheduler": {
      "Enable": true,
      "NextRun": "2024-01-01 00:00:00",
      "Command": "Dungeon"
    },
    "Dungeon": {
      "Name": "Calyx_Golden_Treasures",
      "Team": 1
    },
    ...
  },
  ...
}
```

### Task System

Tasks are scheduled based on:
- `Scheduler.Enable`: Whether task is active
- `Scheduler.NextRun`: When to run next
- `Scheduler.Command`: Task identifier

Priority is determined by `SCHEDULER_PRIORITY` in config.

## CLI Architecture

### Command Groups

1. **Project Management**: `new`, `load`, `save`, `info`, `status`
2. **Emulator Configuration**: `emulator show`, `emulator set`
3. **Dungeon Configuration**: `dungeon show`, `dungeon set`
4. **Rogue Configuration**: `rogue show`, `rogue set`
5. **Task Management**: `task list`, `task enable`, `task disable`, `task run`
6. **Session Control**: `undo`, `redo`

### State Model

- **Project**: Configuration profile with all settings
- **Session**: Runtime state with undo/redo history
- **TaskRunner**: Executes tasks and tracks results

### Output Formats

- **Human-readable**: Tables, colored messages, status indicators
- **JSON**: Structured output for AI agent consumption via `--json` flag

## Integration Points

### Running Tasks

Tasks are executed by:
1. Writing configuration to `config/<config_name>.json`
2. Invoking `python src.py` with the config name
3. Monitoring stdout/stderr for results

### Configuration Conversion

The CLI maintains its own project format that converts to StarRailCopilot's
native config format when running tasks.

## Key Lessons

### 1. Configuration Synchronization

The CLI project format must stay synchronized with StarRailCopilot's config schema.
Changes to the upstream config structure require updates to the CLI.

### 2. Task Execution Model

Tasks run asynchronously in the main StarRailCopilot process. The CLI spawns
a subprocess and monitors its output.

### 3. State Management

The CLI provides undo/redo for configuration changes, but task execution
state is managed by the underlying StarRailCopilot system.

### 4. Error Handling

Errors from the underlying system must be caught and presented clearly
to AI agents through structured JSON output.

## Directory Structure

```
agent-harness/
├── setup.py
├── STARRAIL.md
└── cli_anything/
    └── starrail/
        ├── __init__.py
        ├── __main__.py
        ├── README.md
        ├── starrail_cli.py
        ├── core/
        │   ├── __init__.py
        │   ├── project.py
        │   ├── session.py
        │   └── task.py
        ├── utils/
        │   ├── __init__.py
        │   └── repl_skin.py
        └── tests/
            ├── __init__.py
            ├── TEST.md
            └── test_core.py
```

## Usage Examples

### Create and Configure

```bash
cli-anything-starrail new farming -o farming.json
cli-anything-starrail -p farming.json emulator set serial "127.0.0.1:5555"
cli-anything-starrail -p farming.json dungeon set name Calyx_Golden_Treasures
cli-anything-starrail -p farming.json task enable Dungeon
```

### Run Tasks

```bash
cli-anything-starrail -p farming.json --json task run dungeon
```

### Interactive REPL

```bash
cli-anything-starrail
starrail> new farming
starrail[farming]> emulator set serial 127.0.0.1:5555
starrail[farming]*> save farming.json
starrail[farming]> task run dungeon
```
