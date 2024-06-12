import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from prophet import Prophet
import pandas as pd

# Funzione per visualizzare i dati in una nuova finestra
def display_data(data, title):
    window = tk.Toplevel()
    window.title(title)
    text = tk.Text(window, wrap='none')
    text.insert(tk.END, data)
    text.pack(expand=True, fill='both')

# Funzione per recuperare e visualizzare i dati storici di mercato
def show_hist_data():
    ticker = ticker_entry.get()
    start_date = start_entry.get()
    end_date = end_entry.get()
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        display_data(hist.to_string(), "Dati Storici di Mercato")
        plot_data(hist, ticker)
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# Funzione per recuperare e visualizzare i bilanci
def show_financial_data(data_type):
    ticker = ticker_entry.get()
    try:
        stock = yf.Ticker(ticker)
        if data_type == "income_stmt":
            data = stock.income_stmt
        elif data_type == "balance_sheet":
            data = stock.balance_sheet
        elif data_type == "cashflow":
            data = stock.cashflow
        display_data(data.to_string(), data_type.replace("_", " ").title())
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# Funzione per tracciare i dati storici
def plot_data(data, ticker):
    fig, ax = plt.subplots()
    data['Close'].plot(ax=ax, title=f'Prezzi di Chiusura Storici di {ticker}')
    ax.set_xlabel("Data")
    ax.set_ylabel("Prezzo di Chiusura")

    window = tk.Toplevel()
    window.title(f'Grafico Dati Storici di {ticker}')
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Funzione per prevedere i prezzi delle azioni utilizzando Prophet
def forecast_data():
    ticker = ticker_entry.get()
    start_date = start_entry.get()
    end_date = end_entry.get()
    forecast_end_date = forecast_end_entry.get()
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        df = hist[['Close']].reset_index()
        df['Date'] = df['Date'].dt.tz_localize(None)  # Rimuove il fuso orario
        df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=(datetime.strptime(forecast_end_date, '%Y-%m-%d') - datetime.strptime(end_date, '%Y-%m-%d')).days)
        forecast = m.predict(future)

        fig1 = m.plot(forecast)
        fig2 = m.plot_components(forecast)

        display_forecast(fig1, ticker)
        display_forecast(fig2, ticker)
    except Exception as e:
        messagebox.showerror("Errore", str(e))

# Funzione per visualizzare i grafici delle previsioni
def display_forecast(fig, ticker):
    window = tk.Toplevel()
    window.title(f'Previsione di {ticker}')
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Finestra principale della GUI
root = tk.Tk()
root.title("Informazioni Azionarie")

# Etichette e campi di inserimento per ticker e intervallo di date
ttk.Label(root, text="Ticker:").grid(row=0, column=0, padx=5, pady=5)
ticker_entry = ttk.Entry(root)
ticker_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(root, text="Data Inizio (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
start_entry = ttk.Entry(root)
start_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(root, text="Data Fine (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
end_entry = ttk.Entry(root)
end_entry.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(root, text="Data Fine Previsione (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
forecast_end_entry = ttk.Entry(root)
forecast_end_entry.grid(row=3, column=1, padx=5, pady=5)

# Crea pulsanti per ciascuna categoria di dati
ttk.Button(root, text="Mostra Dati Storici di Mercato", command=show_hist_data).grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Mostra Bilancio", command=lambda: show_financial_data("income_stmt")).grid(row=5, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Mostra Stato Patrimoniale", command=lambda: show_financial_data("balance_sheet")).grid(row=6, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Mostra Flusso di Cassa", command=lambda: show_financial_data("cashflow")).grid(row=7, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Prevedi Prezzi delle Azioni", command=forecast_data).grid(row=8, column=0, columnspan=2, pady=5, padx=10, sticky='ew')

root.mainloop()
