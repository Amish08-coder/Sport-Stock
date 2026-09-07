import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox
import customtkinter as ctk
import json
import os


file_name = "sportstock_data.json"

# ------------------------------ Theme
SIDEBAR_BG = "#0f172a"
SIDEBAR_HOVER = "#1e293b"
SIDEBAR_TEXT = "#cbd5e1"

ACCENT = "#6366f1"
ACCENT_DARK = "#4f46e5"

CONTENT_BG = "#f1f5f9"
CARD_BG = "#ffffff"

BORDER = "#e2e8f0"

TEXT_DARK = "#0f172a"
TEXT_MUTED = "#64748b"

GREEN = "#059669"
GREEN_BG = "#d1fae5"
RED = "#dc2626"
RED_BG = "#fee2e2"
AMBER = "#d97706"
AMBER_BG = "#fef3c7"

FONT = "Segoe UI"
LOW_STOCK_LIMIT = 2




# The Default Data that my program is going to use
def default_data():
    return {
        "stock": {
            'Football': 10,
            'Cricket Bat': 10,
            'Leather Ball': 30,
            'Cottonian': 20,
            'House Flags': 8
        },
        "issued_items": [], # Till now there is no Item issued yet
        "next_issue_id": 1
    }

# To Save the Data. It converts the data of the file into JSON format and then saves it in the database
def save_data(data):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

# To load the data form the JSON file
def load_data():
    if not os.path.exists(file_name):
        data = default_data()
        save_data(data)
        return data

    with  open(file_name, 'r') as file:
        return json.load(file)

data = load_data()
print(data)

#The GUI part starts -->

window = tk.Tk()
window.title("Sports Stock ")
window.geometry('1000x650')
window.configure(bg='#f1f5f9')

sidebar = tk.Frame(master = window,
                    bg = "#0f172a",
                    width = 250)
sidebar.pack(side = 'left', fill = 'y')

sidebar.pack_propagate(False)

content = tk.Frame(master = window,
                   bg="#f1f5f9")

content.pack(side = "right", fill = 'both', expand = True)

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def show_dashboard():
    #This will clear the content from the previous page before starting a new one or else it will overlap
    clear_content()

    title = tk.Label(
        content,
        text="Dashboard",
        bg="#f1f5f9",
        fg="#0f172a",
        font=("Segoe UI", 22, "bold")
    )
    title.pack(anchor="w", padx=30, pady=30)


def show_stock():
    clear_content()

    title = tk.Label(
        content,
        text="Available Stock",
        bg="#f1f5f9",
        fg="#0f172a",
        font=("Segoe UI", 22, "bold")
    )
    title.pack(anchor="w", padx=30, pady=30)


tk.Button(master = sidebar,
          text = 'DashBoard',
          command = show_dashboard,
          bg = "#0f172a",
          fg="white",
          bd = 0,
          anchor = 'w',
          padx = 25,
          pady = 12).pack(fill = 'x')

tk.Button(master = sidebar,
          text="View Stock",
          command=show_stock,
          bg="#0f172a",
          fg="white",
          bd=0,
          anchor="w",
          padx=25,
          pady=12).pack(fill="x")

def show_add_button():
    clear_content()

    tk.Label(master = content,
             text = 'Add New Item',
             bg = "#f1f5f9",
             fg = "#0f172a",
             font = ("Segoe UI", 22, "bold")
             ).pack(anchor = 'w', padx = 30, pady = 30)

    tk.Button(master = content,
              text = 'Add Item',
              command = show_add_button,
              bg = "#0f172a",
              fg = "white",
              bd = 0,
              anchor = 'w',
              padx = 25,
              pady = 12).pack(fill = 'x')

def create_card(parent,title,value,color):
    card = tk.Frame(master = parent,
                    bg = 'white',
                    highlightbackground = '#e2e8f0',
                    highlightthickness = 1
                    )
    tk.Frame(master = card, bg = color, height = 4 ).pack(fill = 'x')

    tk.Label(master = card,
             text = value,
             bg = 'white',
             fg = '#64748b',
             font = ('Segoe UI', 26, 'bold')
             ).pack(pady = (15,0))
    
    tk.Label(master = card,
             text=title,
             bg="white",
             fg="#64748b",
             font=("Segoe UI", 10)
    ).pack(pady=(0, 15))

    return card

stock = data['stock']
pending = [
    record for record in data['issued_items']
    if record['status'] == 'issued'
          ]

cards_frame = tk.Frame(content, bg = "#f1f5f9")
cards_frame.pack(pady = 30, padx = 30, fill = 'x')

card1 = create_card(
    parent=cards_frame,
    title="Total Units In Stock",
    value=sum(stock.values()),
    color="#6366f1"
)

card1.pack(padx = 5, side = 'left', expand = True, fill = 'x')

total_units = sum(data['stock'].values())
equipment_types = len(data['stock'])
pending_returns = len(pending)
low_stock_count = sum(
    1 for quantity in data['stock'].values()
    if quantity <= 2
)


tree = ttk.Treeview(master = content,
                    columns = ('equipment', 'quantity', 'status'),
                    show = 'headings')

tree.heading('equipment', text = 'Equipment')
tree.heading('quantity', text = 'Quantity')
tree.heading('status', text = 'Status')

tree.column('equipment', width = 250)
tree.column('quantity', width = 100)
tree.column('status', width = 100)
tree.pack(pady = 20, padx = 30 , fill = 'x', expand = True)

for item,quantity in data['stock'].items():
    if quantity <= 2:
        status = 'LOW STOCK!'
    else:
        status = 'Available'
    tree.insert('', 'end', values = (item, quantity, status))

tree.tag_configure(
    "low",
    background="#fee2e2",
    foreground="#dc2626")

for item, quantity in data["stock"].items():
    status = "LOW STOCK!" if quantity <= 2 else "Available"
    tag = "low" if quantity <= 2 else ""

    tree.insert(
        "",
        "end",
        values=(item, quantity, status),
        tags=(tag,)
    )

name_entry = tk.Entry(content)
name_entry.pack(pady = 5)

quantity_entry = tk.Entry(content)
quantity_entry.pack(pady = 5)

def add_equipment():
    name = name_entry.get().strip()
    text = quantity_entry.get().strip()

    if not name:
        messagebox.showerror("Missing Name", "Equipment name cannot be empty.")
        return
    try:
        quantity = int(text)

        if quantity <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Quantity",
            "Please enter a whole number greater than 0.")
        return
    existing_name = None

    for items in data['stock']:
        if item.casefold() == name.casefold():
            existing_name = items
            break

    if existing_name:
        data['stock'][existing_name] += quantity
    else:
        data['stock'][name] = quantity

    save_data(data)

    messagebox.showinfo("Success",
                        f"{quantity} units added successfully.")


def issue_equipment(student_name, class_house, item_name, quantity):
    available = data['stock'].get(item_name, quantity)

    if quantity > available:
        messagebox.showerror(
            "Insufficient Stock",
            f"Only {available} units of {item_name} are available.")
        return
    record = {
        'issue_id' : data['next_issue_id'],
        'student_name' : student_name,
        'class_house' : class_house,
        'item_name' : item_name,
        'quantity' : quantity,
        'issue_date' : str(date.today()),
        'status' : 'issued',
        'return_date' : ''
    }

    data['stock'][item_name] -= quantity
    data['issued_items'].append(record)
    data['next_issue_id'] += 1

    save_data(data)

    messagebox.showinfo(

        "Success done"
        f"Equipment issued successfully!"
    )

def return_equipment(issue_id):
    for record in data['issued_items']:
        if (record['issue_id'] == issue_id and record['status'] == 'issued'):
            record['status'] = 'Returned'
            record['return_date'] = str(date.today())

            item_name = record['item_name']
            quantity = record['quantity']

            data['stock'].setdefault(item_name, 0)
            data['stock'][item_name] += quantity

            save_data(data)

            messagebox.showinfo(
                "Thanks for Returning",
                f"{quantity} units of {item_name} returned."
            )
            return

    messagebox.showerror(
        "error",
        "no such issue id found."
    )

class SportStockApp:
    def __init__(self, root):
        self.root = root
        self.data = load_data()
        self.active_view = None

        self.setup_style()
        self.build_layout()
        self.switch_view("dashboard")

def show_dashboard(self):
    pass


def show_stock(self):
    pass


def show_add_form(self):
    pass


def show_issue_form(self):
    pass


def show_returns(self):
    pass


def show_history(self):
    pass


window.mainloop()

