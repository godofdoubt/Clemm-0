# clemm08/bridge/tools/voice_control.py
import datetime
import os
import shutil
import subprocess
import time
import webbrowser
import wikipedia
import pyttsx3
import speech_recognition as sr
import pyjokes
import pyautogui
import platform
from typing import Optional, Dict, Callable
from playwright.sync_api import sync_playwright
from pathlib import Path
from .weapon import fire_laser, launch_missile


print("TEST1")

class VoiceControl:
    """Complete voice control system merging Poe v0.01 with Clemm enhancements, cross-platform."""

    def __init__(self):
        # Initialize text-to-speech engine with fallback
        try:
            driver = 'sapi5' if platform.system() == 'Windows' else 'espeak'
            self.engine = pyttsx3.init(driver)
            voices = self.engine.getProperty('voices')
            if voices:  # Ensure voices are available
                self.engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"Warning: Text-to-speech initialization failed: {e}")
            print("Audio output will be text-only.")
            self.engine = None
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize command registry
        self.commands = self._initialize_commands()
        
        # Set up display (Poe-style)
        columns = shutil.get_terminal_size().columns
        print("#####################".center(columns))
        print("hoş geldiniz".center(columns))
        print("#####################".center(columns))
        
        # Announce initialization
        self.speak("My name is Poe version 0.01, enhanced for Clemm.")
        self.wish_me()

    def speak(self, text: str) -> None:
        """Synthesize and speak the given text, with fallback if TTS fails."""
        print(f"System: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e} - Continuing with text output only.")

    def wish_me(self) -> None:
        """Provide time-based greeting (from Poe)."""
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            self.speak("Good Morning!")
        elif 12 <= hour < 18:
            self.speak("Good Afternoon!")
        else:
            self.speak("Good Evening!")
        self.speak("How can I help you?")

    def listen(self) -> Optional[str]:
        """Listen for voice commands and convert to text (from Poe)."""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.pause_threshold = 1
                audio = self.recognizer.listen(source)
                print("Recognizing...")
                command = self.recognizer.recognize_google(audio, language='en-in')
                print(f"Command received: {command}")
                return command.lower()
        except Exception as e:
            print(f"Command recognition error: {e}")
            self.speak("Unable to recognize your voice.")
            return None

    def _initialize_commands(self) -> Dict[str, Callable]:
        """Initialize all command handlers, merging Poe and Clemm features with OS checks."""
        commands = {
            # Clemm weapon commands
            'fire laser': self._handle_laser_command,
            'launch missile': self._handle_missile_command,
            'weapon status': self._handle_status_request,
            
            # Poe web commands
            'wikipedia': self._handle_wikipedia_search,
            'open youtube': lambda _: webbrowser.open("https://youtube.com"),
            'open google': lambda _: webbrowser.open("https://google.com"),
            '9gag': lambda _: webbrowser.open("https://9gag.com"),
            'open box': lambda _: webbrowser.open("https://dizibox.in"),
            'search': self._handle_web_search,
            'where is': self._handle_location_search,
            
            # Poe interaction commands
            'tell joke': lambda _: self.speak(pyjokes.get_joke()),
            'how are you': lambda _: [self.speak("I am fine, thank you"), self.speak("How are you?")],
            'fine': lambda _: self.speak("It's good to know that you're fine"),
            'who made you': lambda _: self.speak("I have been created by Okan Bilge Öz"),
            'who i am': lambda _: self.speak("If you talk then definitely you're human"),
            'is love': lambda _: self.speak("It is the 7th sense that destroys all other senses"),
            'who are you': lambda _: self.speak("I am Poe, your virtual assistant, enhanced by Okan"),
            'reason for you': lambda _: self.speak("I was created as a minor project by Okan Bilge Öz"),
            'good morning': lambda _: [self.speak("A warm Good Morning"), self.speak("How are you?")],
            
            # Poe system commands (adapted for cross-platform)
            'shutdown system': lambda _: self._handle_system_command("shutdown"),
            'restart': lambda _: self._handle_system_command("restart"),
            'hibernate': lambda _: self._handle_system_command("hibernate"),
            'log off': lambda _: self._handle_system_command("log off"),
            'empty recycle bin': self._handle_empty_recycle_bin,
            
            # Poe note commands
            'write note': self._handle_note_writing,
            'show note': self._handle_note_reading,
            
            # Poe automation commands (using pyautogui)
            'next': lambda _: [pyautogui.hotkey('shift', 'n')],
            'full screen': lambda _: [time.sleep(3), pyautogui.press('f')]
        }
        
        # Add Windows-only command if on Windows
        if platform.system() == 'Windows':
            commands['lock window'] = lambda _: ctypes.windll.user32.LockWorkStation()
        else:
            commands['lock window'] = lambda _: self.speak("Locking the screen is not supported on this OS")
            
        return commands

    def _handle_wikipedia_search(self, command: str) -> str:
        """Handle Wikipedia search."""
        try:
            self.speak("Searching Wikipedia...")
            query = command.replace("wikipedia", "").strip()
            results = wikipedia.summary(query, sentences=3)
            self.speak("According to Wikipedia")
            print(results)
            self.speak(results)
            return results
        except Exception as e:
            error_msg = f"Wikipedia search failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_web_search(self, command: str) -> str:
        """Handle web search with Playwright."""
        try:
            search_term = command.replace("search", "").strip()
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f"https://www.google.com/search?q={search_term}")
                self.speak(f"Searching for {search_term}")
                browser.close()
            return f"Searching for {search_term}"
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_location_search(self, command: str) -> str:
        """Handle location search with Playwright."""
        try:
            location = command.replace("where is", "").strip()
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f"https://www.google.com/maps/place/{location}")
                self.speak(f"Locating {location}")
                browser.close()
            return f"Looking up location: {location}"
        except Exception as e:
            error_msg = f"Location search failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_note_writing(self, command: str) -> str:
        """Handle note writing."""
        try:
            self.speak("What should I write?")
            note_content = self.listen()
            if not note_content:
                return "No note content received"
            with open('poe_notes.txt', 'a') as file:
                self.speak("Should I include date and time?")
                include_dt = self.listen()
                if include_dt and ('yes' in include_dt or 'sure' in include_dt):
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"[{timestamp}] {note_content}\n")
                else:
                    file.write(f"{note_content}\n")
            self.speak("Note has been written")
            return "Note saved successfully"
        except Exception as e:
            error_msg = f"Note writing failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_note_reading(self, command: str) -> str:
        """Handle note reading."""
        try:
            if not os.path.exists('poe_notes.txt'):
                self.speak("No notes found")
                return "No notes available"
            with open('poe_notes.txt', 'r') as file:
                notes = file.read()
            self.speak("Here are your notes")
            print(notes)
            self.speak(notes[:50])  # Limit speech
            return "Notes displayed"
        except Exception as e:
            error_msg = f"Note reading failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_empty_recycle_bin(self, command: str) -> str:
        """Handle recycle bin emptying (Linux/Windows adapted)."""
        try:
            if platform.system() == 'Windows':
                subprocess.run('rd /s /q %systemdrive%\\$Recycle.Bin', shell=True, check=False)
                self.speak("Recycle bin emptied")
                return "Recycle bin emptied"
            else:
                self.speak("Emptying the trash is not fully supported on this OS")
                trash_dir = os.path.expanduser("~/.local/share/Trash/files")
                if os.path.exists(trash_dir):
                    shutil.rmtree(trash_dir, ignore_errors=True)
                    os.makedirs(trash_dir, exist_ok=True)
                return "Trash emptying attempted"
        except Exception as e:
            error_msg = f"Recycle bin emptying failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_system_command(self, command_type: str) -> str:
        """Handle system commands cross-platform."""
        try:
            if platform.system() == 'Windows':
                if command_type == "shutdown":
                    self.speak("Hold on! Your system is shutting down")
                    subprocess.call('shutdown /p /f')
                elif command_type == "restart":
                    self.speak("System restarting")
                    subprocess.call(["shutdown", "/r"])
                elif command_type == "hibernate":
                    self.speak("Hibernating")
                    subprocess.call("shutdown /h")
                elif command_type == "log off":
                    self.speak("Make sure all applications are closed")
                    time.sleep(5)
                    subprocess.call(["shutdown", "/l"])
            else:  # Linux
                if command_type == "shutdown":
                    self.speak("Shutting down system")
                    subprocess.call(["shutdown", "-h", "now"])
                elif command_type == "restart":
                    self.speak("System restarting")
                    subprocess.call(["reboot"])
                elif command_type == "hibernate":
                    self.speak("Hibernation may not be supported")
                    subprocess.call(["systemctl", "hibernate"])
                elif command_type == "log off":
                    self.speak("Logging off not directly supported, closing session")
                    subprocess.call(["pkill", "-u", os.getlogin()])
            return f"System {command_type} initiated"
        except Exception as e:
            error_msg = f"System command failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_laser_command(self, command: str) -> str:
        """Handle firing the laser weapon."""
        try:
            target = command.replace("fire laser", "").strip() or "unknown target"
            result = fire_laser(target, power_level=50)
            self.speak(result)
            return result
        except Exception as e:
            error_msg = f"Laser command failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_missile_command(self, command: str) -> str:
        """Handle launching a missile."""
        try:
            target = command.replace("launch missile", "").strip() or "unknown target"
            result = launch_missile(target, warhead_type="standard")
            self.speak(result)
            return result
        except Exception as e:
            error_msg = f"Missile command failed: {str(e)}"
            self.speak(error_msg)
            return error_msg

    def _handle_status_request(self, command: str) -> str:
        """Handle weapon status request."""
        self.speak("Weapons systems online. Laser and missile capabilities operational.")
        return "Weapons status: Operational"

    def run(self) -> None:
        """Main loop for running the voice control system."""
        while True:
            command = self.listen()
            if not command:
                continue
            if 'exit' in command:
                self.speak("Goodbye!")
                break
            for trigger, handler in self.commands.items():
                if trigger in command:
                    handler(command)
                    break
            else:
                self.speak("Command not recognized")

#def initialize_voice_control() -> VoiceControl:
   # """Initialize and return a new voice control system."""
    #return VoiceControl()

if __name__ == "__main__":
    #os.system('cls' if os.name == 'nt' else 'clear')
    #control_system = initialize_voice_control()
    #control_system.run()
    