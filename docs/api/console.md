### core/clemm_console.py (Console UI)

- **Function**: `clemm_console(model, crew, max_tokens)`
  - Text console with commands and tool integration

Commands:
- `help` — Show commands and available tools
- `status` — System status
- `destination` — Show current destination
- `crew` — List crew names
- `use <name>` — Switch crew (`crew` maps to `tool_crew`)
- `reset` — Reset active crew memory
- `ask <question>` — Ask active crew
- `run_code` — Execute last code from `code_expert` (with confirmation)
- `run_tool <tool_name>` — Run tool without args, or reply-driven with args
- `exit` — Quit console

Run:
```python
from core.clemm_console import clemm_console
# Given model_obj and crew dict
d = clemm_console(model_obj, crew, 512)
```