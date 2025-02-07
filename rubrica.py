import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyttsx3
import json
import threading
import os
import webbrowser
import urllib.parse

# Imposta il percorso per salvare i contatti nella cartella dell'utente
if os.name == 'nt':  # Windows
    DATA_FOLDER = os.path.join(os.getenv('APPDATA'), 'Rubrica')
else:  # macOS/Linux
    DATA_FOLDER = os.path.join(os.path.expanduser("~"), '.rubrica')

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

CONTACTS_FILE = os.path.join(DATA_FOLDER, "contacts.json")

def load_contacts():
    try:
        with open(CONTACTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_contacts(contacts):
    with open(CONTACTS_FILE, "w") as file:
        json.dump(contacts, file, indent=4)

def convert_contact(data):
    """
    Se il contatto non è già un dizionario, lo converte in un dizionario
    usando la stringa come numero di telefono principale.
    """
    if isinstance(data, dict):
        return data
    else:
        return {"tel": data, "mobile": "", "email": ""}

def import_contacts():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        try:
            with open(file_path, "r") as file:
                imported_contacts = json.load(file)
                contacts.update(imported_contacts)
                save_contacts(contacts)
                update_contact_list()
                messagebox.showinfo("Successo", "Rubrica importata con successo!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'importazione: {e}")

def export_contacts():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        try:
            with open(file_path, "w") as file:
                json.dump(contacts, file, indent=4)
                messagebox.showinfo("Successo", "Rubrica esportata con successo!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione: {e}")

def add_contact():
    name = name_entry.get().strip()
    tel = tel_entry.get().strip()
    mobile = mobile_entry.get().strip()
    email = email_entry.get().strip()
    
    if not name or (not tel and not mobile and not email):
        messagebox.showwarning("Errore", "Inserisci almeno il nome e un contatto (telefono, cellulare o email)!")
        return
    
    if name in contacts:
        messagebox.showerror("Errore", "Un contatto con questo nome esiste già!")
        return
    
    contacts[name] = {"tel": tel, "mobile": mobile, "email": email}
    save_contacts(contacts)
    update_contact_list()
    name_entry.delete(0, tk.END)
    tel_entry.delete(0, tk.END)
    mobile_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

def find_contact(event=None):
    query = search_entry.get().strip().lower()
    if not query:
        messagebox.showwarning("Attenzione", "Inserisci un termine di ricerca!")
        return
    for name, data in contacts.items():
        if query in name.lower():
            data = convert_contact(data)
            threading.Thread(target=speak_number, args=(name, data), daemon=True).start()
            details = (f"Nome: {name}\n"
                       f"Telefono: {data.get('tel', '')}\n"
                       f"Cellulare: {data.get('mobile', '')}\n"
                       f"Email: {data.get('email', '')}")
            messagebox.showinfo("Risultato", details)
            return
    messagebox.showerror("Errore", "Contatto non trovato!")

def delete_contact():
    selected = contact_list.curselection()
    if selected:
        contact_text = contact_list.get(selected[0])
        # Usa " | " per separare il nome dagli altri dati
        name = contact_text.split(" | ", 1)[0].strip()
        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare {name}?"):
            if name in contacts:
                del contacts[name]
                save_contacts(contacts)
                update_contact_list()
            else:
                messagebox.showerror("Errore", "Contatto non trovato!")
    else:
        messagebox.showwarning("Errore", "Seleziona un contatto da eliminare!")

def modify_contact():
    selected = contact_list.curselection()
    if not selected:
        messagebox.showwarning("Errore", "Seleziona un contatto da modificare!")
        return

    contact_text = contact_list.get(selected[0])
    # Usa " | " come delimitatore per estrarre correttamente il nome
    old_name = contact_text.split(" | ", 1)[0].strip()
    if old_name not in contacts:
        messagebox.showerror("Errore", "Contatto non trovato!")
        return
    data = convert_contact(contacts[old_name])
    
    # Finestra di modifica
    mod_window = tk.Toplevel(root)
    mod_window.title("Modifica Contatto")
    mod_window.geometry("350x220")
    mod_window.resizable(False, False)
    
    ttk.Label(mod_window, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky="W")
    new_name_entry = ttk.Entry(mod_window, width=30)
    new_name_entry.grid(row=0, column=1, padx=10, pady=5)
    new_name_entry.insert(0, old_name)
    
    ttk.Label(mod_window, text="Telefono:").grid(row=1, column=0, padx=10, pady=5, sticky="W")
    new_tel_entry = ttk.Entry(mod_window, width=30)
    new_tel_entry.grid(row=1, column=1, padx=10, pady=5)
    new_tel_entry.insert(0, data.get("tel", ""))
    
    ttk.Label(mod_window, text="Cellulare:").grid(row=2, column=0, padx=10, pady=5, sticky="W")
    new_mobile_entry = ttk.Entry(mod_window, width=30)
    new_mobile_entry.grid(row=2, column=1, padx=10, pady=5)
    new_mobile_entry.insert(0, data.get("mobile", ""))
    
    ttk.Label(mod_window, text="Email:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
    new_email_entry = ttk.Entry(mod_window, width=30)
    new_email_entry.grid(row=3, column=1, padx=10, pady=5)
    new_email_entry.insert(0, data.get("email", ""))
    
    def save_modification():
        new_name = new_name_entry.get().strip()
        new_tel = new_tel_entry.get().strip()
        new_mobile = new_mobile_entry.get().strip()
        new_email = new_email_entry.get().strip()
        
        if not new_name or (not new_tel and not new_mobile and not new_email):
            messagebox.showwarning("Errore", "Inserisci almeno il nome e un contatto (telefono, cellulare o email)!")
            return
        
        if new_name != old_name and new_name in contacts:
            messagebox.showerror("Errore", "Un contatto con questo nome esiste già!")
            return
        
        if new_name != old_name:
            del contacts[old_name]
        contacts[new_name] = {"tel": new_tel, "mobile": new_mobile, "email": new_email}
        save_contacts(contacts)
        update_contact_list()
        mod_window.destroy()
    
    save_button = ttk.Button(mod_window, text="Salva", command=save_modification)
    save_button.grid(row=4, column=0, columnspan=2, pady=10)

def send_contact_email():
    selected = contact_list.curselection()
    if not selected:
        messagebox.showwarning("Errore", "Seleziona un contatto da inviare via email!")
        return
    contact_text = contact_list.get(selected[0])
    # Usa " | " per estrarre il nome correttamente
    name = contact_text.split(" | ", 1)[0].strip()
    if name in contacts:
        data = convert_contact(contacts[name])
        tel = data.get("tel", "")
        mobile = data.get("mobile", "")
        email = data.get("email", "")
        subject = f"Contatto: {name}"
        body = f"Nome: {name}\nTelefono: {tel}\nCellulare: {mobile}\nEmail: {email}"
        subject_encoded = urllib.parse.quote(subject)
        body_encoded = urllib.parse.quote(body)
        if email:
            mailto_link = f"mailto:{email}?subject={subject_encoded}&body={body_encoded}"
        else:
            mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"
        webbrowser.open(mailto_link)
    else:
        messagebox.showerror("Errore", "Contatto non trovato!")

def speak_number(name, data):
    data = convert_contact(data)
    tel = data.get("tel", "")
    mobile = data.get("mobile", "")
    message = f"Il contatto {name} ha "
    if tel and mobile:
        message += f"telefono {tel} e cellulare {mobile}."
    elif tel:
        message += f"telefono {tel}."
    elif mobile:
        message += f"cellulare {mobile}."
    else:
        message += "nessun numero di telefono."
    
    if os.name == 'posix':  # macOS/Linux
        os.system(f'say "{message}"')
    else:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "italian" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(message)
        engine.runAndWait()

def update_contact_list():
    contact_list.delete(0, tk.END)
    for name, data in sorted(contacts.items()):
        data = convert_contact(data)
        summary = name
        if data.get("tel"):
            summary += f" | Tel: {data.get('tel')}"
        if data.get("mobile"):
            summary += f" | Cell: {data.get('mobile')}"
        if data.get("email"):
            summary += f" | Email: {data.get('email')}"
        contact_list.insert(tk.END, summary)

def toggle_contact_list():
    global list_visible
    if list_visible:
        list_frame.grid_remove()
        toggle_list_button.config(text="Mostra Lista")
        list_visible = False
    else:
        list_frame.grid(row=2, column=0, sticky="NSEW", padx=5, pady=5)
        toggle_list_button.config(text="Nascondi Lista")
        list_visible = True

# Funzione per disporre automaticamente i pulsanti nel frame delle azioni
def arrange_action_buttons(event):
    frame_width = event.width
    min_button_width = 120  # Larghezza minima per ogni pulsante (inclusi margini)
    columns = max(1, frame_width // (min_button_width + 10))
    for i, btn in enumerate(action_buttons):
        btn.grid_forget()
        r = i // columns
        c = i % columns
        btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
    for col in range(columns):
        action_frame.columnconfigure(col, weight=1)

# Carica i contatti salvati
contacts = load_contacts()

# Crea la finestra principale
root = tk.Tk()
root.title("Rubrica")
root.geometry("600x650")
root.resizable(False, False)

# Utilizza ttk per una grafica più moderna
style = ttk.Style(root)
style.theme_use('clam')

# Menù principale
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Importa Rubrica", command=import_contacts)
file_menu.add_command(label="Esporta Rubrica", command=export_contacts)
file_menu.add_separator()
file_menu.add_command(label="Esci", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

# Frame principale
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(fill=tk.BOTH, expand=True)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=0)  # Impedisce alla lista di espandersi troppo
main_frame.rowconfigure(3, minsize=50)  # Altezza minima per il frame dei pulsanti

# === Frame per l'inserimento dei contatti ===
entry_frame = ttk.LabelFrame(main_frame, text="Aggiungi Contatto", padding="10 10 10 10")
entry_frame.grid(row=0, column=0, sticky="EW", padx=5, pady=5)

ttk.Label(entry_frame, text="Nome:").grid(row=0, column=0, sticky="W", padx=5, pady=5)
name_entry = ttk.Entry(entry_frame, width=40)
name_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(entry_frame, text="Telefono:").grid(row=1, column=0, sticky="W", padx=5, pady=5)
tel_entry = ttk.Entry(entry_frame, width=40)
tel_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(entry_frame, text="Cellulare:").grid(row=2, column=0, sticky="W", padx=5, pady=5)
mobile_entry = ttk.Entry(entry_frame, width=40)
mobile_entry.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(entry_frame, text="Email:").grid(row=3, column=0, sticky="W", padx=5, pady=5)
email_entry = ttk.Entry(entry_frame, width=40)
email_entry.grid(row=3, column=1, padx=5, pady=5)

add_button = ttk.Button(entry_frame, text="Aggiungi", command=add_contact)
add_button.grid(row=4, column=0, columnspan=2, pady=10)

# === Frame per la ricerca dei contatti ===
search_frame = ttk.LabelFrame(main_frame, text="Cerca Contatto", padding="10 10 10 10")
search_frame.grid(row=1, column=0, sticky="EW", padx=5, pady=5)
search_frame.columnconfigure(0, weight=1)

search_entry = ttk.Entry(search_frame, width=40)
search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="EW")
search_entry.bind("<Return>", find_contact)
search_button = ttk.Button(search_frame, text="Trova Contatto", command=find_contact)
search_button.grid(row=0, column=1, padx=5, pady=5)

# === Frame per la lista dei contatti ===
list_frame = ttk.LabelFrame(main_frame, text="Lista Contatti", padding="10 10 10 10")
list_frame.grid(row=2, column=0, sticky="NSEW", padx=5, pady=5)
list_frame.columnconfigure(0, weight=1)
list_frame.rowconfigure(0, weight=1)
list_frame.config(height=200)
list_frame.grid_propagate(False)

contact_list = tk.Listbox(list_frame, height=10)
contact_list.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)
scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=contact_list.yview)
scrollbar.grid(row=0, column=1, sticky="NS", padx=0, pady=5)
contact_list.config(yscrollcommand=scrollbar.set)

# === Frame per le azioni aggiuntive ===
action_frame = ttk.Frame(main_frame, padding="10 10 10 10")
action_frame.grid(row=3, column=0, sticky="EW", padx=5, pady=5)

# Creazione dei pulsanti
delete_button = ttk.Button(action_frame, text="Elimina Contatto", command=delete_contact)
modify_button = ttk.Button(action_frame, text="Modifica Contatto", command=modify_contact)
try:
    mail_icon = tk.PhotoImage(file="mail_icon.png")
except Exception:
    mail_icon = None
if mail_icon:
    send_email_button = ttk.Button(action_frame, image=mail_icon, text="Invia Email", compound="left", command=send_contact_email)
else:
    send_email_button = ttk.Button(action_frame, text="Invia Email", command=send_contact_email)
import_button = ttk.Button(action_frame, text="Importa Rubrica", command=import_contacts)
export_button = ttk.Button(action_frame, text="Esporta Rubrica", command=export_contacts)
toggle_list_button = ttk.Button(action_frame, text="Nascondi Lista", command=toggle_contact_list)

# Raggruppiamo i pulsanti in una lista per la disposizione automatica
action_buttons = [
    delete_button,
    modify_button,
    send_email_button,
    import_button,
    export_button,
    toggle_list_button
]

# Associa la funzione di disposizione al frame delle azioni
action_frame.bind("<Configure>", arrange_action_buttons)
action_frame.update_idletasks()
dummy_event = type("Event", (), {"width": action_frame.winfo_width()})()
arrange_action_buttons(dummy_event)

# Imposta di default la lista dei contatti come nascosta
list_visible = False
list_frame.grid_remove()
toggle_list_button.config(text="Mostra Lista")

update_contact_list()
root.mainloop()
