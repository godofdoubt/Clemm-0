Basic cybertient framework for with cuda and llamacpp python module to run space ship like roleplay. Agentic AI crews no ready pure python. CLI and UI option.

correct env file. and paths for tools.

#Windows cuda 12.9 

py -3.12 -m venv .rvn #create env

.rvn\Scripts\Activate.ps1 # activate


python.exe -m pip install --upgrade pip

pip install --upgrade pip setuptools wheel

pip install python-dotenv pydantic

pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu125 --upgrade --force-reinstall --no-cache-dir

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

pip install requests

#this should work or re

for linux and not cuda change this commands and  correct raven.py

run warpcore.py




