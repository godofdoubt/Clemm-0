# clemm09/core/clemm_console.py
import subprocess
from bridge.tools.tools import list_tools, run_tool

def clemm_console(model, crew, max_tokens):
    """Console interface."""
    print("Clemm 09 Console Online. Type 'help' for commands or 'exit'")

    # Validate and set initial crew
    if not crew:
        print("Error: No crew members available. Exiting.")
        return
    current_crew = next(iter(crew))
    print(f"Current crew: {current_crew}")
    last_code_response = ""
    available_tools_console = list_tools()

    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'help':
            print("Available commands: help, exit, status, destination, ask, crew, use [crew_name], reset, run_code, run_tool [tool_name]")
            print("\nAvailable tools: ", ", ".join(available_tools_console))
        elif user_input.lower() == 'status':
            print("System Status: All systems nominal.")
        elif user_input.lower() == 'destination':
            print("Current Destination: Europa(Jupiter II)")
        elif user_input.lower() == 'crew':
            print("Available crew members:", ", ".join(crew.keys()))
        elif user_input.lower().startswith('use'):
            try:
                parts = user_input.split()
                if len(parts) > 1:
                    crew_name = parts[1].strip()
                    if crew_name.lower() == 'crew':
                        crew_name = 'tool_crew'
                    if crew_name in crew:
                        current_crew = crew_name
                        print(f"Switched to crew: {current_crew}")
                        crew[current_crew].reset()
                        last_code_response = ""
                    else:
                        print("Crew member not found.")
                else:
                    print("Please specify a crew member's name.")
            except IndexError:
                print("Please specify a crew member name to use.")
        elif user_input.lower() == 'reset':
            if current_crew in crew:
                crew[current_crew].reset()
                print(f"crew '{current_crew}' reset.")
                last_code_response = ""
            else:
                print(f"Error: crew '{current_crew}' not found.")
        elif user_input.lower().startswith('ask'):
            query = user_input[4:].strip()
            if query:
                if current_crew not in crew:
                    print(f"Error: crew '{current_crew}' not found. Available crews: {', '.join(crew.keys())}")
                else:
                    response = crew[current_crew].chat(query)
                    # Handle tool execution responses
                    if isinstance(response, str) and response.lower().startswith("run_tool "):
                        try:
                            tool_command = response[8:].strip()
                            parts = tool_command.split(maxsplit=1)
                            tool_name = parts[0]
                            tool_kwargs = {}
                            if len(parts) > 1:
                                args_part = parts[1]
                                arg_pairs = [pair.strip() for pair in args_part.split(',')]
                                for pair in arg_pairs:
                                    if '=' in pair:
                                        key, value = pair.split('=', 1)
                                        tool_kwargs[key.strip()] = value.strip()
                            print(f"\nExecuting tool: {tool_name}")
                            if tool_kwargs:
                                print(f"With arguments: {tool_kwargs}")
                            tool_result = run_tool(tool_name, crew_instance=crew, **tool_kwargs)  # Pass the crew!
                            print(f"Tool result: {tool_result}")
                            feedback_response = crew[current_crew].chat(f"Tool execution result: {tool_result}")
                            if not feedback_response.lower().startswith("run_tool "):
                                print(f"{current_crew}: {feedback_response}")
                        except Exception as e:
                            print(f"Error executing tool: {e}")
                    else:
                        print(f"{current_crew}: {response}")
                    if current_crew == "code_expert":
                        last_code_response = response
            else:
                print("Please provide a question.")
        elif user_input.lower() == 'run_code':
            if current_crew == "code_expert" and last_code_response:
                print("\n--- SECURITY WARNING ---")
                print("Review the code carefully before proceeding.")
                print("Last generated code:\n")
                print(last_code_response)
                if input("Execute code? (yes/no): ").lower() == 'yes':
                    try:
                        print("\n--- Executing code ---")
                        process = subprocess.run(['python', '-c', last_code_response], capture_output=True, text=True, check=False)
                        if process.returncode == 0:
                            print("--- Code execution output ---\n")
                            print(process.stdout)
                        else:
                            print("--- Code execution error ---\n")
                            print(process.stderr)
                    except Exception as e:
                        print(f"Error executing code: {e}")
                else:
                    print("Code execution cancelled.")
            else:
                print("No code to run or incorrect crew selected.")
        elif user_input.lower().startswith('run_tool'):
            try:
                parts = user_input.split(maxsplit=1)
                tool_name = parts[1].strip()
                 # No need to parse arguments for mainstream, it takes the crew
                print(f"Running tool: '{tool_name}'")
                tool_result = run_tool(tool_name, crew_instance=crew) #Pass the crew
                print(f"Tool Result: {tool_result}")

            except IndexError:
                print("Please specify a tool name after 'run_tool'.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        else:
            print("Command not recognized.")