### core/clemmui.py (Matrix UI)

- **Class**: `ClemmMatrixUI(tk.Tk)`
  - Constructor parameters: `crew_instance`, `model`, `max_tokens`, `model_name`, `available_tools`
  - Key features:
    - Crew selector, reset, and ASK/CMD input mode
    - Typewriter output with Matrix rain background
    - Tool shortcuts (Open Notes, Create File, Fire Laser, Launch Missile)
  - Important methods:
    - `process_command()` / `execute_command()` for CLI-like commands within UI
    - `execute_tool(tool_name, tool_args=None)` to run registry tools
    - `process_ask(query)` to talk with active crew
    - `run_code` flow to safely execute last code from `code_expert`

- **Widgets**:
  - `MatrixRain(tk.Canvas)`: animated background
  - `TypewriterText(ScrolledText)`: typewriter-style rendering

- **Function**: `launch_matrix_ui(model_obj, crew_instance, max_tokens)`
  - Detects model name, lists tools, and starts the main loop

Usage:
```python
from core.clemmui import launch_matrix_ui
from bridge.crew import initialize_crew
from core.raven import activate_raven

model_obj = activate_raven('server')
crew = initialize_crew(model_obj, 512)
launch_matrix_ui(model_obj, crew, 512)
```