import customtkinter as ctk
from tkinter import messagebox
from mongodb import cars_collection, rentals_collection
from admin.car_management import CarManagementFrame 
from admin.rental_approvals import RentalApprovalsFrame
from admin.finances_frame import FinancesFrame 
from admin.customers_frame import CustomersFrame

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master)
        self.on_logout = on_logout

        # --- Sidebar Layout ---
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar, 
            text="VROOMIFY ADMIN PANEL", 
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        # Navigation menu entries
        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_stats).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Cars", command=self.show_cars_section).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Customers", command=self.show_customers).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Rentals", command=self.show_rentals_section).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Finances", command=self.show_finances).pack(pady=10, padx=20)

        ctk.CTkButton(
            self.sidebar, 
            text="Logout", 
            fg_color="#922B21", 
            hover_color="#641E16",
            command=self.logout
        ).pack(pady=30, padx=20)

        # --- Main Layout Canvas ---
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_stats()

    def clear_main_area(self):
        """Removes the current frame before loading a new one"""
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_stats(self):
        """Displays interactive KPI summary cards and lists recent transactions"""
        self.clear_main_area()
        
        ctk.CTkLabel(self.main, text="System Overview", font=("Arial", 28, "bold")).pack(pady=(10, 20), anchor="w", padx=20)

        # Live data aggregation from MongoDB
        total_cars = cars_collection.count_documents({})
        available_cars = cars_collection.count_documents({"status": "Available"})
        rented_cars = cars_collection.count_documents({"status": "Rented"})
        pending_requests = rentals_collection.count_documents({"status": "Pending"})

        # KPI dashboard layout layout frame
        stats_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        stats_frame.pack(pady=(0, 25), fill="x", padx=10)
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        # --- CLICKABLE KPI CARDS ---
        ctk.CTkButton(
            stats_frame, text=f"Total Fleet\n\n{total_cars}", font=("Arial", 14, "bold"),
            width=160, height=100, fg_color="gray25", hover_color="gray30", corner_radius=10,
            command=self.show_cars_section
        ).grid(row=0, column=0, padx=10, sticky="nsew")

        ctk.CTkButton(
            stats_frame, text=f"Available\n\n{available_cars}", font=("Arial", 14, "bold"),
            width=160, height=100, fg_color="#239B56", hover_color="#1E8449", corner_radius=10,
            command=self.show_cars_section
        ).grid(row=0, column=1, padx=10, sticky="nsew")

        ctk.CTkButton(
            stats_frame, text=f"Active Rentals\n\n{rented_cars}", font=("Arial", 14, "bold"),
            width=160, height=100, fg_color="#2E86C1", hover_color="#2471A3", corner_radius=10,
            command=self.show_rentals_section
        ).grid(row=0, column=2, padx=10, sticky="nsew")

        ctk.CTkButton(
            stats_frame, text=f"Pending Requests\n\n{pending_requests}", font=("Arial", 14, "bold"),
            width=160, height=100, fg_color="#D35400", hover_color="#BA4A00", corner_radius=10,
            command=self.show_rentals_section
        ).grid(row=0, column=3, padx=10, sticky="nsew")

        # --- RECENT RENTALS SECTION ---
        ctk.CTkLabel(self.main, text="Recent Activity Logs", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        table_background = ctk.CTkFrame(self.main, fg_color=("#EAECEE", "#242424"), corner_radius=8, border_width=1, border_color="#333333")
        table_background.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        # Scrollable container for logs data rows
        scroll_table = ctk.CTkScrollableFrame(table_background, fg_color="transparent")
        scroll_table.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_table.columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Set up log table headers
        headers = ["Customer", "Vehicle Model", "Duration", "Total Price", "Status"]
        for col_idx, text in enumerate(headers):
            ctk.CTkLabel(scroll_table, text=text, font=("Arial", 12, "bold"), text_color="#888888").grid(row=0, column=col_idx, pady=10, padx=10, sticky="w")

        # Fetch recent rentals tracking down from newest timestamp
        recent_rentals = list(rentals_collection.find().sort("booking_date", -1).limit(15))

        if not recent_rentals:
            ctk.CTkLabel(scroll_table, text="No transactional history found.", font=("Arial", 14, "italic")).grid(row=1, column=0, columnspan=5, pady=40)
            return

        # Populate transaction rows dynamically
        for row_idx, rental in enumerate(recent_rentals, start=1):
            user = rental.get("username", "Unknown User")
            vehicle = f"{rental.get('brand', '')} {rental.get('model', 'Vehicle')}".strip()
            days = f"{rental.get('days', 0)} Days"
            price = f"KES {float(rental.get('total_price', 0)):,.2f}"
            status = str(rental.get("status", "Pending"))

            # Status colors assignment map
            status_colors = {"Completed": "#239B56", "Pending": "#D35400", "Approved": "#2E86C1", "Rejected": "#922B21"}
            current_status_color = status_colors.get(status, "#AAAAAA")

            # Grid labels cleanly across text columns
            ctk.CTkLabel(scroll_table, text=user, font=("Arial", 13, "bold")).grid(row=row_idx, column=0, pady=8, padx=10, sticky="w")
            ctk.CTkLabel(scroll_table, text=vehicle, font=("Arial", 13)).grid(row=row_idx, column=1, pady=8, padx=10, sticky="w")
            ctk.CTkLabel(scroll_table, text=days, font=("Arial", 13)).grid(row=row_idx, column=2, pady=8, padx=10, sticky="w")
            ctk.CTkLabel(scroll_table, text=price, font=("Arial", 13, "bold")).grid(row=row_idx, column=3, pady=8, padx=10, sticky="w")
            ctk.CTkLabel(scroll_table, text=status, font=("Arial", 12, "bold"), text_color=current_status_color).grid(row=row_idx, column=4, pady=8, padx=10, sticky="w")

    def show_cars_section(self):
        """Switches main frame to the fleet management view"""
        self.clear_main_area()
        car_section = CarManagementFrame(self.main)
        car_section.pack(fill="both", expand=True)

    def show_rentals_section(self):
        """Switches main frame to the rental routing approvals table"""
        self.clear_main_area()
        rental_section = RentalApprovalsFrame(self.main)
        rental_section.pack(fill="both", expand=True)
        
    def show_finances(self):
        """Switches main frame to financial metric reporting view"""
        self.clear_main_area()
        FinancesFrame(self.main).pack(fill="both", expand=True)

    def show_customers(self):
        """Switches main frame to the customer directory view"""
        self.clear_main_area()
        CustomersFrame(self.main).pack(fill="both", expand=True)

    def logout(self):
        """Confirms logout action and executes callback script execution"""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.on_logout()