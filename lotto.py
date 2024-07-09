import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
import csv
import random
from collections import Counter

# Funzione per selezionare il file
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("File di testo", "*.txt")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Funzione per inserire i dati nel database
def insert_data():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showwarning("Errore", "Seleziona un file di origine!")
        return
    
    try:
        conn = sqlite3.connect("lotto.db")
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS storico (
                          data TEXT,
                          città TEXT,
                          num1 INTEGER,
                          num2 INTEGER,
                          num3 INTEGER,
                          num4 INTEGER,
                          num5 INTEGER)''')
        
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                cursor.execute('INSERT INTO storico VALUES (?, ?, ?, ?, ?, ?, ?)', row)
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Successo", "Dati inseriti con successo nel database!")
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore: {e}")

# Funzione per visualizzare i dati dal database
def view_data():
    try:
        conn = sqlite3.connect("lotto.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM storico")
        rows = cursor.fetchall()
        
        conn.close()
        
        # Creazione della finestra per visualizzare i dati
        view_window = tk.Toplevel(root)
        view_window.title("Dati Inseriti")
        
        frame = tk.Frame(view_window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(frame, columns=('Data', 'Città', 'Num1', 'Num2', 'Num3', 'Num4', 'Num5'), show='headings')
        tree.heading('Data', text='Data')
        tree.heading('Città', text='Città')
        tree.heading('Num1', text='Num1')
        tree.heading('Num2', text='Num2')
        tree.heading('Num3', text='Num3')
        tree.heading('Num4', text='Num4')
        tree.heading('Num5', text='Num5')
        
        for row in rows:
            tree.insert('', tk.END, values=row)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Aggiungi la barra di scorrimento verticale
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Aggiungi la barra di scorrimento orizzontale
        h_scrollbar = ttk.Scrollbar(view_window, orient="horizontal", command=tree.xview)
        tree.configure(xscroll=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore: {e}")

# Funzione per calcolare la frequenza dei numeri estratti
def get_frequent_numbers(rows):
    all_numbers = []
    for row in rows:
        all_numbers.extend(row)
    frequency = Counter(all_numbers)
    return frequency.most_common()

# Funzione per calcolare i numeri ritardatari
def get_late_numbers(rows):
    all_numbers = list(range(1, 91))
    extracted_numbers = set(num for row in rows for num in row)
    late_numbers = [num for num in all_numbers if num not in extracted_numbers]
    return late_numbers

# Funzione per generare una quaterna secca e due ambi basati sui numeri frequenti e ritardatari
def generate_based_on_analysis(most_common_numbers, late_numbers):
    # Unisci i numeri più frequenti e ritardatari
    combined_numbers = [num for num, _ in most_common_numbers] + late_numbers
    # Assicurati che non ci siano duplicati
    combined_numbers = list(dict.fromkeys(combined_numbers))
    
    if len(combined_numbers) < 8:
        messagebox.showwarning("Errore", "Non ci sono abbastanza dati per generare i numeri.")
        return [], []
    
    # Seleziona la quaterna secca dai primi 4 numeri
    quaterna_secca = combined_numbers[:4]
    # Mescola i restanti numeri per creare gli ambi
    remaining_numbers = combined_numbers[4:]
    random.shuffle(remaining_numbers)
    ambi = [tuple(sorted(remaining_numbers[:2])), tuple(sorted(remaining_numbers[2:4]))]
    return quaterna_secca, ambi

# Funzione per analizzare i dati e trovare la quaterna secca e due ambi
def analyze_data():
    try:
        start_date = start_date_entry.get().replace("-", "/")
        end_date = end_date_entry.get().replace("-", "/")
        selected_ruota = ruota_var.get()
        
        if not start_date or not end_date or not selected_ruota:
            messagebox.showwarning("Errore", "Inserisci tutte le informazioni richieste!")
            return
        
        conn = sqlite3.connect("lotto.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT num1, num2, num3, num4, num5 FROM storico WHERE città = ? AND data BETWEEN ? AND ?", 
                       (selected_ruota, start_date, end_date))
        rows = cursor.fetchall()
        
        conn.close()
        
        if not rows:
            messagebox.showinfo("Risultato", "Nessun dato trovato per i criteri selezionati.")
            return
        
        # Calcolo dei numeri più frequenti
        most_common_numbers = get_frequent_numbers(rows)
        
        # Calcolo dei numeri ritardatari
        late_numbers = get_late_numbers(rows)
        
        # Generazione dei numeri basati sui più frequenti e ritardatari
        quaterna_secca, ambi = generate_based_on_analysis(most_common_numbers, late_numbers)
        
        if not quaterna_secca or not ambi:
            return
        
        quaterna_message = f"La quaterna secca suggerita per la ruota {selected_ruota} è: {', '.join(map(str, quaterna_secca))}"
        ambi_message = f"I due ambi suggeriti sono: {ambi[0]} e {ambi[1]}"
        
        messagebox.showinfo("Risultato Analisi", f"{quaterna_message}\n\n{ambi_message}")
        
        # Visualizza la frequenza dei numeri
        show_frequent_numbers(most_common_numbers)
        
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore: {e}")

# Funzione per mostrare la frequenza dei numeri
def show_frequent_numbers(most_common_numbers):
    freq_window = tk.Toplevel(root)
    freq_window.title("Frequenza Numeri")
    
    frame = tk.Frame(freq_window)
    frame.pack(fill=tk.BOTH, expand=True)
    
    tree = ttk.Treeview(frame, columns=('Numero', 'Frequenza'), show='headings')
    tree.heading('Numero', text='Numero')
    tree.heading('Frequenza', text='Frequenza')
    
    for num, freq in most_common_numbers:
        tree.insert('', tk.END, values=(num, freq))
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Aggiungi la barra di scorrimento verticale
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Aggiungi la barra di scorrimento orizzontale
    h_scrollbar = ttk.Scrollbar(freq_window, orient="horizontal", command=tree.xview)
    tree.configure(xscroll=h_scrollbar.set)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Creazione dell'interfaccia grafica
root = tk.Tk()
root.title("Inserimento Dati Lotto")

tk.Label(root, text="Seleziona il file sorgente:").grid(row=0, column=0, padx=10, pady=10)

file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Button(root, text="Sfoglia", command=select_file).grid(row=0, column=2, padx=10, pady=10)
tk.Button(root, text="Inserisci Dati", command=insert_data).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Visualizza Dati", command=view_data).grid(row=1, column=2, padx=10, pady=10)

# Sezione per l'analisi dei dati
tk.Label(root, text="Data Inizio (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10)
start_date_entry = tk.Entry(root)
start_date_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Data Fine (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10)
end_date_entry = tk.Entry(root)
end_date_entry.grid(row=3, column=1, padx=10, pady=10)

tk.Label(root, text="Seleziona Ruota:").grid(row=4, column=0, padx=10, pady=10)
ruota_var = tk.StringVar()
ruota_menu = ttk.Combobox(root, textvariable=ruota_var)
ruota_menu['values'] = ['BA', 'FI', 'MI', 'NA', 'PA', 'RM', 'TO', 'VE']
ruota_menu.grid(row=4, column=1, padx=10, pady=10)

tk.Button(root, text="Analizza Dati", command=analyze_data).grid(row=5, column=1, padx=10, pady=10)

root.mainloop()
