import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to display data in a new window
def display_data(data, title):
    window = tk.Toplevel()
    window.title(title)
    text = tk.Text(window, wrap='none')
    text.insert(tk.END, data)
    text.pack(expand=True, fill='both')

# Function to fetch and display historical market data
def show_hist_data():
    ticker = ticker_entry.get()
    start_date = start_entry.get()
    end_date = end_entry.get()
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        display_data(hist.to_string(), "Historical Market Data")
        plot_data(hist, ticker)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to fetch and display financial statements
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
        messagebox.showerror("Error", str(e))

# Function to plot historical data
def plot_data(data, ticker):
    fig, ax = plt.subplots()
    data['Close'].plot(ax=ax, title=f'{ticker} Historical Closing Prices')
    ax.set_xlabel("Date")
    ax.set_ylabel("Closing Price")

    window = tk.Toplevel()
    window.title(f'{ticker} Historical Data Plot')
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Main GUI window
root = tk.Tk()
root.title("Stock Information")

# Labels and entry widgets for ticker and date range
ttk.Label(root, text="Ticker:").grid(row=0, column=0, padx=5, pady=5)
ticker_entry = ttk.Entry(root)
ticker_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(root, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
start_entry = ttk.Entry(root)
start_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(root, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
end_entry = ttk.Entry(root)
end_entry.grid(row=2, column=1, padx=5, pady=5)

# Create buttons for each data category
ttk.Button(root, text="Show Historical Market Data", command=show_hist_data).grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Show Income Statement", command=lambda: show_financial_data("income_stmt")).grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Show Balance Sheet", command=lambda: show_financial_data("balance_sheet")).grid(row=5, column=0, columnspan=2, pady=5, padx=10, sticky='ew')
ttk.Button(root, text="Show Cash Flow Statement", command=lambda: show_financial_data("cashflow")).grid(row=6, column=0, columnspan=2, pady=5, padx=10, sticky='ew')

root.mainloop()
