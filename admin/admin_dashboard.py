import customtkinter as ctk
from tkinter import messagebox
from mongodb import cars_collection, customers_collection, rentals_collection
from admin.car_management import CarManagementFrame 
from admin.rental_approvals import RentalApprovalsFrame # Import the approvals page

class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vroomify Admin Panel")
        self.geometry("1100x700")

        # =========================
        # SIDEBAR
        # =========================
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar, 
            text="ADMIN PANEL", 
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_stats).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Cars", command=self.show_cars_section).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Customers", command=lambda: self.placeholder("Customers")).pack(pady=10, padx=20)
        
        # --- FIXED RENTALS BUTTON ---
        ctk.CTkButton(self.sidebar, text="Rentals", command=self.show_rentals_section).pack(pady=10, padx=20)

        ctk.CTkButton(
            self.sidebar, 
            text="Logout", 
            fg_color="#922B21", 
            command=self.logout
        ).pack(pady=30, padx=20)

        # =========================
        # MAIN AREA
        # =========================
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_stats()

    def clear_main_area(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_stats(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main, text="System Overview", font=("Arial", 28, "bold")).pack(pady=20)

        # Stats Calculations
        total_cars = cars_collection.count_documents({})
        available_cars = cars_collection.count_documents({"status": "Available"})
        rented_cars = cars_collection.count_documents({"status": "Rented"})
        pending_requests = rentals_collection.count_documents({"status": "Pending"})

        stats_frame = ctk.CTkFrame(self.main)
        stats_frame.pack(pady=20)

        # Added a specific badge for Pending Requests to alert the admin
        ctk.CTkLabel(stats_frame, text=f"Total Fleet\n{total_cars}", width=160, height=80, fg_color="gray25", corner_radius=10).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Available\n{available_cars}", width=160, height=80, fg_color="#239B56", corner_radius=10).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Active Rentals\n{rented_cars}", width=160, height=80, fg_color="#2E86C1", corner_radius=10).grid(row=0, column=2, padx=10)
        ctk.CTkLabel(stats_frame, text=f"PENDING\n{pending_requests}", width=160, height=80, fg_color="#D35400", corner_radius=10).grid(row=0, column=3, padx=10)

    def show_cars_section(self):
        self.clear_main_area()
        car_section = CarManagementFrame(self.main)
        car_section.pack(fill="both", expand=True)

    def show_rentals_section(self):
        """Switches the view to the Rental Approvals interface"""
        self.clear_main_area()
        rental_section = RentalApprovalsFrame(self.main)
        rental_section.pack(fill="both", expand=True)

    def placeholder(self, name):
        self.clear_main_area()
        ctk.CTkLabel(self.main, text=f"{name} Management Coming Soon", font=("Arial", 20)).pack(pady=50)

    def logout(self):
        self.destroy()
        messagebox.showinfo("Logout", "Admin logged out.")