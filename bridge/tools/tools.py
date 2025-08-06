# bridge/tools/tools.py
import subprocess
import os
import platform
import logging
from .weapon import fire_laser, launch_missile
#from .voice_control import VoiceControl
#disabled in this version
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# --- Tool Functions ---
def open_notes() -> str:
    """Opens the Notes.txt file, attempting cross-platform compatibility."""
    notes_path = "\Clemm-0\bridge\tools\Captains_Log.txt"   #correct path 
    try:
        if platform.system() == 'Windows':
            os.startfile(notes_path)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', notes_path])
        else:
            subprocess.run(['xdg-open', notes_path])
        return "Successfully opened Captains_Log.txt."
    except FileNotFoundError:
        logging.error("Captains_Log.txt file not found at %s", notes_path)
        return "Error: Captains_Log.txt file not found."
    except Exception as e:
        logging.exception("Unexpected error opening Captains_Log.txt:")
        return f"Error opening Captains_Log.txt: {e}"

def create_new_file(filename: str = "new_file.txt", content: str = "This is a new file created by Clemm.") -> str:
    """Creates a new text file with specified filename and content."""
    output_dir = "output_files"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully created file: {filepath}"
    except Exception as e:
        logging.exception("Error creating file:")
        return f"Error creating file: {e}"

def status_log(filename: str) -> str:
    """Reads the content of a text file from the output directory."""
    output_dir = "output_files"
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return f"Successfully read file: {filepath}\nContent:\n{content}"
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file: {e}"

@dataclass
class Tool:
    description: str
    function: Callable[..., str]
    parameters: Optional[List[str]] = None
    crew_dependent: bool = False

TOOL_LIST: Dict[str, Tool] = {
    "open_notes": Tool(
        description="Opens the Captains_Log.txt file for viewing.",
        function=open_notes
    ),
    "create_file": Tool(
        description="Creates a new text file. You can specify the filename and content.",
        function=create_new_file,
        parameters=["filename", "content"]
    ),
    "fire_laser": Tool(
        description="Fires the laser weapon.",
        function=fire_laser,
        parameters=["target", "power_level"]
    ),
    "launch_missile": Tool(
        description="Launches a missile.",
        function=launch_missile,
        parameters=["target", "warhead_type"]
    ),
    # --- FIXED status_log DEFINITION ---
    "status_log": Tool(
        description="Reads the content of a text file from the output directory.",
        function=status_log,
        parameters=["filename"] # <-- ADDED MISSING PARAMETER
    )
    # "mainstream": Tool(
    #    description="Launches the Streamlit interface.",
    #    function=run_mainstream,
    #    crew_dependent=True
    # )
}

def get_tool_description(tool_name: str) -> Optional[str]:
    """Returns the description of a tool along with its parameters if available."""
    tool = TOOL_LIST.get(tool_name)
    if tool:
        params_info = f" Parameters: {', '.join(tool.parameters)}" if tool.parameters else " Parameters: None"
        return f"{tool_name}: {tool.description}{params_info}"
    return None

def list_tools() -> List[str]:
    """Returns a list of available tool names."""
    return list(TOOL_LIST.keys())

def run_tool(tool_name: str, crew_instance=None, model=None, **kwargs: Any) -> str:
    """Runs a tool function by name, handling crew dependency."""
    tool = TOOL_LIST.get(tool_name)
    if not tool:
        return f"Tool '{tool_name}' not found."
    if tool.crew_dependent:
        if crew_instance is None:
            return "Error: This tool requires a crew instance."
        return tool.function(crew_instance=crew_instance, model=model, **kwargs)
    return tool.function(**kwargs)
