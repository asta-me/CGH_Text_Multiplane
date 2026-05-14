
# =============================================================
# demo_text_holograms_v2.py
#
# Demo for generating and displaying multiplane text holograms
# using phase-only computer-generated holography (CGH).
#
# Features:
# - Interactive GUI for text, position, and focus control
# - Real-time hologram update and display using pygame
# - Minimal Random Superposition (RS) algorithm for phase calculation
#
# Author: Marco Astarita
# =============================================================

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pygame_functions import *
import matplotlib.pyplot as plt


# --- Auxiliary FFT functions ---
fft2 = np.fft.fft2
ifft2 = np.fft.ifft2
fftshift = np.fft.fftshift
ifftshift = np.fft.ifftshift

## Generate a centered grayscale image of the input text
def generate_text_image(text, image_size=1080, text_area_size=540):
    image = Image.new('L', (image_size, image_size), color=0)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_x = (image_size - (text_bbox[2] - text_bbox[0])) / 2
    text_y = (image_size - (text_bbox[3] - text_bbox[1])) / 2
    draw.text((text_x, text_y), text, fill=255, font=font)
    return np.array(image)

## Minimal Random Superposition (RS) phase calculation
def RS_minimal(target, phase_0):
    E_0 = np.sqrt(target) * np.exp(1j * phase_0)
    return np.angle(fftshift(fft2(ifftshift(E_0))))

## GUI dialog for interactive text and hologram parameter control
class InputDialog(tk.Toplevel):
    def __init__(self, parent, settings, update_callback, close_callback):
        super().__init__(parent)
        self.title("Hologram Controls")
        self.settings = settings
        self.update_callback = update_callback
        self.close_callback = close_callback
        self.frames = []

        for i, setting in enumerate(self.settings):
            frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.frames.append(frame)

            # Titolo
            label_title = tk.Label(frame, text=f"Text {i+1}")
            label_title.grid(row=0, column=0, columnspan=2, pady=5)

            # Campo per il testo
            label_text = tk.Label(frame, text="Text:")
            label_text.grid(row=1, column=0, sticky=tk.W)
            entry_text = tk.Entry(frame, width=20)
            entry_text.insert(0, setting["text"])
            entry_text.bind('<Return>', lambda e, idx=i: self.update_text(idx))
            entry_text.grid(row=1, column=1)
            setting["entry_text"] = entry_text

            # Spinbox per Yshift
            label_Yshift = tk.Label(frame, text="Y shift:")
            label_Yshift.grid(row=2, column=0, sticky=tk.W)
            spin_Yshift = tk.Spinbox(frame, from_=-600, to=600, increment=10, width=10,
                                     command=lambda idx=i: self.update_spinbox(idx, "Yshift"))
            spin_Yshift.delete(0, "end")
            spin_Yshift.insert(0, setting["Yshift"])
            spin_Yshift.bind('<Return>', lambda e, idx=i: self.update_spinbox(idx, "Yshift"))
            spin_Yshift.grid(row=2, column=1)
            setting["spin_Yshift"] = spin_Yshift

            # Spinbox per Defocus
            label_defocus = tk.Label(frame, text="Defocus:")
            label_defocus.grid(row=3, column=0, sticky=tk.W)
            spin_defocus = tk.Spinbox(frame, from_=-20, to=50, increment=10, width=10,
                                      command=lambda idx=i: self.update_spinbox(idx, "defocus"))
            spin_defocus.delete(0, "end")
            spin_defocus.insert(0, setting["defocus"])
            spin_defocus.bind('<Return>', lambda e, idx=i: self.update_spinbox(idx, "defocus"))
            spin_defocus.grid(row=3, column=1)
            setting["spin_defocus"] = spin_defocus

            # Spinbox per Xshift
            label_Xshift = tk.Label(frame, text="X shift:")
            label_Xshift.grid(row=4, column=0, sticky=tk.W)
            spin_Xshift = tk.Spinbox(frame, from_=-800, to=800, increment=10, width=10,
                                     command=lambda idx=i: self.update_spinbox(idx, "Xshift"))
            spin_Xshift.delete(0, "end")
            spin_Xshift.insert(0, setting["Xshift"])
            spin_Xshift.bind('<Return>', lambda e, idx=i: self.update_spinbox(idx, "Xshift"))
            spin_Xshift.grid(row=4, column=1)
            setting["spin_Xshift"] = spin_Xshift

            # Pulsante SHOW
            setting["var_show"] = tk.BooleanVar(value=setting["show"])
            button_show = tk.Checkbutton(
                frame,
                text="SHOW",
                variable=setting["var_show"],
                command=lambda idx=i: self.update_show(idx),
                font=("Arial", 12),  # Cambia "Arial" e "12" secondo le tue preferenze
                padx=10,  # Padding orizzontale
                pady=5    # Padding verticale
            )
            button_show.grid(row=5, column=0, columnspan=2, pady=5)
            setting["button_show"] = button_show

        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def update_text(self, idx):
        self.settings[idx]["text"] = self.settings[idx]["entry_text"].get()
        self.update_callback(self.settings)

    def update_spinbox(self, idx, param):
        self.settings[idx][param] = int(self.settings[idx][f"spin_{param}"].get())
        self.update_callback(self.settings)

    def update_show(self, idx):
        self.settings[idx]["show"] = self.settings[idx]["var_show"].get()
        self.update_callback(self.settings)

    def close_dialog(self):
        try:
            self.close_callback()  # Chiama la funzione per chiudere pygame
            if self.winfo_exists():  # Controlla se la finestra esiste ancora
                self.destroy()
        except tk.TclError:
            pass  # Se la finestra è già stata chiusa, ignora l'errore

## Real-time update of the combined hologram based on GUI settings
def update_hologram(settings):
    global phase_0

    combined_field = None

    for setting in settings:
        if setting["show"]:
            quadatic_phase = setting["defocus"] * (xx**2 + yy**2)
            linear_phase = setting["Yshift"] * yy + setting["Xshift"] * xx

            target = generate_text_image(setting["text"], image_size=1080, text_area_size=540)
            hologram_RS = RS_minimal(target, phase_0)
            hologram_RS_shifted_lensed = ((hologram_RS + linear_phase + quadatic_phase) % (2 * np.pi))

            if combined_field is None:
                combined_field = np.exp(1j * hologram_RS_shifted_lensed)
            else:
                combined_field += np.exp(1j * hologram_RS_shifted_lensed)

    if combined_field is not None:
        hologram_RS_combined = np.angle(combined_field)
        hologram_RS_toproject = (hologram_RS_combined + np.pi) / np.pi / 2 * 255
        hologram_RS_toproject = np.flipud(hologram_RS_toproject)
        hologram_RS_toproject = np.fliplr(hologram_RS_toproject)
        display_numpy_hologram(np.rot90(hologram_RS_toproject, -1), window)
    else:
        # Se nessun ologramma è attivo, pulisce lo schermo
        clear_display(window)

## Properly close pygame and exit the application
def close_pygame_and_exit():
    close_pygame()
    root.destroy()

## Clear the display if no hologram is active
def clear_display(window):
    window.fill((0, 0, 0))  # Riempie lo schermo di nero
    pygame.display.flip()
    

# ================= Initialization and Main Loop =================

# Ask user to select the display screen for pygame window
screen_index = get_screen_index()

# Initialize pygame window on the selected screen
window = init_pygame(screen_index=screen_index)

# Initial random phase for RS algorithm
phase_0 = 2 * np.pi * np.random.rand(1080, 1080) - np.pi

# Coordinate grids for phase manipulation
x = np.linspace(-1, 1, 1080)
xx, yy = np.meshgrid(x, x)

# Initial settings for each text hologram (text, position, focus, visibility)
settings = [
    {"text": "<= Duck", "Yshift": -500, "defocus": -10, "Xshift": 400, "show": False},
    {"text": "Dog =>", "Yshift": 500, "defocus": 30, "Xshift": -80, "show": False},
    {"text": "Hello!", "Yshift": -200, "defocus": 10, "Xshift": 0, "show": False},
]

# Start the Tkinter GUI and main event loop
Running = True
root = tk.Tk()
root.withdraw()
dialog = InputDialog(root, settings, update_hologram, close_pygame_and_exit)
root.mainloop()
