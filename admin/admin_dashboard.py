import customtkinter as ctk
from tkinter import messagebox
from mongodb import cars_collection, customers_collection
from admin.car_management import CarManagementFrame # Import the new file

class AdminDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Admin Dashboard")
        self.geometry("1000x600")

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

        # Buttons with commands linked to navigation functions
        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_stats).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Cars", command=self.show_cars_section).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Customers").pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Rentals").pack(pady=10, padx=20)

        ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="red",
            command=self.logout
        ).pack(pady=30, padx=20)

        # =========================
        # MAIN AREA
        # =========================
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        # Show the stats by default on startup
        self.show_stats()

    def clear_main_area(self):
        """Helper to remove all widgets from the main area before switching pages"""
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_stats(self):
        """Displays the overview statistics (The default view)"""
        self.clear_main_area()

        ctk.CTkLabel(
            self.main,
            text="Admin Dashboard Overview",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        total_cars = cars_collection.count_documents({})
        available_cars = cars_collection.count_documents({"status": "Available"})
        rented_cars = cars_collection.count_documents({"status": "Rented"})
        total_customers = customers_collection.count_documents({})

        stats_frame = ctk.CTkFrame(self.main)
        stats_frame.pack(pady=20)

        ctk.CTkLabel(stats_frame, text=f"Cars\n{total_cars}", width=150, fg_color="gray25", corner_radius=10).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Available\n{available_cars}", width=150, fg_color="gray25", corner_radius=10).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Rented\n{rented_cars}", width=150, fg_color="gray25", corner_radius=10).grid(row=0, column=2, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Customers\n{total_customers}", width=150, fg_color="gray25", corner_radius=10).grid(row=0, column=3, padx=10)

    def show_cars_section(self):
        """Switches the view to the Car Management CRUD interface"""
        self.clear_main_area()
        
        # Initialize and pack the frame from car_management.py
        car_section = CarManagementFrame(self.main)
        car_section.pack(fill="both", expand=True)

    def logout(self):
        self.destroy()
        messagebox.showinfo("Logout", "Logged out successfully")