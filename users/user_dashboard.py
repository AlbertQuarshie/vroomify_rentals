import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, cars_collection, rentals_collection
from users.available_cars import AvailableCarsFrame
from users.my_rentals import MyRentalsFrame # Import the new page

# Collection for accurate stats
car_models_col = db["car_models"]

class UserDashboard(ctk.CTk):
    def __init__(self, username):
        super().__init__()

        self.username = username
        self.title(f"Vroomify - {self.username}")
        self.geometry("1100x750")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="USER PANEL", font=("Arial", 20, "bold")).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_home).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Available Cars", command=self.show_available_cars).pack(pady=10, padx=20)
        
        # --- FIXED BUTTON ---
        ctk.CTkButton(self.sidebar, text="My Rentals", command=self.show_my_rentals).pack(pady=10, padx=20)
        
        ctk.CTkButton(self.sidebar, text="Payment History", command=lambda: self.placeholder("Payment History")).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Profile", command=lambda: self.placeholder("Profile")).pack(pady=10, padx=20)

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#922B21", command=self.logout).pack(pady=30, padx=20)

        # Main Area
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_home()

    def clear_main_area(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main, text=f"Welcome, {self.username}!", font=("Arial", 28, "bold")).pack(pady=20)

        stats_frame = ctk.CTkFrame(self.main)
        stats_frame.pack(pady=20)

        # Updated Stats Logic
        active = rentals_collection.count_documents({"username": self.username, "status": "Active"})
        
        # Sum of available_count across all models for a true inventory count
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$available_count"}}}]
        result = list(car_models_col.aggregate(pipeline))
        avail = result[0]['total'] if result else 0

        ctk.CTkLabel(stats_frame, text=f"Active Rentals\n{active}", width=200, height=100, fg_color="#2E86C1", corner_radius=10).grid(row=0, column=0, padx=20)
        ctk.CTkLabel(stats_frame, text=f"Available Now\n{avail}", width=200, height=100, fg_color="#239B56", corner_radius=10).grid(row=0, column=1, padx=20)

        ctk.CTkButton(self.main, text="Start Booking a Car", width=300, height=50, command=self.show_available_cars).pack(pady=30)

    def show_available_cars(self):
        self.clear_main_area()
        grid_view = AvailableCarsFrame(self.main, self.username)
        grid_view.pack(fill="both", expand=True)

    def show_my_rentals(self):
        """Displays the MyRentalsFrame instead of a placeholder"""
        self.clear_main_area()
        rentals_view = MyRentalsFrame(self.main, self.username)
        rentals_view.pack(fill="both", expand=True)

    def placeholder(self, name):
        self.clear_main_area()
        ctk.CTkLabel(self.main, text=f"{name} Coming Soon", font=("Arial", 20)).pack(pady=50)

    def logout(self):
        self.destroy()
        messagebox.showinfo("Logout", "Logged out successfully")