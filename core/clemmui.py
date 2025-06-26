import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import threading
import subprocess
import random
import time
import os
import sys
import string
from typing import List, Dict, Optional, Any
import re
import ast

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend components
from bridge.tools.tools import list_tools, run_tool, get_tool_description
import core.raven as raven
import bridge.crew as crew

# (MatrixRain and TypewriterText classes remain unchanged)
class MatrixRain(tk.Canvas):
    """Digital rain effect in Matrix style"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg='black', highlightthickness=0)
        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()
        self.chars = "a〒bc*defgh010㋞10ijclemmklmnopqrstuvw0101※01010x1SgodofdoubtBBCﾇDEF〒GHIJKL0MNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,./<>?"
        self.streams = []
        self.active = False
        
    def start_animation(self):
        self.active = True
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        # Create initial streams
        self.streams = []
        for i in range(int(self.width / 20)):  # Adjust density of streams
            x = random.randint(10, self.width - 10)
            speed = random.uniform(1, 3)
            self.streams.append({"x": x, "y": 0, "speed": speed, "length": random.randint(5, 15), 
                                "chars": [random.choice(self.chars) for _ in range(20)]})
        self.animate()
    
    def animate(self):
        if not self.active:
            return
        
        self.delete("all")
        
        # Process each stream
        for stream in self.streams:
            x, y = stream["x"], stream["y"]
            speed = stream["speed"]
            stream_chars = stream["chars"]
            length = stream["length"]
            
            # Draw characters in stream with fading effect
            for i in range(length):
                char_y = y - (i * 15)
                if 0 <= char_y <= self.height:
                    # Calculate green intensity based on position (brighter at head)
                    intensity = int(255 * (1 - i/length))
                    color = f"#{0:02x}{intensity:02x}{0:02x}"
                    self.create_text(x, char_y, text=stream_chars[i % len(stream_chars)], 
                                    fill=color, font=("Courier", 12, "bold"))
            
            # Move stream down
            stream["y"] += speed
            
            # Replace first character randomly
            if random.random() < 0.1:
                stream_chars[0] = random.choice(self.chars)
            
            # Restart stream if it's gone too far
            if y > self.height + length * 15:
                stream["y"] = 0
                stream["x"] = random.randint(10, self.width - 10)
                stream["chars"] = [random.choice(self.chars) for _ in range(20)]
        
        # Randomly add new streams
        if random.random() < 0.05 and len(self.streams) < self.width / 10:
            x = random.randint(10, self.width - 10)
            speed = random.uniform(1, 3)
            self.streams.append({"x": x, "y": 0, "speed": speed, "length": random.randint(5, 15), 
                                "chars": [random.choice(self.chars) for _ in range(20)]})
        
        self.after(50, self.animate)
    
    def stop_animation(self):
        self.active = False


class TypewriterText(ScrolledText):
    """Text widget that displays text with a typewriter effect and initial garbled text"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.is_typing = False
        self._typing_thread = None
    
    def typewrite(self, text, delay=10, callback=None, garble_duration=100, garble_speed=20):
        """Add text with typewriter effect and initial garbled text, processing character by character"""
        if self.is_typing:  # Prevent multiple simultaneous typing animations
            return
            
        self.is_typing = True
        
        # Fix: Make sure text is properly prepared for line processing
        lines = text.splitlines() if text else [""]
        
        def _process_lines():
            """Process the text line by line with a proper typewriter effect"""
            try:
                for line in lines:
                    self.configure(state='normal')
                    current_pos = self.index(tk.END + "-1c")
                    
                    # Process each character with garbled text effect
                    for char in line:
                        # Add a garbled character first
                        garbled_char = random.choice(string.ascii_letters + string.digits)
                        self.insert(current_pos, garbled_char)
                        self.see(tk.END)
                        self.update_idletasks()
                        time.sleep(garble_speed / 1000)
                        
                        # Replace with correct character
                        self.delete(current_pos)
                        self.insert(current_pos, char)
                        self.see(tk.END)
                        self.update_idletasks()
                        time.sleep(delay / 1000)
                        
                        # Update current position
                        current_pos = self.index(tk.END + "-1c")
                    
                    # Add a newline after each line
                    self.insert(tk.END, "\n")
                    self.see(tk.END)
                    self.update_idletasks()
                    time.sleep(delay / 1000)
                    
            finally:
                self.is_typing = False
                self.configure(state='disabled')
                if callback:
                    self.after(0, callback)
        
        # Start the typing process in a separate thread to prevent UI freezing
        self._typing_thread = threading.Thread(target=_process_lines, daemon=True)
        self._typing_thread.start()


class ClemmMatrixUI(tk.Tk):
    def __init__(self, crew_instance=None, model=None, max_tokens=None, model_name="UNKNOWN_MODEL", available_tools=None):
        super().__init__()
        self.title("CLEMM- MATRIX TERMINAL")
        self.geometry("1400x900")
        self.configure(bg='black')
        
        # Store backend components
        self.model = model # This is the full model_obj dictionary
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.available_tools = available_tools if available_tools else []
        self.crew_instance = crew_instance
        
        # Matrix theme colors
        self.matrix_green = "#00ff00"
        self.lime_green = "#32CD32" # Brighter green for highlights
        self.dark_green = "#003300"
        self.black = "#000000"
        self.warning_red = "#ff3300"
        
        # --- UI COMPONENTS SETUP ---
        
        # Background Frame and Canvas
        self.bg_frame = tk.Frame(self, bg=self.black)
        self.bg_frame.place(relwidth=1, relheight=1)
        self.matrix_canvas = MatrixRain(self.bg_frame, bg=self.black, highlightthickness=0)
        self.matrix_canvas.place(relwidth=1, relheight=1)

        # Main Content Frame
        self.content_frame = tk.Frame(self, bg=self.black)
        self.content_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Header
        self.header_frame = tk.Frame(self.content_frame, bg=self.black)
        self.header_frame.pack(fill='x', pady=(0, 5))
        self.title_label = tk.Label(self.header_frame, text="CLEMM MATRIX TERMINAL", bg=self.black, fg=self.matrix_green, font=("Courier", 18, "bold"))
        self.title_label.pack(side="left", padx=10)
        self.status_label = tk.Label(self.header_frame, text="STATUS: CONNECTED", bg=self.black, fg=self.matrix_green, font=("Courier", 12))
        self.status_label.pack(side="right", padx=10)

        # Toolbar
        self.toolbar_frame = tk.Frame(self.content_frame, bg=self.black)
        self.toolbar_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Tool Buttons
        self.tool_buttons_frame = tk.Frame(self.toolbar_frame, bg=self.black)
        self.tool_buttons_frame.pack(side="left", fill="x", expand=True)
        self.open_notes_button = tk.Button(self.tool_buttons_frame, text="Captain's Log", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 9, "bold"), relief="raised", bd=1, command=self.run_open_notes_tool)
        self.open_notes_button.pack(side="left", padx=2)
        self.create_file_button = tk.Button(self.tool_buttons_frame, text="Create File", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 9, "bold"), relief="raised", bd=1, command=self.run_create_file_tool)
        self.create_file_button.pack(side="left", padx=2)
        self.fire_laser_button = tk.Button(self.tool_buttons_frame, text="Fire Laser", bg=self.warning_red, fg=self.matrix_green, font=("Courier", 9, "bold"), relief="raised", bd=1, command=self.run_fire_laser_tool)
        self.fire_laser_button.pack(side="left", padx=2)
        self.launch_missile_button = tk.Button(self.tool_buttons_frame, text="Launch Missile", bg=self.warning_red, fg=self.matrix_green, font=("Courier", 9, "bold"), relief="raised", bd=1, command=self.run_launch_missile_tool)
        self.launch_missile_button.pack(side="left", padx=2)
        
        # Crew Selector
        self.crew_frame = tk.Frame(self.toolbar_frame, bg=self.black)
        self.crew_frame.pack(side="right")
        self.crew_label = tk.Label(self.crew_frame, text="ACTIVE CREW:", bg=self.black, fg=self.matrix_green, font=("Courier", 10, "bold"))
        self.crew_label.pack(side="left", padx=(0, 5))
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Matrix.TCombobox', fieldbackground=self.black, background=self.dark_green, foreground=self.matrix_green, bordercolor=self.matrix_green, arrowcolor=self.matrix_green, selectbackground=self.dark_green, selectforeground=self.matrix_green)
        self.crew_selector = ttk.Combobox(self.crew_frame, style='Matrix.TCombobox', font=("Courier", 10, "bold"), width=15, state="readonly")
        self.crew_selector.pack(side="left", padx=2)
        self.crew_selector.bind('<<ComboboxSelected>>', self.on_crew_selected)
        self.reset_crew_button = tk.Button(self.crew_frame, text="Reset", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 9, "bold"), relief="raised", bd=1, command=self.reset_current_crew)
        self.reset_crew_button.pack(side="left", padx=2)

        # Output Text Area
        self.output_frame = tk.Frame(self.content_frame, bg=self.dark_green, bd=2, relief="sunken", padx=2, pady=2)
        self.output_frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.output_text = TypewriterText(self.output_frame, wrap='word', bg=self.black, fg=self.matrix_green, insertbackground=self.matrix_green, selectbackground=self.dark_green, selectforeground=self.matrix_green, font=("Courier", 11), bd=0, padx=10, pady=10)
        self.output_text.pack(expand=True, fill='both')
        self.output_text.configure(state='disabled')

        # Command Input
        self.command_frame = tk.Frame(self.content_frame, bg=self.black)
        self.command_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.ask_mode_button = tk.Button(self.command_frame, text="[CMD]", bg=self.black, fg=self.matrix_green, font=("Courier", 12, "bold"), relief="flat", command=self.toggle_ask_mode)
        self.ask_mode_button.pack(side="left")
        
        self.prompt_label = tk.Label(self.command_frame, text=" > ", bg=self.black, fg=self.matrix_green, font=("Courier", 12, "bold"))
        self.prompt_label.pack(side="left")
        
        self.input_entry = tk.Entry(self.command_frame, bg=self.black, fg=self.matrix_green, insertbackground=self.matrix_green, bd=0, font=("Courier", 12), relief="flat")
        self.input_entry.pack(fill='x', expand=True)
        self.input_entry.bind("<Return>", self.process_command_event)

        # Status Bar
        self.status_bar = tk.Frame(self.content_frame, bg=self.dark_green, height=25)
        self.status_bar.pack(fill='x', padx=10, pady=(0, 10))
        self.crew_status = tk.Label(self.status_bar, text="NO CREW SELECTED", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 10))
        self.crew_status.pack(side="left", padx=5)
        self.tools_status = tk.Label(self.status_bar, text="TOOLS LOADING...", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 10))
        self.tools_status.pack(side="left", padx=5)
        self.model_status = tk.Label(self.status_bar, text=f"MODEL: {self.model_name[:20]}", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 10))
        self.model_status.pack(side="left", padx=5)
        self.system_status = tk.Label(self.status_bar, text="INITIALIZING...", bg=self.dark_green, fg=self.matrix_green, font=("Courier", 10))
        self.system_status.pack(side="right", padx=5)
        
        # --- INITIALIZATION ---
        
        self.cursor_visible = True
        self.ask_mode_active = False # New state for ASK mode
        self.cursor_blink()
        
        self.last_code_response = ""
        self.crew = {}
        self.current_crew = None
        self.available_tools = []
        
        self.load_tools()
        
        if crew_instance:
            self.crew = crew_instance
            self.populate_crew_selector()
        else:
            threading.Thread(target=self.initialize_system, daemon=True).start()

        self.setup_menus()
        
        self.after(500, self.boot_sequence)
        self.after(1000, self.matrix_canvas.start_animation)
        self.after(2000, lambda: self.input_entry.focus_set())

    def toggle_ask_mode(self):
        """Toggles the ASK mode on and off."""
        self.ask_mode_active = not self.ask_mode_active
        if self.ask_mode_active:
            self.ask_mode_button.config(text="[ASK]", fg=self.lime_green)
            self.prompt_label.config(text=" ASK> ")
            self.cursor_blink() # Start blinking
        else:
            self.ask_mode_button.config(text="[CMD]", fg=self.matrix_green)
            self.prompt_label.config(text=" > ")
            self.input_entry.config(insertbackground=self.matrix_green) # Solid cursor

    def load_tools(self):
        """Load available tools and update UI"""
        try:
            self.available_tools = list_tools()
            tool_count = len(self.available_tools)
            self.tools_status.config(text=f"TOOLS: {tool_count} LOADED")
        except Exception as e:
            self.tools_status.config(text="TOOLS: ERROR LOADING")
            print(f"Error loading tools: {e}")

    def populate_crew_selector(self):
        """Populate the crew selector dropdown"""
        if self.crew and isinstance(self.crew, dict):
            crew_names = list(self.crew.keys())
            self.crew_selector['values'] = [name.upper() for name in crew_names]
            if crew_names:
                if not self.current_crew:
                    self.current_crew = crew_names[0]
                self.crew_selector.set(self.current_crew.upper())
                self.crew_status.config(text=f"ACTIVE: {self.current_crew.upper()}")
        else:
            self.crew_selector['values'] = []
            self.crew_status.config(text="NO CREW AVAILABLE")

    def on_crew_selected(self, event):
        """Handle crew selection from dropdown"""
        selected = self.crew_selector.get().lower()
        if selected in self.crew:
            self.current_crew = selected
            self.crew[selected].reset()
            self.last_code_response = ""
            self.append_output(f"SWITCHING NEURAL LINK: {selected.upper()}")
            self.crew_status.config(text=f"ACTIVE: {selected.upper()}")

    def reset_current_crew(self):
        """Reset the currently selected crew member"""
        if self.crew and self.current_crew in self.crew:
            self.crew[self.current_crew].reset()
            self.last_code_response = ""
            self.append_output(f"MEMORY PURGE COMPLETE: {self.current_crew.upper()}")
        else:
            self.append_output("ERROR: NO CREW MEMBER ACTIVE")

    def setup_menus(self):
        menubar = tk.Menu(self, bg=self.black, fg=self.matrix_green, activebackground=self.dark_green, activeforeground=self.matrix_green, bd=0)
        self.config(menu=menubar)
        crew_menu = tk.Menu(menubar, tearoff=0, bg=self.black, fg=self.matrix_green, activebackground=self.dark_green, activeforeground=self.matrix_green)
        crew_menu.add_command(label="LIST ALL CREW", command=self.list_crew)
        crew_menu.add_command(label="RESET ALL CREW", command=self.reset_all_crew)
        crew_menu.add_separator()
        crew_menu.add_command(label="CREW STATUS", command=self.show_crew_status)
        menubar.add_cascade(label="CREW", menu=crew_menu)
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.black, fg=self.matrix_green, activebackground=self.dark_green, activeforeground=self.matrix_green)
        tools_menu.add_command(label="LIST ALL TOOLS", command=self.list_tools)
        tools_menu.add_command(label="TOOL DESCRIPTIONS", command=self.show_tool_descriptions)
        menubar.add_cascade(label="TOOLS", menu=tools_menu)
        system_menu = tk.Menu(menubar, tearoff=0, bg=self.black, fg=self.matrix_green, activebackground=self.dark_green, activeforeground=self.matrix_green)
        system_menu.add_command(label="MODEL INFO", command=self.show_model_info)
        system_menu.add_command(label="SYSTEM STATUS", command=self.show_system_status)
        system_menu.add_separator()
        system_menu.add_command(label="CLEAR OUTPUT", command=self.clear_output)
        menubar.add_cascade(label="SYSTEM", menu=system_menu)

    def run_open_notes_tool(self):
        self.append_output("> Running tool: open_notes")
        self.system_status.config(text="RUNNING TOOL...")
        threading.Thread(target=self.execute_tool, args=("open_notes",), kwargs={}, daemon=True).start()

    def run_create_file_tool(self):
        filename = simpledialog.askstring("Input", "Enter filename (e.g., log.txt):", parent=self)
        if not filename: self.append_output("File creation cancelled."); return
        content = simpledialog.askstring("Input", f"Enter content for {filename}:", parent=self)
        if content is None: self.append_output("File creation cancelled."); return
        tool_args = {"filename": filename, "content": content}
        self.append_output(f"> Running tool: create_file with {tool_args}")
        self.system_status.config(text="RUNNING TOOL...")
        threading.Thread(target=self.execute_tool, args=("create_file",), kwargs={'tool_args': tool_args}, daemon=True).start()

    def run_fire_laser_tool(self):
        target = simpledialog.askstring("Target Input", "Enter target coordinates:", parent=self)
        if not target: self.append_output("Laser firing cancelled."); return
        power_level = simpledialog.askstring("Power Level", "Enter power level (1-10):", parent=self) or "5"
        tool_args = {"target": target, "power_level": power_level}
        self.append_output(f"> FIRING LASER AT: {target.upper()}")
        self.system_status.config(text="WEAPONS FIRING...")
        threading.Thread(target=self.execute_tool, args=("fire_laser",), kwargs={'tool_args': tool_args}, daemon=True).start()

    def run_launch_missile_tool(self):
        target = simpledialog.askstring("Target Input", "Enter target coordinates:", parent=self)
        if not target: self.append_output("Missile launch cancelled."); return
        warhead_type = simpledialog.askstring("Warhead Type", "Enter warhead type (standard/plasma/nuclear):", parent=self) or "standard"
        tool_args = {"target": target, "warhead_type": warhead_type}
        self.append_output(f"> LAUNCHING {warhead_type.upper()} MISSILE AT: {target.upper()}")
        self.system_status.config(text="MISSILE LAUNCHING...")
        threading.Thread(target=self.execute_tool, args=("launch_missile",), kwargs={'tool_args': tool_args}, daemon=True).start()

    def boot_sequence(self):
        welcome_text = """


 ██████╗██╗     ███████╗███╗   ███╗███╗   ███╗
██╔════╝██║     ██╔════╝████╗ ████║████╗ ████║
██║     ██║     █████╗  ██╔████╔██║██╔████╔██║
██║     ██║     ██╔══╝  ██║╚██╔╝██║██║╚██╔╝██║
╚██████╗███████╗███████╗██║ ╚═╝ ██║██║ ╚═╝ ██║
 ╚═════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝


INITIALIZING CONNECTION TO THE CONSTRUCT...
NEURAL LINK SYNCHRONIZED.
LOADING CLEMM CORE SYSTEMS...
...
...
...
CLEMM v2.1 MATRIX INTERFACE ONLINE.
"""
        self.output_text.configure(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state='disabled')
        self.output_text.typewrite(welcome_text, delay=5, callback=lambda: self.append_output("SYSTEM READY. TYPE 'HELP' FOR AVAILABLE COMMANDS."))

# In class ClemmMatrixUI:

    def cursor_blink(self):
        """Blinks the cursor only when ASK mode is active."""
        # Use a try-except block to gracefully handle focus errors, especially with ttk widgets.
        try:
            is_focused = self.focus_get() == self.input_entry
        except (tk.TclError, KeyError):
            # This can happen when focus is on a transient widget (e.g., combobox popdown).
            # Safely assume focus is not on the entry.
            is_focused = False

        if self.ask_mode_active:
            if is_focused:
                # Blink the cursor if entry is focused in ASK mode
                self.input_entry.config(insertbackground=self.matrix_green if self.cursor_visible else self.black)
                self.cursor_visible = not self.cursor_visible
            else:
                # Make cursor invisible if not focused in ASK mode
                self.input_entry.config(insertbackground=self.black)
        else:
            # In CMD mode, the cursor should be a solid, non-blinking line
            self.input_entry.config(insertbackground=self.matrix_green)

        # Always reschedule the next check to keep the loop running and prevent it from dying
        if self.winfo_exists():
            self.after(500, self.cursor_blink)

    def initialize_system(self):
        loading_messages = [
            "ACCESSING CREW DATABASE...",
            "VERIFYING NEURAL HANDSHAKES...",
            "CALIBRATING REALITY MATRIX...",
            "LOADING CREW PROFILES: [COMMANDER, CODE_EXPERT, WEAPONS_OFFICER]..."
        ]
        for msg in loading_messages: 
            self.after(0, lambda m=msg: self.append_output(m))
            time.sleep(0.5)
        self.after(0, lambda: self.append_output("INITIALIZATION COMPLETE. SYSTEM READY."))
        self.after(0, lambda: self.system_status.config(text="READY FOR COMMANDS"))

    def append_output(self, text):
        if not text: return
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state='disabled')

    def clear_output(self):
        self.output_text.configure(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state='disabled')
        self.append_output("OUTPUT BUFFER CLEARED")

    def process_command_event(self, event): self.process_command()

    def process_command(self):
        command = self.input_entry.get().strip()
        if not command: return

        prompt = self.prompt_label.cget("text")
        self.append_output(f"{prompt}{command}")
        self.input_entry.delete(0, tk.END)
        
        if self.ask_mode_active:
            command_to_execute = f"ask {command}"
        else:
            command_to_execute = command
            
        self.system_status.config(text="PROCESSING...")
        self.after(100, lambda: self.execute_command(command_to_execute))

    def execute_command(self, command):
        command_lower = command.lower()
        print(f"Executing command: {command_lower}")
        
        if command_lower == "exit":
            self.after(1000, self.quit)
        
        elif command_lower == "help":
            help_text = """
    AVAILABLE COMMANDS:
    ═══════════════════
    Use the [CMD]/[ASK] button to toggle input mode.
    
    [CMD] MODE:
    HELP               - Shows this help message.
    USE <crew_name>    - Switches to a different crew member (e.g., 'use commander').
    CREW / LIST CREW   - Displays the status of all crew members.
    RESET              - Resets the memory of the current crew member.
    TOOLS / LIST TOOLS - Lists all available tools and their descriptions.
    RUN_TOOL <name> [args] - Manually run a tool (e.g., 'run_tool create_file filename="test.txt"').
    RUN_CODE           - Executes Python code from the last response of 'code_expert'.
    MODEL_INFO         - Displays information about the loaded AI model.
    CLEAR              - Clears the output screen.
    EXIT               - Disconnects from the Matrix and closes the terminal.

    [ASK] MODE:
    Any text entered is sent as a query to the active crew member.
    """
            self.output_text.typewrite(help_text, delay=1)
            self.system_status.config(text="READY FOR COMMANDS")
        
        elif command_lower in ["crew", "list crew"]:
            self.list_crew()
            self.system_status.config(text="READY FOR COMMANDS")
        
        elif command_lower in ["tools", "list tools"]:
            self.list_tools()
            self.system_status.config(text="READY FOR COMMANDS")
        
        elif command_lower in ["model_info", "model info"]:
            self.show_model_info()
            self.system_status.config(text="READY FOR COMMANDS")

        elif command_lower == "clear":
            self.clear_output()
            self.system_status.config(text="READY FOR COMMANDS")
            
        elif command_lower.startswith("use "):
            crew_name = command[4:].strip().lower()
            if self.crew and crew_name in self.crew:
                self.crew_selector.set(crew_name.upper())
                self.on_crew_selected(None)
            else:
                self.append_output(f"ERROR: CREW MEMBER '{crew_name.upper()}' NOT FOUND")
            self.system_status.config(text="READY FOR COMMANDS")

        elif command_lower == "reset":
            self.reset_current_crew()
            self.system_status.config(text="READY FOR COMMANDS")
            
        elif command_lower.startswith("ask "):
            query = command[4:].strip()
            if not query:
                self.append_output("ERROR: QUERY REQUIRED")
                self.system_status.config(text="READY FOR COMMANDS")
                return
            if self.crew and self.current_crew in self.crew:
                self.append_output(f"PROCESSING QUERY THROUGH {self.current_crew.upper()}...")
                threading.Thread(target=self.process_ask, args=(query,), daemon=True).start()
            else:
                self.append_output("ERROR: NO ACTIVE CREW")
                self.system_status.config(text="READY FOR COMMANDS")

        elif command_lower.startswith("run_tool"):
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                self.append_output("ERROR: run_tool requires a tool name and optional arguments.")
                self.system_status.config(text="READY FOR COMMANDS")
                return

            tool_call = parts[1]
            tool_name_match = re.match(r'^(\w+)', tool_call)
            if not tool_name_match:
                self.append_output("ERROR: Could not parse tool name.")
                self.system_status.config(text="READY FOR COMMANDS")
                return
            
            tool_name = tool_name_match.group(1)
            kwargs = {}
            # Regex to find key=value or key="value" or key='value' pairs
            arg_pattern = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')
            for match in arg_pattern.finditer(tool_call[len(tool_name):]):
                key = match.group(1)
                # The value can be in group 2 (double quotes), 3 (single quotes), or 4 (no quotes)
                value = next((v for v in match.groups()[1:] if v is not None), None)
                kwargs[key] = value

            self.append_output(f"> Running tool: {tool_name} with args: {kwargs}")
            threading.Thread(target=self.execute_tool, args=(tool_name,), kwargs={'tool_args': kwargs}, daemon=True).start()

        elif command_lower == "run_code":
            if self.current_crew == "code_expert" and self.last_code_response:
                code_to_run = self.extract_python_code(self.last_code_response)
                if not code_to_run:
                    self.append_output("ERROR: No Python code block found in the last response.")
                    self.system_status.config(text="READY FOR COMMANDS")
                    return

                def show_confirm_dialog():
                    confirm_msg = "The following code will be executed. Proceed?\n\n---\n" + code_to_run[:500] + ("..." if len(code_to_run) > 500 else "")
                    confirm = messagebox.askyesno("Confirm Code Execution", confirm_msg, parent=self)
                    
                    if confirm:
                        self.append_output("[CONFIRMED] EXECUTING CODE...")
                        self.system_status.config(text="EXECUTING SCRIPT...")
                        threading.Thread(target=self.execute_python_script, args=(code_to_run,), daemon=True).start()
                    else:
                        self.append_output("CODE EXECUTION CANCELLED.")
                        self.system_status.config(text="READY FOR COMMANDS")
                
                self.after(10, show_confirm_dialog)
            else:
                self.append_output("ERROR: NO CODE OR 'code_expert' NOT ACTIVE")
                self.system_status.config(text="READY FOR COMMANDS")
        else:
            self.append_output("COMMAND NOT RECOGNIZED")
            self.system_status.config(text="READY FOR COMMANDS")
            
    def execute_tool(self, tool_name: str, tool_args: Optional[Dict[str, Any]] = None):
        tool_args = tool_args or {}
        try:
            result = run_tool(tool_name, crew_instance=self.crew, **tool_args)
            self.after(0, lambda: self.append_output(f"TOOL EXECUTION COMPLETE"))
            self.after(0, lambda r=result: self.append_output(f"RESULT: {r}"))
        except Exception as e:
            self.after(0, lambda err=e: self.append_output(f"ERROR IN TOOL EXECUTION: {err}"))
        finally:
            self.after(0, lambda: self.system_status.config(text="READY FOR COMMANDS"))

    def process_ask(self, query: str):
        try:
            self.after(0, lambda: self.system_status.config(text="QUERYING NEURAL INTERFACE..."))
            final_response = self.crew[self.current_crew].chat(query)
            header = f"\n[{self.current_crew.upper()} RESPONSE]:\n"
            full_text = header + "═" * (len(header) - 2) + "\n" + (final_response or "[NO RESPONSE]")
            self.after(0, lambda: self.output_text.typewrite(full_text, delay=5, callback=lambda: self.after(0, self.store_code_if_expert, final_response)))
        except Exception as e:
            self.after(0, lambda err=e: self.append_output(f"\nERROR IN NEURAL INTERFACE: {err}"))
        finally:
            self.after(0, lambda: self.system_status.config(text="READY FOR COMMANDS"))

    def store_code_if_expert(self, response: str):
        if self.current_crew == "code_expert":
            self.last_code_response = response
            self.append_output("\n[CODE SEQUENCE STORED. Use 'run_code' to execute.]")

    def extract_python_code(self, response: str) -> Optional[str]:
        """Extracts Python code from a markdown-style code block."""
        match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback for code that isn't in a block, attempts to parse it
        try:
            ast.parse(response)
            return response
        except (SyntaxError, TypeError):
            return None

    def execute_python_script(self, code: str):
        """Executes a string of Python code in a subprocess."""
        try:
            temp_filename = f"temp_script_{random.randint(1000,9999)}.py"
            with open(temp_filename, "w", encoding='utf-8') as f:
                f.write(code)
            
            process = subprocess.Popen(
                [sys.executable, temp_filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            stdout, stderr = process.communicate()
            
            os.remove(temp_filename)

            self.after(0, lambda: self.append_output("\n--- EXECUTION OUTPUT ---"))
            if stdout:
                self.after(0, lambda: self.append_output(f"STDOUT:\n{stdout}"))
            if stderr:
                self.after(0, lambda: self.append_output(f"STDERR:\n{stderr}"))
            self.after(0, lambda: self.append_output("--- EXECUTION FINISHED ---"))

        except Exception as e:
            self.after(0, lambda err=e: self.append_output(f"ERROR EXECUTING SCRIPT: {err}"))
        finally:
            self.after(0, lambda: self.system_status.config(text="READY FOR COMMANDS"))

    def reset_all_crew(self):
        if self.crew:
            for crew_name in self.crew: self.crew[crew_name].reset()
            self.last_code_response = ""
            self.append_output("MEMORY PURGE COMPLETE FOR ALL CREW MEMBERS")
        else: self.append_output("ERROR: CREW DATABASE EMPTY")
            
    def show_crew_status(self):
        if not self.crew: self.append_output("ERROR: CREW DATABASE EMPTY"); return
        status_lines = ["\n╔═══════════════ CREW STATUS ═══════════════╗"]
        for name, instance in self.crew.items():
            status = 'ACTIVE' if name == self.current_crew else 'STANDBY'
            msg_count = len(instance.messages) - 1 if hasattr(instance, 'messages') else 'N/A'
            status_lines.append(f"║ {name.upper():<15} │ STATUS: {status:<10} │ MEMORY: {msg_count: >2} ENTRIES ║")
        status_lines.append("╚═══════════════════════════════════════════╝")
        self.append_output("\n".join(status_lines))

    def show_system_status(self): self.append_output("SYSTEM STATUS CHECK PENDING IMPLEMENTATION")
    def list_crew(self): self.show_crew_status() if self.crew and isinstance(self.crew, dict) and len(self.crew) > 0 else self.append_output("ERROR: CREW DATABASE EMPTY")
    def list_tools(self): self.show_tool_descriptions() if self.available_tools else self.append_output("No tools available.")

    def show_tool_descriptions(self):
        if not self.available_tools: self.append_output("ERROR: NO TOOLS LOADED"); return
        desc_lines = ["\n╔═══════════════ TOOL DESCRIPTIONS ═══════════════╗"]
        for tool_name in self.available_tools:
            description = get_tool_description(tool_name)
            if description: desc_lines.append(f"╟─ {description}")
        desc_lines.append("╚════════════════════════════════════════════════╝")
        self.append_output("\n".join(desc_lines))

    def show_model_info(self):
        """Display model information"""
        backend_type = "UNKNOWN"
        status = "NOT LOADED"
        
        # self.model is the model_obj dictionary passed during initialization
        if self.model: 
            model_type_key = self.model.get("type")
            if model_type_key == "programmatic_gguf":
                backend_type = "CUDA (Local Library)"
                status = "LOADED" if self.model.get("model") else "ERROR"
            elif model_type_key == "llamacpp_server":
                backend_type = "Llama.cpp Server"
                status = "CONNECTED" if self.model.get("url") else "ERROR"
        
        model_info = f"""
    MODEL INFORMATION:
    ══════════════════
    NAME: {self.model_name}
    TYPE: GGUF
    MAX TOKENS: {self.max_tokens or 'N/A'}
    BACKEND: {backend_type}
    STATUS: {status}
    """
        self.append_output(model_info)


def launch_matrix_ui(model_obj, crew_instance, max_tokens):
    """Initializes and launches the main UI window."""
    model_name = "Unknown GGUF Model"
    
    # Intelligently get model name based on backend type
    if model_obj:
        if model_obj.get("type") == "programmatic_gguf":
            # For local CUDA, model object is nested
            llama_instance = model_obj.get("model")
            if llama_instance and hasattr(llama_instance, 'model_path'):
                model_name = llama_instance.model_path
        elif model_obj.get("type") == "llamacpp_server":
            # For server, the model path isn't directly in the object, so we get it from the environment variable
            model_path_from_env = os.getenv("RAVEN_GGUF_MODEL_PATH")
            if model_path_from_env:
                model_name = model_path_from_env

    # Clean up the path to just the filename for display
    if isinstance(model_name, str) and ('/' in model_name or '\\' in model_name):
        model_name = os.path.basename(model_name)
    
    available_tools = list_tools() if 'list_tools' in globals() else []
    
    app = ClemmMatrixUI(
        crew_instance=crew_instance,
        model=model_obj,  # Pass the whole object
        max_tokens=max_tokens,
        model_name=model_name,
        available_tools=available_tools
    )
    app.mainloop()

if __name__ == "__main__":
    # This block allows running the UI in a limited, standalone test mode
    # without needing the full application to be running.
    app = ClemmMatrixUI(model_name="STANDALONE_TEST")
    try:
        # Mock the backend components for testing purposes
        class MockModel:
            def __init__(self): self.model_path = "mock_model.gguf"
        model_obj = {"model": MockModel(), "type": "programmatic_gguf"}
        app.model = model_obj
        app.crew = crew.initialize_crew(model_obj, 512)
        app.populate_crew_selector()
        app.append_output("[STANDALONE MODE]: Initialized with test crew.")
    except (ImportError, FileNotFoundError, NameError) as e:
        app.append_output(f"[STANDALONE MODE]: Could not load test crew. Error: {e}")
        app.append_output("UI is running in limited mode. 'ask' commands will fail.")
    app.mainloop()