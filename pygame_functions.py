
# =============================================================
# pygame_functions.py
#
# Utility functions for displaying holograms and images on an SLM
# (Spatial Light Modulator) using pygame.
#
# Features:
#   - Initialize and manage fullscreen pygame windows on any monitor
#   - Display numpy arrays or BMP images as holograms
#   - Play BMP video sequences at a specified framerate
#
# Author: Marco Astarita
# Date: 30-03-2024
# =============================================================

import pygame
import numpy as np
import os
import tkinter as tk


def init_pygame(screen_index = 0):
    from screeninfo import get_monitors
    if get_monitors()[screen_index].is_primary:
        print("Warning, screen is primary")
    #Initialize
    pygame.init()
    # Get width and height of selected screen
    width, height = pygame.display.get_desktop_sizes()[screen_index]
    # Create window
    window = pygame.display.set_mode((width,height), pygame.NOFRAME, display=screen_index)
    return window

def close_pygame():
    pygame.quit()

def display_numpy_hologram(hologram, window):
    # hologram is a numpy array in 0-255
    # window is a pygame window
    slm_size = window.get_size()[1],window.get_size()[0]
    if hologram.shape[0]>slm_size[0] or hologram.shape[1]>slm_size[1]:
        print("The hologram is too big!")
    #Convert to rgb array
    array = np.stack((hologram, hologram, hologram), axis=2)
    # Converte il numpy array in una superficie Pygame
    surf = pygame.surfarray.make_surface(array)
    # Ottieni le dimensioni della superficie
    surf_rect = surf.get_rect()
    #Center the image
    surf_rect.center = window.get_rect().center
    # Disegna la superficie sulla finestra
    window.blit(surf, surf_rect)
    # Update window
    pygame.display.flip()

def display_bmp_hologram(filename, window):
    # filename is a bmp path
    # window is a pygame window
    
    #Fill w black
    # window.fill((0, 0, 0))
    
    #Load bmp hologram
    image = pygame.image.load(filename)
    #Get center coordinates
    window_width, window_height = window.get_size()
    image_width, image_height = image.get_size()
    x = (window_width - image_width) // 2
    y = (window_height - image_height) // 2
    window.blit(image, (x, y))
    # Update window
    pygame.display.flip()


def display_bmp_video(folder_path, framerate, window):
    """
    Displays a sequence of BMP frames in a loop at a specified framerate.
    Press ESC to exit the loop.

    Parameters:
    - folder_path (str): Path to the folder containing BMP frames.
    - framerate (int): Desired playback framerate.
    - window (pygame.Surface): Pygame window object where the frames will be displayed.
    """
    # Ottieni la lista di tutti i file BMP nella cartella
    bmp_files = [f for f in os.listdir(folder_path) if f.endswith('.bmp')]
    # Ordina i file BMP
    bmp_files.sort()

    # Verifica che ci siano file BMP nella cartella
    if not bmp_files:
        raise FileNotFoundError(f"No BMP files found in {folder_path}")

    # Ottieni le dimensioni della finestra
    window_width, window_height = window.get_size()

    # Creazione del clock per regolare il framerate
    clock = pygame.time.Clock()

    running = True
    while running:
        for bmp_file in bmp_files:
            # Gestione degli eventi pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Se la finestra viene chiusa
                    running = False
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Se viene premuto ESC
                    running = False
                    break

            if not running:
                break  # Esci dal ciclo se richiesto

            # Carica il frame BMP
            image = pygame.image.load(os.path.join(folder_path, bmp_file))
            # Ottieni le dimensioni dell'immagine
            image_width, image_height = image.get_size()
            # Calcola le coordinate per centrare l'immagine
            x = (window_width - image_width) // 2
            y = (window_height - image_height) // 2
            # Riempie lo sfondo di nero
            window.fill((0, 0, 0))
            # Mostra il frame corrente
            window.blit(image, (x, y))
            # Aggiorna la finestra
            pygame.display.flip()
            # Imposta il framerate
            clock.tick(framerate)

    # Pulizia e chiusura pygame
    pygame.quit()



def navigate_bmp_frames(folder_path, window):
    # Ottieni la lista di tutti i file BMP nella cartella
    bmp_files = [f for f in os.listdir(folder_path) if f.endswith('.bmp')]
    # Ordina i file BMP
    bmp_files.sort()

    # Indice corrente per il frame attualmente visualizzato
    current_frame = 0

    # Carica e visualizza il primo frame
    image = pygame.image.load(os.path.join(folder_path, bmp_files[current_frame]))
    window_width, window_height = window.get_size()
    image_width, image_height = image.get_size()
    x = (window_width - image_width) // 2
    y = (window_height - image_height) // 2
    window.blit(image, (x, y))
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    # Avanza al frame successivo
                    current_frame = (current_frame + 1) % len(bmp_files)
                elif event.key == pygame.K_LEFT:
                    # Torna al frame precedente
                    current_frame = (current_frame - 1) % len(bmp_files)
                elif event.key == pygame.K_ESCAPE:
                    # Premendo Esc chiudi il programma
                    running = False
                
                # Carica e visualizza il nuovo frame
                image = pygame.image.load(os.path.join(folder_path, bmp_files[current_frame]))
                window.blit(image, (x, y))
                pygame.display.flip()

    pygame.quit()

def get_screen_index():
    # Inizializza pygame per ottenere informazioni sugli schermi
    pygame.init()

    # Ottieni le dimensioni degli schermi
    screen_info = pygame.display.get_desktop_sizes()

    screen_dialog = tk.Tk()
    screen_dialog.title("Select Screen Index")
    label = tk.Label(screen_dialog, text="Select the screen index (0, 1, or 2):", font=("Arial", 12))
    label.pack(pady=10)
    selected_index = tk.IntVar(value=0)

    def on_ok():
        screen_dialog.destroy()

    # Mostra informazioni sugli schermi
    for i, (width, height) in enumerate(screen_info):
        rb_text = f"Screen {i}: {width}x{height}"
        rb = tk.Radiobutton(screen_dialog, text=rb_text, variable=selected_index, value=i, font=("Arial", 10))
        rb.pack(anchor="w", padx=20)

    button_ok = tk.Button(screen_dialog, text="OK", command=on_ok, font=("Arial", 10))
    button_ok.pack(pady=10)

    # Forza la finestra in primo piano
    screen_dialog.lift()
    screen_dialog.attributes("-topmost", True)
    screen_dialog.after_idle(screen_dialog.attributes, "-topmost", False)

    screen_dialog.mainloop()

    # Termina pygame dopo aver ottenuto l'indice
    pygame.quit()

    return selected_index.get()


if __name__ == "__main__":
    screen_index=1
    framerate=30
    
    #Test phase
    phase=np.random.rand(1080,1920)*2*np.pi
    phase*=255/np.pi/2
    phase=phase.astype(int)
    # phase=np.random.randint(0, 256, size=(1080, 1920));
    
    
    #Test the functions
    window = init_pygame(screen_index);
    # display_numpy_hologram(phase, window)
    # display_bmp_hologram("pentagon_phase_lines_resc_1.bmp", window)
    # display_bmp_video(r"C:\Users\astam\Desktop\OneDrive - Politecnico di Milano\Polimi\Astarita_Holography_Data\Nbody_video",framerate,  window)
    navigate_bmp_frames(r"C:\Users\astam\Desktop\Repositories\holography_astarita\RGB first trials\RGB pentagon", window)

    close_pygame()






