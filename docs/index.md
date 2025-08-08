# CLEMM Project Documentation

## Overview
This project is a spaceship-themed, agentic AI framework powered by Llama (GGUF) that offers both a console interface and a Tkinter Matrix UI. It includes:
- Core model activation and response generation (`core.raven`, `core.core`)
- Crew orchestration and memory (`bridge.crew`)
- Tool registry and actions (`bridge.tools.tools`, `bridge.tools.weapon`)
- User interfaces (`core.clemmui`, `core.clemm_console`)
- Optional voice control prototype (`bridge.tools.voice`)
- Entry point (`warp-core.py`)

## Quick start
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (example)
export WARP_DRIVE_KEY="example-strong-key"
export RAVEN_GGUF_MODEL_PATH="/absolute/path/to/model.gguf"
# If using server backend
export LLAMACPP_SERVER_EXECUTABLE_PATH="/absolute/path/to/llama.cpp/server"
export LLAMACPP_SERVER_URL="http://127.0.0.1:8080"

# Launch
python warp-core.py
```

## API Reference
- Core
  - [Warp Core](./api/warp_core.md)
  - [Core Startup](./api/core.md)
  - [Raven Model API](./api/raven.md)
- Bridge
  - [Crew and Orchestration](./api/crew.md)
  - [Tools Registry and Built-ins](./api/tools.md)
  - [Weapons API](./api/weapon.md)
- Interfaces
  - [Matrix UI (Tkinter)](./api/ui.md)
  - [Console UI](./api/console.md)
- Optional
  - [Voice Control (prototype)](./api/voice.md)