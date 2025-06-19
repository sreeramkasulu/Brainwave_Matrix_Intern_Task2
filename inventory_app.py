import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import hashlib

# -------------------- Database Setup --------------------
def connect_db():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )
    """)
    conn.commit()
    return conn

# -------------------- Authentication --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hash_password(password)))
        db.commit()
        messagebox.showinfo("Success", "User registered successfully.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

def login_user(username, password):
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cur.fetchone()
    if result and result[0] == hash_password(password):
        return True
    return False

# -------------------- Inventory Operations --------------------
def add_product(name, quantity, price):
    if not name or quantity < 0 or price < 0:
        messagebox.showerror("Validation Error", "Invalid product data.")
        return
    cur = db.cursor()
    cur.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                (name, quantity, price))
    db.commit()
    refresh_table()

def update_product(pid, name, quantity, price):
    cur = db.cursor()
    cur.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", 
                (name, quantity, price, pid))
    db.commit()
    refresh_table()

def delete_product(pid):
    cur = db.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (pid,))
    db.commit()
    refresh_table()

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    cur = db.cursor()
    cur.execute("SELECT * FROM products")
    for row in cur.fetchall():
        tree.insert("", "end", values=row)

def low_stock_report():
    cur = db.cursor()
    cur.execute("SELECT * FROM products WHERE quantity < 5")
    low_stock = cur.fetchall()
    msg = "\n".join([f"{r[1]} - Qty: {r[2]}" for r in low_stock]) or "No low-stock items."
    messagebox.showinfo("Low Stock Alert", msg)

def sales_summary():
    cur = db.cursor()
    cur.execute("SELECT SUM(quantity*price) FROM products")
    total_value = cur.fetchone()[0] or 0
    messagebox.showinfo("Sales Summary", f"Total Inventory Value: ₹{total_value:.2f}")

# -------------------- GUI --------------------
def main_window():
    global tree
    root = tk.Tk()
    root.title("Inventory Management System")
    root.geometry("700x500")

    frm = tk.Frame(root)
    frm.pack(pady=10)

    tk.Label(frm, text="Product Name").grid(row=0, column=0)
    tk.Label(frm, text="Quantity").grid(row=0, column=1)
    tk.Label(frm, text="Price").grid(row=0, column=2)

    name_entry = tk.Entry(frm)
    qty_entry = tk.Entry(frm)
    price_entry = tk.Entry(frm)
    name_entry.grid(row=1, column=0)
    qty_entry.grid(row=1, column=1)
    price_entry.grid(row=1, column=2)

    def on_add():
        try:
            add_product(name_entry.get(), int(qty_entry.get()), float(price_entry.get()))
            name_entry.delete(0, 'end')
            qty_entry.delete(0, 'end')
            price_entry.delete(0, 'end')
        except:
            messagebox.showerror("Error", "Invalid input.")

    def on_update():
        selected = tree.selection()
        if not selected:
            return
        pid, name, qty, price = tree.item(selected[0])['values']
        update_product(pid, name_entry.get(), int(qty_entry.get()), float(price_entry.get()))

    def on_delete():
        selected = tree.selection()
        if not selected:
            return
        pid = tree.item(selected[0])['values'][0]
        delete_product(pid)

    tk.Button(frm, text="Add", command=on_add).grid(row=1, column=3)
    tk.Button(frm, text="Update", command=on_update).grid(row=1, column=4)
    tk.Button(frm, text="Delete", command=on_delete).grid(row=1, column=5)

    tree = ttk.Treeview(root, columns=("ID", "Name", "Qty", "Price"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Qty", text="Quantity")
    tree.heading("Price", text="Price")
    tree.pack(fill=tk.BOTH, expand=True)

    report_frame = tk.Frame(root)
    report_frame.pack(pady=10)
    tk.Button(report_frame, text="Low Stock Report", command=low_stock_report).pack(side=tk.LEFT, padx=10)
    tk.Button(report_frame, text="Sales Summary", command=sales_summary).pack(side=tk.LEFT, padx=10)

    refresh_table()
    root.mainloop()

# -------------------- Entry Point --------------------
def login_screen():
    login = tk.Tk()
    login.title("Login")
    login.geometry("300x200")

    tk.Label(login, text="Username").pack()
    username_entry = tk.Entry(login)
    username_entry.pack()

    tk.Label(login, text="Password").pack()
    password_entry = tk.Entry(login, show="*")
    password_entry.pack()

    def attempt_login():
        if login_user(username_entry.get(), password_entry.get()):
            login.destroy()
            main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    def register():
        uname = username_entry.get()
        pwd = password_entry.get()
        if uname and pwd:
            register_user(uname, pwd)

    tk.Button(login, text="Login", command=attempt_login).pack(pady=5)
    tk.Button(login, text="Register", command=register).pack(pady=5)
    login.mainloop()

# -------------------- Main --------------------
db = connect_db()
login_screen()
