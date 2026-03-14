# Test Plan and Results for cli-anything-starrail

## Test Inventory Plan

- `test_core.py`: ~30 unit tests planned
- `test_full_e2e.py`: ~10 E2E tests planned

## Unit Test Plan

### Module: `project.py`

| Function | Tests | Edge Cases |
|----------|-------|------------|
| `TaskConfig.create` | 2 | Default values, custom values |
| `TaskConfig.to_dict/from_dict` | 2 | Round-trip, None values |
| `EmulatorConfig.create` | 2 | Default values, custom serial |
| `DungeonConfig.create` | 2 | Default, with support |
| `RogueConfig.create` | 2 | Default, with bonus |
| `Project.create` | 2 | Default tasks initialized |
| `Project.to_dict/from_dict` | 2 | Round-trip |
| `create_project` | 1 | Basic creation |
| `load_project` | 2 | JSON, YAML formats |
| `save_project` | 2 | JSON, YAML formats |
| `project_to_src_config` | 2 | Conversion correctness |

**Estimated: 21 tests**

### Module: `session.py`

| Function | Tests | Edge Cases |
|----------|-------|------------|
| `Session.create` | 2 | Empty, with project |
| `Session.undo/redo` | 3 | Basic, empty stack, limit |
| `Session.state` | 2 | State transitions |
| `Session.task_status` | 2 | Set/get/clear |
| `Session.to_dict` | 1 | Serialization |

**Estimated: 10 tests**

### Module: `task.py`

| Function | Tests | Edge Cases |
|----------|-------|------------|
| `TaskRunner.available_tasks` | 1 | List correctness |
| `TaskRunner.task_info` | 2 | Known/unknown task |
| `TaskRunner.run_task` | 2 | Unknown task, no project |
| `TaskResult.to_dict` | 1 | Serialization |

**Estimated: 6 tests**

### Module: `repl_skin.py`

| Function | Tests | Edge Cases |
|----------|-------|------------|
| `ReplSkin.create` | 1 | Basic creation |
| `ReplSkin.prompt` | 2 | With/without project |

**Estimated: 3 tests**

## E2E Test Plan

### Workflow: Project Lifecycle

1. Create new project
2. Configure emulator settings
3. Configure dungeon settings
4. Enable tasks
5. Save to file
6. Load from file
7. Verify all settings preserved

### Workflow: Session Management

1. Create project
2. Make modifications
3. Undo modifications
4. Redo modifications
5. Verify state consistency

### Workflow: Task Configuration

1. Create project
2. Enable multiple tasks
3. Disable tasks
4. Verify task states

### Workflow: JSON Output

1. Run commands with --json flag
2. Verify JSON structure
3. Verify all fields present

### Workflow: CLI Subprocess

1. Install package
2. Run `cli-anything-starrail --help`
3. Run `cli-anything-starrail --version`
4. Run `cli-anything-starrail new test --json`
5. Verify JSON output

---

## Test Results

*Tests will be run after implementation is complete.*

```
================================ Test Summary ================================
(Results will be appended here after running pytest)
```
