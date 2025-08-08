### warp-core.py

- **Function**: `initialize_warp_drive()`
- **Purpose**: Validates `WARP_DRIVE_KEY` and starts the core system.
- **Environment**:
  - `WARP_DRIVE_KEY`: any non-empty key length > 8

Usage:
```bash
python warp-core.py
```

Programmatic:
```python
from warp_core import initialize_warp_drive
initialize_warp_drive()
```

Behavior:
- Loads `.env`
- Validates `WARP_DRIVE_KEY`
- Imports `core.core` and calls `start_core()`