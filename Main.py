import json
import os
from datetime import date

import tkinter as tk
from tkinter import ttk, messagebox


FILE_NAME = "sportstock_data.json"

SIDEBAR_BG    = "#0f172a"   # deep navy
SIDEBAR_HOVER = "#1e293b"
SIDEBAR_TEXT  = "#cbd5e1"
ACCENT        = "#6366f1"   # indigo
ACCENT_DARK   = "#4f46e5"
CONTENT_BG    = "#f1f5f9"   # soft slate
CARD_BG       = "#ffffff"
BORDER        = "#e2e8f0"
TEXT_DARK     = "#0f172a"
TEXT_MUTED    = "#64748b"
GREEN         = "#059669"
GREEN_BG      = "#d1fae5"
RED           = "#dc2626"
RED_BG        = "#fee2e2"
AMBER         = "#d97706"
AMBER_BG      = "#fef3c7"

FONT   = "Segoe UI"
LOW_STOCK_LIMIT = 2

def default_data():
    return {
        "stock": {
            "Football": 10,
            "Cricket Bat": 5,
            "Tennis-Ball": 15,
            "Basketball": 10,
            "House-Flags": 12,
            "Cottonian": 18,
        },
        'issued_items': [],
        'next_issue_id': 1,
    }

def clean_data(data):
    if not isinstance(data, dict): raise ValueError
    stock = {}
    for name, qty in dict(data.get('stock', {})).items():
        try:
            qty = int(qty)
        except(TypeError, ValueError):
            continue
        if qty >= 0:
            stock[str(name)] = qty
    record = []
    for rec in data.get('issued_items', []):
        if isinstance(rec, dict) and 'issue_id' in rec and 'item_name' in rec:
            record.append(rec)

    max_id = max((int(r.get('issue_id' , 0)) for r in record), default = 0)

    try:
        stored_next = int(data.get('next_issue_id', 1))

    except (TypeError, ValueError):
        stored_next = 1
    next_id = max(stored_next, max_id + 1, 1)

    return {
        "stock": stock,
        "issued_items": record,
        "next_issue_id": next_id,
    }

def load_data():
    if not os.path.exists(FILE_NAME):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(FILE_NAME, "r") as file:
            return clean_data(json.load(file))

    except (json.JSONDecodeError, OSError, ValueError):
        messagebox.showwarning(
            "Data File Error",
            "The data file could not be read.\n"
            "A fresh data file has been created."
        )

        data = default_data()
        save_data(data)
        return data

def save_data(data):
    temp_name = FILE_NAME + ".tmp"
    with open( temp_name, 'w') as file:
        json.dump(data, file, indent = 4)
    os.replace(temp_name, FILE_NAME)

def find_item_name(stock, item_name):

    for item in stock:
        if item.casefold() == item_name.strip().casefold():
            return item
    return None

class SportStockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SportStock Pro — Sports Equipment Manager")
        self.root.geometry("1150x700")
        self.root.minsize(980, 600)
        self.root.configure(bg=CONTENT_BG)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)

        self.data = load_data()
        self.nav_buttons = {}
        self.active_view = None

        self.setup_style()
        self.build_layout()
        self.switch_view("dashboard")

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            'Treeview',
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_DARK,
            rowheight=34,
            font=(FONT, 10),
            borderwidth=0,
        )
        style.configure(
            'Treeview.Heading',
            font=(FONT, 10, 'bold'),
            background="#e2e8f0",
            foreground=TEXT_DARK,
            padding=8,
        )
        style.map('Treeview', background=[('selected', ACCENT)],
                  foreground=[('selected', '#ffffff')])

        style.configure('TCombobox', padding=6)
        style.configure('Vertical.TScrollbar', background=BORDER)

    def build_layout(self):
        self.sidebar = tk.Frame(master=self.root, bg=SIDEBAR_BG, width=240)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        logo = tk.Label(master=self.sidebar,
                        text="SportStock Pro",
                        bg=SIDEBAR_BG,
                        fg="#ffffff",
                        font=(FONT, 16, 'bold'),
                        anchor='w',
                        pady=24,
                        padx=22)
        logo.pack(fill='x')

        tk.Label(master=self.sidebar,
                 text="Equipment Manager",
                 bg=SIDEBAR_BG,
                 fg=TEXT_MUTED,
                 font=(FONT, 9),
                 anchor='w',
                 padx=24
                 ).pack(fill='x', pady=(0, 18))

        # Automated method to create a series of navigation button without writing again and again
        nav_items = [
            ('dashboard', 'Dashboard'),
            ('stock', 'View Stock'),
            ('add', 'Add Equipment'),
            ('issue', 'Issue Equipment'),
            ('returns', 'Return Equipment'),
            ('history', 'History')
        ]
        for key, text in nav_items:
            self.make_nav_button(key, text)

        exit_btn = tk.Button(master=self.sidebar,
                             text="Exit Program!",
                             anchor='w',
                             bd=0,
                             bg=SIDEBAR_BG,
                             fg='#f87171',
                             activebackground=SIDEBAR_HOVER,
                             activeforeground='#fca5a5',
                             font=(FONT, 11),
                             padx=24,
                             pady=12,
                             cursor='hand2',
                             command=self.exit_program)
        exit_btn.pack(side='bottom', fill='x', pady=14)
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg=SIDEBAR_HOVER))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg=SIDEBAR_BG))

        main_column = tk.Frame(master=self.root, bg=CONTENT_BG)
        main_column.pack(side='right', fill='both', expand=True)

        self.status_label = tk.Label(master=main_column,
                                     text='Ready',
                                     bg='#ffffff',
                                     fg=TEXT_MUTED,
                                     font=(FONT, 9),
                                     anchor='w',
                                     pady=8,
                                     padx=16)
        self.status_label.pack(side='bottom', fill='x')

        self.content = tk.Frame(master=main_column, bg=CONTENT_BG)
        self.content.pack(fill='both', expand=True, padx=28, pady=24)

    def make_nav_button(self, key,
                        text):  # The internal name and the name displayed to the user is taken as a parameter
        btn = tk.Button(master=self.sidebar,
                        text=text,
                        anchor='w',
                        bd=0,  # border
                        bg=SIDEBAR_BG,
                        fg=SIDEBAR_TEXT,
                        activebackground=SIDEBAR_HOVER,  # The background when clicking
                        activeforeground='#ffffff',  # The text color when clicking
                        font=(FONT, 11),
                        padx=24,
                        pady=12,
                        cursor='hand2',  # It changes the mouse pointer to a hand when hovered over
                        command=lambda: self.switch_view(
                            key))  # Temprory function to switch the view upon clicking the button
        btn.pack(fill='x')
        btn.bind("<Enter>", lambda e: self.on_nav_hover(key, True))
        btn.bind("<Leave>", lambda e: self.on_nav_hover(key, False))
        self.nav_buttons[key] = btn

    def on_nav_hover(self, key, entering):
        if key == self.active_view:
            return
        self.nav_buttons[key].config(bg=SIDEBAR_HOVER if entering else SIDEBAR_BG)

    def switch_view(self, key):

        self.active_view = key  # saving the key

        for name, btn in self.nav_buttons.items():  # highlighting the active button
            if name == key:
                btn.config(bg=ACCENT, fg='#ffffff')
            else:
                btn.config(bg=SIDEBAR_BG, fg=SIDEBAR_TEXT)

        for widget in self.content.winfo_children():  # it removes the previous widgets from the frame so that they don't overlap
            widget.destroy()

        # calls the various different views
        views = {
            'dashboard': self.show_dashboard,
            'stock': self.show_stock,
            'add': self.show_add_form,
            'issue': self.show_issue_form,
            'returns': self.show_returns,
            'history': self.show_history
        }
        views[key]()  # find the function which is matching the selected key

    def set_status(self, message):
        self.status_label.config(text=message)

    def page_header(self, title, subtitle=""):
        tk.Label(master=self.content,
                 text=title,
                 bg=CONTENT_BG,
                 fg=TEXT_DARK,
                 font=(FONT, 19, 'bold'),
                 anchor='w',
                 ).pack(fill='x')
        if subtitle:
            tk.Label(master=self.content,
                     text=subtitle,
                     bg=CONTENT_BG,
                     fg=TEXT_MUTED,
                     font=(FONT, 10),
                     anchor='w'
                     ).pack(fill = 'x', pady = (2, 0))

    def card(self, parent=None):
        parent = parent or self.content
        frame = tk.Frame(master=parent,
                         bg=CARD_BG,
                         highlightbackground=BORDER,
                         highlightthickness=1)
        return frame

    def accent_button(self, parent, text, command, color=ACCENT, hover=ACCENT_DARK):
        btn = tk.Button(master=parent,
                        text=text,
                        command=command,
                        bd=0,
                        cursor='hand2',
                        bg=color,
                        fg='#ffffff',
                        activebackground=hover,
                        activeforeground='#ffffff',
                        font=(FONT, 11, 'bold'),
                        padx=22,
                        pady=9)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))  # When the mouse enters the button it changes it's color
        btn.bind("<Leave>", lambda e: btn.config(
            bg=color))  # When the mouse leaves the button it changes it's color back to normal
        return btn

    def make_tree(self, parent, columns, headings, widths):

        wrapper = tk.Frame(parent, bg=CARD_BG)
        wrapper.pack(fill='both', expand=True, padx=1,
                     pady=1)  # used the y and x axis as 1 so that the border remains a bit visible

        scrollbar = ttk.Scrollbar(master=wrapper,
                                  orient="vertical")
        scrollbar.pack(side='right', fill='y')

        tree = ttk.Treeview(master=wrapper,
                            columns=columns,
                            show='headings',
                            yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)  # it tells the scrollbar to scroll the tree when it is scrolled

        for column, heading, width in zip(columns, headings, widths):
            tree.heading(column, text=heading)
            tree.column(column, width=width, anchor='center')

        tree.pack(fill='both', expand=True)

        tree.tag_configure('odd', background='#f8fafc')
        tree.tag_configure('even', background=CARD_BG)
        tree.tag_configure('low', background=RED_BG, foreground=RED)
        tree.tag_configure('returned', background=GREEN_BG, foreground=GREEN)
        tree.tag_configure('issued', background=AMBER_BG, foreground=AMBER)
        return tree

    def form_row(self, parent, row, label_text):
        tk.Label(master=parent,
                 text=label_text,
                 bg=CARD_BG,
                 fg=TEXT_MUTED,
                 font=(FONT, 10, 'bold')).grid(row=row, column=0, sticky='w', pady=10, padx=(24, 14))

        entry = tk.Entry(master=parent,
                         font=(FONT, 11),
                         width=30,
                         relief='solid',
                         bd=1,
                         highlightthickness=1,
                         highlightcolor=ACCENT,
                         highlightbackground=BORDER)

        entry.grid(row=row, column=1, sticky='w', pady=10, ipady=5, padx=(0, 24))
        return entry

    def pending_records(self):
        return [r for r in self.data['issued_items'] if r[
            'status'] == 'Issued']  # goes through each record one by one, and when it finds any record issued then it creates a new label for the next issue id

    def show_dashboard(self):
        # it creates a label which shows the Dashboard, overview for the day and then the exact date,month, and year
        self.page_header("DashBoard", f"Overview for {date.today().strftime('%d %B %Y')}")

        stock = self.data['stock']
        pending = self.pending_records()
        low_stock = [name for name, qty in stock.items() if qty <= LOW_STOCK_LIMIT]

        stats_frame = tk.Frame(self.content, bg=CONTENT_BG)
        stats_frame.pack(fill='x', pady=(18, 6))  # 18 pixels above and 6 pixels below

        stats = [
            ("Total Units In Stock", sum(stock.values()), ACCENT),  # adds all the items in stock and shows as one unit
            ("Equipment Types", len(stock), GREEN),
            ("Pending Returns", len(pending), AMBER),
            ("Low Stock Alerts", len(low_stock), RED),
        ]
        for i, (title, value, color) in enumerate(
                stats):  # something new I learned . so basically enumerate shows both the index number of the item and it's value also
            card = self.card(stats_frame)
            card.grid(row=0,
                      column=i,
                      sticky="nsew",  # tells the card to spread in all the 4 directions
                      padx=(0 if i == 0 else 14, 0))
            stats_frame.grid_columnconfigure(i, weight=1)

            strip = tk.Frame(master=card,
                             bg=color,
                             height=4)
            strip.pack(fill='x')

            tk.Label(master=card,
                     text=str(value),
                     bg=CARD_BG,
                     fg=color,
                     font=(FONT, 26, 'bold')).pack(pady=(14, 0))
            tk.Label(
                card, text=title, bg=CARD_BG, fg=TEXT_MUTED, font=(FONT, 10),
            ).pack(pady=(0, 16))

        if low_stock:
            alert = tk.Label(
                self.content,
                text="LOW STOCK ALERT:  " + ", ".join(sorted(low_stock)),
                # sorts the item in low_stock alphabetically and then shows them with commas in between
                bg=RED_BG, fg=RED, font=(FONT, 10, "bold"),
                anchor="w", padx=16, pady=10,
            )
            alert.pack(fill="x", pady=(12, 0))

        tk.Label(
            self.content, text="Recent Activity", bg=CONTENT_BG, fg=TEXT_DARK, font=(FONT, 13, "bold"), anchor="w",
        ).pack(fill="x", pady=(20, 8))

        table_card = self.card()
        table_card.pack(fill="both", expand=True)

        columns = ("id", "student", "item", "qty", "date", "status")  # provides with the value
        headings = ("ID", "Student", "Equipment", "Qty", "Issue Date", "Status")  # provides with the text
        widths = (60, 190, 190, 70, 120, 110)
        tree = self.make_tree(table_card, columns, headings, widths)

        recent = list(reversed(self.data["issued_items"]))[:8]
        if not recent:
            tree.insert("", "end", values=("—", "No activity yet", "", "", "", ""))
        for record in recent:
            tag = "returned" if record["status"] == "Returned" else "issued"
            tree.insert("", "end", tags=(tag,), values=(
                record["issue_id"],
                record["student_name"],
                record["item_name"],
                record["quantity"],
                record["issue_date"],
                record["status"],
            ))

        self.set_status("Viewing dashboard.")

    def show_stock(self):
        self.page_header("Available Stock",
                         f"Items with quantity {LOW_STOCK_LIMIT} or below are highlighted as low stock.")

        toolbar = tk.Frame(self.content, bg=CARD_BG)
        toolbar.pack(fill='x', pady=(16, 10))

        tk.Label(
            master=toolbar,
            text="Search:",
            bg=CONTENT_BG,
            fg=TEXT_MUTED,
            font=(FONT, 10, 'bold')
        ).pack(side='left')

        self.search_var = tk.StringVar()

        search_entry = tk.Entry(master=toolbar,
                                textvariable=self.search_var,
                                font=(FONT, 11),
                                width=30,
                                relief='solid',
                                bd=1,
                                highlightthickness=1,
                                highlightcolor=ACCENT,
                                highlightbackground=BORDER)
        search_entry.pack(side='left', padx=8, ipady=5)
        search_entry.insert(0, '')
        self.search_var.trace_add("write", lambda *args: self.fill_stock_tree())

        remove_btn = self.accent_button(toolbar, "Remove Selected", self.remove_selected_stock, color=RED,
                                        hover='#b91c1c')
        remove_btn.pack(side='right')

        table_card = self.card()
        table_card.pack(fill='both', expand=True)

        columns = ("equipment", "quantity", "status")
        headings = ("Equipment", "Available Quantity", "Stock Status")
        widths = (340, 190, 200)
        self.stock_tree = self.make_tree(table_card, columns, headings, widths)

        self.stock_summary = tk.Label(
            self.content, bg=CONTENT_BG, fg=TEXT_DARK, font=(FONT, 11, "bold"),
            anchor="w",
        )
        self.stock_summary.pack(fill="x", pady=(12, 0))

        self.fill_stock_tree()
        self.set_status("Viewing available stock. Type in the search box to filter.")

    def fill_stock_tree(self):
        tree = self.stock_tree
        for row in tree.get_children():
            tree.delete(row)

        query = self.search_var.get().strip().casefold()
        shown = 0
        for i, (items, quantity) in enumerate(sorted(self.data['stock'].items())):
            if query and query not in items.casefold():
                continue
            shown += 1
            if quantity <= LOW_STOCK_LIMIT:
                tag, status = "low", "LOW STOCK!"
            else:
                tag, status = ("odd" if i % 2 else "even"), "Available"
            tree.insert("", "end", tags=(tag,), values=(items, quantity, status))

        if shown == 0:
            tree.insert("", "end", values=("No matching equipment found", "", ""))

        total = sum(self.data["stock"].values())
        self.stock_summary.config(
            text=f"Showing {shown} of {len(self.data['stock'])} equipment types   |   "
                 f"{total} total units in stock"
        )

    def remove_selected_stock(self):

        selected = self.stock_tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection", "Please select an equipment row first.")
            return

        item = self.stock_tree.item(selected[0], "values")[0]
        if item not in self.data["stock"]:
            return

        still_out = [r for r in self.pending_records() if r["item_name"] == item]
        warning = ""
        if still_out:
            warning = (f"\n\nNote: {len(still_out)} issue record(s) for this item "
                       "are still pending. Returns will still be accepted.")

        if messagebox.askyesno(
                "Remove Equipment",
                f"Remove '{item}' and its {self.data['stock'][item]} unit(s) "
                f"from stock?{warning}",
        ):
            del self.data["stock"][item]
            save_data(self.data)
            self.fill_stock_tree()
            self.set_status(f"'{item}' removed from stock.")

    def show_add_form(self):
        self.page_header("Add Equipment",
                         "Add stock to an existing item or create a new one. ")

        card = self.card()
        card.pack(fill='x', pady=(20, 0))

        inner = tk.Frame(master=card, bg=CARD_BG)
        inner.pack(padx=10, pady=18, anchor = 'w')

        name_entry = self.form_row(inner, 0, "Equipment Name")
        qty_entry = self.form_row(inner, 1, "Quantity to Add")

        def add_item(event=None):

            item_name = name_entry.get().strip()
            quantity_text = qty_entry.get().strip()

            if not item_name:
                messagebox.showerror("Missing Name", "Equipment name cannot be empty.")
                return
            try:
                quantity = int(quantity_text)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Quantity",
                    "Please enter a whole number greater than 0.")
                return

            existing = find_item_name(self.data["stock"], item_name)

            if existing:
                self.data["stock"][existing] += quantity
                message = (f"{quantity} unit(s) added to '{existing}'.\n"
                           f"New quantity: {self.data['stock'][existing]}")
            else:
                self.data["stock"][item_name] = quantity
                message = f"New equipment '{item_name}' added with {quantity} unit(s)."

            save_data(self.data)

            messagebox.showinfo("Success", message)

            self.set_status(f"Stock updated: {existing or item_name}")

            name_entry.delete(0, "end")

            qty_entry.delete(0, "end")

            name_entry.focus()

        button = self.accent_button(inner, "Add to Stock", add_item, color=GREEN, hover="#047857")
        button.grid(row=2, column=1, sticky="w", pady=(14, 6))

        qty_entry.bind("<Return>", add_item)
        name_entry.focus()
        self.set_status("Adding equipment.")

    def show_issue_form(self):

        self.page_header("Issue Equipment", "Record equipment being given out to a student.")
        available = sorted(n for n, q in self.data["stock"].items() if q > 0)
        card = self.card()
        card.pack(fill="x", pady=(20, 0))
        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(padx=10, pady=18, anchor="w")

        if not available:
            tk.Label(
                inner, text="No equipment is currently available to issue.",
                bg=CARD_BG, fg=RED, font=(FONT, 11, "bold"), padx=24, pady=20,
            ).pack()
            self.set_status("No stock available to issue.")
            return

        student_entry = self.form_row(inner, 0, "Student Name")
        class_entry = self.form_row(inner, 1, "Class / House")

        tk.Label(
            inner, text="Equipment", bg=CARD_BG, fg=TEXT_MUTED,
            font=(FONT, 10, "bold"),
        ).grid(row=2, column=0, sticky="w", pady=10, padx=(24, 14))
        item_combo = ttk.Combobox(
            inner, values=available, width=28, state="readonly", font=(FONT, 11),
        )
        item_combo.grid(row=2, column=1, sticky="w", pady=10)

        available_label = tk.Label(inner, text="", bg=CARD_BG, fg=TEXT_MUTED, font=(FONT, 9))
        available_label.grid(row=3, column=1, sticky="w")

        def update_available(event=None):
            name = item_combo.get()
            if name:
                available_label.config(
                    text=f"{self.data['stock'][name]} unit(s) available")

        item_combo.bind("<<ComboboxSelected>>", update_available)

        qty_entry = self.form_row(inner, 4, "Quantity")

        def issue_item(event=None):
            student_name = student_entry.get().strip()
            student_class = class_entry.get().strip()
            item_name = item_combo.get().strip()
            quantity_text = qty_entry.get().strip()

            if not student_name or not student_class or not item_name:
                messagebox.showerror("Missing Details", "Please fill in all details.")
                return
            try:
                quantity = int(quantity_text)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Quantity",
                    "Please enter a whole number greater than 0.")
                return

            in_stock = self.data["stock"].get(item_name, 0)
            if in_stock < quantity:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {in_stock} {item_name}(s) are currently available.")
                return

            self.data["stock"][item_name] -= quantity
            record = {
                "issue_id": self.data["next_issue_id"],
                "student_name": student_name,
                "class_house": student_class,
                "item_name": item_name,
                "quantity": quantity,
                "issue_date": str(date.today()),
                "status": "Issued",
                "return_date": "",
            }
            self.data["issued_items"].append(record)
            self.data["next_issue_id"] += 1
            save_data(self.data)

            messagebox.showinfo("Equipment Issued",
                                f"Issue ID:{record['issue_id']} \n"
                                f"Student: {record['student_name']} \n"
                                f"Class / House: {record['class_house']}\n"
                                f"Item: {item_name}  x  {quantity}\n"
                                f"Remaining stock: {self.data['stock'][item_name]}",
                                )
            self.set_status(f"{quantity} {item_name}(s) issued to {student_name}")
            self.switch_view("issue")

        button = self.accent_button(inner, "Issue Equipment", issue_item)
        button.grid(row=5, column=1, sticky="w", pady=(14, 6))
        qty_entry.bind("<Return>", issue_item)
        student_entry.focus()
        self.set_status("Issuing equipment.")

    def show_returns(self):
        self.page_header("Return The Equipment BOII", "Select the equipment first and then tap 'RETURN' ")

        pending = self.pending_records()

        toolbar = tk.Frame(self.content, bg=CONTENT_BG)
        toolbar.pack(fill='x', pady=(16, 10))
        return_btn = self.accent_button(toolbar, 'Return selected !!', self.return_selected, color=GREEN,
                                        hover='#047857')

        return_btn.pack(side="left")

        table_card = self.card()
        table_card.pack(fill="both", expand=True)

        columns = ("id", "student", "class", "item", "qty", "date")
        headings = ("Issue ID", "Student", "Class / House", "Equipment", "Qty", "Issue Date")
        widths = (80, 170, 130, 170, 70, 120)
        self.returns_tree = self.make_tree(table_card, columns, headings, widths)

        if not pending:
            self.returns_tree.insert(
                "", "end", values=("—", "No pending returns", "", "", "", ""))
        for i, record in enumerate(pending):
            self.returns_tree.insert(
                "", "end", tags=("odd" if i % 2 else "even",), values=(
                    record["issue_id"], record["student_name"],
                    record["class_house"], record["item_name"],
                    record["quantity"], record["issue_date"],
                ))

        tk.Label(
            self.content, text=f"Total pending records: {len(pending)}",
            bg=CONTENT_BG, fg=TEXT_DARK, font=(FONT, 11, "bold"), anchor="w",
        ).pack(fill="x", pady=(12, 0))
        self.set_status("Viewing pending returns.")

    def return_selected(self):

        selected = self.returns_tree.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a issue slot first.")
            return

        values = self.returns_tree.item(selected[0], "values")

        try:
            issue_id = int(values[0])
        except ValueError:
            return

        for record in self.data["issued_items"]:
            if record["issue_id"] == issue_id and record['status'] == 'Issued':
                if not messagebox.askyesno("Confirm Return",
                                           f"Return {record['quantity']} {record['item_name']} "
                                           f"from {record['student_name']}?",
                                           ):
                    return

                record['status'] = "Returned"
                record['return_date'] = str(date.today())
                self.data["stock"].setdefault(record["item_name"], 0)
                self.data["stock"][record["item_name"]] += record["quantity"]
                save_data(self.data)

                messagebox.showinfo("Equipment has been returned Succesfully!!!",
                                    f"{record['item_name']} x {record['quantity']} has been returned."
                                    f"Updated stock is :{self.data['stock'][record['item_name']]}")

                self.set_status(
                    f"{record['item_name']} returned by {record['student_name']}.")
                self.switch_view("returns")
                return

    def show_history(self):
        self.page_header("Equipment History", "View the history of the equipment Issued and Returned.")

        table_card = self.card()
        table_card.pack(fill='both', expand=True, pady=(18, 0))

        columns = ("id", "student", "class", "item", "qty", "issued", "returned", "status")
        headings = ("ID", "Student", "Class / House", "Equipment", "Qty", "Issue Date", "Return Date", "Status")
        width = (55, 150, 115, 150, 60, 110, 110, 100)
        tree = self.make_tree(table_card, columns, headings, width)

        records = list(reversed(self.data["issued_items"]))
        if not records:
            tree.insert("", "end", values=("—", "No records yet", "", "", "", "", "", ""))
        for record in records:
            tag = "returned" if record["status"] == "Returned" else "issued"
            tree.insert("", "end", tags=(tag,), values=(
                record["issue_id"],
                record["student_name"],
                record["class_house"],
                record["item_name"],
                record["quantity"],
                record["issue_date"],
                record["return_date"],
                record["status"]
            ))

        issued_count = len(self.pending_records())
        returned_count = len(records) - issued_count
        tk.Label(
            self.content,
            text=f" {len(records)} total records   |   {issued_count} still issued   |   {returned_count} returned",
            bg=CONTENT_BG, fg=TEXT_DARK, font=(FONT, 11, "bold"), anchor="w").pack(fill='x', pady=(12, 0))
        self.set_status("Viewing full history.")

    def exit_program(self):
        """Save data and close the app safely."""

        if messagebox.askyesno(
                "Exit SportStock Pro",
                "Save all the data and exit?"
        ):
            try:
                save_data(self.data)
            except Exception as e:
                messagebox.showerror(
                    "Save Error",
                    f"Could not save data:\n{e}"
                )
                return

            self.root.destroy()


def main():
    """Create the window, start the app, run the event loop."""
    root = tk.Tk()
    try:
        app = SportStockApp(root)
        root.protocol("WM_DELETE_WINDOW", app.exit_program)  # X button also asks to save
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Startup Error", f"SportStock Pro failed to start:\n{e}")
        root.destroy()


if __name__ == "__main__":
    main()