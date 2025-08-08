### core/raven.py

- **Function**: `load_gguf_model(system_prompt=None)`
  - Loads a GGUF model using `llama_cpp.Llama` with CUDA offload
  - Env: `RAVEN_GGUF_MODEL_PATH`, `CPU_THREADS`, `CONTEXT_SIZE`
  - Returns: `Llama` instance or `None`

- **Function**: `format_prompt(messages: list[dict], add_generation_prompt=True) -> str`
  - Formats chat messages for Qwen2-style prompts

- **Function**: `generate_response(model_obj, messages, max_tokens=72, temperature=0.8, top_k=50, top_p=0.95, repetition_penalty=1.15, stream=False)`
  - Dispatches to local or server generation based on `model_obj["type"]`

- **Function**: `generate_local_response(model, messages, ...)`
  - Uses `Llama.__call__` to get text from local GGUF model

- **Function**: `generate_server_response(model_obj, messages, ...)`
  - Calls Llama.cpp server `/completion` endpoint; supports streaming

- **Function**: `get_raven_prompt() -> str`
  - Builds a persona prompt and embeds tool descriptions from `bridge.tools.tools`

- **Function**: `activate_raven(backend='cuda') -> dict | None`
  - CUDA: returns `{ "model": Llama, "type": "programmatic_gguf", "process": None }`
  - Server: auto-starts server, waits for health, returns `{ "url", "type": "llamacpp_server", "process" }`
  - Env (server): `LLAMACPP_SERVER_EXECUTABLE_PATH`, `RAVEN_GGUF_MODEL_PATH`, `LLAMACPP_SERVER_URL`, `SERVER_CONTEXT_SIZE`, `SERVER_GPU_LAYERS`

- **Function**: `main()`
  - Standalone interactive loop for testing Raven directly

Example (non-streamed):
```python
from core import raven
model_obj = raven.activate_raven(backend='server')
messages = [{"role": "system", "content": raven.get_raven_prompt()}, {"role": "user", "content": "Hello"}]
text = raven.generate_response(model_obj, messages, max_tokens=128)
print(text)
```