### core/core.py

- **Function**: `start_core()`
- **Purpose**: Interactive startup to select backend, initialize Raven, assemble crew, and choose UI.

Flow:
1. Prompt backend: `1` CUDA (local `llama_cpp_python`), `2` Llama.cpp server
2. Activate Raven via `core.raven.activate_raven(backend)`
3. Prompt for `max_tokens`
4. Build crew via `bridge.crew.initialize_crew(model_obj, max_tokens)`
5. Choose interface: `1` Matrix UI (`core.clemmui.launch_matrix_ui`) or `2` Console UI (`core.clemm_console.clemm_console`)
6. If server backend was started, ensures graceful shutdown on exit

Example session:
```text
Choose backend for Raven:
1 - CUDA (local library)
2 - LlamaCPP Server
Enter your choice (1/2): 2
Core systems online. Initiating Raven with SERVER backend...
Enter maximum response length (default is 1022): 512
Choose interface:
1 - Matrix UI
2 - Console UI
Enter your choice (1/2): 1
```