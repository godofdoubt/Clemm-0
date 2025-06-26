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
                    
                    self.configure(state='disabled')
            
            finally:
                self.is_typing = False
                if callback:
                    self.after(0, callback)
        
        # Start the typing process in a separate thread to prevent UI freezing
        self._typing_thread = threading.Thread(target=_process_lines, daemon=True)
        self._typing_thread.start()


class ClemmMatrixUI(tk.Tk):
    def __init__(self, crew_instance=None, model=None, max_tokens=None, model_name="UNKNOWN_MODEL", available_tools=None):
        super().__init__()
        self.title("CLEMM- MATRIX TERMINAL")
        self.geometry("1400x900")  # Made even wider for new components
        self.configure(bg='black')
        
        # Store backend components
        self.model = model
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.available_tools = available_tools if available_tools else []
        self.crew_instance = crew_instance
        
        # Matrix theme colors
        self.matrix_green = "#00ff00"
        self.dark_green = "#003300"
        self.black = "#000000"
        self.warning_red = "#ff3300"
        
        # Create frame for the matrix rain effect background
        self.bg_frame = tk.Frame(self, bg=self.black)
        self.bg_frame.place(relwidth=1, relheight=1)
        
        # Matrix rain canvas in background
        self.matrix_canvas = MatrixRain(self.bg_frame, bg=self.black, highlightthickness=0)
        self.matrix_canvas.place(relwidth=1, relheight=1)
        
        # Semi-transparent frame for content
        self.content_frame = tk.Frame(self, bg=self.black)
        self.content_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Header with system title
        self.header_frame = tk.Frame(self.content_frame, bg=self.black)
        self.header_frame.pack(fill='x', pady=(0, 5))
        
        self.title_label = tk.Label(self.header_frame, text="CLEMM MATRIX TERMINAL", 
                                   bg=self.black, fg=self.matrix_green, 
                                   font=("Courier", 18, "bold"))
        self.title_label.pack(side="left", padx=10)
        
        self.status_label = tk.Label(self.header_frame, text="STATUS: CONNECTED", 
                                    bg=self.black, fg=self.matrix_green, 
                                    font=("Courier", 12))
        self.status_label.pack(side="right", padx=10)

        # Enhanced Toolbar with Crew Selection
        self.toolbar_frame = tk.Frame(self.content_frame, bg=self.black)
        self.toolbar_frame.pack(fill='x', padx=10, pady=(0, 10))

        # Left side - Tool buttons
        self.tool_buttons_frame = tk.Frame(self.toolbar_frame, bg=self.black)
        self.tool_buttons_frame.pack(side="left", fill="x", expand=True)

        self.open_notes_button = tk.Button(self.tool_buttons_frame, text="Captain's Log",
                                           bg=self.dark_green, fg=self.matrix_green,
                                           font=("Courier", 9, "bold"), relief="raised",
                                           bd=1, command=self.run_open_notes_tool)
        self.open_notes_button.pack(side="left", padx=2)

        self.create_file_button = tk.Button(self.tool_buttons_frame, text="Create File",
                                             bg=self.dark_green, fg=self.matrix_green,
                                             font=("Courier", 9, "bold"), relief="raised",
                                             bd=1, command=self.run_create_file_tool)
        self.create_file_button.pack(side="left", padx=2)

        self.fire_laser_button = tk.Button(self.tool_buttons_frame, text="Fire Laser",
                                           bg=self.warning_red, fg=self.matrix_green,
                                           font=("Courier", 9, "bold"), relief="raised",
                                           bd=1, command=self.run_fire_laser_tool)
        self.fire_laser_button.pack(side="left", padx=2)

        self.launch_missile_button = tk.Button(self.tool_buttons_frame, text="Launch Missile",
                                               bg=self.warning_red, fg=self.matrix_green,
                                               font=("Courier", 9, "bold"), relief="raised",
                                               bd=1, command=self.run_launch_missile_tool)
        self.launch_missile_button.pack(side="left", padx=2)

        # Right side - Crew selection
        self.crew_frame = tk.Frame(self.toolbar_frame, bg=self.black)
        self.crew_frame.pack(side="right")

        self.crew_label = tk.Label(self.crew_frame, text="ACTIVE CREW:", 
                                  bg=self.black, fg=self.matrix_green, 
                                  font=("Courier", 10, "bold"))
        self.crew_label.pack(side="left", padx=(0, 5))

        # Style for the combobox to match matrix theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Matrix.TCombobox',
                            fieldbackground=self.black,
                            background=self.dark_green,
                            foreground=self.matrix_green,
                            bordercolor=self.matrix_green,
                            arrowcolor=self.matrix_green,
                            selectbackground=self.dark_green,
                            selectforeground=self.matrix_green)
        
        self.crew_selector = ttk.Combobox(self.crew_frame, 
                                         style='Matrix.TCombobox',
                                         font=("Courier", 10, "bold"),
                                         width=15,
                                         state="readonly")
        self.crew_selector.pack(side="left", padx=2)
        self.crew_selector.bind('<<ComboboxSelected>>', self.on_crew_selected)

        self.reset_crew_button = tk.Button(self.crew_frame, text="Reset",
                                          bg=self.dark_green, fg=self.matrix_green,
                                          font=("Courier", 9, "bold"), relief="raised",
                                          bd=1, command=self.reset_current_crew)
        self.reset_crew_button.pack(side="left", padx=2)
        
        # Output text area with matrix styling
        self.output_frame = tk.Frame(self.content_frame, bg=self.dark_green, bd=2, 
                                   relief="sunken", padx=2, pady=2)
        self.output_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.output_text = TypewriterText(self.output_frame, wrap='word', 
                                         bg=self.black, fg=self.matrix_green,
                                         insertbackground=self.matrix_green,
                                         selectbackground=self.dark_green,
                                         selectforeground=self.matrix_green,
                                         font=("Courier", 11),
                                         bd=0, padx=10, pady=10)
        self.output_text.pack(expand=True, fill='both')
        self.output_text.configure(state='disabled')
        
        # Command prompt frame
        self.command_frame = tk.Frame(self.content_frame, bg=self.black)
        self.command_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.prompt_label = tk.Label(self.command_frame, text="> ", 
                                    bg=self.black, fg=self.matrix_green, 
                                    font=("Courier", 12, "bold"))
        self.prompt_label.pack(side="left")
        
        # Input field with matrix styling
        self.input_entry = tk.Entry(self.command_frame, bg=self.black, fg=self.matrix_green,
                                  insertbackground=self.matrix_green, bd=0,
                                  font=("Courier", 12), relief="flat")
        self.input_entry.pack(fill='x', expand=True)
        self.input_entry.bind("<Return>", self.process_command_event)
        
        # Enhanced Status bar
        self.status_bar = tk.Frame(self.content_frame, bg=self.dark_green, height=25)
        self.status_bar.pack(fill='x', padx=10, pady=(0, 10))
        
        self.crew_status = tk.Label(self.status_bar, text="NO CREW SELECTED", 
                                  bg=self.dark_green, fg=self.matrix_green, 
                                  font=("Courier", 10))
        self.crew_status.pack(side="left", padx=5)
        
        # Add tools status label
        self.tools_status = tk.Label(self.status_bar, text="TOOLS LOADING...", 
                                  bg=self.dark_green, fg=self.matrix_green, 
                                  font=("Courier", 10))
        self.tools_status.pack(side="left", padx=5)

        # Model status
        self.model_status = tk.Label(self.status_bar, text=f"MODEL: {self.model_name[:20]}", 
                                   bg=self.dark_green, fg=self.matrix_green, 
                                   font=("Courier", 10))
        self.model_status.pack(side="left", padx=5)
        
        self.system_status = tk.Label(self.status_bar, text="INITIALIZING...", 
                                    bg=self.dark_green, fg=self.matrix_green, 
                                    font=("Courier", 10))
        self.system_status.pack(side="right", padx=5)
        
        # Animation and blinking cursor effect
        self.cursor_visible = True
        self.cursor_blink()
        
        # Store last code response
        self.last_code_response = ""
        
        # Initialize crew and tools
        self.crew = {}
        self.current_crew = None
        
        # Load available tools
        self.available_tools = []
        self.load_tools()
        
        # Initialize crew if provided
        if crew_instance:
            self.crew = crew_instance
            self.populate_crew_selector()
        else:
            # Initialize the system in a separate thread
            threading.Thread(target=self.initialize_system, daemon=True).start()
        
        # Setup enhanced menu
        self.setup_menus()
        
        # Boot sequence - make sure to run this AFTER UI setup is complete
        self.after(500, self.boot_sequence)
        
        # Start matrix rain effect after a short delay
        self.after(1000, self.matrix_canvas.start_animation)
        
        # Focus on input entry after initialization
        self.after(2000, lambda: self.input_entry.focus_set())

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
        """Setup enhanced menu bar"""
        menubar = tk.Menu(self, bg=self.black, fg=self.matrix_green, 
                         activebackground=self.dark_green, 
                         activeforeground=self.matrix_green, bd=0)
        self.config(menu=menubar)
        
        # Crew menu
        crew_menu = tk.Menu(menubar, tearoff=0, bg=self.black, fg=self.matrix_green,
                          activebackground=self.dark_green, activeforeground=self.matrix_green)
        crew_menu.add_command(label="LIST ALL CREW", command=self.list_crew)
        crew_menu.add_command(label="RESET ALL CREW", command=self.reset_all_crew)
        crew_menu.add_separator()
        crew_menu.add_command(label="CREW STATUS", command=self.show_crew_status)
        menubar.add_cascade(label="CREW", menu=crew_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.black, fg=self.matrix_green,
                           activebackground=self.dark_green, activeforeground=self.matrix_green)
        tools_menu.add_command(label="LIST ALL TOOLS", command=self.list_tools)
        tools_menu.add_command(label="TOOL DESCRIPTIONS", command=self.show_tool_descriptions)
        menubar.add_cascade(label="TOOLS", menu=tools_menu)
        
        # System menu
        system_menu = tk.Menu(menubar, tearoff=0, bg=self.black, fg=self.matrix_green,
                            activebackground=self.dark_green, activeforeground=self.matrix_green)
        system_menu.add_command(label="MODEL INFO", command=self.show_model_info)
        system_menu.add_command(label="SYSTEM STATUS", command=self.show_system_status)
        system_menu.add_separator()
        system_menu.add_command(label="CLEAR OUTPUT", command=self.clear_output)
        menubar.add_cascade(label="SYSTEM", menu=system_menu)

    # Enhanced tool button methods
    def run_open_notes_tool(self):
        """Callback for the 'Open Notes' button."""
        self.append_output("> Running tool: open_notes")
        self.system_status.config(text="RUNNING TOOL...")
        threading.Thread(target=self.execute_tool, args=("open_notes",), kwargs={}, daemon=True).start()

    def run_create_file_tool(self):
        """Callback for the 'Create New File' button."""
        filename = simpledialog.askstring("Input", "Enter filename (e.g., log.txt):", parent=self)
        if not filename:
            self.append_output("File creation cancelled.")
            return

        content = simpledialog.askstring("Input", f"Enter content for {filename}:", parent=self)
        if content is None:
            self.append_output("File creation cancelled.")
            return
            
        tool_args = {"filename": filename, "content": content}
        self.append_output(f"> Running tool: create_file with {tool_args}")
        self.system_status.config(text="RUNNING TOOL...")
        threading.Thread(target=self.execute_tool, args=("create_file",), kwargs={'tool_args': tool_args}, daemon=True).start()

    def run_fire_laser_tool(self):
        """Callback for the 'Fire Laser' button."""
        target = simpledialog.askstring("Target Input", "Enter target coordinates:", parent=self)
        if not target:
            self.append_output("Laser firing cancelled.")
            return

        power_level = simpledialog.askstring("Power Level", "Enter power level (1-10):", parent=self)
        if not power_level:
            power_level = "5"  # Default power level
            
        tool_args = {"target": target, "power_level": power_level}
        self.append_output(f"> FIRING LASER AT: {target.upper()}")
        self.system_status.config(text="WEAPONS FIRING...")
        threading.Thread(target=self.execute_tool, args=("fire_laser",), kwargs={'tool_args': tool_args}, daemon=True).start()

    def run_launch_missile_tool(self):
        """Callback for the 'Launch Missile' button."""
        target = simpledialog.askstring("Target Input", "Enter target coordinates:", parent=self)
        if not target:
            self.append_output("Missile launch cancelled.")
            return

        warhead_type = simpledialog.askstring("Warhead Type", "Enter warhead type (standard/plasma/nuclear):", parent=self)
        if not warhead_type:
            warhead_type = "standard"  # Default warhead type
            
        tool_args = {"target": target, "warhead_type": warhead_type}
        self.append_output(f"> LAUNCHING {warhead_type.upper()} MISSILE AT: {target.upper()}")
        self.system_status.config(text="MISSILE LAUNCHING...")
        threading.Thread(target=self.execute_tool, args=("launch_missile",), kwargs={'tool_args': tool_args}, daemon=True).start()

    def boot_sequence(self):
        """Display Matrix-style boot sequence"""
        welcome_text = """



 ██████╗██╗     ███████╗███╗   ███╗███╗   ███╗
██╔════╝██║     ██╔════╝████╗ ████║████╗ ████║
██║     ██║     █████╗  ██╔████╔██║██╔████╔██║
██║     ██║     ██╔══╝  ██║╚██╔╝██║██║╚██╔╝██║
╚██████╗███████╗███████╗██║ ╚═╝ ██║██║ ╚═╝ ██║
 ╚═════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝

            CLEMM-09 QUANTUM INTERFACE SYSTEM
            MISSION: EUROPA(JUPITER II) EXPLORATION
        
            INITIALIZING NEURAL INTERFACE...
            QUANTUM ENCRYPTION: ACTIVE
            QUANTUM TUNNELING: STABLE
        
            ACCESSING CREWNET...
        
            CONNECTING...
        """
        
        # Clear output text area first
        self.output_text.configure(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state='disabled')
        self.output_text.typewrite(welcome_text, delay=5, callback=lambda: self.append_output(
            "SYSTEM READY. TYPE 'HELP' FOR AVAILABLE COMMANDS."))

    def cursor_blink(self):
        """Create blinking cursor effect in input field"""
        if self.cursor_visible:
            self.input_entry.config(insertbackground=self.matrix_green)
        else:
            self.input_entry.config(insertbackground=self.black)
        
        self.cursor_visible = not self.cursor_visible
        self.after(500, self.cursor_blink)
    
    def initialize_system(self):
        """Initialize the system with Matrix-style messages. Runs in a thread."""
        loading_messages = [
           "DECRYPTING QUANTUM DATABASE...",
           "ESTABLISHING NEURAL LINK...",
           "CALCULATING QUANTUM PATHWAYS...",
           "SYNCHRONIZING TIMELINES...",
           "LOADING AI CREW PROFILES..."
        ]
        
        for msg in loading_messages:
            self.after(0, lambda m=msg: self.append_output(m))
            time.sleep(0.5)
        
        self.after(0, lambda: self.append_output("INITIALIZATION COMPLETE. SYSTEM READY."))
        self.after(0, lambda: self.system_status.config(text="READY FOR COMMANDS"))

    def append_output(self, text):
        """Add text to output directly. Must be called from the main UI thread."""
        if not text:
            return
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state='disabled')
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.configure(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state='disabled')
        self.append_output("OUTPUT BUFFER CLEARED")
    
    def process_command_event(self, event):
        """Process command when Enter is pressed"""
        self.process_command()
    
    def process_command(self):
        """Process entered command with Matrix-style feedback"""
        command = self.input_entry.get().strip()
        if not command:
            return
        
        # Display command with green color
        self.append_output(f"> {command}")
        self.input_entry.delete(0, tk.END)
        
        # Process with some visual effects
        self.system_status.config(text="PROCESSING...")
        self.after(100, lambda: self.execute_command(command))
    
    def execute_command(self, command):
        """Execute the command with Matrix flair"""
        command_lower = command.lower()
        print(f"Executing command: {command_lower}")
        
        if command_lower == "exit":
            self.append_output("DISCONNECTING FROM MATRIX...")
            self.after(1000, self.quit)
        
        elif command_lower == "help":
            help_text = """
AVAILABLE COMMANDS:
===================
HELP                - ACCESS THIS INFORMATION NODE
EXIT                - TERMINATE NEURAL CONNECTION
STATUS              - DISPLAY SYSTEM DIAGNOSTICS
DESTINATION         - REVEAL CURRENT MISSION COORDINATES
MODEL_INFO          - DISPLAY ACTIVE MODEL CONFIGURATION
ASK [QUERY]         - INTERROGATE CREW KNOWLEDGE BASE (AI can use tools)
CREW                - LIST AVAILABLE CREW MEMBERS
TOOLS               - LIST AVAILABLE SPECIALIZED TOOLS
USE [NAME]          - SWITCH ACTIVE CREW MEMBER (or use dropdown)
RESET               - PURGE CONVERSATION MEMORY OF ACTIVE CREW
RUN_TOOL <name> ... - EXECUTE A TOOL MANUALLY (e.g., run_tool create_file filename="log.txt" content="hello")
RUN_CODE            - EXECUTE LAST GENERATED CODE SEQUENCE (code_expert only)
CLEAR               - CLEAR OUTPUT BUFFER
"""
            self.output_text.configure(state='normal')
            self.output_text.typewrite(help_text, delay=1, 
                                      callback=lambda: self.output_text.see(tk.END))
            
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
                # This will trigger the on_crew_selected event handler
                self.crew_selector.set(crew_name.upper())
                self.on_crew_selected(None) # Pass None as event object
            else:
                self.append_output(f"ERROR: CREW MEMBER '{crew_name.upper()}' NOT FOUND IN DATABASE")
            self.system_status.config(text="READY FOR COMMANDS")
        
        elif command_lower == "reset":
            self.reset_current_crew()
            self.system_status.config(text="READY FOR COMMANDS")
        
        elif command_lower.startswith("ask "):
            query = command[4:].strip()
            if not query:
                self.append_output("ERROR: QUERY PARAMETER REQUIRED")
                self.system_status.config(text="READY FOR COMMANDS")
                return
            
            if self.crew and self.current_crew in self.crew:
                self.append_output(f"PROCESSING QUERY THROUGH {self.current_crew.upper()}...")
                threading.Thread(target=self.process_ask, args=(query,), daemon=True).start()
            else:
                self.append_output("ERROR: NO ACTIVE CREW MEMBER. SELECT CREW FROM DROPDOWN.")
                self.system_status.config(text="READY FOR COMMANDS")
        
        elif command_lower.startswith("run_tool"):
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                self.append_output("ERROR: TOOL IDENTIFIER AND ARGUMENTS REQUIRED")
                self.system_status.config(text="READY FOR COMMANDS")
                return

            tool_call_str = parts[1]
            match = re.match(r'(\w+)\s*(.*)', tool_call_str)
            if not match:
                self.append_output("ERROR: INVALID TOOL COMMAND FORMAT. Use: run_tool <tool_name> [arg1=val1] ...")
                self.system_status.config(text="READY FOR COMMANDS")
                return

            tool_name = match.group(1)
            args_str = match.group(2)
            kwargs = {}
            if args_str:
                try:
                    # Robust key=value parsing
                    kv_pattern = re.compile(r'(\w+)\s*=\s*(".*?"|\'.*?\'|[^,\s]+)')
                    matches = kv_pattern.findall(args_str)
                    
                    if not matches and args_str.strip():
                        raise ValueError("Arguments must be in 'key=value' format.")

                    for key, value in matches:
                        try:
                            kwargs[key] = ast.literal_eval(value)
                        except (ValueError, SyntaxError):
                            kwargs[key] = value # Keep as unquoted string
                            
                except (ValueError, SyntaxError, TypeError) as e:
                    self.append_output(f"ERROR: COULD NOT PARSE TOOL ARGUMENTS: {e}")
                    self.system_status.config(text="READY FOR COMMANDS")
                    return
            
            self.append_output(f"EXECUTING TOOL: '{tool_name.upper()}' with args: {kwargs}")
            self.system_status.config(text="RUNNING TOOL...")
            
            threading.Thread(target=self.execute_tool, args=(tool_name,), kwargs={'tool_args': kwargs}, daemon=True).start()
        
        elif command_lower == "run_code":
            if self.current_crew == "code_expert" and self.last_code_response:
                self.append_output("\n\u26A0 SECURITY WARNING \u26A0")
                self.append_output("UNAUTHORIZED CODE EXECUTION DETECTED")
                self.append_output("REVIEW BEFORE PROCEEDING:\n")
                self.append_output(self.last_code_response)
                
                def show_confirm_dialog():
                    confirm = messagebox.askyesno(
                        "EXECUTE CODE?", 
                        "EXECUTE POTENTIALLY DANGEROUS CODE SEQUENCE?",
                        icon="warning"
                    )
                    if confirm:
                        try:
                            self.append_output("\n--- EXECUTING CODE SEQUENCE ---")
                            # Sanitize to remove markdown code blocks
                            code_to_run = re.sub(r'```python\n|```', '', self.last_code_response, flags=re.IGNORECASE)
                            process = subprocess.run(
                                [sys.executable, '-c', code_to_run.strip()],
                                capture_output=True, text=True, check=False, timeout=30
                            )
                            if process.returncode == 0:
                                self.append_output("--- EXECUTION SUCCESSFUL ---")
                                if process.stdout: self.append_output(process.stdout)
                            else:
                                self.append_output("--- EXECUTION ERROR ---")
                                if process.stderr: self.append_output(process.stderr)
                        except subprocess.TimeoutExpired:
                             self.append_output("--- EXECUTION TIMEOUT AFTER 30 SECONDS ---")
                        except Exception as e:
                            self.append_output(f"FATAL ERROR DURING EXECUTION: {e}")
                    else:
                        self.append_output("CODE EXECUTION ABORTED")
                    self.system_status.config(text="READY FOR COMMANDS")
                
                self.after(500, show_confirm_dialog)
            else:
                self.append_output("ERROR: NO CODE SEQUENCE AVAILABLE OR 'code_expert' NOT ACTIVE")
                self.system_status.config(text="READY FOR COMMANDS")
        
        else:
            self.append_output("COMMAND NOT RECOGNIZED")
            self.append_output("TYPE 'HELP' FOR COMMAND LIST")
            self.system_status.config(text="READY FOR COMMANDS")
    
    def execute_tool(self, tool_name: str, tool_args: Optional[Dict[str, Any]] = None):
        """Execute a tool in a separate thread, for manual runs."""
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
        """Process an 'ask' command by calling the crew's chat method, which handles the agentic loop."""
        try:
            self.after(0, lambda: self.system_status.config(text="QUERYING NEURAL INTERFACE..."))
            
            # The .chat() method in the Crew class now handles the entire tool-use loop internally.
            # The UI just needs to send the query and display the final, consolidated response.
            final_response = self.crew[self.current_crew].chat(query)
            
            header = f"\n[{self.current_crew.upper()} RESPONSE]:\n"
            full_text = header + "═" * (len(header) - 2) + "\n" + (final_response or "[NO RESPONSE]")

            # Use typewrite for a better visual effect for the final answer
            self.after(0, lambda: self.output_text.typewrite(
                full_text,
                delay=5,
                callback=lambda: self.after(0, self.store_code_if_expert, final_response)
            ))
                
        except Exception as e:
            self.after(0, lambda err=e: self.append_output(f"\nERROR IN NEURAL INTERFACE: {err}"))
        finally:
            self.after(0, lambda: self.system_status.config(text="READY FOR COMMANDS"))

    def store_code_if_expert(self, response: str):
        """Checks if the current crew is code_expert and stores the response."""
        if self.current_crew == "code_expert":
            self.last_code_response = response
            self.append_output("\n[CODE SEQUENCE STORED. Use 'run_code' to execute.]")
    
    def reset_all_crew(self):
        """Resets all crew members' conversation history."""
        if self.crew:
            for crew_name in self.crew:
                self.crew[crew_name].reset()
            self.last_code_response = ""
            self.append_output("MEMORY PURGE COMPLETE FOR ALL CREW MEMBERS")
        else:
            self.append_output("ERROR: CREW DATABASE EMPTY")

    def show_crew_status(self):
        """Displays the status of all available crew members."""
        if not self.crew:
            self.append_output("ERROR: CREW DATABASE EMPTY")
            return
        
        status_lines = ["\n╔═══════════════ CREW STATUS ═══════════════╗"]
        for name, instance in self.crew.items():
            status = 'ACTIVE' if name == self.current_crew else 'STANDBY'
            msg_count = len(instance.messages) - 1 # -1 for system prompt
            status_lines.append(f"║ {name.upper():<15} │ STATUS: {status:<10} │ MEMORY: {msg_count: >2} ENTRIES ║")
        status_lines.append("╚═══════════════════════════════════════════╝")
        self.append_output("\n".join(status_lines))

    def show_system_status(self):
        """Displays a detailed system status screen."""
        self.execute_command("status") # Reuse the command for consistency

    def list_crew(self):
        """List available crew members in the output."""
        if self.crew and isinstance(self.crew, dict) and len(self.crew) > 0:
            self.show_crew_status()
        else:
            self.append_output("ERROR: CREW DATABASE EMPTY")
    
    def list_tools(self):
        """Tool information"""
        if self.available_tools:
             self.show_tool_descriptions()
        else:
             self.append_output("No tools available.")

    def show_tool_descriptions(self):
        """Displays detailed descriptions for all available tools."""
        if not self.available_tools:
            self.append_output("ERROR: NO TOOLS LOADED")
            return
        
        desc_lines = ["\n╔═══════════════ TOOL DESCRIPTIONS ═══════════════╗"]
        for tool_name in self.available_tools:
            description = get_tool_description(tool_name)
            if description:
                desc_lines.append(f"╟─ {description}")
        desc_lines.append("╚════════════════════════════════════════════════╝")
        self.append_output("\n".join(desc_lines))

    def show_model_info(self):
        """Display model information"""
        model_type = "GGUF"
        model_info = f"""
    MODEL INFORMATION:
    ══════════════════
    NAME: {self.model_name}
    TYPE: {model_type}
    MAX TOKENS: {self.max_tokens or 'N/A'}
    BACKEND: LLAMA.CPP
    STATUS: {'LOADED' if self.model is not None else 'NOT LOADED'}
    """
        self.append_output(model_info)


def launch_matrix_ui(model, crew_instance, max_tokens):
    """Initializes and launches the main UI window."""
    model_name = getattr(model, 'model_path', 'Unknown GGUF Model')
    if isinstance(model_name, str) and ('/' in model_name or '\\' in model_name):
        model_name = os.path.basename(model_name)
    available_tools = list_tools() if 'list_tools' in globals() else []
    
    app = ClemmMatrixUI(
        crew_instance=crew_instance,
        model=model,
        max_tokens=max_tokens,
        model_name=model_name,
        available_tools=available_tools
    )
    app.mainloop()

if __name__ == "__main__":
    # This allows running the UI directly for testing purposes without a pre-loaded model or crew.
    # In a real application, launch_matrix_ui would be called by the main script.
    app = ClemmMatrixUI(model_name="STANDALONE_TEST")
    
    # Manually initialize a dummy crew for testing UI features
    try:
        # A mock model object for UI testing.
        class MockModel:
            def __init__(self):
                self.model_path = "mock_model.gguf"

        model_obj = MockModel() 
        app.model = model_obj
        app.crew = crew.initialize_crew(model_obj, 512)
        app.populate_crew_selector()
        app.append_output("[STANDALONE MODE]: Initialized with test crew.")
    except (ImportError, FileNotFoundError, NameError) as e:
        app.append_output(f"[STANDALONE MODE]: Could not load test crew. Error: {e}")
        app.append_output("UI is running in limited mode. 'ask' commands will fail.")

    app.mainloop()