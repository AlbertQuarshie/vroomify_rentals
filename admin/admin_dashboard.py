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

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar, 
            text="ADMIN PANEL", 
            font=("Arial", 20, "bold")
        ).pack(pady=20)

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

       
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_stats()

    def clear_main_area(self):
        """Removes the current frame before loading a new one"""
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_stats(self):
        """Displays the high-level overview statistics cards"""
        self.clear_main_area()
        ctk.CTkLabel(self.main, text="System Overview", font=("Arial", 28, "bold")).pack(pady=20)

        # Live data aggregation from MongoDB
        total_cars = cars_collection.count_documents({})
        available_cars = cars_collection.count_documents({"status": "Available"})
        rented_cars = cars_collection.count_documents({"status": "Rented"})
        pending_requests = rentals_collection.count_documents({"status": "Pending"})

        stats_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        stats_frame.pack(pady=20)

        ctk.CTkLabel(stats_frame, text=f"Total Fleet\n{total_cars}", width=160, height=80, fg_color="gray25", corner_radius=10).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Available\n{available_cars}", width=160, height=80, fg_color="#239B56", corner_radius=10).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Active Rentals\n{rented_cars}", width=160, height=80, fg_color="#2E86C1", corner_radius=10).grid(row=0, column=2, padx=10)
        ctk.CTkLabel(stats_frame, text=f"PENDING\n{pending_requests}", width=160, height=80, fg_color="#D35400", corner_radius=10).grid(row=0, column=3, padx=10)

    def show_cars_section(self):
        self.clear_main_area()
        car_section = CarManagementFrame(self.main)
        car_section.pack(fill="both", expand=True)

    def show_rentals_section(self):
        self.clear_main_area()
        rental_section = RentalApprovalsFrame(self.main)
        rental_section.pack(fill="both", expand=True)
        
    def show_finances(self):
        """Displays the financial reports and charts"""
        self.clear_main_area()
        FinancesFrame(self.main).pack(fill="both", expand=True)

    def show_customers(self):
        """Displays the grid view of all registered users"""
        self.clear_main_area()
        CustomersFrame(self.main).pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.on_logout()