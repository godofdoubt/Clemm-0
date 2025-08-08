### bridge/crew.py

- **Class**: `Crew`
  - Fields: `name`, `system_prompt`, `model` (model_obj dict), `max_tokens`, `temperature`, `top_k`, `top_p`, `repetition_penalty`, `messages`, `available_tools`
  - On init: seeds `messages` with system prompt

- **Method**: `chat(user_input: str) -> str`
  - Appends user message, calls `raven.generate_response`
  - Strips `<think>...</think>` blocks
  - Parses `run_tool ...` commands; executes via `bridge.tools.tools.run_tool`
  - Returns combined conversational text and tool results

- **Method**: `reset()`
  - Resets conversation to system prompt only

- **Function**: `initialize_crew(model_obj, max_tokens_console) -> dict[str, Crew]`
  - Creates crews: `captain_raven`, `code_expert`, `tool_crew`, `creative_writer`
  - `tool_crew` is deterministic and outputs only tool commands

Example:
```python
from bridge.crew import initialize_crew
from core.raven import activate_raven

model_obj = activate_raven('server')
crew = initialize_crew(model_obj, max_tokens_console=512)

reply = crew["captain_raven"].chat("Open my notes")
print(reply)

crew["code_expert"].reset()
```