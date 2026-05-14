import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, rentals_collection
from users.available_cars import AvailableCarsFrame
from users.my_rentals import MyRentalsFrame
from users.profile_frame import ProfileFrame  # Import the standalone file

# Collection for accurate inventory stats
car_models_col = db["car_models"]

class UserDashboard(ctk.CTkFrame):
    def __init__(self, master, username, on_logout):
        super().__init__(master)
        self.username = username
        self.on_logout = on_logout

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar, 
            text="VROOMIFY", 
            font=("Arial", 24, "bold"), 
            text_color="#3498DB"
        ).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_home).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Available Cars", command=self.show_available_cars).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="My Rentals", command=self.show_my_rentals).pack(pady=10, padx=20)
        
        # Linked to the new show_profile method
        ctk.CTkButton(self.sidebar, text="Profile", command=self.show_profile).pack(pady=10, padx=20)

        ctk.CTkButton(
            self.sidebar, 
            text="Logout", 
            fg_color="#922B21", 
            hover_color="#641E16",
            command=self.logout
        ).pack(side="bottom", pady=30, padx=20)

        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_home()

    def clear_main_area(self):
        """Clears the current view before loading a new frame"""
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_home(self):
        """Calculates and displays user-specific and fleet-wide statistics"""
        self.clear_main_area()
        ctk.CTkLabel(self.main, text=f"Welcome back, {self.username}!", font=("Arial", 28, "bold")).pack(pady=20)

        stats_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        stats_frame.pack(pady=20)

        # Count active rentals for the specific logged-in user
        active = rentals_collection.count_documents({"username": self.username, "status": "Active"})
        
        # Sum total available inventory across ALL models using MongoDB Aggregation
        try:
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$available_count"}}}]
            result = list(car_models_col.aggregate(pipeline))
            avail = result[0]['total'] if result else 0
        except Exception:
            avail = 0

        # Stats Cards
        ctk.CTkLabel(stats_frame, text=f"Active Rentals\n{active}", width=220, height=120, fg_color="#2E86C1", corner_radius=15, font=("Arial", 16, "bold")).grid(row=0, column=0, padx=20)
        ctk.CTkLabel(stats_frame, text=f"Available Now\n{avail}", width=220, height=120, fg_color="#239B56", corner_radius=15, font=("Arial", 16, "bold")).grid(row=0, column=1, padx=20)

        ctk.CTkButton(self.main, text="Start Booking a Car", width=300, height=50, command=self.show_available_cars).pack(pady=40)

    def show_available_cars(self):
        self.clear_main_area()
        grid_view = AvailableCarsFrame(self.main, self.username)
        grid_view.pack(fill="both", expand=True)

    def show_my_rentals(self):
        self.clear_main_area()
        rentals_view = MyRentalsFrame(self.main, self.username)
        rentals_view.pack(fill="both", expand=True)

    def show_profile(self):
        """Swaps the main area to the ProfileFrame"""
        self.clear_main_area()
        # Uses the standalone ProfileFrame from users/profile_frame.py
        ProfileFrame(self.main, self.username).pack(fill="both", expand=True)

    def placeholder(self, name):
        self.clear_main_area()
        ctk.CTkLabel(self.main, text=f"{name} Section\n(Under Development)", font=("Arial", 20)).pack(pady=50)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.on_logout()