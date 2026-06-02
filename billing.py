
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class billingClass:
    def __init__(self, root):
        self.root = root 
        self.root.state('zoomed')
       # self.root.geometry("1350x700+0+0")
        self.root.title("ALI SALEH AL-JERYAN - Billing System By Bhasith")
        self.root.config(bg="white")
        self.root.focus_force()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Database connection
        self.connection = self.create_db_connection()
        self.initialize_database()

        # Variables
        self.var_invoice = StringVar()
        self.var_customer_name = StringVar()
        self.var_contact = StringVar()
        self.var_vehicle_no = StringVar()
        self.var_vehicle_model = StringVar()
        self.var_service_date = StringVar()
        self.var_search_txt = StringVar()
        self.var_search_by = StringVar(value="Select")
        self.var_bill_type = StringVar(value="invoice")  # Default bill type

        
        # Current date
        self.var_service_date.set(datetime.now().strftime("%d-%m-%Y"))
        
        # Auto-generate invoice number
        self.generate_invoice()
        # Title
        title = Label(self.root, text="Workshop Billing System", 
                     font=("times new roman", 25, "bold"), bg="#010c48", fg="white")
        title.pack(side=TOP, fill=X)
        
        # Main Frame
        MainFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        MainFrame.place(relx=0.005, rely=0.07, relwidth=0.99, relheight=0.91)
        
        # Customer Frame
        customer_frame = LabelFrame(MainFrame, text="Customer Details", 
                                  font=("times new roman", 15, "bold"), bg="white")
        customer_frame.place(relx=0.01, rely=0.01, relwidth=0.25, relheight=0.20)
        
        # Labels and Entries
        lbl_invoice = Label(customer_frame, text="Invoice No.", font=("times new roman", 15), bg="white")
        lbl_invoice.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        txt_invoice = Entry(customer_frame, textvariable=self.var_invoice, font=("times new roman", 15), 
                          bg="lightyellow", state='readonly',width=25)
        txt_invoice.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        
        lbl_name = Label(customer_frame, text="Name", font=("times new roman", 15), bg="white")
        lbl_name.grid(row=1, column=0, sticky="w", padx=5, pady=3)
        txt_name = Entry(customer_frame, textvariable=self.var_customer_name, font=("times new roman", 15), 
                        bg="lightyellow",width=25)
        txt_name.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        
        lbl_contact = Label(customer_frame, text="Contact", font=("times new roman", 15), bg="white")
        lbl_contact.grid(row=2, column=0, sticky="w", padx=5, pady=3)
        txt_contact = Entry(customer_frame, textvariable=self.var_contact, font=("times new roman", 15), 
                           bg="lightyellow",width=25)
        txt_contact.grid(row=2, column=1, sticky="w", padx=5, pady=3)
       
        lbl_bill_type = Label(customer_frame, text="Bill Type", font=("times new roman", 15), bg="white")
        lbl_bill_type.grid(row=3, column=0, sticky="w", padx=5, pady=3)

        cmb_bill_type = ttk.Combobox(customer_frame, textvariable=self.var_bill_type, 
                                    values=("invoice", "quotation"), state="readonly", font=("times new roman", 15))
        cmb_bill_type.grid(row=3, column=1, sticky="w", padx=5, pady=3)
        cmb_bill_type.current(0)
 
        # Vehicle Frame
        vehicle_frame = LabelFrame(MainFrame, text="Vehicle Details", 
                                 font=("times new roman", 15, "bold"), bg="white")
        vehicle_frame.place(relx=0.30, rely=0.01, relwidth=0.25, relheight=0.20)
        
        lbl_vehicle_no = Label(vehicle_frame, text="Vehicle No.", font=("times new roman", 15), bg="white")
        lbl_vehicle_no.grid(row=0, column=0, sticky="w", padx=5, pady=3)
        txt_vehicle_no = Entry(vehicle_frame, textvariable=self.var_vehicle_no, font=("times new roman", 15), 
                             bg="lightyellow",width=25)
        txt_vehicle_no.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        
        lbl_vehicle_model = Label(vehicle_frame, text="Model", font=("times new roman", 15), bg="white")
        lbl_vehicle_model.grid(row=1, column=0, sticky="w", padx=5, pady=3)
        txt_vehicle_model = Entry(vehicle_frame, textvariable=self.var_vehicle_model, font=("times new roman", 15), 
                                bg="lightyellow",width=25)
        txt_vehicle_model.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        
        lbl_service_date = Label(vehicle_frame, text="Service Date", font=("times new roman", 15), bg="white")
        lbl_service_date.grid(row=2, column=0, sticky="w", padx=5, pady=3)
        txt_service_date = Entry(vehicle_frame, textvariable=self.var_service_date, font=("times new roman", 15), 
                               bg="lightyellow",width=25)
        txt_service_date.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        
        # ================= SERVICE FRAME =================
        service_frame = LabelFrame(MainFrame, text="Services",
                                font=("times new roman", 15, "bold"), bg="white")
        service_frame.place(relx=0.01, rely=0.22, relwidth=0.54, relheight=0.50)
        service_frame.grid_propagate(False) #this fixes the resizing of the frame when widgets are added/removed, allowing us to use relative placement for the tree and custom input frames inside it without them resizing the main service frame

        # ====== FRAME INSIDE (for tree + scrollbars) ======
        tree_frame = Frame(service_frame, bg="white")
        tree_frame.place(relx=0, rely=0, relwidth=1, relheight=0.75)

        # ====== SCROLLBARS ======
        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)

        # ====== TREEVIEW ======
        self.service_table = ttk.Treeview(
            tree_frame,
            columns=("sr", "sid", "service", "price"),
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            show="headings"
        )

        # Attach scrollbars
        scroll_y.config(command=self.service_table.yview)
        scroll_x.config(command=self.service_table.xview)

        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.service_table.pack(fill=BOTH, expand=True)

        # ====== HEADINGS ======
        self.service_table.heading("sr", text="Sr.No")
        self.service_table.heading("sid", text="ID")
        self.service_table.heading("service", text="Service")
        self.service_table.heading("price", text="Price")

        # ====== COLUMN SETTINGS ======
        self.service_table.column("sr", anchor=CENTER, width=60, minwidth=40)
        self.service_table.column("sid", anchor=CENTER, width=80, minwidth=50)
        self.service_table.column("service", anchor=W, width=300, minwidth=150)
        self.service_table.column("price", anchor=CENTER, width=100, minwidth=80)
        # responsive resizing hook
        self.service_table.bind("<Configure>", self.resize_service_columns)

        # Load services from database
        self.load_services()

# ================= CUSTOM SERVICE INPUTS (FIXED SINGLE LINE) =================

        custom_frame = Frame(service_frame, bg="white")
        custom_frame.place(relx=0, rely=0.80, relwidth=1, relheight=0.25)

        custom_frame.grid_columnconfigure((0,1,2,3,4,5), weight=0)

        # Service Name
        Label(custom_frame, text="Service Name",
            font=("times new roman", 13), bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_custom_service = Entry(custom_frame,
                                        font=("times new roman", 13),
                                        bg="lightyellow",
                                        width=20)
        self.entry_custom_service.grid(row=0, column=1, padx=(0,5), pady=5)

        # Price
        Label(custom_frame, text="Price",
            font=("times new roman", 13), bg="white").grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.entry_custom_price = Entry(custom_frame,
                                        font=("times new roman", 13),
                                        bg="lightyellow",
                                        width=10)
        self.entry_custom_price.grid(row=0, column=3, padx=(0,5), pady=5)

        # Qty
        Label(custom_frame, text="Qty",
            font=("times new roman", 13), bg="white").grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.entry_custom_qty = Entry(custom_frame,
                                    font=("times new roman", 13),
                                    bg="lightyellow",
                                    width=6)
        self.entry_custom_qty.grid(row=0, column=5, padx=(0,5), pady=5)

        # Save to DB (same line after Qty)
        self.save_to_db = IntVar()

        Checkbutton(custom_frame,
                    text="Save to DB",
                    variable=self.save_to_db,
                    bg="white",
                    font=("times new roman", 12)
                    ).grid(row=0, column=6, padx=(2,2), pady=5, sticky="w")

        # Buttons (still same line)
        Button(custom_frame, text="Add Custom", command=self.add_custom_service,
            font=("times new roman", 12), bg="purple", fg="white", width=11,height=1).grid(row=0, column=7, padx=(0,1), sticky="w")

        Button(custom_frame, text="Update", command=self.update_service,
            font=("times new roman", 12), bg="blue", fg="white", width=12,height=1).grid(row=0, column=8, padx=1)

        Button(custom_frame, text="Delete", command=self.delete_service,
            font=("times new roman", 12), bg="red", fg="white", width=12,height=1).grid(row=0, column=9, padx=1)

        
        # Billing Frame
        billing_frame = Frame(MainFrame, bd=2, relief=RIDGE, bg="white")
        billing_frame.place(relx=0.56, rely=0.001, relwidth=0.44, relheight=0.67)

        lbl_title = Label(billing_frame, text="Billing Details", font=("times new roman", 20, "bold"), bg="orange")
        lbl_title.pack(side=TOP, fill=X)
        
        # Scrollbar for selected services
        scroll_y2 = Scrollbar(billing_frame, orient=VERTICAL)
        self.cart_table = ttk.Treeview(billing_frame, columns=("sr", "sid", "service", "price", "qty", "total"), 
                                     yscrollcommand=scroll_y2.set)
        scroll_y2.pack(side=RIGHT, fill=Y)
        scroll_y2.config(command=self.cart_table.yview)
        
        self.cart_table.heading("sr", text="Sr.No")
        self.cart_table.heading("sid", text="ID")
        self.cart_table.heading("service", text="Service")
        self.cart_table.heading("price", text="Price")
        self.cart_table.heading("qty", text="Qty")
        self.cart_table.heading("total", text="Total")
        
        self.cart_table["show"] = "headings"
        
        self.cart_table.column("sr", width=50)
        self.cart_table.column("sid", width=50)
        self.cart_table.column("service", width=150)
        self.cart_table.column("price", width=80)
        self.cart_table.column("qty", width=50)
        self.cart_table.column("total", width=80)
        
        self.cart_table.pack(fill=BOTH, expand=1)
        
        # Bind double click to add service to cart
        self.service_table.bind("<Double-1>", self.add_to_cart)
        
        # Buttons
        btn_frame = Frame(billing_frame, bd=2, relief=RIDGE, bg="white")
        btn_frame.place(relx=0.01, rely=0.84, relwidth=0.96, relheight=0.15)
        
        btn_add = Button(btn_frame, text="Add", command=self.add_to_cart, font=("times new roman", 18), 
                        bg="green", fg="white", cursor="hand2")
        btn_add.grid(row=0, column=2, padx=(270,5), pady=5, sticky="w")
        
        btn_remove = Button(btn_frame, text="Remove", command=self.remove_from_cart, font=("times new roman", 18), 
                           bg="red", fg="white", cursor="hand2")
        btn_remove.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        btn_clear = Button(btn_frame, text="Clear", command=self.clear_cart, font=("times new roman", 18), 
                          bg="gray", fg="white", cursor="hand2")
        btn_clear.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        btn_generate = Button(btn_frame, text="Generate Bill", command=self.generate_bill, 
                             font=("times new roman", 18), bg="blue", fg="white", cursor="hand2")
        btn_generate.grid(row=0, column=5, padx=5, pady=5)
        
        # Quantity adjustment buttons
        btn_increase = Button(btn_frame, text="+", command=self.increase_quantity, font=("times new roman", 15), 
                             bg="lightgreen", fg="black", cursor="hand2",width=3)
        btn_increase.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        btn_decrease = Button(btn_frame, text="-", command=self.decrease_quantity, font=("times new roman", 15), 
                             bg="lightcoral", fg="black", cursor="hand2",width=3)
        btn_decrease.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Total Frame
        total_frame = Frame(MainFrame, bd=2, relief=RIDGE, bg="white")
        
        total_frame.place(relx=0.56, rely=0.69, relwidth=0.43, relheight=0.30)
        
        lbl_total = Label(total_frame, text="Bill Total", font=("times new roman", 23, "bold"), bg="lightgray")
        lbl_total.pack(side=TOP, fill=X)
        
        self.lbl_subtotal = Label(total_frame, text="Sub Total: 0.00", font=("times new roman", 20), bg="white")
        self.lbl_subtotal.place(x=10, y=100)
        
     #   self.lbl_tax = Label(total_frame, text="Tax (5%): 0.00", font=("times new roman", 15), bg="white")
      #  self.lbl_tax.place(x=10, y=80)
        
        self.lbl_grandtotal = Label(total_frame, text="Grand Total: 0.00", font=("times new roman", 25, "bold"), 
                                  bg="lightyellow")
        self.lbl_grandtotal.place(x=10, y=180)
        
        # Search Frame
        search_frame = LabelFrame(MainFrame, text="Search Bills", font=("times new roman", 15, "bold"), bg="white")
        
        search_frame.place(relx=0.01, rely=0.68, relwidth=0.54, relheight=0.10)
        
        cmb_search = ttk.Combobox(search_frame, textvariable=self.var_search_by, 
                                 values=("Select", "Invoice No.", "Customer Name", "Contact", "Vehicle No.", "Model"), 
                                 state="readonly", font=("times new roman", 15))
        cmb_search.place(x=10, y=10, width=180)
        cmb_search.current(0)
        
        txt_search = Entry(search_frame, textvariable=self.var_search_txt, font=("times new roman", 15), 
                         bg="lightyellow")
        txt_search.place(x=200, y=10, width=180)
        
        btn_search = Button(search_frame, text="Search", command=self.search_bill, 
                           font=("times new roman", 15), bg="blue", fg="white", cursor="hand2")
        btn_search.place(x=390, y=10, width=120, height=30)
        
        btn_show_all = Button(search_frame, text="Show All", command=self.show_all_bills, 
                             font=("times new roman", 15), bg="gray", fg="white", cursor="hand2")
        btn_show_all.place(x=520, y=10, width=120, height=30)
        
        # Bill History Frame
        history_frame = Frame(MainFrame, bd=3, relief=RIDGE, bg="white")
        
        history_frame.place(relx=0.01, rely=0.78, relwidth=0.54, relheight=0.22)
        
        scroll_y3 = Scrollbar(history_frame, orient=VERTICAL)
        scroll_x3 = Scrollbar(history_frame, orient=HORIZONTAL)
        
        self.bill_history = ttk.Treeview(history_frame, columns=("invoice", "date", "customer", "contact", "vehicle", "model", "total"), 
                                       yscrollcommand=scroll_y3.set, xscrollcommand=scroll_x3.set)
        
        scroll_y3.pack(side=RIGHT, fill=Y)
        scroll_x3.pack(side=BOTTOM, fill=X)
        
        scroll_y3.config(command=self.bill_history.yview)
        scroll_x3.config(command=self.bill_history.xview)
        
        self.bill_history.heading("invoice", text="Invoice No.")
        self.bill_history.heading("date", text="Date")
        self.bill_history.heading("customer", text="Customer")
        self.bill_history.heading("contact", text="Contact")
        self.bill_history.heading("vehicle", text="Vehicle No.")
        self.bill_history.heading("model", text="Model")
        self.bill_history.heading("total", text="Total")
        
        self.bill_history["show"] = "headings"
        
        self.bill_history.column("invoice", width=100)
        self.bill_history.column("date", width=100)
        self.bill_history.column("customer", width=150)
        self.bill_history.column("contact", width=100)
        self.bill_history.column("vehicle", width=100)
        self.bill_history.column("model", width=100)
        self.bill_history.column("total", width=100)
        
        self.bill_history.pack(fill=BOTH, expand=1)
        
        self.bill_history.bind("<Double-1>", self.load_bill_details)
        # Load initial data
        self.show_all_bills()
        
        #create double click loading of the customer and vehicle details also the billing details


    def load_bill_details(self, event=None):
        selected = self.bill_history.focus()

        if not selected:
            return

        data = self.bill_history.item(selected)["values"]

        invoice_no = data[0]

        try:
            # Get bill information
            query = """
            SELECT b.invoice_no,
                b.bill_date,
                c.customer_name,
                c.contact,
                COALESCE(v.vehicle_number,''),
                COALESCE(v.vehicle_model,'')
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.invoice_no = ?
            """

            result = self.execute_query(query, (invoice_no,), fetch=True)

            if result:
                bill = result[0]

                self.var_invoice.set(bill[0])
                self.var_service_date.set(bill[1])
                self.var_customer_name.set(bill[2])
                self.var_contact.set(bill[3])
                self.var_vehicle_no.set(bill[4])
                self.var_vehicle_model.set(bill[5])

            # Clear existing cart
            self.cart_table.delete(*self.cart_table.get_children())

            # Load bill items
            item_query = """
            SELECT bi.service_id,
                s.service_name,
                bi.price,
                bi.quantity,
                bi.total
            FROM bill_items bi
            JOIN services s ON bi.service_id = s.service_id
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE b.invoice_no = ?
            """

            items = self.execute_query(item_query, (invoice_no,), fetch=True)

            if items:
                for i, item in enumerate(items, 1):
                    self.cart_table.insert(
                        "",
                        END,
                        values=(
                            i,
                            item[0],  # service_id
                            item[1],  # service_name
                            item[2],  # price
                            item[3],  # qty
                            item[4]   # total
                        )
                    )

            self.calculate_total()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unable to load bill details\n{str(e)}",
                parent=self.root
            )



    def resize_service_columns(self, event=None):
        total_width = self.service_table.winfo_width()

        self.service_table.column("sr", width=int(total_width * 0.10))
        self.service_table.column("sid", width=int(total_width * 0.10))
        self.service_table.column("service", width=int(total_width * 0.55))
        self.service_table.column("price", width=int(total_width * 0.25))


    def on_close(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
            if self.connection:
                self.connection.close()
            self.root.destroy()
                    
    def create_db_connection(self):
        try:
            connection = sqlite3.connect("billing.db")
            return connection
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to SQLite Database: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and return results if fetch is True"""
        try:
            if self.connection is None:
                self.connection = self.create_db_connection()

            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error executing query: {e}")
            return None

    
    def generate_invoice(self):

        """Generate a unique invoice number"""
        try:
            # Get the last invoice number from database
            query = "SELECT invoice_no FROM bills ORDER BY bill_id DESC LIMIT 1"
            result = self.execute_query(query, fetch=True)

            if result:
                last_invoice = result[0][0]
                parts = last_invoice.split('-')
                if len(parts) == 3 and parts[2].isdigit():
                    num = int(parts[2]) + 1
                    new_invoice = f"{parts[0]}-{parts[1]}-{num:03d}"
                else:
                    new_invoice = f"INV-{datetime.now().strftime('%d%m%Y')}-001"
            else:
                new_invoice = f"INV-{datetime.now().strftime('%d%m%Y')}-001"

            self.var_invoice.set(new_invoice)

        except Exception as e:
            messagebox.showerror("Error", f"Error generating invoice: {str(e)}")
            self.var_invoice.set(f"INV-{datetime.now().strftime('%d%m%Y')}-001")

    def load_services(self):
        """Load services from database"""
        try:
            query = "SELECT service_id, service_name, service_price FROM services WHERE is_active = 1"
            services = self.execute_query(query, fetch=True)

            if services:
                self.service_table.delete(*self.service_table.get_children())
                for i, service in enumerate(services, 1):
                    self.service_table.insert("", END, values=(i, service[0], service[1], service[2]))
            else:
                messagebox.showwarning("Warning", "No active services found in database", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading services: {str(e)}", parent=self.root)
    
    def add_to_cart(self, event=None):
        """Add selected service to cart"""
        selected_item = self.service_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a service first", parent=self.root)
            return
            
        item_data = self.service_table.item(selected_item)
        item_values = item_data['values']
        
        # Check if already in cart
        for child in self.cart_table.get_children():
            cart_item = self.cart_table.item(child)['values']
            if cart_item[1] == item_values[1]:  # Compare service IDs
                messagebox.showwarning("Warning", "This service is already in the cart", parent=self.root)
                return
                
        # Add to cart with default quantity 1
        sr_no = len(self.cart_table.get_children()) + 1
        self.cart_table.insert("", END, values=(sr_no, item_values[1], item_values[2], item_values[3], 1, item_values[3]))
        self.calculate_total()
        
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selected_item = self.cart_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to remove", parent=self.root)
            return
            
        self.cart_table.delete(selected_item)
        
        # Update serial numbers after removal
        for i, child in enumerate(self.cart_table.get_children(), 1):
            item_values = list(self.cart_table.item(child)['values'])
            item_values[0] = i  # Update serial number
            self.cart_table.item(child, values=item_values)
        
        self.calculate_total()
        
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_table.delete(*self.cart_table.get_children())
        self.calculate_total()
        
    def increase_quantity(self):
        """Increase quantity of selected item in cart"""
        selected_item = self.cart_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item first", parent=self.root)
            return
            
        item_data = self.cart_table.item(selected_item)
        item_values = list(item_data['values'])
        
        # Increase quantity
        item_values[4] += 1  # qty
        item_values[5] = float(item_values[3]) * int(item_values[4])
        
        # Update the row
        self.cart_table.item(selected_item, values=item_values)
        self.calculate_total()

    def decrease_quantity(self):
        """Decrease quantity of selected item in cart"""
        selected_item = self.cart_table.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item first", parent=self.root)
            return
            
        item_data = self.cart_table.item(selected_item)
        item_values = list(item_data['values'])
        
        # Decrease quantity but not below 1
        if item_values[4] > 1:
            item_values[4] -= 1  # qty
            item_values[5] = float(item_values[3]) * int(item_values[4])
            
            # Update the row
            self.cart_table.item(selected_item, values=item_values)
            self.calculate_total()
    
    def calculate_total(self):
        """Calculate subtotal, tax, and grand total"""
        subtotal = 0
        for child in self.cart_table.get_children():
            item = self.cart_table.item(child)['values']
            subtotal += float(item[5])  # Total for each item
            
      #  tax = subtotal * 0.05  # 5% tax
        grand_total = subtotal 
        
        self.lbl_subtotal.config(text=f"Sub Total: {subtotal:.2f}")
      #  self.lbl_tax.config(text=f"Tax (5%): {tax:.2f}")
        self.lbl_grandtotal.config(text=f"Grand Total: {grand_total:.2f}")
        
            
           
    def create_pdf_bill(self):
        """Create PDF invoice file"""
        # Create bills directory if not exists
        if not os.path.exists("bills"):
            os.makedirs("bills")
            
        # PDF filename
        pdf_filename = f"bills/{self.var_invoice.get()}.pdf"
        
        # Create PDF
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        
        # Header
        from reportlab.lib.pagesizes import A4

        # Get page width and height
        page_width, page_height = A4  

        # Header
        c.setFont("Times-Bold", 16)
        c.drawCentredString(page_width/2, 740, "ALI SALEH AL-JERYAN CAR MAINTENANCE WORKSHOP")

        c.setFont("Times-Roman", 11)
        c.drawCentredString(page_width/2, 725, "Rikas Sanaya Al Thuqbha Al Khobar Ash Sharqiyah Saudi Arabia | +966 539487113")

                
            # y-coordinate for heading
        y = 680
        z = 640
        page_width, page_height = A4

        if self.var_bill_type.get() == "invoice":
            c.setFont("Times-Bold", 18)
            c.drawCentredString(page_width/2, y, "INVOICE")
            c.setFont("Times-Roman", 12)
            c.drawString(50, z, f"{self.var_invoice.get()}")
        elif self.var_bill_type.get() == "quotation":
            c.setFont("Times-Bold", 18)
            c.drawCentredString(page_width/2, y, "QUOTATION")
            c.setFont("Times-Roman", 12)   # 🔹 add this line so date is not bold



        c.drawString(50, 620, f"Date: {self.var_service_date.get()}")
        label_x = 50        # start of label
        colon_x = 130       # fixed position for all colons
        value_x = 140       # start of value (right after colon)
        line_height = 20

        c.setFont("Times-Bold", 14)
        c.drawString(label_x, 520, "Customer Details")

        c.setFont("Times-Roman", 12)
        c.drawString(label_x, 500, "Name")
        c.drawString(colon_x, 500, ":")
        c.drawString(value_x, 500, f"{self.var_customer_name.get()}")

        c.drawString(label_x, 480, "Contact")
        c.drawString(colon_x, 480, ":")
        c.drawString(value_x, 480, f"{self.var_contact.get()}")

        c.drawString(label_x, 460, "Vehicle No")
        c.drawString(colon_x, 460, ":")
        c.drawString(value_x, 460, f"{self.var_vehicle_no.get()}")

        c.drawString(label_x, 440, "Vehicle Model")
        c.drawString(colon_x, 440, ":")
        c.drawString(value_x, 440, f"{self.var_vehicle_model.get()}")


        # Add logo image (PNG)
        try:
            img_path = resource_path("assets/car.png")  # Use dynamic path for .exe
            c.drawImage(img_path, 350, 540, width=250, height=80) 
     
 

        except:
            pass  # If image not found or error occurs, skip it silently

        
        
        # Start position for bill items section (adjust this to move whole section up/down)
        y_position = 400 

        # Bill items header background (black rectangle)
        c.setFillColorRGB(0, 0, 0)  # Black fill
        c.rect(40, y_position, 520, 20, fill=1, stroke=0)

        # Bill items header text (white color)
        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position + 5, "Sl.No")
        c.drawString(220, y_position + 5, "Service")
        c.drawString(400, y_position + 5, "Qty")
        c.drawString(450, y_position + 5, "Price")
        c.drawString(500, y_position + 5, "Total")

        # Reset text color back to black
        c.setFillColorRGB(0, 0, 0)

        # Move y_position down for the items (so items print below header)
        y_position -= 30

        
                ## Bill items
        y_position = 380
        subtotal = 0
        c.setFont("Times-Roman", 12)
        max_service_width = 300  # Adjust this value as needed
        line_height = 15  # Space between wrapped lines

        for i, child in enumerate(self.cart_table.get_children(), 1):
            item = self.cart_table.item(child)['values']
            
            # Draw serial number
            c.drawString(50, y_position, str(i))
            
            # Service name with text wrapping - REPLACE THIS SECTION
            service_text = item[2]
            words = service_text.split()
            current_line = ""
            lines = []
            
            for word in words:
                test_line = current_line + word + " "
                if c.stringWidth(test_line, "Times-Roman", 12) <= max_service_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)
            
            # Draw each line of service description
            for j, line in enumerate(lines):
                c.drawString(100, y_position - (j * line_height), line)
            
            # Draw other columns aligned with first line
            c.drawString(400, y_position, str(item[4]))  # Qty
            c.drawString(450, y_position, f"{float(item[3]):.2f}")  # Price
            c.drawString(500, y_position, f"{float(item[5]):.2f}")  # Total
            
            # Move y_position down for next item (based on number of lines)
            y_position -= max(line_height * len(lines), 20)  # Use at least 20 units spacing
            subtotal += float(item[5])
            
        # Totals
       # tax = subtotal * 0.05
        grand_total = subtotal 
        
# Horizontal line
        c.line(50, y_position-10, 550, y_position-10)       
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y_position - 30, "Sub Total:")
        c.drawString(500, y_position - 30, f"{subtotal:.2f}")
        from reportlab.lib import colors

        # Coordinates and dimensions
        rect_x = 380  # left edge of rectangle
        rect_y = y_position - 82  # bottom edge of rectangle
        rect_width = 180  # width of rectangle
        rect_height = 24  # height of rectangle

        # Draw light grey rectangle
        c.setFillColorRGB(0.9, 0.9, 0.9)  # light grey
        c.rect(rect_x, rect_y, rect_width, rect_height, fill=1, stroke=0)

        # Set text color back to black
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)

        # Draw Grand Total text on top
        c.drawString(390, y_position - 70, "Grand Total:")
        c.drawString(470, y_position - 70, "SAR")
        c.drawString(500, y_position - 70, f"{grand_total:.2f}")


        
        from reportlab.lib.pagesizes import A4
        page_width, page_height = A4

        # Footer (fixed position at bottom)
        c.setFont("Times-Roman", 11)
        c.drawString(50, 80, "Note:")
        c.drawString(50, 60, "Thanks for your business")
      #  c.drawString(50, 40, "For any inquiries, please contact: +966 539487113")

        
        # Save PDF
        c.save()
        
    def clear_for_next_bill(self):
        """Clear fields for next bill"""
        self.generate_invoice()
        self.var_customer_name.set("")
        self.var_contact.set("")
        self.var_vehicle_no.set("")
        self.var_vehicle_model.set("")
        self.clear_cart()
        
    def search_bill(self):
        """Search bills based on criteria"""
        if self.var_search_by.get() == "Select":
            messagebox.showerror("Error", "Please select search criteria", parent=self.root)
            return
        if self.var_search_txt.get() == "":
            messagebox.showerror("Error", "Search input is required", parent=self.root)
            return
            
        search_column = ""
        if self.var_search_by.get() == "Invoice No.":
            search_column = "b.invoice_no"
        elif self.var_search_by.get() == "Customer Name":
            search_column = "c.customer_name"
        elif self.var_search_by.get() == "Contact":
            search_column = "c.contact"
        elif self.var_search_by.get() == "Vehicle No.":
            search_column = "v.vehicle_number"
        elif self.var_search_by.get() == "Model":
            search_column = "v.vehicle_model"
            
        try:
            query = f"""
            SELECT b.invoice_no,
                b.bill_date,
                c.customer_name,
                c.contact,
                COALESCE(v.vehicle_number,'N/A'),
                COALESCE(v.vehicle_model,'N/A'),
                b.total_amount
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE {search_column} LIKE ?
            ORDER BY b.bill_date DESC
            """
            
            search_param = f"%{self.var_search_txt.get()}%"
            bills = self.execute_query(query, (search_param,), fetch=True)
            
            if bills:
                self.bill_history.delete(*self.bill_history.get_children())
                for bill in bills:
                    self.bill_history.insert("", END, values=bill)
            else:
                messagebox.showinfo("Info", "No matching bills found", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error searching bills: {str(e)}", parent=self.root)
 
 
    def generate_bill(self):
        """Generate and save the bill to database and create PDF"""
        # Confirm before generating bill
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to generate this bill?", parent=self.root)
        if not confirm:
            self.generate_invoice()  # regenerate fresh invoice if canceled
            return

        # Validate inputs
        if not self.var_customer_name.get():
            messagebox.showerror("Error", "Customer Name is required", parent=self.root)
            return
        if not self.var_contact.get():
            messagebox.showerror("Error", "Contact Number is required", parent=self.root)
            return
        if len(self.cart_table.get_children()) == 0:
            messagebox.showerror("Error", "Please add services to the cart", parent=self.root)
            return

        try:
            # Calculate totals
            subtotal = 0
            for child in self.cart_table.get_children():
                item = self.cart_table.item(child)['values']
                subtotal += float(item[5])

          #  tax = subtotal * 0.05
            grand_total = subtotal 

            # Save customer (check if exists)
            customer_query = "SELECT customer_id FROM customers WHERE contact = ?"
            customer_result = self.execute_query(customer_query, (self.var_contact.get(),), fetch=True)

            if customer_result:
                customer_id = customer_result[0][0]
                update_customer_query = "UPDATE customers SET customer_name = ? WHERE contact = ?"
                self.execute_query(update_customer_query, (self.var_customer_name.get(), self.var_contact.get()))
            else:
                insert_customer = "INSERT INTO customers (customer_name, contact) VALUES (?, ?)"
                self.execute_query(insert_customer, (self.var_customer_name.get(), self.var_contact.get()))
                customer_result = self.execute_query(customer_query, (self.var_contact.get(),), fetch=True)
                customer_id = customer_result[0][0]

            # Save or update vehicle
            if self.var_vehicle_no.get():
                vehicle_check = "SELECT vehicle_id FROM vehicles WHERE vehicle_number = ?"
                vehicle_result = self.execute_query(vehicle_check, (self.var_vehicle_no.get(),), fetch=True)

                if vehicle_result:
                    update_vehicle = "UPDATE vehicles SET vehicle_model = ? WHERE vehicle_number = ?"
                    self.execute_query(update_vehicle, (self.var_vehicle_model.get(), self.var_vehicle_no.get()))
                    vehicle_id = vehicle_result[0][0]
                else:
                    insert_vehicle = "INSERT INTO vehicles (customer_id, vehicle_number, vehicle_model) VALUES (?, ?, ?)"
                    self.execute_query(insert_vehicle, (customer_id, self.var_vehicle_no.get(), self.var_vehicle_model.get()))
                    vehicle_result = self.execute_query(vehicle_check, (self.var_vehicle_no.get(),), fetch=True)
                    vehicle_id = vehicle_result[0][0]
            else:
                vehicle_id = None
                

            # Save bill
            insert_bill = """INSERT INTO bills 
                (invoice_no, customer_id, vehicle_id, bill_date, subtotal, total_amount, payment_status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.execute_query(insert_bill, (
                self.var_invoice.get(),
                customer_id,
                vehicle_id,
                self.var_service_date.get(),
                subtotal,
             #   tax,
                grand_total,
                'Paid'
            ))

            # Get bill ID
            bill_id_query = "SELECT bill_id FROM bills WHERE invoice_no = ?"
            bill_id_result = self.execute_query(bill_id_query, (self.var_invoice.get(),), fetch=True)
            if not bill_id_result:
                messagebox.showerror("Error", "Failed to get bill ID", parent=self.root)
                return
            bill_id = bill_id_result[0][0]

            # Save bill items
            for child in self.cart_table.get_children():
                item = self.cart_table.item(child)['values']
                insert_item = """INSERT INTO bill_items (bill_id, service_id, quantity, price, total) 
                                VALUES (?, ?, ?, ?, ?)"""
                self.execute_query(insert_item, (
                    bill_id,
                    item[1],  # service_id
                    item[4],  # quantity
                    item[3],  # price
                    item[5]   # total
                ))

            # Create PDF bill
            # Create PDF bill (with invoice/quotation toggle)
            self.create_pdf_bill()

            # Show success
            messagebox.showinfo("Success", f"Bill generated successfully\nInvoice: {self.var_invoice.get()}", parent=self.root)

            # Refresh & clear
            self.show_all_bills()
            self.clear_for_next_bill()

        except Exception as ex:
            self.generate_invoice()  # Prevent reuse of same invoice if error
            messagebox.showerror("Error", f"Error generating bill: {str(ex)}", parent=self.root)
                    
    def show_all_bills(self):
        """Show all bills from database"""
        try:
            query = """SELECT b.invoice_no, b.bill_date, c.customer_name, c.contact,
                    COALESCE(v.vehicle_number, 'N/A'),
                    COALESCE(v.vehicle_model, 'N/A'),
                    b.total_amount
                    FROM bills b
                    JOIN customers c ON b.customer_id = c.customer_id
                    LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                    ORDER BY b.bill_date DESC"""
            
            bills = self.execute_query(query, fetch=True)
            
            if bills:
                self.bill_history.delete(*self.bill_history.get_children())
                for bill in bills:
                    self.bill_history.insert("", END, values=bill)
            else:
                messagebox.showinfo("Info", "No bills found in database", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading bills: {str(e)}", parent=self.root)


    def add_custom_service(self):
        name = self.entry_custom_service.get()
        price = self.entry_custom_price.get()
        qty = self.entry_custom_qty.get()

        if name == "" or price == "" or qty == "":
            messagebox.showerror("Error", "Please fill all fields", parent=self.root)
            return

        try:
            price = float(price)
            qty = int(qty)
            total = price * qty

            # If checkbox checked, save to DB
            if self.save_to_db.get() == 1:
                insert_query = "INSERT INTO services (service_name, service_price, is_active) VALUES (?, ?, ?)"
                self.execute_query(insert_query, (name, price, 1))

                # Get inserted ID
                get_id_query = "SELECT service_id FROM services WHERE service_name = ? ORDER BY service_id DESC LIMIT 1"
                result = self.execute_query(get_id_query, (name,), fetch=True)
                service_id = result[0][0]
            else:
                messagebox.showerror("Error", "Custom services must be saved to DB (check 'Save to DB')", parent=self.root)
                return


            # Add to cart
            sr_no = len(self.cart_table.get_children()) + 1
            self.cart_table.insert("", END, values=(sr_no, service_id, name, price, qty, total))
            self.calculate_total()

            self.entry_custom_service.delete(0, END)
            self.entry_custom_price.delete(0, END)
            self.entry_custom_qty.delete(0, END)

            if self.save_to_db.get() == 1:
                self.load_services()
                messagebox.showinfo("Saved", "Service saved to database!", parent=self.root)

        except:
            messagebox.showerror("Error", "Invalid price or quantity", parent=self.root)
            
            
            
    def fill_service_fields(self, event):
        selected = self.service_table.focus()
        if selected:
            data = self.service_table.item(selected)["values"]
            self.entry_custom_service.delete(0, END)
            self.entry_custom_service.insert(0, data[2])

            self.entry_custom_price.delete(0, END)
            self.entry_custom_price.insert(0, data[3])
    def delete_service(self):
        selected = self.service_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select a service to delete", parent=self.root)
            return

        data = self.service_table.item(selected)["values"]
        service_id = data[1]

        try:
            # Check if the service is used in any previous bills
            query_check = "SELECT COUNT(*) FROM bill_items WHERE service_id = ?"
            result = self.execute_query(query_check, (service_id,), fetch=True)
            count = result[0][0]
        
            if count > 0:
                messagebox.showwarning("Warning", "Cannot delete service. It is used in previous bills.", parent=self.root)
                return

            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this service?", parent=self.root)
            if confirm:
                delete_query = "DELETE FROM services WHERE service_id = ?"
                self.execute_query(delete_query, (service_id,))
                self.load_services()
                messagebox.showinfo("Deleted", "Service deleted successfully!", parent=self.root)

        except Exception as e:
            messagebox.showerror("Error", f"Error deleting service: {str(e)}", parent=self.root)



    def update_service(self):
        selected = self.service_table.focus()
        if not selected:
            messagebox.showerror("Error", "Select a service to update", parent=self.root)
            return

        data = self.service_table.item(selected)["values"]
        service_id = data[1]

        name = self.entry_custom_service.get()
        price = self.entry_custom_price.get()

        if name == "" or price == "":
            messagebox.showerror("Error", "Name and price required", parent=self.root)
            return

        try:
            price = float(price)
            query = "UPDATE services SET service_name = ?, service_price = ? WHERE service_id = ?"
            self.execute_query(query, (name, price, service_id))
            self.load_services()
            messagebox.showinfo("Updated", "Service updated", parent=self.root)
        except:
            messagebox.showerror("Error", "Invalid price", parent=self.root)


    
#########################################datbase scherma############################################################

    def initialize_database(self):
        """Create all required tables for billing system"""
        create_tables_query = """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            contact TEXT UNIQUE NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            vehicle_number TEXT UNIQUE,
            vehicle_model TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            service_price REAL NOT NULL,
            is_active INTEGER DEFAULT 1
        );
        
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            vehicle_id INTEGER,
            bill_date TEXT,
            subtotal REAL,
            total_amount REAL,
            payment_status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        );
        
        CREATE TABLE IF NOT EXISTS bill_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            service_id INTEGER,
            quantity INTEGER,
            price REAL,
            total REAL,
            FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
            FOREIGN KEY (service_id) REFERENCES services(service_id)
        );
        """
        try:
            cursor = self.connection.cursor()
            cursor.executescript(create_tables_query)
            self.connection.commit()
            cursor.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error initializing database: {e}")





if __name__ == "__main__":
    root = Tk()
    obj = billingClass(root)
    root.mainloop()