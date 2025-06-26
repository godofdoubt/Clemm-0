# core.py

import core.raven as raven
from bridge.crew import initialize_crew

def start_core():
    """Starts the core systems of Clemm08."""

    backend_choice = input("Choose backend for Raven:\n1 - CUDA (local library)\n2 - LlamaCPP Server\nEnter your choice (1/2): ").strip()
    backend = 'server' if backend_choice == '2' else 'cuda'
    
    print(f"Core systems online. Initiating Raven with {backend.upper()} backend...")
    
    model_obj = raven.activate_raven(backend=backend)
    
    # --- NEW: Add a try...finally block to ensure server shutdown ---
    server_process = None
    if model_obj:
        # Check if a server process was started and store it for cleanup
        if model_obj.get("process"):
            server_process = model_obj["process"]
    
    try:
        if model_obj:
            max_tokens = int(input("Enter maximum response length (default is 1022): ") or 1022)
            
            print("Loading crew...")
            clemm_crew = initialize_crew(model_obj, max_tokens)

            print("Loading other tools (Placeholder)...")
            
            ui_choice = input("\nChoose interface:\n1 - Matrix UI\n2 - Console UI\nEnter your choice (1/2): ").strip()
            if ui_choice == '1':
                from core.clemmui import launch_matrix_ui
                launch_matrix_ui(model_obj, clemm_crew, max_tokens)
            else:
                from core.clemm_console import clemm_console
                clemm_console(model_obj, clemm_crew, max_tokens)
        else:
            if backend == 'cuda':
                print("Failed to start Raven. Please ensure you have a CUDA-enabled GPU and the correct drivers.")
            else:
                print("Failed to start or connect to the LlamaCPP server. Check your .env paths and settings.")
            print("System shutdown initiated.")
            exit()
            
    finally:
        # This block will run when the try block finishes or if an error occurs
        if server_process:
            print("\nShutting down LlamaCPP server...")
            server_process.terminate()
            server_process.wait() # Wait for the process to fully close
            print("Server has been shut down.")

if __name__ == "__main__":
    start_core()