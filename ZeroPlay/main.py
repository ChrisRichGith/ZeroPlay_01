# main.py
"""
Main entry point for the RPG. Launches the main Game controller.
"""
import tkinter as tk
from tkinter import ttk
from character import Character
from start_menu_gui import StartMenu
from class_selection_frame import ClassSelectionFrame
from rpg_gui import RpgGui
from save_load_system import save_game, load_game, get_save_files, SAVE_DIR
from highscore_gui import HighscoreWindow
from splash_screen import SplashScreen
import os

class Game:
    """The main controller for the application, manages scenes."""
    def __init__(self, root):
        self.root = root
        self.root.title("Chronicle of the Idle Hero")
        self.root.attributes('-zoomed', True) # Alternative for maximizing on Linux

        # Apply a modern theme
        style = ttk.Style(self.root)
        style.theme_use('clam')

        self.current_frame = None
        self.character = None
        self.language = "de" # Default language

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.show_splash_screen()

    def switch_frame(self, frame_class, *args, **kwargs):
        """Destroys the current frame and replaces it with a new one."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = frame_class(self.root, *args, **kwargs)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_splash_screen(self):
        """Displays the initial splash screen for language selection."""
        callbacks = {'continue': self.start_game_from_splash}
        self.switch_frame(SplashScreen, callbacks=callbacks)

    def start_game_from_splash(self, selected_language):
        """Sets the language and proceeds to the main menu."""
        self.language = selected_language
        self.show_start_menu()

    def show_start_menu(self):
        callbacks = {
            'load': self.load_and_show_game,
            'new': self.show_character_creation,
            'quit': self.quit_game,
            'highscores': self.show_highscores
        }
        self.switch_frame(StartMenu, callbacks=callbacks, language=self.language)

    def show_highscores(self):
        HighscoreWindow(self.root)

    def show_character_creation(self):
        callbacks = {
            'back': self.show_start_menu,
            'confirm': self.create_character_and_show_game
        }
        self.switch_frame(ClassSelectionFrame, callbacks=callbacks)

    def create_character_and_show_game(self, name, klasse):
        self.character = Character(name, klasse)
        self.show_game()

    def load_and_show_game(self, character_name):
        self.character = load_game(character_name)
        if self.character:
            self.show_game()
        else:
            # Handle failed load, maybe show an error and return to start menu
            self.show_start_menu()

    def show_game(self):
        self.root.title(f"Chronicle of the Idle Hero - {self.character.name}")
        callbacks = {
            'game_over': self.handle_game_over_and_restart,
        }

        # Check for any pending messages from the rebirth process
        initial_messages = self.character.pending_unlock_messages
        self.character.pending_unlock_messages = [] # Clear messages after retrieving

        # The RpgGui now takes the character object directly
        self.switch_frame(RpgGui, character=self.character, callbacks=callbacks, initial_messages=initial_messages)


    def handle_game_over_and_restart(self, death_by_boss):
        """
        Handles the game over logic.
        - If death by boss: performs rebirth, saves, and restarts the game.
        - If death by quest: deletes the save file and returns to the start menu.
        """
        if death_by_boss:
            print(f"{self.character.name} wurde von einem Boss besiegt. Wiedergeburt wird eingeleitet.")
            self.character.rebirth()
            save_game(self.character)
            # Reload the game screen with the reborn character
            self.show_game()
        else:
            print(f"{self.character.name} ist bei einer Quest gestorben. Spielstand wird gelöscht.")
            save_file_path = os.path.join(SAVE_DIR, f"{self.character.name}.sav")
            if os.path.exists(save_file_path):
                os.remove(save_file_path)
                print(f"Spielstand für {self.character.name} gelöscht.")

            self.character = None
            self.show_start_menu()

    def on_closing(self):
        """Handles the main window closing event."""
        # If the game screen is active, save the character
        if isinstance(self.current_frame, RpgGui) and not self.current_frame.game_over:
            save_game(self.character)
        self.quit_game()

    def quit_game(self):
        """Stops the main loop and closes the application."""
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Starts the main tkinter loop."""
        self.root.mainloop()

if __name__ == "__main__":
    main_root = tk.Tk()
    app = Game(main_root)
    app.run()
