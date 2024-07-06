import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd

# Function to create the Excel file and save it to the specified location
def crea_excel():
    try:
        # Get input values
        area_start = area_start_entry.get()
        area_end = area_end_entry.get()
        scaffale_start = scaffale_start_entry.get()
        scaffale_end = scaffale_end_entry.get()
        campata_start = campata_start_entry.get()
        campata_end = campata_end_entry.get()
        piano_start = piano_start_entry.get()
        piano_end = piano_end_entry.get()
        posizione_start = posizione_start_entry.get()
        posizione_end = posizione_end_entry.get()
        file_path = file_path_entry.get()

        if not file_path:
            messagebox.showerror("Errore", "Per favore, seleziona un percorso valido per il file.")
            return

        # Generate data
        data = []
        area_range = range(int(area_start), int(area_end) + 1) if area_start and area_end else [""]
        scaffale_range = range(int(scaffale_start), int(scaffale_end) + 1) if scaffale_start and scaffale_end else [""]
        campata_range = range(int(campata_start), int(campata_end) + 1) if campata_start and campata_end else [""]
        piano_range = range(int(piano_start), int(piano_end) + 1) if piano_start and piano_end else [""]
        posizione_range = range(int(posizione_start), int(posizione_end) + 1) if posizione_start and posizione_end else [""]

        for area in area_range:
            for scaffale in scaffale_range:
                for campata in campata_range:
                    for piano in piano_range:
                        for posizione in posizione_range:
                            data.append([
                                f"{area:02}" if area != "" else "",
                                f"{scaffale:02}" if scaffale != "" else "",
                                f"{campata:02}" if campata != "" else "",
                                f"{piano:02}" if piano != "" else "",
                                f"{posizione:02}" if posizione != "" else ""
                            ])

        # Create DataFrame and save to Excel
        df = pd.DataFrame(data, columns=["Area", "Scaffale", "Campata", "Piano", "Posizione"])
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Successo", "File Excel creato con successo!")

    except ValueError:
        messagebox.showerror("Errore", "Per favore, inserisci valori numerici validi.")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la creazione del file Excel: {e}")

# Function to open the file dialog and select the file path
def seleziona_percorso():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if file_path:
        file_path_entry.delete(0, tk.END)
        file_path_entry.insert(0, file_path)

# Create the main window
root = tk.Tk()
root.title("Creazione Etichette Magazzino")

# Create input fields
tk.Label(root, text="Area da").grid(row=0, column=0)
area_start_entry = tk.Entry(root)
area_start_entry.grid(row=0, column=1)

tk.Label(root, text="Area a").grid(row=0, column=2)
area_end_entry = tk.Entry(root)
area_end_entry.grid(row=0, column=3)

tk.Label(root, text="Scaffale da").grid(row=1, column=0)
scaffale_start_entry = tk.Entry(root)
scaffale_start_entry.grid(row=1, column=1)

tk.Label(root, text="Scaffale a").grid(row=1, column=2)
scaffale_end_entry = tk.Entry(root)
scaffale_end_entry.grid(row=1, column=3)

tk.Label(root, text="Campata da").grid(row=2, column=0)
campata_start_entry = tk.Entry(root)
campata_start_entry.grid(row=2, column=1)

tk.Label(root, text="Campata a").grid(row=2, column=2)
campata_end_entry = tk.Entry(root)
campata_end_entry.grid(row=2, column=3)

tk.Label(root, text="Piano da").grid(row=3, column=0)
piano_start_entry = tk.Entry(root)
piano_start_entry.grid(row=3, column=1)

tk.Label(root, text="Piano a").grid(row=3, column=2)
piano_end_entry = tk.Entry(root)
piano_end_entry.grid(row=3, column=3)

tk.Label(root, text="Posizione da").grid(row=4, column=0)
posizione_start_entry = tk.Entry(root)
posizione_start_entry.grid(row=4, column=1)

tk.Label(root, text="Posizione a").grid(row=4, column=2)
posizione_end_entry = tk.Entry(root)
posizione_end_entry.grid(row=4, column=3)

tk.Label(root, text="Percorso File").grid(row=5, column=0)
file_path_entry = tk.Entry(root)
file_path_entry.grid(row=5, column=1, columnspan=2, sticky="we")

sfoglia_button = tk.Button(root, text="Sfoglia", command=seleziona_percorso)
sfoglia_button.grid(row=5, column=3)

# Create the button to generate the Excel file
crea_button = tk.Button(root, text="Crea Excel", command=crea_excel)
crea_button.grid(row=6, column=0, columnspan=4, pady=10)

# Start the Tkinter main loop
root.mainloop()
