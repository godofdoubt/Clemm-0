Basic cybertient framework for with cuda and llamacpp python module to run space ship like roleplay. Agentic AI crews no ready pure python. CLI and UI option.

correct env file. and paths for tools.

#Windows cuda python 12.9 

#use requirements.txt or ..

py -3.12 -m venv .rvn #create env

.rvn\Scripts\Activate.ps1 # activate

python.exe -m pip install --upgrade pip

pip install --upgrade pip setuptools wheel

pip install python-dotenv pydantic

pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu125 --upgrade --force-reinstall --no-cache-dir

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

pip install requests

#for AMD support and linux install change raven.py and this commands. 

run warpcore.py




