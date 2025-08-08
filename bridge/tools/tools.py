# bridge/tools/tools.py
import subprocess
import os
import platform
import logging
import re
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

def ask_crew(crew_member: str, question: str, context: str = "", *, crew_instance: Any = None, model: Any = None) -> str:
    """Delegates a question to another crew member and returns their response.

    Accepts either:
    - crew_instance: an object with attribute 'crew_registry' that is a dict[str, Crew]
    - crew_instance: a dict[str, Crew] directly (e.g., console passes the crew map)
    """
    if crew_instance is None:
        return "Error: This tool requires a crew instance."

    crew_registry = None
    if isinstance(crew_instance, dict):
        crew_registry = crew_instance
    else:
        crew_registry = getattr(crew_instance, "crew_registry", None)

    if not isinstance(crew_registry, dict):
        return "Error: Crew registry not available from the provided crew instance."

    target_key = (crew_member or "").strip()
    if target_key.lower() == "crew":
        target_key = "tool_crew"

    if target_key not in crew_registry:
        available = ", ".join(sorted(crew_registry.keys()))
        return f"Error: Crew member '{crew_member}' not found. Available: {available}"

    target = crew_registry[target_key]

    try:
        full_question = question if not context else f"{context}\n\n{question}"
        delegated_response = target.chat(full_question)

        # If the delegated crew returns a tool command, execute it immediately
        if isinstance(delegated_response, str):
            match = re.match(r"^\s*run_tool\s+([a-zA-Z0-9_]+)\s*(.*)$", delegated_response.strip())
            if match:
                tool_name = match.group(1).strip()
                params_str = match.group(2).strip()
                kwargs: Dict[str, Any] = {}
                if params_str:
                    param_pairs = re.findall(r'(\w+)\s*=\s*("([^"]*)"|\'([^\']*)\'|([^,]+))', params_str)
                    for key, _, q1, q2, unq in param_pairs:
                        value = q1 if q1 is not None else q2
                        if value is None:
                            value = (unq or "").strip()
                        kwargs[key.strip()] = value
                result = run_tool(tool_name, crew_instance=crew_instance, model=model, **kwargs)
                return result

        return delegated_response
    except Exception as e:
        logging.exception("Error while delegating to crew member:")
        return f"Error asking crew member '{target_key}': {e}"

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
    ),
    "ask_crew": Tool(
        description="Delegates a question to another crew member and returns their response.",
        function=ask_crew,
        parameters=["crew_member", "question", "context"],
        crew_dependent=True
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
