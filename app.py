import tkinter as tk
from tkinter import ttk, messagebox

from models.customer import Customer
from models.menu import Menu, FoodItem, DrinkItem, MenuItem
from models.order import Order, OrderStatus
from models.payment import CreditCardPayment, CashOnDelivery, EWalletPayment, PaymentProcessor
from models.delivery import StandardDelivery, ExpressDelivery, DeliveryAgent, Delivery
from models.transaction import Transaction, TransactionHistory


class FoodDeliveryApp(tk.Tk):
    def __init__(self, menu: Menu, customers: list[Customer], agents: list[DeliveryAgent]):
        super().__init__()
        self.title("Food Delivery System")
        self.geometry("950x700")
        self.minsize(850, 600)

        self.menu = menu
        self.customers = customers
        self.agents = agents
        self.orders: list[Order] = []
        self.active_order: Order | None = None
        self.active_delivery: Delivery | None = None
        self.transaction_history = TransactionHistory()
        self.order_counter = 1001
        self.customer_counter = len(customers) + 1
        self.tx_counter = 5001

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Tab 1: Menu & Ordering
        self.tab_order = ttk.Frame(notebook)
        notebook.add(self.tab_order, text="  Browse Menu & Order  ")
        self._build_ordering_tab()

        # Tab 2: Payment & Delivery
        self.tab_checkout = ttk.Frame(notebook)
        notebook.add(self.tab_checkout, text="  Payment & Delivery  ")
        self._build_checkout_tab()

        # Tab 3: Customer Management
        self.tab_customers = ttk.Frame(notebook)
        notebook.add(self.tab_customers, text="  Manage Customers  ")
        self._build_customer_tab()

        # Tab 4: Transaction History
        self.tab_history = ttk.Frame(notebook)
        notebook.add(self.tab_history, text="  Transaction History  ")
        self._build_history_tab()

    # ------------------ Tab 1: Ordering ------------------
    def _build_ordering_tab(self):
        top_frame = ttk.LabelFrame(self.tab_order, text="Customer Selection", padding=8)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top_frame, text="Select Customer:").pack(side=tk.LEFT, padx=5)
        self.cust_combobox = ttk.Combobox(top_frame, state="readonly", width=40)
        self.cust_combobox.pack(side=tk.LEFT, padx=5)
        self._refresh_customer_combobox()

        paned = ttk.PanedWindow(self.tab_order, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Menu
        menu_frame = ttk.LabelFrame(paned, text="Available Menu Items", padding=8)
        paned.add(menu_frame, weight=3)

        cols = ("id", "name", "category", "price", "details")
        self.menu_tree = ttk.Treeview(menu_frame, columns=cols, show="headings", height=12)
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Name")
        self.menu_tree.heading("category", text="Category")
        self.menu_tree.heading("price", text="Price")
        self.menu_tree.heading("details", text="Details")

        self.menu_tree.column("id", width=50, anchor=tk.CENTER)
        self.menu_tree.column("name", width=140)
        self.menu_tree.column("category", width=70, anchor=tk.CENTER)
        self.menu_tree.column("price", width=65, anchor=tk.E)
        self.menu_tree.column("details", width=220)
        self.menu_tree.pack(fill=tk.BOTH, expand=True)

        self._refresh_menu_tree()

        add_bar = ttk.Frame(menu_frame)
        add_bar.pack(fill=tk.X, pady=(6, 0))

        ttk.Label(add_bar, text="Qty:").pack(side=tk.LEFT, padx=2)
        self.qty_spin = ttk.Spinbox(add_bar, from_=1, to=20, width=4)
        self.qty_spin.set(1)
        self.qty_spin.pack(side=tk.LEFT, padx=3)

        ttk.Label(add_bar, text="Notes:").pack(side=tk.LEFT, padx=2)
        self.note_entry = ttk.Entry(add_bar, width=18)
        self.note_entry.pack(side=tk.LEFT, padx=3)

        ttk.Button(add_bar, text="Add to Cart", command=self._add_to_cart).pack(side=tk.RIGHT, padx=5)

        # Right: Cart
        cart_frame = ttk.LabelFrame(paned, text="Current Cart", padding=8)
        paned.add(cart_frame, weight=2)

        cart_cols = ("name", "qty", "price", "note")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_cols, show="headings", height=12)
        self.cart_tree.heading("name", text="Item")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("price", text="Subtotal")
        self.cart_tree.heading("note", text="Note")

        self.cart_tree.column("name", width=120)
        self.cart_tree.column("qty", width=45, anchor=tk.CENTER)
        self.cart_tree.column("price", width=65, anchor=tk.E)
        self.cart_tree.column("note", width=90)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        cart_btn_bar = ttk.Frame(cart_frame)
        cart_btn_bar.pack(fill=tk.X, pady=4)
        ttk.Button(cart_btn_bar, text="Remove Selected", command=self._remove_from_cart).pack(side=tk.LEFT)
        ttk.Button(cart_btn_bar, text="Clear Cart", command=self._clear_cart).pack(side=tk.LEFT, padx=5)

        self.lbl_cart_total = ttk.Label(cart_frame, text="Subtotal: $0.00 | Tax (5%): $0.00 | Total: $0.00", font=("Arial", 9, "bold"))
        self.lbl_cart_total.pack(pady=4)

        ttk.Button(cart_frame, text="Place Order -> Proceed to Payment", command=self._place_order).pack(fill=tk.X, pady=4)

        self.current_cart_items: list[tuple[MenuItem, int, str]] = []

    def _refresh_customer_combobox(self):
        options = [f"{c.customer_id} - {c.name} ({c.phone})" for c in self.customers]
        self.cust_combobox["values"] = options
        if options:
            self.cust_combobox.current(0)

    def _refresh_menu_tree(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        for item in self.menu.get_all_items():
            self.menu_tree.insert(
                "",
                tk.END,
                iid=item.item_id,
                values=(item.item_id, item.name, item.category, f"${item.price:.2f}", item.get_details()),
            )

    def _add_to_cart(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select a menu item from the list.")
            return

        item_id = selected[0]
        item = self.menu.get_item(item_id)
        if not item:
            return

        try:
            qty = int(self.qty_spin.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Please enter a valid positive quantity.")
            return

        note = self.note_entry.get().strip()
        self.current_cart_items.append((item, qty, note))
        self.note_entry.delete(0, tk.END)
        self.qty_spin.set(1)
        self._update_cart_display()

    def _remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(self.current_cart_items):
            self.current_cart_items.pop(idx)
            self._update_cart_display()

    def _clear_cart(self):
        self.current_cart_items.clear()
        self._update_cart_display()

    def _update_cart_display(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        subtotal = 0.0
        for idx, (item, qty, note) in enumerate(self.current_cart_items):
            cost = item.price * qty
            subtotal += cost
            self.cart_tree.insert("", tk.END, iid=str(idx), values=(item.name, qty, f"${cost:.2f}", note))

        tax = subtotal * 0.05
        total = subtotal + tax
        self.lbl_cart_total.config(text=f"Subtotal: ${subtotal:.2f} | Tax (5%): ${tax:.2f} | Total: ${total:.2f}")

    def _place_order(self):
        if not self.current_cart_items:
            messagebox.showwarning("Empty Cart", "Your cart is empty. Add some items first.")
            return

        cust_idx = self.cust_combobox.current()
        if cust_idx < 0:
            messagebox.showwarning("Select Customer", "Please select a customer.")
            return

        customer = self.customers[cust_idx]
        order_id = f"ORD-{self.order_counter}"
        self.order_counter += 1

        order = Order(order_id, customer)
        for item, qty, note in self.current_cart_items:
            order.add_item(item, qty, note)

        self.orders.append(order)
        self.active_order = order
        self.current_cart_items.clear()
        self._update_cart_display()

        self._refresh_checkout_orders()
        messagebox.showinfo("Order Created", f"Order {order_id} created for {customer.name}!\nProceed to Payment & Delivery.")

    # ------------------ Tab 2: Checkout & Delivery ------------------
    def _build_checkout_tab(self):
        container = ttk.PanedWindow(self.tab_checkout, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Left Column: Order Summary & Delivery
        left_box = ttk.Frame(container, padding=5)
        container.add(left_box, weight=1)

        sel_frame = ttk.LabelFrame(left_box, text="Select Pending Order", padding=6)
        sel_frame.pack(fill=tk.X, pady=4)
        self.order_combobox = ttk.Combobox(sel_frame, state="readonly")
        self.order_combobox.pack(fill=tk.X)
        self.order_combobox.bind("<<ComboboxSelected>>", self._on_order_selected)

        self.order_summary_txt = tk.Text(left_box, height=10, width=45, wrap=tk.WORD)
        self.order_summary_txt.pack(fill=tk.BOTH, expand=True, pady=4)
        self.order_summary_txt.config(state=tk.DISABLED)

        # Delivery Settings
        deliv_frame = ttk.LabelFrame(left_box, text="Delivery Options", padding=6)
        deliv_frame.pack(fill=tk.X, pady=4)

        self.deliv_type_var = tk.StringVar(value="Standard")
        ttk.Radiobutton(
            deliv_frame, text="Standard Delivery ($2.50 base + $0.75/km)", variable=self.deliv_type_var, value="Standard", command=self._recalculate_total
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            deliv_frame, text="Express Delivery ($5.00 base + $1.25/km)", variable=self.deliv_type_var, value="Express", command=self._recalculate_total
        ).pack(anchor=tk.W)

        dist_bar = ttk.Frame(deliv_frame)
        dist_bar.pack(fill=tk.X, pady=3)
        ttk.Label(dist_bar, text="Distance (km):").pack(side=tk.LEFT)
        self.dist_entry = ttk.Entry(dist_bar, width=8)
        self.dist_entry.insert(0, "3.5")
        self.dist_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(dist_bar, text="Update Fee", command=self._recalculate_total).pack(side=tk.LEFT)

        agent_bar = ttk.Frame(deliv_frame)
        agent_bar.pack(fill=tk.X, pady=3)
        ttk.Label(agent_bar, text="Assign Courier:").pack(side=tk.LEFT)
        self.agent_combobox = ttk.Combobox(agent_bar, state="readonly", width=25)
        self.agent_combobox["values"] = [f"{a.name} ({a.vehicle_type})" for a in self.agents]
        if self.agents:
            self.agent_combobox.current(0)
        self.agent_combobox.pack(side=tk.LEFT, padx=5)

        # Right Column: Payment & Dispatch
        right_box = ttk.Frame(container, padding=5)
        container.add(right_box, weight=1)

        pay_frame = ttk.LabelFrame(right_box, text="Payment Method", padding=8)
        pay_frame.pack(fill=tk.X, pady=4)

        self.pay_method_var = tk.StringVar(value="Card")
        ttk.Radiobutton(pay_frame, text="Credit / Debit Card", variable=self.pay_method_var, value="Card", command=self._toggle_pay_fields).pack(anchor=tk.W)
        ttk.Radiobutton(pay_frame, text="Cash on Delivery", variable=self.pay_method_var, value="Cash", command=self._toggle_pay_fields).pack(anchor=tk.W)
        ttk.Radiobutton(pay_frame, text="E-Wallet", variable=self.pay_method_var, value="Wallet", command=self._toggle_pay_fields).pack(anchor=tk.W)

        # Method specific input frame
        self.pay_fields_frame = ttk.Frame(pay_frame)
        self.pay_fields_frame.pack(fill=tk.X, pady=6)
        self._build_payment_inputs()

        self.lbl_pay_total = ttk.Label(right_box, text="Final Payable Amount: $0.00", font=("Arial", 11, "bold"))
        self.lbl_pay_total.pack(pady=6)

        ttk.Button(right_box, text="Process Payment & Dispatch", command=self._process_payment_and_dispatch).pack(fill=tk.X, pady=4)

        # Live Tracker Box
        track_frame = ttk.LabelFrame(right_box, text="Order Tracking & Status Updates", padding=6)
        track_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        status_bar = ttk.Frame(track_frame)
        status_bar.pack(fill=tk.X, pady=2)
        ttk.Button(status_bar, text="Mark Preparing", command=lambda: self._advance_status("Preparing")).pack(side=tk.LEFT, padx=2)
        ttk.Button(status_bar, text="Out for Delivery", command=lambda: self._advance_status("Out for Delivery")).pack(side=tk.LEFT, padx=2)
        ttk.Button(status_bar, text="Mark Delivered", command=lambda: self._advance_status("Delivered")).pack(side=tk.LEFT, padx=2)

        self.tracking_txt = tk.Text(track_frame, height=9, width=45, wrap=tk.WORD)
        self.tracking_txt.pack(fill=tk.BOTH, expand=True, pady=4)
        self.tracking_txt.config(state=tk.DISABLED)

    def _build_payment_inputs(self):
        for child in self.pay_fields_frame.winfo_children():
            child.destroy()

        method = self.pay_method_var.get()
        if method == "Card":
            ttk.Label(self.pay_fields_frame, text="Cardholder Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.ent_card_name = ttk.Entry(self.pay_fields_frame, width=22)
            self.ent_card_name.insert(0, "Alice Smith")
            self.ent_card_name.grid(row=0, column=1, pady=2)

            ttk.Label(self.pay_fields_frame, text="Card Number (16-digits):").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.ent_card_num = ttk.Entry(self.pay_fields_frame, width=22)
            self.ent_card_num.insert(0, "4111222233334444")
            self.ent_card_num.grid(row=1, column=1, pady=2)

            ttk.Label(self.pay_fields_frame, text="Expiry (MM/YY):").grid(row=2, column=0, sticky=tk.W, pady=2)
            self.ent_card_exp = ttk.Entry(self.pay_fields_frame, width=22)
            self.ent_card_exp.insert(0, "11/28")
            self.ent_card_exp.grid(row=2, column=1, pady=2)

            ttk.Label(self.pay_fields_frame, text="CVV:").grid(row=3, column=0, sticky=tk.W, pady=2)
            self.ent_card_cvv = ttk.Entry(self.pay_fields_frame, width=22)
            self.ent_card_cvv.insert(0, "123")
            self.ent_card_cvv.grid(row=3, column=1, pady=2)

        elif method == "Cash":
            ttk.Label(self.pay_fields_frame, text="Amount Tendered ($):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.ent_cash = ttk.Entry(self.pay_fields_frame, width=18)
            self.ent_cash.insert(0, "50.00")
            self.ent_cash.grid(row=0, column=1, pady=2)

        elif method == "Wallet":
            ttk.Label(self.pay_fields_frame, text="Wallet Provider:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.cmb_wallet_provider = ttk.Combobox(self.pay_fields_frame, values=["GCash", "PayPal", "GrabPay"], state="readonly", width=16)
            self.cmb_wallet_provider.current(0)
            self.cmb_wallet_provider.grid(row=0, column=1, pady=2)

            ttk.Label(self.pay_fields_frame, text="Account Number:").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.ent_wallet_acc = ttk.Entry(self.pay_fields_frame, width=18)
            self.ent_wallet_acc.insert(0, "09171234567")
            self.ent_wallet_acc.grid(row=1, column=1, pady=2)

    def _toggle_pay_fields(self):
        self._build_payment_inputs()

    def _refresh_checkout_orders(self):
        values = [f"{o.order_id} - {o.customer.name} ({o.status.value})" for o in self.orders]
        self.order_combobox["values"] = values
        if values:
            self.order_combobox.current(len(values) - 1)
            self._on_order_selected(None)

    def _on_order_selected(self, event):
        idx = self.order_combobox.current()
        if idx < 0 or idx >= len(self.orders):
            return
        self.active_order = self.orders[idx]
        self._recalculate_total()

    def _get_selected_distance(self) -> float:
        try:
            return float(self.dist_entry.get())
        except ValueError:
            return 3.0

    def _create_delivery_instance(self, order: Order) -> Delivery:
        dist = self._get_selected_distance()
        deliv_id = f"DEL-{order.order_id[-4:]}"
        if self.deliv_type_var.get() == "Express":
            deliv = ExpressDelivery(deliv_id, order, distance_km=dist)
        else:
            deliv = StandardDelivery(deliv_id, order, distance_km=dist)

        agent_idx = self.agent_combobox.current()
        if agent_idx >= 0 and agent_idx < len(self.agents):
            deliv.assign_agent(self.agents[agent_idx])
        return deliv

    def _recalculate_total(self):
        if not self.active_order:
            return

        temp_deliv = self._create_delivery_instance(self.active_order)
        deliv_fee = temp_deliv.calculate_delivery_fee()
        final_total = self.active_order.get_total(delivery_fee=deliv_fee)

        self.order_summary_txt.config(state=tk.NORMAL)
        self.order_summary_txt.delete("1.0", tk.END)
        self.order_summary_txt.insert(tk.END, self.active_order.get_summary(delivery_fee=deliv_fee))
        self.order_summary_txt.config(state=tk.DISABLED)

        self.lbl_pay_total.config(text=f"Final Payable Amount: ${final_total:.2f}")

    def _process_payment_and_dispatch(self):
        if not self.active_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return

        if self.active_order.status not in (OrderStatus.PENDING, OrderStatus.CANCELLED):
            messagebox.showinfo("Already Paid", f"Order {self.active_order.order_id} is already {self.active_order.status.value}.")
            return

        delivery = self._create_delivery_instance(self.active_order)
        final_amount = self.active_order.get_total(delivery_fee=delivery.calculate_delivery_fee())

        # Construct polymorphic payment processor
        method = self.pay_method_var.get()
        processor: PaymentProcessor
        if method == "Card":
            processor = CreditCardPayment(
                card_number=self.ent_card_num.get(),
                card_holder=self.ent_card_name.get(),
                expiry_date=self.ent_card_exp.get(),
                cvv=self.ent_card_cvv.get(),
            )
        elif method == "Cash":
            try:
                tendered = float(self.ent_cash.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid cash amount.")
                return
            processor = CashOnDelivery(amount_tendered=tendered)
        else:
            processor = EWalletPayment(
                provider=self.cmb_wallet_provider.get(),
                account_number=self.ent_wallet_acc.get(),
                balance=500.0,
            )

        success, message = processor.process_payment(final_amount)
        if not success:
            messagebox.showerror("Payment Failed", message)
            return

        # Advance order and delivery state
        self.active_order.status = OrderStatus.PAID
        delivery.update_status("Preparing")
        self.active_delivery = delivery

        # Record completed transaction
        tx_id = f"TXN-{self.tx_counter}"
        self.tx_counter += 1
        tx = Transaction(tx_id, self.active_order, processor, delivery)
        self.transaction_history.record_transaction(tx)

        # Refresh UI displays
        self._update_tracking_view()
        self._refresh_history_tree()
        self._refresh_checkout_orders()

        messagebox.showinfo("Success", f"{message}\n\nTransaction ID: {tx_id}\nOrder dispatched for preparation.")

    def _advance_status(self, new_status: str):
        if not self.active_delivery:
            messagebox.showwarning("No Active Delivery", "No active delivery to update.")
            return

        self.active_delivery.update_status(new_status)
        self._update_tracking_view()
        self._refresh_checkout_orders()
        self._refresh_history_tree()

    def _update_tracking_view(self):
        if not self.active_delivery:
            return
        self.tracking_txt.config(state=tk.NORMAL)
        self.tracking_txt.delete("1.0", tk.END)
        self.tracking_txt.insert(tk.END, self.active_delivery.get_tracking_info())
        self.tracking_txt.config(state=tk.DISABLED)

    # ------------------ Tab 3: Customers ------------------
    def _build_customer_tab(self):
        paned = ttk.PanedWindow(self.tab_customers, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # List
        left_frame = ttk.LabelFrame(paned, text="Registered Customers", padding=6)
        paned.add(left_frame, weight=3)

        c_cols = ("id", "name", "phone", "address")
        self.cust_tree = ttk.Treeview(left_frame, columns=c_cols, show="headings", height=15)
        self.cust_tree.heading("id", text="ID")
        self.cust_tree.heading("name", text="Name")
        self.cust_tree.heading("phone", text="Phone")
        self.cust_tree.heading("address", text="Delivery Address")

        self.cust_tree.column("id", width=60, anchor=tk.CENTER)
        self.cust_tree.column("name", width=140)
        self.cust_tree.column("phone", width=110)
        self.cust_tree.column("address", width=220)
        self.cust_tree.pack(fill=tk.BOTH, expand=True)

        self._refresh_customer_tree()

        # Add Customer Form
        right_frame = ttk.LabelFrame(paned, text="Register New Customer", padding=10)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Full Name:").pack(anchor=tk.W, pady=2)
        self.new_cust_name = ttk.Entry(right_frame, width=30)
        self.new_cust_name.pack(fill=tk.X, pady=2)

        ttk.Label(right_frame, text="Phone Number:").pack(anchor=tk.W, pady=2)
        self.new_cust_phone = ttk.Entry(right_frame, width=30)
        self.new_cust_phone.pack(fill=tk.X, pady=2)

        ttk.Label(right_frame, text="Delivery Address:").pack(anchor=tk.W, pady=2)
        self.new_cust_addr = ttk.Entry(right_frame, width=30)
        self.new_cust_addr.pack(fill=tk.X, pady=2)

        ttk.Button(right_frame, text="Register Customer", command=self._add_customer).pack(fill=tk.X, pady=12)

    def _refresh_customer_tree(self):
        for row in self.cust_tree.get_children():
            self.cust_tree.delete(row)
        for c in self.customers:
            self.cust_tree.insert("", tk.END, values=(c.customer_id, c.name, c.phone, c.address))

    def _add_customer(self):
        name = self.new_cust_name.get().strip()
        phone = self.new_cust_phone.get().strip()
        addr = self.new_cust_addr.get().strip()

        if not name or not phone or not addr:
            messagebox.showwarning("Incomplete Form", "Please fill in all customer fields.")
            return

        cid = f"C{self.customer_counter:03d}"
        self.customer_counter += 1
        new_cust = Customer(cid, name, phone, addr)
        self.customers.append(new_cust)

        self.new_cust_name.delete(0, tk.END)
        self.new_cust_phone.delete(0, tk.END)
        self.new_cust_addr.delete(0, tk.END)

        self._refresh_customer_tree()
        self._refresh_customer_combobox()
        messagebox.showinfo("Success", f"Customer {name} ({cid}) registered successfully.")

    # ------------------ Tab 4: Transactions ------------------
    def _build_history_tab(self):
        paned = ttk.PanedWindow(self.tab_history, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left_frame = ttk.LabelFrame(paned, text="Completed Transactions", padding=6)
        paned.add(left_frame, weight=3)

        tx_cols = ("id", "order_id", "customer", "amount", "payment", "status")
        self.tx_tree = ttk.Treeview(left_frame, columns=tx_cols, show="headings", height=15)
        self.tx_tree.heading("id", text="Tx ID")
        self.tx_tree.heading("order_id", text="Order")
        self.tx_tree.heading("customer", text="Customer")
        self.tx_tree.heading("amount", text="Amount")
        self.tx_tree.heading("payment", text="Payment Method")
        self.tx_tree.heading("status", text="Delivery Status")

        self.tx_tree.column("id", width=80, anchor=tk.CENTER)
        self.tx_tree.column("order_id", width=80, anchor=tk.CENTER)
        self.tx_tree.column("customer", width=120)
        self.tx_tree.column("amount", width=80, anchor=tk.E)
        self.tx_tree.column("payment", width=150)
        self.tx_tree.column("status", width=110, anchor=tk.CENTER)
        self.tx_tree.pack(fill=tk.BOTH, expand=True)

        self.tx_tree.bind("<<TreeviewSelect>>", self._on_tx_selected)

        self.lbl_sales_summary = ttk.Label(left_frame, text="Total Revenue: $0.00 | Total Transactions: 0", font=("Arial", 10, "bold"))
        self.lbl_sales_summary.pack(pady=4)

        # Right: Receipt text view
        right_frame = ttk.LabelFrame(paned, text="Receipt Details", padding=6)
        paned.add(right_frame, weight=2)

        self.receipt_txt = tk.Text(right_frame, height=20, width=42, font=("Courier New", 9))
        self.receipt_txt.pack(fill=tk.BOTH, expand=True)
        self.receipt_txt.config(state=tk.DISABLED)

    def _refresh_history_tree(self):
        for row in self.tx_tree.get_children():
            self.tx_tree.delete(row)

        txs = self.transaction_history.get_all()
        for tx in txs:
            self.tx_tree.insert(
                "",
                tk.END,
                iid=tx.transaction_id,
                values=(
                    tx.transaction_id,
                    tx.order.order_id,
                    tx.order.customer.name,
                    f"${tx.total_amount:.2f}",
                    tx.payment.method_name,
                    tx.delivery.status,
                ),
            )

        total_sales = self.transaction_history.get_total_sales()
        self.lbl_sales_summary.config(text=f"Total Revenue: ${total_sales:.2f} | Total Transactions: {len(txs)}")

    def _on_tx_selected(self, event):
        selected = self.tx_tree.selection()
        if not selected:
            return
        tx_id = selected[0]
        tx = self.transaction_history.find_by_id(tx_id)
        if not tx:
            return

        self.receipt_txt.config(state=tk.NORMAL)
        self.receipt_txt.delete("1.0", tk.END)
        self.receipt_txt.insert(tk.END, tx.get_receipt())
        self.receipt_txt.config(state=tk.DISABLED)
