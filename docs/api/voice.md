### bridge/tools/voice.py (Optional prototype)

- **Class**: `VoiceControl`
  - Text-to-speech, speech recognition, and command registry
  - Built-in commands: web/search, jokes, notes, system actions, and weapons passthrough

Notes:
- Requires additional packages (e.g., `speech_recognition`, `pyttsx3`, `pyjokes`, `pyautogui`, `wikipedia`, `playwright`)
- Platform-dependent behavior; some actions are Windows-only

Basic usage:
```python
from bridge.tools.voice import VoiceControl
vc = VoiceControl()
vc.run()  # loop; say 'exit' to quit
```

Weapon handlers delegate to `bridge.tools.weapon` functions.