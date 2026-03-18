# StarRailCopilotPro

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**[中文文档](README.md)** | English Documentation

A professional CLI interface for [StarRailCopilot](https://github.com/LmeSzinc/StarRailCopilot) that allows AI agents to control Honkai: Star Rail automation without needing the GUI or web interface.

## ✨ Features

- **Dual Mode**: Interactive REPL mode and command-line subcommand mode
- **JSON Output**: Machine-readable output for AI agent consumption via `--json` flag
- **Stateful Session**: Full undo/redo support for configuration changes
- **Task Management**: Enable, disable, and run automation tasks
- **Configuration Management**: Complete control over emulator, dungeon, and rogue settings
- **Project Files**: Save and load configuration profiles in JSON or YAML format
- **Version Compatibility**: Automatic detection of StarRailCopilot version and compatibility checking

## 📦 Installation

### From GitHub

```bash
pip install git+https://github.com/awaxiaoyu/cli-anything-starrail.git
```

### From Source

```bash
git clone https://github.com/awaxiaoyu/cli-anything-starrail.git
cd cli-anything-starrail
pip install -e .
```

## 🔧 Prerequisites

- Python 3.10+
- [StarRailCopilot](https://github.com/LmeSzinc/StarRailCopilot) installed and configured
- An emulator or device with Honkai: Star Rail installed
- ADB connection to your emulator/device

## 🚀 Quick Start

### 1. Connect Your Emulator

```bash
# MuMu 12
adb connect 127.0.0.1:16384

# BlueStacks / LDPlayer
adb connect 127.0.0.1:5555

# Verify connection
adb devices
```

### 2. Create a Configuration

```bash
# Create new project
starrail-pro new my_config -o my_config.json

# Configure emulator
starrail-pro -p my_config.json emulator set serial 127.0.0.1:16384

# Configure dungeon
starrail-pro -p my_config.json dungeon set name Calyx_Golden_Treasures
starrail-pro -p my_config.json dungeon set team 1

# Enable and run task
starrail-pro -p my_config.json task enable Dungeon
starrail-pro -p my_config.json task run dungeon
```

### 3. Interactive REPL Mode

```bash
starrail-pro
```

```
╭──────────────────────────────────────────────────────────────────────╮
│  ◆  StarRailCopilotPro                                              │
│     v1.0.0                                                          │
│                                                                      │
│     Type help for commands, quit to exit                            │
╰──────────────────────────────────────────────────────────────────────╯

starrail ❯ new farming
starrail[farming]> emulator set serial 127.0.0.1:16384
starrail[farming]*> dungeon set name Calyx_Golden_Treasures
starrail[farming]*> task enable Dungeon
starrail[farming]*> save farming.json
starrail[farming]> task run dungeon
```

## 📖 Command Reference

### Project Management

| Command | Description |
|---------|-------------|
| `new <name>` | Create a new project |
| `load <path>` | Load a project file |
| `save [path]` | Save current project |
| `info` | Show project information |
| `status` | Show session status |

### Emulator Configuration

| Command | Description |
|---------|-------------|
| `emulator show` | Show emulator configuration |
| `emulator set <key> <value>` | Set emulator option |

**Valid keys**: `serial`, `game_client`, `package_name`, `game_language`, `screenshot_method`, `control_method`

### Dungeon Configuration

| Command | Description |
|---------|-------------|
| `dungeon show` | Show dungeon configuration |
| `dungeon set <key> <value>` | Set dungeon option |

**Valid keys**: `name`, `team`, `use_support`, `support_character`, `stamina_consume`, `stamina_fuel`

### Rogue Configuration

| Command | Description |
|---------|-------------|
| `rogue show` | Show rogue configuration |
| `rogue set <key> <value>` | Set rogue option |

**Valid keys**: `world`, `path`, `team`, `use_support`, `support_character`, `bonus`

### Task Management

| Command | Description |
|---------|-------------|
| `task list` | List available tasks |
| `task enable <name>` | Enable a task |
| `task disable <name>` | Disable a task |
| `task run <name>` | Run a task |

### Session Management

| Command | Description |
|---------|-------------|
| `undo` | Undo last action |
| `redo` | Redo last action |
| `help` | Show help |
| `quit` | Exit REPL |

## 🎮 Available Tasks

| Task | Description |
|------|-------------|
| `dungeon` | Run dungeon farming |
| `weekly` | Run weekly dungeon (Echo of War) |
| `daily_quest` | Complete daily quests |
| `battle_pass` | Claim battle pass rewards |
| `assignment` | Dispatch and claim assignments |
| `data_update` | Update character/item data |
| `freebies` | Claim mail and redeem codes |
| `rogue` | Run Simulated Universe |
| `ornament` | Run Ornament Extractions |
| `benchmark` | Run performance benchmark |
| `daemon` | Run daemon mode (continuous) |
| `planner_scan` | Scan materials for planner |

## 🤖 JSON Output (for AI Agents)

All commands support the `--json` flag for structured, parseable output:

```bash
starrail-pro --json task list
```

```json
{
  "tasks": [
    "dungeon",
    "weekly",
    "daily_quest",
    ...
  ]
}
```

```bash
starrail-pro --json -p config.json task run dungeon
```

```json
{
  "task_name": "dungeon",
  "status": "success",
  "start_time": "2024-01-01T12:00:00",
  "end_time": "2024-01-01T12:05:00",
  "duration": 300.0,
  "message": "Task dungeon completed successfully",
  "error": null,
  "data": {}
}
```

## 📁 Project Structure

```
starrailcopilotpro/
├── setup.py                 # Package installation
├── STARRAIL.md              # Architecture documentation
└── cli_anything/
    └── starrail/
        ├── __init__.py
        ├── __main__.py      # python -m entry point
        ├── README.md        # Detailed usage guide
        ├── starrail_cli.py  # Main CLI implementation
        ├── core/
        │   ├── project.py   # Project & configuration management
        │   ├── session.py   # Session & undo/redo
        │   ├── task.py      # Task execution
        │   ├── mapping.py   # Configuration mapping
        │   └── version.py   # Version detection
        ├── utils/
        │   └── repl_skin.py # Terminal UI styling
        └── tests/
            └── test_core.py # Unit tests
```

## 🔨 Development

### Run Tests

```bash
pytest cli_anything/starrail/tests/ -v
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

## 🤝 Integration with AI Agents

This CLI is designed to be easily used by AI agents:

1. **Discovery**: Use `--help` on any command to discover available options
2. **JSON Output**: Use `--json` flag for structured, parseable output
3. **State Inspection**: Use `info` and `status` commands to understand current state
4. **Error Handling**: Errors are returned in JSON format with clear messages

### Example AI Agent Workflow

```python
import subprocess
import json

def run_cli(args: list[str]) -> dict:
    result = subprocess.run(
        ["starrail-pro", "--json"] + args,
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# Create and configure
run_cli(["new", "farming", "-o", "farming.json"])
run_cli(["-p", "farming.json", "emulator", "set", "serial", "127.0.0.1:16384"])
run_cli(["-p", "farming.json", "task", "enable", "Dungeon"])

# Run task
result = run_cli(["-p", "farming.json", "task", "run", "dungeon"])
print(f"Status: {result['status']}")
```

## 🔗 Related Projects

- [StarRailCopilot](https://github.com/LmeSzinc/StarRailCopilot) - The main automation project
- [CLI-Anything](https://github.com/your-repo/cli-anything) - The CLI framework pattern

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
