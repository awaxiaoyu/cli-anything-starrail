# cli-anything-starrail

A stateful CLI interface for StarRailCopilot that allows AI agents to control
Honkai: Star Rail automation without needing the GUI or web interface.

## Features

- **Stateful REPL Mode**: Interactive session with undo/redo support
- **JSON Output**: Machine-readable output for AI agent consumption
- **Task Management**: Enable, disable, and run automation tasks
- **Configuration Management**: Full control over emulator, dungeon, and rogue settings
- **Project Files**: Save and load configuration profiles

## Installation

```bash
# From source
cd agent-harness
pip install -e .
```

## Prerequisites

- Python 3.10+
- StarRailCopilot installed and configured
- An emulator or device with Honkai: Star Rail installed

## Usage

### REPL Mode (Interactive)

```bash
cli-anything-starrail
```

This opens an interactive REPL where you can manage projects and run tasks.

### Subcommand Mode (Scripting)

```bash
# Create a new project
cli-anything-starrail new my_config -o config.json

# Load and configure
cli-anything-starrail -p config.json emulator set serial "127.0.0.1:5555"
cli-anything-starrail -p config.json dungeon set name "Calyx_Golden_Treasures"
cli-anything-starrail -p config.json dungeon set team 1

# Enable and run tasks
cli-anything-starrail -p config.json task enable Dungeon
cli-anything-starrail -p config.json task run dungeon

# Save changes
cli-anything-starrail -p config.json save
```

### JSON Output (for AI Agents)

```bash
# All commands support --json flag
cli-anything-starrail --json -p config.json info
```

## Available Commands

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

Valid keys: `serial`, `game_client`, `package_name`, `game_language`, `screenshot_method`, `control_method`

### Dungeon Configuration

| Command | Description |
|---------|-------------|
| `dungeon show` | Show dungeon configuration |
| `dungeon set <key> <value>` | Set dungeon option |

Valid keys: `name`, `team`, `use_support`, `support_character`, `stamina_consume`, `stamina_fuel`

### Rogue Configuration

| Command | Description |
|---------|-------------|
| `rogue show` | Show rogue configuration |
| `rogue set <key> <value>` | Set rogue option |

Valid keys: `world`, `path`, `team`, `use_support`, `support_character`, `bonus`

### Task Management

| Command | Description |
|---------|-------------|
| `task list` | List available tasks |
| `task enable <name>` | Enable a task |
| `task disable <name>` | Disable a task |
| `task run <name>` | Run a task |

### Available Tasks

- `dungeon` - Run dungeon farming
- `weekly` - Run weekly dungeon
- `daily_quest` - Complete daily quests
- `battle_pass` - Claim battle pass rewards
- `assignment` - Dispatch and claim assignments
- `data_update` - Update character/item data
- `freebies` - Claim mail and redeem codes
- `rogue` - Run Simulated Universe
- `ornament` - Run Ornament Extractions
- `benchmark` - Run performance benchmark
- `daemon` - Run daemon mode (continuous)
- `planner_scan` - Scan materials for planner

### Session Management

| Command | Description |
|---------|-------------|
| `undo` | Undo last action |
| `redo` | Redo last action |
| `help` | Show help |
| `quit` | Exit REPL |

## Example Workflow

```bash
# Start REPL
cli-anything-starrail

# In REPL:
starrail> new farming_config
starrail[farming_config]> emulator set serial 127.0.0.1:5555
starrail[farming_config]*> dungeon set name Calx_Golden_Treasures
starrail[farming_config]*> dungeon set team 1
starrail[farming_config]*> task enable Dungeon
starrail[farming_config]*> save farming_config.json
starrail[farming_config]> task run dungeon
starrail[farming_config]> quit
```

## Integration with AI Agents

The CLI is designed to be easily used by AI agents:

1. **Discovery**: Use `--help` on any command to discover available options
2. **JSON Output**: Use `--json` flag for structured, parseable output
3. **State Inspection**: Use `info` and `status` commands to understand current state
4. **Error Handling**: Errors are returned in JSON format with clear messages

## License

MIT License - See LICENSE file for details.
