# wf-panel-pi GUI Configurator

A simple Python GTK GUI for editing your `~/.config/wf-panel-pi.ini` file.  
Easily add, remove, and reorder panel launchers for [wf-panel-pi](https://github.com/WayfireWM/wf-panel-pi) without editing INI files by hand.

---

## Features

- Displays launcher icons (from .desktop files) to the left of the launcher name
- Allows click-and-drag reordering
- Lets you add and remove launchers.
- Saves the order and selection to ~/.config/wf-panel-pi.ini
- Designed and tested for Raspberry Pi OS

---

## Installation

### 1. Install Dependencies

#### Raspberry Pi OS (Debian-based)

sudo apt update && sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

---

### 2. Download the Script

wf_panel_pi_config.py

---

### 3. Run the GUI

chmod +x wf_panel_pi_config.py && python3 wf_panel_pi_config.py

---

## License

MIT License
