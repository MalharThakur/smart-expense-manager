import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyodbc
import joblib
from config import conn_str
from categorize import auto_categorize

# --- GLOBAL VARIABLES (All initial assignments here) ---
chart_container = None
tree = None
label_total = None
from_date_view = None
to_date_view = None
category_combobox_var = None
chart_type_combobox_var = None
current_from_date = ""
current_to_date = ""
current_category = ""
selected_expense_id = None
edit_btn = None 

# --- ML Model Loading and Prediction ---
model = joblib.load(r"C:\Users\tmalh\Documents\personal_expense_manager\ai_model\model.pkl")
vectorizer = joblib.load(r"C:\Users\tmalh\Documents\personal_expense_manager\ai_model\vectorizer.pkl")

def predict_top_level_type_ml(description):
    vect_text = vectorizer.transform([description])
    return model.predict(vect_text)[0]

def get_unique_categories():
    """Fetches unique categories from the database."""
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Category FROM Expenses ORDER BY Category")
        categories = [row[0] for row in cursor.fetchall() if row[0] is not None]
        conn.close()
        return ["All Categories"] + categories
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not load categories: {str(e)}")
        return ["All Categories"]

def insert_expense(date, amount, description):
    try:
        amount = float(amount)

        auto_type, auto_category, auto_subcategory = auto_categorize(description)

        final_type = auto_type
        final_category = auto_category
        final_subcategory = auto_subcategory

        if auto_type == "Uncategorized":
            ml_predicted_type = predict_top_level_type_ml(description)
            final_type = ml_predicted_type

            if ml_predicted_type.lower() == "essential":
                final_category = "General"
                final_subcategory = "General Essentials"
            elif ml_predicted_type.lower() == "non-essential":
                final_category = "General"
                final_subcategory = "Leisure/Optional"
            elif ml_predicted_type.lower() == "investment":
                final_category = "Finance"
                final_subcategory = "ML Predicted"
            elif ml_predicted_type.lower() == "miscellaneous":
                final_category = "Others"
                final_subcategory = "ML Predicted"
            else:
                final_category = "Others"
                final_subcategory = "Uncategorized"


        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Expenses (Date, Amount, Description, Type, Category, SubCategory) VALUES (?, ?, ?, ?, ?, ?)",
            date, amount, description, final_type, final_category, final_subcategory
        )
        conn.commit()
        messagebox.showinfo("Success", f"Saved as {final_type} → {final_subcategory}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_expenses(tree_widget, from_date_str, to_date_str, selected_category, label_total_widget, chart_frame_widget):
    global current_from_date, current_to_date, current_category
    global edit_btn
    
    current_from_date = from_date_str
    current_to_date = to_date_str
    current_category = selected_category
    
    if edit_btn: edit_btn.config(state="disabled")

    for row in tree_widget.get_children():
        tree_widget.delete(row)

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        sql_query = """
            SELECT ExpenseID, Date, Amount, Description, Type, Category, SubCategory
            FROM Expenses
            WHERE Date BETWEEN ? AND ?
        """
        params = [from_date_str, to_date_str]

        if selected_category != "All Categories":
            sql_query += " AND Category = ?"
            params.append(selected_category)

        sql_query += " ORDER BY Date DESC"

        cursor.execute(sql_query, *params)
        rows = cursor.fetchall()

        total = 0
        for i, row in enumerate(rows):
            expense_id = row[0]
            date_obj = row[1]
            date_str = date_obj.strftime("%Y-%m-%d") if hasattr(date_obj, "strftime") else str(date_obj)
            amount = float(row[2])
            total += amount
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree_widget.insert("", tk.END, iid=expense_id, values=(date_str, f"{amount:.2f}", row[3], row[4], row[5], row[6]), tags=(tag,))


        label_total_widget.config(text=f"Total: ₹{total:.2f}")

        if chart_container:
            show_chart(chart_frame_widget, current_from_date, current_to_date, current_category, chart_type_combobox_var.get())

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_chart(frame_widget, from_date_str, to_date_str, selected_category, chart_type):
    for widget in frame_widget.winfo_children():
        widget.destroy()
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        sql_query = """
            SELECT Category, SUM(Amount)
            FROM Expenses
            WHERE Date BETWEEN ? AND ?
        """
        params = [from_date_str, to_date_str]

        if selected_category != "All Categories":
            sql_query += " AND Category = ?"
            params.append(selected_category)

        sql_query += " GROUP BY Category"

        cursor.execute(sql_query, *params)
        data = cursor.fetchall()

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        if not amounts:
            ttk.Label(frame_widget, text="No expense data for the selected date range and category to display chart.",
                      font=("Segoe UI", 12, "italic"), background="#F5F7FA", foreground="#888888").pack(pady=50)
            return

        fig, ax = plt.subplots(figsize=(7, 6), facecolor="#F5F7FA") 
        ax.set_facecolor("#F5F7FA")
        
        colors = ['#4285F4', '#DB4437', '#F4B400', '#0F9D58', '#4286f4', '#AA6C39', '#663399']
        
        if chart_type == "Pie Chart":
            wedges, texts, autotexts = ax.pie(
                amounts, labels=categories, autopct="%1.1f%%", startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
                textprops={'fontsize': 10, 'color': '#333333'},
                colors=colors[:len(categories)]
            )
            for autotexts in autotexts:
                autotexts.set_color('white')
            ax.axis('equal')
            ax.legend(wedges, categories,
                      title="Categories",
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1),
                      frameon=False,
                      fontsize=10,
                      labelcolor='#333333')
        
        elif chart_type == "Bar Graph":
            ax.bar(categories, amounts, color=colors[:len(categories)])
            ax.set_xlabel("Category", fontsize=12, fontweight='bold', color='#333333')
            ax.set_ylabel("Amount", fontsize=12, fontweight='bold', color='#333333')
            ax.set_xticklabels(categories, rotation=45, ha="right", fontsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.25, left=0.15)

        ax.set_title(f"Spending by {chart_type}", fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': '#333333'})
        
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame_widget)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    except Exception as e:
        messagebox.showerror("Chart Error", str(e))
        
def delete_expense(tree_widget, popup_window):
    global selected_expense_id
    if not selected_expense_id:
        return
    
    popup_window.destroy()
    
    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this expense? This action cannot be undone."):
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Expenses WHERE ExpenseID = ?", selected_expense_id)
            conn.commit()
            messagebox.showinfo("Success", "Expense deleted successfully!")
            
            load_expenses(tree_widget, current_from_date, current_to_date, current_category, label_total, chart_container)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")

def modify_expense(tree_widget, popup_window):
    global selected_expense_id, root
    if not selected_expense_id:
        return
        
    popup_window.destroy()
        
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT Date, Amount, Description, Category FROM Expenses WHERE ExpenseID = ?", selected_expense_id)
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", "Expense not found in the database.")
            return

        date, amount, description, category = row
        
        modify_window = tk.Toplevel()
        modify_window.title(f"Modify Expense #{selected_expense_id}")
        modify_window.configure(bg="#F0F2F5")
        
        # Pack widgets first to determine the window's ideal size
        form_frame = ttk.LabelFrame(modify_window, text=f"Edit Expense #{selected_expense_id}", padding=(20, 15), style="TLabelframe")
        form_frame.pack(padx=20, pady=20)
        
        ttk.Label(form_frame, text="📅 Date:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        date_entry = DateEntry(form_frame, width=18, font=("Segoe UI", 10), date_pattern="yyyy-mm-dd")
        date_entry.set_date(date)
        date_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="💰 Amount:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        amount_entry = ttk.Entry(form_frame, width=25)
        amount_entry.insert(0, str(amount))
        amount_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(form_frame, text="📝 Description:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        desc_entry = ttk.Entry(form_frame, width=25)
        desc_entry.insert(0, description)
        desc_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        
        ttk.Label(form_frame, text="📂 Category:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        category_modify_var = tk.StringVar()
        category_modify_combobox = ttk.Combobox(form_frame, textvariable=category_modify_var,
                                     values=get_unique_categories(), state="readonly", width=25)
        category_modify_combobox.set(category)
        category_modify_combobox.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        
        def on_update():
            new_date = date_entry.get()
            new_amount = amount_entry.get()
            new_desc = desc_entry.get()
            new_category = category_modify_combobox.get()
            
            try:
                new_amount_float = float(new_amount)
                
                auto_type, _, auto_subcategory = auto_categorize(new_desc)
                
                update_query = """
                    UPDATE Expenses SET Date = ?, Amount = ?, Description = ?, Type = ?, Category = ?, SubCategory = ?
                    WHERE ExpenseID = ?
                """
                
                cursor.execute(update_query, new_date, new_amount_float, new_desc, auto_type, new_category, auto_subcategory, selected_expense_id)
                conn.commit()
                messagebox.showinfo("Success", "Expense updated successfully!")
                modify_window.destroy()
                
                load_expenses(tree_widget, current_from_date, current_to_date, current_category, label_total, chart_container)
                
            except ValueError:
                messagebox.showerror("Invalid Amount", "Amount must be a number.")
            except Exception as e:
                messagebox.showerror("Update Error", f"Failed to update expense: {str(e)}")

        update_btn = ttk.Button(modify_window, text="Update Expense", command=on_update, style="Accent.TButton")
        update_btn.pack(pady=10)
        
        # Now that widgets are packed, get the geometry and center the window
        modify_window.update_idletasks()
        mod_width = modify_window.winfo_width()
        mod_height = modify_window.winfo_height()
        
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        pos_x = root_x + (root_width - mod_width) // 2
        pos_y = root_y + (root_height - mod_height) // 2
        
        modify_window.geometry(f"+{pos_x}+{pos_y}")

        modify_window.resizable(False, False)
        modify_window.transient(root)
        modify_window.grab_set()
        
        modify_window.wait_window()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve expense data: {str(e)}")
        
def on_tree_select(event):
    global selected_expense_id, tree, edit_btn
    
    selected_items = tree.selection()
    if selected_items:
        selected_expense_id = selected_items[0]
        if edit_btn:
            edit_btn.config(state="enabled")
    else:
        selected_expense_id = None
        if edit_btn:
            edit_btn.config(state="disabled")

def show_edit_options(tree_widget):
    global selected_expense_id, root
    if not selected_expense_id:
        return
        
    options_window = tk.Toplevel()
    options_window.title("Edit Options")
    
    options_window.update_idletasks()
    opt_width = 250
    opt_height = 120
    
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    
    pos_x = root_x + (root_width - opt_width) // 2
    pos_y = root_y + (root_height - opt_height) // 2
    options_window.geometry(f"{opt_width}x{opt_height}+{pos_x}+{pos_y}")

    options_window.resizable(False, False)
    options_window.transient(root)
    options_window.grab_set()
    
    frame = ttk.Frame(options_window, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Button(frame, text="✏️ Modify", style="Accent.TButton",
               command=lambda: modify_expense(tree_widget, options_window)).pack(fill=tk.X, pady=5)
               
    ttk.Button(frame, text="❌ Delete", style="Accent.TButton",
               command=lambda: delete_expense(tree_widget, options_window)).pack(fill=tk.X, pady=5)

    options_window.wait_window()


# --- GUI Creation ---
def create_gui():
    global chart_container, tree, label_total, from_date_view, to_date_view, category_combobox_var, chart_type_combobox_var
    global edit_btn, root
    
    root = tk.Tk()
    root.title("💰 ExpenseIQ - Smart Personal Expense Manager")
    root.geometry("1200x750")
    root.minsize(1000, 600)
    root.configure(bg="#F0F2F5")

    # --- STYLE CONFIGURATION ---
    style = ttk.Style()
    style.theme_use("clam")
    style.layout("Nav.TButton", style.layout("TButton"))
    style.layout("Nav.TButton.Selected", style.layout("TButton"))
    style.configure(".", font=("Segoe UI", 10), background="#F0F2F5", foreground="#333333")
    style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1A2B42", background="#F0F2F5")
    style.configure("Section.TLabel", font=("Segoe UI", 14, "bold"), foreground="#333333", background="#FFFFFF")
    style.configure("MainFrame.TFrame", background="#F0F2F5", borderwidth=0)
    style.configure("Card.TFrame", background="white", borderwidth=1, relief="flat", highlightbackground="#E0E0E0", highlightcolor="#E0E0E0", highlightthickness=1)
    style.configure("ChartFrame.TFrame", background="#F5F7FA", borderwidth=1, relief="solid", bordercolor="#DDDDDD")
    style.configure("TLabelframe", background="white", borderwidth=1, relief="solid", bordercolor="#DDDDDD", padding=[15,10])
    style.configure("TLabelframe.Label", background="white", foreground="#1A2B42", font=("Segoe UI", 12, "bold"))
    style.configure("TEntry", fieldbackground="white", foreground="#333333", borderwidth=1, relief="solid", padding=[5, 8])
    style.map("TEntry", fieldbackground=[('focus', '#E8F0FE')])
    style.configure("TCombobox", fieldbackground="white", foreground="#333333", borderwidth=1, relief="solid", padding=5)
    style.map("TCombobox", fieldbackground=[('readonly', 'white'), ('focus', '#E8F0FE')])
    style.configure("Nav.TButton", font=("Segoe UI", 11, "bold"), padding=[15, 12], background="#F0F2F5", foreground="#555555", borderwidth=0, relief="flat", focusthickness=0)
    style.map("Nav.TButton", background=[('active', '#E0E0E0')], foreground=[('active', '#007BFF')], )
    style.configure("Nav.TButton.Selected", background="#E8F0FE", foreground="#007BFF", font=("Segoe UI", 11, "bold"), borderwidth=0, relief="flat")
    style.map("Nav.TButton.Selected", background=[('active', '#E8F0FE')], foreground=[('active', '#007BFF')])
    
    style.configure("Small.Accent.TButton",
                    font=("Segoe UI", 10, "bold"),
                    padding=[10, 5],
                    background="#007BFF",
                    foreground="white",
                    borderwidth=0,
                    relief="flat",
                    focusthickness=0)
    style.map("Small.Accent.TButton",
              background=[('active', '#0056B3'), ('pressed', '#004085')],
              foreground=[('active', 'white'), ('active', 'white')])

    style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=[20, 10], background="#007BFF", foreground="white", borderwidth=0, relief="flat", focusthickness=0)
    style.map("Accent.TButton", background=[('active', '#0056B3'), ('pressed', '#004085')], foreground=[('active', 'white'), ('active', 'white')])
    style.configure("Treeview", font=("Segoe UI", 9), rowheight=30, background="white", fieldbackground="white", foreground="#333333", borderwidth=1, relief="solid", bordercolor="#DDDDDD")
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E0E0E0", foreground="#333333", padding=[10, 8], relief="flat")
    style.map("Treeview", background=[('selected', '#BEE3F8')])
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    # --- MAIN LAYOUT ---
    nav_frame = ttk.Frame(root, width=200, style="MainFrame.TFrame")
    nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    content_area = ttk.Frame(root, style="MainFrame.TFrame")
    content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Navigation Buttons ---
    logo_label = ttk.Label(nav_frame, text="ExpenseIQ", font=("Segoe UI", 18, "bold"), foreground="#007BFF", background="#F0F2F5", anchor="center")
    logo_label.pack(pady=(20, 30), fill=tk.X)
    add_expense_frame = ttk.Frame(content_area, style="MainFrame.TFrame")
    view_expenses_frame = ttk.Frame(content_area, style="MainFrame.TFrame")
    insights_frame = ttk.Frame(content_area, style="MainFrame.TFrame")
    
    chart_container = ttk.Frame(insights_frame, style="ChartFrame.TFrame")
    chart_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)


    def show_content_frame(frame_to_show, nav_button_to_select):
        global tree, label_total, from_date_view, to_date_view, category_combobox_var, chart_type_combobox_var
        
        for frame in [add_expense_frame, view_expenses_frame, insights_frame]:
            frame.pack_forget()
        
        for btn in [nav_add_btn, nav_view_btn, nav_insights_btn]:
            btn.config(style="Nav.TButton")
        
        frame_to_show.pack(fill=tk.BOTH, expand=True)
        nav_button_to_select.config(style="Nav.TButton.Selected")
        
        if frame_to_show == insights_frame:
            if from_date_view and to_date_view and category_combobox_var and chart_type_combobox_var:
                show_chart(chart_container, current_from_date, current_to_date, current_category, chart_type_combobox_var.get())
            else:
                for widget in chart_container.winfo_children():
                    widget.destroy()
                ttk.Label(chart_container, text="Select a date range and category in 'View Expenses' to see insights.",
                          font=("Segoe UI", 12, "italic"), background="#F5F7FA", foreground="#888888").pack(pady=50)

    nav_add_btn = ttk.Button(nav_frame, text=" ➕ Add Expense", style="Nav.TButton",
                             command=lambda: show_content_frame(add_expense_frame, nav_add_btn))
    nav_add_btn.pack(fill=tk.X, pady=5, padx=10)

    nav_view_btn = ttk.Button(nav_frame, text=" 📋 View Expenses", style="Nav.TButton",
                              command=lambda: show_content_frame(view_expenses_frame, nav_view_btn))
    nav_view_btn.pack(fill=tk.X, pady=5, padx=10)

    nav_insights_btn = ttk.Button(nav_frame, text=" 📊 Insights", style="Nav.TButton",
                                  command=lambda: show_content_frame(insights_frame, nav_insights_btn))
    nav_insights_btn.pack(fill=tk.X, pady=5, padx=10)

    show_content_frame(add_expense_frame, nav_add_btn)

    # --- ADD EXPENSE CONTENT ---
    ttk.Label(add_expense_frame, text="💰 Add New Expense", style="Title.TLabel").pack(pady=(25, 35))
    input_card_add = ttk.LabelFrame(add_expense_frame, text=" Expense Details ", padding=(30, 20), style="TLabelframe")
    input_card_add.pack(pady=15, padx=50, fill="x", ipadx=10, ipady=5)
    ttk.Label(input_card_add, text="📅 Date:").grid(row=0, column=0, sticky="w", pady=10, padx=10)
    date_picker = DateEntry(input_card_add, width=22, font=("Segoe UI", 10), date_pattern="yyyy-mm-dd")
    date_picker.grid(row=0, column=1, pady=10, padx=10, sticky="ew")
    ttk.Label(input_card_add, text="💰 Amount:").grid(row=1, column=0, sticky="w", pady=10, padx=10)
    entry_amount = ttk.Entry(input_card_add, width=35)
    entry_amount.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
    entry_amount.insert(0, "e.g., 500.00")
    entry_amount.bind("<FocusIn>", lambda event: entry_amount.delete(0, tk.END) if entry_amount.get() == "e.g., 500.00" else None)
    entry_amount.bind("<FocusOut>", lambda event: entry_amount.insert(0, "e.g., 500.00") if not entry_amount.get() else None)
    ttk.Label(input_card_add, text="📝 Description:").grid(row=2, column=0, sticky="w", pady=10, padx=10)
    entry_desc = ttk.Entry(input_card_add, width=35)
    entry_desc.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
    entry_desc.insert(0, "e.g., Monthly groceries, Dinner out")
    entry_desc.bind("<FocusIn>", lambda event: entry_desc.delete(0, tk.END) if entry_desc.get() == "e.g., Monthly groceries, Dinner out" else None)
    entry_desc.bind("<FocusOut>", lambda event: entry_desc.insert(0, "e.g., Monthly groceries, Dinner out") if not entry_desc.get() else None)
    input_card_add.grid_columnconfigure(1, weight=1)
    def on_submit():
        date = date_picker.get()
        amount = entry_amount.get().strip()
        desc = entry_desc.get().strip()
        if amount == "e.g., 500.00": amount = ""
        if desc == "e.g., Monthly groceries, Dinner out": desc = ""
        if not amount or not desc:
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return
        try:
            float(amount)
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a number.")
            return
        insert_expense(date, amount, desc)
        entry_amount.delete(0, tk.END)
        entry_amount.insert(0, "e.g., 500.00")
        entry_desc.delete(0, tk.END)
        entry_desc.insert(0, "e.g., Monthly groceries, Dinner out")
    add_btn = ttk.Button(add_expense_frame, text="Add Expense", command=on_submit, style="Accent.TButton")
    add_btn.pack(pady=40)

    # --- VIEW EXPENSES CONTENT ---
    ttk.Label(view_expenses_frame, text="📋 Your Expense History", style="Title.TLabel").pack(pady=(25, 35))
    filter_card_view = ttk.Frame(view_expenses_frame, style="Card.TFrame", padding=(20, 15))
    filter_card_view.pack(pady=15, padx=50, fill="x", ipadx=5, ipady=5)
    ttk.Label(filter_card_view, text="From:").pack(side=tk.LEFT, padx=8)
    from_date_view = DateEntry(filter_card_view, width=15, date_pattern="yyyy-mm-dd", font=("Segoe UI", 10))
    from_date_view.pack(side=tk.LEFT, padx=8)
    ttk.Label(filter_card_view, text="To:").pack(side=tk.LEFT, padx=8)
    to_date_view = DateEntry(filter_card_view, width=15, date_pattern="yyyy-mm-dd", font=("Segoe UI", 10))
    to_date_view.pack(side=tk.LEFT, padx=8)
    ttk.Label(filter_card_view, text="Category:").pack(side=tk.LEFT, padx=8)
    category_combobox_var = tk.StringVar()
    category_combobox = ttk.Combobox(filter_card_view, textvariable=category_combobox_var, values=get_unique_categories(), state="readonly", width=20)
    category_combobox.set("All Categories")
    category_combobox.pack(side=tk.LEFT, padx=8)
    
    # Buttons for filtering and Edit options
    action_buttons_frame = ttk.Frame(view_expenses_frame, style="TFrame")
    action_buttons_frame.pack(pady=5, padx=50, fill="x")
    
    ttk.Button(filter_card_view, text="🔍 Show", style="Accent.TButton",
               command=lambda: load_expenses(tree, from_date_view.get(), to_date_view.get(), category_combobox_var.get(), label_total, chart_container)).pack(side=tk.LEFT, padx=20)
    
    edit_btn = ttk.Button(action_buttons_frame, text="✏️ Edit", style="Small.Accent.TButton", state="disabled", command=lambda: show_edit_options(tree))
    edit_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    label_total = ttk.Label(view_expenses_frame, text="Total: ₹0.00", font=("Segoe UI", 12, "bold"), foreground="#007BFF", background="#F0F2F5")
    label_total.pack(pady=15)
    
    columns = ("Date", "Amount", "Description", "Type", "Category", "SubCategory")
    tree = ttk.Treeview(view_expenses_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        if col == "Date": tree.column(col, anchor="center", width=95)
        elif col == "Amount": tree.column(col, anchor="e", width=75)
        elif col == "Description": tree.column(col, anchor="center", width=220)
        elif col == "Type": tree.column(col, anchor="center", width=95)
        elif col == "Category": tree.column(col, anchor="center", width=120)
        elif col == "SubCategory": tree.column(col, anchor="center", width=130)
        
    tree.tag_configure("oddrow", background="#F8F9FA", foreground="#333333")
    tree.tag_configure("evenrow", background="white", foreground="#333333")
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    tree.pack(fill="both", expand=True, padx=30, pady=20)

    # --- INSIGHTS CONTENT ---
    ttk.Label(insights_frame, text="📊 Spending Insights", style="Title.TLabel").pack(pady=(25, 35))
    chart_type_frame = ttk.Frame(insights_frame, style="Card.TFrame", padding=(20, 15))
    chart_type_frame.pack(pady=10, padx=50, fill="x")
    ttk.Label(chart_type_frame, text="Select Chart Type:").pack(side=tk.LEFT, padx=10, pady=5)
    chart_type_combobox_var = tk.StringVar()
    chart_type_combobox = ttk.Combobox(chart_type_frame, textvariable=chart_type_combobox_var, values=["Pie Chart", "Bar Graph"], state="readonly", width=15)
    chart_type_combobox.set("Pie Chart")
    chart_type_combobox.bind("<<ComboboxSelected>>", lambda event: show_chart(chart_container, current_from_date, current_to_date, current_category, chart_type_combobox_var.get()))
    chart_type_combobox.pack(side=tk.LEFT, padx=10, pady=5)
    chart_container = ttk.Frame(insights_frame, style="ChartFrame.TFrame")
    chart_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
    root.mainloop()

if __name__ == "__main__":
    create_gui()