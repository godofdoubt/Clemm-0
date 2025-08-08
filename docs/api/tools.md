### bridge/tools/tools.py

- **Dataclass**: `Tool`
  - `description: str`
  - `function: Callable[..., str]`
  - `parameters: list[str] | None`
  - `crew_dependent: bool = False`

- **Registry**: `TOOL_LIST`
  - `open_notes()`
    - Opens `Captains_Log.txt` with system default app
    - Returns status string
  - `create_file(filename: str, content: str)` → `create_new_file`
    - Writes file to `output_files/`
  - `status_log(filename: str)`
    - Reads file from `output_files/`
  - `fire_laser(target: str, power_level: str)`
  - `launch_missile(target: str, warhead_type: str)`

- **Functions**
  - `list_tools() -> list[str]`
  - `get_tool_description(tool_name: str) -> str | None`
  - `run_tool(tool_name: str, crew_instance=None, model=None, **kwargs) -> str`

Python usage:
```python
from bridge.tools.tools import list_tools, run_tool, get_tool_description
print(list_tools())
print(get_tool_description('create_file'))
print(run_tool('create_file', filename='test.txt', content='hello'))
print(run_tool('status_log', filename='test.txt'))
```

In-model tool command (from `Crew.chat`):
```text
run_tool create_file filename="report.txt", content="Sales up"
```