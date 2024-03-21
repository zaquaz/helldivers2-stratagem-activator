import json
import random
import sys
import time
from typing import Dict, List

from app.modules import Config, Key
from app.types.stratagems import ActionMap, AvailableActions
from app.utils import log, showerror


class Stratagems:
    bindings: Dict[AvailableActions, int]
    codes: Dict[str, str]
    active_code_sequence: List[str]
    menu_open: bool = False
    config: Config

    def __init__(self, stratagem_key: str, codes_file_path: str):
        self.config = Config()
        self.map_bindings()
        self.load_key_sequences(codes_file_path)
        self.load_active_key_sequence(stratagem_key)

    def map_bindings(self):
        self.bindings = {
            key: self.config["keybindings"][config_key]
            for (key, config_key) in ActionMap.items()
        }

    def load_key_sequences(self, file_path):
        try:
            log("Loading stratagem key sequences..")
            with open(file_path, encoding="utf-8") as f:
                self.codes = json.load(f)
        except FileNotFoundError:
            showerror("Error", f"File not found: {file_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            showerror("Error", f"Error decoding JSON file: {file_path}")
            sys.exit(1)

    def load_active_key_sequence(self, key):
        if key in self.codes:
            self.active_code_sequence = self.codes[key].split(" ")
        else:
            showerror(
                "Stratagem execution error", f'Key "{key}" not found in codes.json'
            )
            sys.exit(1)

    def simulate_key_presses(self):
        for element in self.active_code_sequence:
            delay = round(
                random.uniform(
                    int(self.config["settings"]["delay_min"]),
                    int(self.config["settings"]["delay_max"]),
                )
                * 0.001,
                4,
            )
            Key.press(self.bindings[element])
            log(f"sleeping for {delay}s")
            time.sleep(delay)

    def toggle_menu(self):
        if self.config["settings"]["open_mode"] == "hold":
            (Key.up if self.menu_open else Key.down)(self.bindings["O"])
        elif not self.menu_open:
            Key.press(self.bindings["O"])
        self.menu_open = not self.menu_open

    def activate(self):
        log(f"Executing stratagem sequence: {self.active_code_sequence}")
        # Open stratagem menu
        self.toggle_menu()
        time.sleep(0.02)

        # Send Key Sequence
        self.simulate_key_presses()

        # Close stratagem menu
        self.toggle_menu()
