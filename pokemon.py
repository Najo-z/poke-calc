import tkinter as tk
from tkinter import ttk

from api import pokemon, pokemon_names, rate, poketypes
from utils import get_ball_rate, get_capture_rate, get_status_rate

pokeball_types = [
    "beastball",
    "cherishball", "gsball", "pokeball", "ancientpokeball",
    "diveball",
    "dreamball",
    "duskball",
    "fastball",
    "featherball",
    "friendball",
    "gigatonball",
    "greatball", "ancientgreatball",
    "healball",
    "heavyball", "ancientheavyball",
    "jetball",
    "leadenball",
    "levelball",
    "loveball",
    "lureball",
    "luxuryball",
    "masterball", "originball", "parkball",
    "moonball",
    "nestball",
    "netball",
    "premierball",
    "quickball",
    "repeatball",
    "safariball",
    "sportball",
    "timerball",
    "ultraball", "ancientultraball",
    "wingball"
]

# Status variables
FREEZE_STATUS = False
SLEEP_STATUS = False
PARALYZED_STATUS = False
BURNED_STATUS = False
POISONED_STATUS = False
HP_RATIO = 1.0
SELECTED_POKEMON = "azelf"
SELECTED_POKEBALL = pokeball_types[0]


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Capture Calculator")
        self.root.geometry("400x500")  # Increased height for extra checkboxes

        # Status BooleanVars
        self.freeze_var = tk.BooleanVar()
        self.sleep_var = tk.BooleanVar()
        self.paralyzed_var = tk.BooleanVar()
        self.burned_var = tk.BooleanVar()
        self.poisoned_var = tk.BooleanVar()

        # Other variables
        self.pokemon_var = tk.StringVar()
        self.pokeball_var = tk.StringVar()
        self.hp_ratio_var = tk.StringVar(value="1")

        self.create_widgets()
        self.update_cap_rate()

    def create_widgets(self):
        # Status effects frame with separate checkboxes
        status_frame = ttk.LabelFrame(self.root, text="Status Effects")
        status_frame.pack(fill="x", padx=10, pady=10)

        self.freeze_check = ttk.Checkbutton(
            status_frame,
            text="Freeze ❄️",
            variable=self.freeze_var,
            command=self.update_status,
        )
        self.freeze_check.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.sleep_check = ttk.Checkbutton(
            status_frame,
            text="Sleep 😴",
            variable=self.sleep_var,
            command=self.update_status,
        )
        self.sleep_check.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.paralyzed_check = ttk.Checkbutton(
            status_frame,
            text="Paralyzed ⚡",
            variable=self.paralyzed_var,
            command=self.update_status,
        )
        self.paralyzed_check.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.burned_check = ttk.Checkbutton(
            status_frame,
            text="Burned 🔥",
            variable=self.burned_var,
            command=self.update_status,
        )
        self.burned_check.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        self.poisoned_check = ttk.Checkbutton(
            status_frame,
            text="Poisoned ☠️",
            variable=self.poisoned_var,
            command=self.update_status,
        )
        self.poisoned_check.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        # HP ratio frame with entry field
        hp_frame = ttk.LabelFrame(self.root, text="HP Percentage (0-100)")
        hp_frame.pack(fill="x", padx=10, pady=10)

        vcmd = (self.root.register(self.validate_float), "%P")
        self.hp_entry = ttk.Entry(
            hp_frame,
            textvariable=self.hp_ratio_var,
            validate="key",
            validatecommand=vcmd,
        )
        self.hp_entry.pack(fill="x", padx=5, pady=5)
        self.hp_entry.bind("<FocusOut>", self.update_hp_ratio)
        self.hp_entry.bind("<Return>", self.update_hp_ratio)
        self.hp_entry.bind("<KP_Enter>", self.update_hp_ratio)

        # Pokemon selection frame with combobox
        pokemon_frame = ttk.LabelFrame(self.root, text="Select Pokemon")
        pokemon_frame.pack(fill="x", padx=10, pady=10)

        self.pokemon_combo = ttk.Combobox(
            pokemon_frame,
            textvariable=self.pokemon_var,
            values=pokemon_names,
        )
        self.pokemon_combo.pack(fill="x", padx=5, pady=5)
        self.pokemon_var.set(SELECTED_POKEMON)
        self.pokemon_combo.bind("<<ComboboxSelected>>", self.on_pokemon_select)
        self.pokemon_combo.bind("<KeyRelease>", self.on_pokemon_key_release)
        self.pokemon_combo.bind("<ButtonPress-3>", self.on_pokemon_right_click)

        # Pokeball selection frame with combobox
        pokeball_frame = ttk.LabelFrame(self.root, text="Select Pokeball")
        pokeball_frame.pack(fill="x", padx=10, pady=10)

        self.pokeball_combo = ttk.Combobox(
            pokeball_frame,
            textvariable=self.pokeball_var,
            values=pokeball_types
        )
        self.pokeball_combo.pack(fill="x", padx=5, pady=5)
        self.pokeball_var.set(SELECTED_POKEBALL)
        self.pokeball_combo.bind("<<ComboboxSelected>>", self.on_pokeball_select)
        self.pokeball_combo.bind("<KeyRelease>", self.on_pokeball_key_release)
        self.pokeball_combo.bind("<ButtonPress-3>", self.on_pokeball_right_click)
        
        # Results frame for capture rate display
        result_frame = ttk.LabelFrame(self.root, text="Capture Rate")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_label = ttk.Label(result_frame, text="", wraplength=350)
        self.result_label.pack(fill="both", expand=True, padx=5, pady=5)

    def validate_float(self, value):
        if value == "":
            return True
        try:
            if value.count(".") <= 1:
                float_val = float(value)
                return 0.0 <= float_val <= 100.0
            return False
        except ValueError:
            return False

    def update_status(self):
        global FREEZE_STATUS, SLEEP_STATUS, PARALYZED_STATUS, BURNED_STATUS, POISONED_STATUS
        FREEZE_STATUS = self.freeze_var.get()
        SLEEP_STATUS = self.sleep_var.get()
        PARALYZED_STATUS = self.paralyzed_var.get()
        BURNED_STATUS = self.burned_var.get()
        POISONED_STATUS = self.poisoned_var.get()

        self.update_cap_rate()

    def update_hp_ratio(self, event=None):
        global HP_RATIO
        try:
            HP_RATIO = float(self.hp_ratio_var.get())
            self.update_cap_rate()
        except ValueError:
            self.hp_ratio_var.set(str(HP_RATIO))

    def on_pokemon_select(self, event):
        global SELECTED_POKEMON
        SELECTED_POKEMON = self.pokemon_var.get()
        self.update_cap_rate()

    def on_pokeball_select(self, event):
        global SELECTED_POKEBALL
        SELECTED_POKEBALL = self.pokeball_var.get()
        self.update_cap_rate()

    def on_pokemon_key_release(self, event):
        typed_text = self.pokemon_var.get().lower()

        if typed_text:
            filtered_options = [
                poke for poke in pokemon_names if poke.lower().startswith(typed_text) #START WITH not 'in'
            ]
            self.pokemon_combo.config(values=filtered_options)
        else:
            self.pokemon_combo.config(values=pokemon_names)


        global SELECTED_POKEMON
        SELECTED_POKEMON = self.pokemon_var.get()
        if SELECTED_POKEMON not in pokemon_names:
            return
        self.update_cap_rate()

    # right click to see combo
    def on_pokemon_right_click(self, event):
        self.pokemon_combo.event_generate("<Down>")

    def on_pokeball_key_release(self, event):
        typed_text = self.pokeball_var.get().lower()

        if typed_text:
            filtered_options = [
                pokeb for pokeb in pokeball_types if pokeb.lower().startswith(typed_text) #START WITH not 'in'
            ]
            self.pokeball_combo.config(values=filtered_options)
        else:
            self.pokeball_combo.config(values=pokeball_types)


        global SELECTED_POKEBALL
        SELECTED_POKEBALL = self.pokeball_var.get()
        if SELECTED_POKEBALL not in pokeball_types:
            return
    
    #Same as on_pokemon_right_click but for pokeballs
    def on_pokeball_right_click(self, event):
        self.pokeball_combo.event_generate("<Down>")


    def update_cap_rate(self):
        # Determine status for capture rate calculation
        status = ""
        if SLEEP_STATUS:
            status = "sleep"  # Both freeze and sleep use the same status modifier
        cap_rate = rate(SELECTED_POKEMON)
        pokemon_types = poketypes(SELECTED_POKEMON)
        cap_rate_text = get_capture_rate(
            cap_rate=cap_rate,
            ball=get_ball_rate(
                SELECTED_POKEBALL,
                {
                    "status": status,
                    "types": pokemon_types,
                    **pokemon(SELECTED_POKEMON),
                },
            ),
            status=get_status_rate(
                FREEZE_STATUS or SLEEP_STATUS,  # Sleep/Freeze status
                PARALYZED_STATUS
                or BURNED_STATUS
                or POISONED_STATUS,  # Other status conditions
            ),
            hp_ratio=HP_RATIO / 100,
        )
        display_val = round(cap_rate_text, 2)
        if display_val > 100:
            display_val = 100
        self.result_label.config(
            text=f"Catch chance: {display_val}%\nCatch rate: {cap_rate}\nPokemon Type(s):{pokemon_types}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
