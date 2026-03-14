# cli-anything-starrail

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[StarRailCopilot](https://github.com/LmeSzinc/StarRailCopilot) 的命令行接口，允许 AI 智能体在没有 GUI 或 Web 界面的情况下控制《崩坏：星穹铁道》自动化。

## 功能特性

- **双模式**：交互式 REPL 模式和命令行子命令模式
- **JSON 输出**：通过 `--json` 标志提供机器可读的输出，便于 AI 智能体消费
- **有状态会话**：完整的撤销/重做支持
- **任务管理**：启用、禁用和运行自动化任务
- **配置管理**：完全控制模拟器、副本和模拟宇宙设置
- **项目文件**：以 JSON 或 YAML 格式保存和加载配置文件

## 安装

### 从 GitHub 安装

```bash
pip install git+https://github.com/awaxiaoyu/cli-anything-starrail.git
```

### 从源码安装

```bash
git clone https://github.com/awaxiaoyu/cli-anything-starrail.git
cd cli-anything-starrail
pip install -e .
```

## 前置条件

- Python 3.10+
- [StarRailCopilot](https://github.com/LmeSzinc/StarRailCopilot) 已安装并配置
- 已安装《崩坏：星穹铁道》的模拟器或设备
- ADB 已连接到模拟器/设备

## 快速开始

### 1. 连接模拟器

```bash
# MuMu 12
adb connect 127.0.0.1:16384

# 蓝叠 / 雷电
adb connect 127.0.0.1:5555

# 验证连接
adb devices
```

### 2. 创建配置

```bash
# 创建新项目
cli-anything-starrail new my_config -o my_config.json

# 配置模拟器
cli-anything-starrail -p my_config.json emulator set serial 127.0.0.1:16384

# 配置副本
cli-anything-starrail -p my_config.json dungeon set name Calyx_Golden_Treasures
cli-anything-starrail -p my_config.json dungeon set team 1

# 启用并运行任务
cli-anything-starrail -p my_config.json task enable Dungeon
cli-anything-starrail -p my_config.json task run dungeon
```

### 3. 交互式 REPL 模式

```bash
cli-anything-starrail
```

```
╭──────────────────────────────────────────────────────────────────────╮
│  ◆  cli-anything · Starrail                                         │
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

## 命令参考

### 项目管理

| 命令 | 描述 |
|------|------|
| `new <name>` | 创建新项目 |
| `load <path>` | 加载项目文件 |
| `save [path]` | 保存当前项目 |
| `info` | 显示项目信息 |
| `status` | 显示会话状态 |

### 模拟器配置

| 命令 | 描述 |
|------|------|
| `emulator show` | 显示模拟器配置 |
| `emulator set <key> <value>` | 设置模拟器选项 |

**有效键名**：`serial`、`game_client`、`package_name`、`game_language`、`screenshot_method`、`control_method`

### 副本配置

| 命令 | 描述 |
|------|------|
| `dungeon show` | 显示副本配置 |
| `dungeon set <key> <value>` | 设置副本选项 |

**有效键名**：`name`、`team`、`use_support`、`support_character`、`stamina_consume`、`stamina_fuel`

### 模拟宇宙配置

| 命令 | 描述 |
|------|------|
| `rogue show` | 显示模拟宇宙配置 |
| `rogue set <key> <value>` | 设置模拟宇宙选项 |

**有效键名**：`world`、`path`、`team`、`use_support`、`support_character`、`bonus`

### 任务管理

| 命令 | 描述 |
|------|------|
| `task list` | 列出可用任务 |
| `task enable <name>` | 启用任务 |
| `task disable <name>` | 禁用任务 |
| `task run <name>` | 运行任务 |

### 会话管理

| 命令 | 描述 |
|------|------|
| `undo` | 撤销上一步操作 |
| `redo` | 重做上一步操作 |
| `help` | 显示帮助 |
| `quit` | 退出 REPL |

## 可用任务

| 任务 | 描述 |
|------|------|
| `dungeon` | 副本刷取 |
| `weekly` | 周本（历战余响） |
| `daily_quest` | 完成每日任务 |
| `battle_pass` | 领取无名勋礼奖励 |
| `assignment` | 委托派遣和领取 |
| `data_update` | 更新角色/物品数据 |
| `freebies` | 领取邮件和兑换码 |
| `rogue` | 模拟宇宙 |
| `ornament` | 凝滞虚影 |
| `benchmark` | 性能测试 |
| `daemon` | 守护进程模式（持续运行） |
| `planner_scan` | 扫描养成材料 |

## JSON 输出（供 AI 智能体使用）

所有命令都支持 `--json` 标志，提供结构化的可解析输出：

```bash
cli-anything-starrail --json task list
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
cli-anything-starrail --json -p config.json task run dungeon
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

## 项目结构

```
cli-anything-starrail/
├── setup.py                 # 包安装配置
├── STARRAIL.md              # 架构文档
└── cli_anything/
    └── starrail/
        ├── __init__.py
        ├── __main__.py      # python -m 入口
        ├── README.md        # 详细使用指南
        ├── starrail_cli.py  # 主 CLI 实现
        ├── core/
        │   ├── project.py   # 项目和配置管理
        │   ├── session.py   # 会话和撤销/重做
        │   └── task.py      # 任务执行
        ├── utils/
        │   └── repl_skin.py # 终端 UI 样式
        └── tests/
            └── test_core.py # 单元测试
```

## 开发

### 运行测试

```bash
pytest cli_anything/starrail/tests/ -v
```

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

## AI 智能体集成

此 CLI 专为 AI 智能体设计，易于使用：

1. **发现**：在任何命令上使用 `--help` 发现可用选项
2. **JSON 输出**：使用 `--json` 标志获取结构化的可解析输出
3. **状态检查**：使用 `info` 和 `status` 命令了解当前状态
4. **错误处理**：错误以 JSON 格式返回，带有清晰的消息

### AI 智能体工作流示例

```python
import subprocess
import json

def run_cli(args: list[str]) -> dict:
    result = subprocess.run(
        ["cli-anything-starrail", "--json"] + args,
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# 创建并配置
run_cli(["new", "farming", "-o", "farming.json"])
run_cli(["-p", "farming.json", "emulator", "set", "serial", "127.0.0.1:16384"])
run_cli(["-p", "farming.json", "task", "enable", "Dungeon"])

# 运行任务
result = run_cli(["-p", "farming.json", "task", "run", "dungeon"])
print(f"状态: {result['status']}")
```

## 相关项目

- [StarRailCopilot](https://github.com/LmeSzinc/StarRailCopilot) - 主要的自动化项目
- [CLI-Anything](https://github.com/your-repo/cli-anything) - CLI 框架模式

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。
