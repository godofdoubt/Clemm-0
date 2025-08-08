
# bridge/crew.py

import core.raven as raven
from .tools.tools import get_tool_description, list_tools, run_tool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from core.raven import get_raven_prompt
import re # <-- Ensure re is imported

class Crew(BaseModel):
    name: str
    system_prompt: str
    model: Any  # This will now hold the entire model_obj dictionary
    max_tokens: int = Field(default=512, gt=0)
    temperature: float = Field(default=0.8, ge=0.0, le=2.0)
    top_k: int = 50
    top_p: float = 0.95
    repetition_penalty: float = 1.15
    messages: List[Dict[str, str]] = []
    available_tools: List[str] = []
    crew_registry: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self.messages = [{"role": "system", "content": self.system_prompt}]

# bridge/crew.py

# ... (imports and class definition remain the same) ...

    def chat(self, user_input: str) -> str:
        """Chats with the crew, maintaining conversation history and handling tool execution."""
        self.messages.append({"role": "user", "content": user_input})
        output_responses = []

        while True:
            response = raven.generate_response(
                self.model,
                self.messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_k=self.top_k,
                top_p=self.top_p,
                repetition_penalty=self.repetition_penalty,
                stream=False
            )

            # --- ADDED: STRIP <think> TAGS ---
            # Remove the <think>...</think> block before any other processing.
            response = re.sub(r'<think>.*?</think>\s*', '', response, flags=re.DOTALL).strip()


            # --- ROBUST TOOL PARSING LOGIC ---
            # Use regex to find all "run_tool" commands in the response.
            tool_calls = re.finditer(r'run_tool\s+([a-zA-Z0-9_]+)\s*(.*)', response)
            commands_found = list(tool_calls) # Materialize iterator to check if it's empty
            
            # --- MODIFIED TOOL HANDLING LOGIC ---
            if commands_found:
                # Extract conversational text that might appear before the command
                preamble = response.split("run_tool")[0].strip()
                if preamble:
                    output_responses.append(preamble)
                    # Add only the conversational part back to history, not the tool command
                    self.messages.append({"role": "assistant", "content": preamble})

                for match in commands_found:
                    tool_name = match.group(1).strip()
                    params_str = match.group(2).strip()
                    params = {}

                    if params_str:
                        # Improved parsing for key="value" or key=value pairs
                        param_pairs = re.findall(r'(\w+)\s*=\s*("([^"]*)"|\'([^\']*)\'|([^,]+))', params_str)
                        for key, full_value, quoted_val1, quoted_val2, unquoted_val in param_pairs:
                            # Prioritize quoted values, then fall back to unquoted
                            value = quoted_val1 if quoted_val1 is not None else quoted_val2
                            if value is None:
                                value = unquoted_val.strip()
                            params[key.strip()] = value

                    try:
                        print(f"Executing tool: {tool_name} with params: {params}") # Debug print
                        result = run_tool(tool_name, crew_instance=self, model=self.model, **params)
                        tool_message = f"Tool '{tool_name}' executed successfully. Result: {result}"
                        self.messages.append({"role": "system", "content": tool_message})
                        # FIX: Add the tool result to the user-facing output
                        output_responses.append(f"TOOL RESULT: {result}")
                    except Exception as e:
                        error_message = f"Error executing tool '{tool_name}': {str(e)}"
                        print(f"ERROR: {error_message}") # Debug print
                        self.messages.append({"role": "system", "content": error_message})
                        # FIX: Also add the error to the user-facing output
                        output_responses.append(error_message)
                
                # FIX: Break the loop after tool execution to prevent infinite loops.
                break

            else:
                # No tool command found, treat as a final response
                if response:
                    output_responses.append(response)
                    self.messages.append({"role": "assistant", "content": response})
                break

        return "\n\n".join(output_responses)

# ... (rest of the file remains the same) ...    

    def reset(self):
        """Resets the crew's conversation history."""
        self.messages = [{"role": "system", "content": self.system_prompt}]


# ... (rest of crew.py remains the same) ...



def initialize_crew(model_obj, max_tokens_console):
    """Initializes a dictionary of crews and ship main bridge."""
    crew: Dict[str, Crew] = {}
    tool_descriptions = "\n".join([get_tool_description(tool_name) for tool_name in list_tools() if get_tool_description(tool_name)])
    system_prompt = get_raven_prompt()
    initial_message = [{"role": "system", "content": system_prompt}]

    crew["captain_raven"] = Crew(
        name="Raven",
        system_prompt=system_prompt,
        model=model_obj,
        max_tokens=1024,
        temperature=0.8,
        available_tools=list_tools()
    )

    crew["code_expert"] = Crew(
        name="Code Expert",
        system_prompt="You are a coding expert. Provide clear and concise code examples and explanations. Focus on Python unless otherwise specified.",
        model=model_obj,
        max_tokens=512,
        temperature=0.1,
    )

    # --- MODIFIED TOOL CREW ---
    crew["tool_crew"] = Crew(
        name="tool_crew",
        system_prompt=f"""Your only function is to translate user requests into tool commands.
    - Respond with ONLY the tool command.
    - The command format is: `run_tool tool_name param1=value1, param2=value2`
    - Do not provide any explanation, preamble, or additional text.
    
    Here are the available tools:
    {tool_descriptions}
    
    ---
    User: Open my notes file.
    AI: run_tool open_notes
    ---
    User: Make a new file called 'report.txt' with 'Sales are up!' inside.
    AI: run_tool create_file filename=report.txt, content="Sales are up!"
    ---
    User: Fire the laser at the asteroid.
    AI: run_tool fire_laser target=asteroid
    ---
    User: What is the status of the 'mission_log.txt' file?
    AI: run_tool status_log filename=mission_log.txt
    ---""",
        model=model_obj,
        max_tokens=150,      # Increased slightly for complex commands
        temperature=0.0,     # Keep at 0.0 for deterministic output
        available_tools=list_tools()
    )

    crew["creative_writer"] = Crew(
        name="Creative Writer",
        system_prompt="You are a creative writer. Write engaging and imaginative stories and descriptions. Be descriptive and interesting.",
        model=model_obj,
        max_tokens=1024,
        temperature=0.9
    )

    # Attach the registry to each crew member so tools can delegate
    for member in crew.values():
        member.crew_registry = crew

    return crew