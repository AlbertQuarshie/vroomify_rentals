import customtkinter as ctk
from tkinter import messagebox
from mongodb import cars_collection, rentals_collection
import login

class UserDashboard(ctk.CTk):

    def __init__(self, username):
        super().__init__()

        self.username = username
        self.title(f"User Dashboard - {self.username}")
        self.geometry("1000x600")

        #sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar,
            text="USER PANEL",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Available Cars").pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="My Rentals").pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Payment History").pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Profile").pack(pady=10, padx=20)

        ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="red",
            command=self.logout
        ).pack(pady=30, padx=20)

     #Main Page
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            self.main,
            text=f"Welcome, {self.username}!",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        # Fetching User Specific Data
        active_rentals = rentals_collection.count_documents({"username": self.username, "status": "Active"})
        available_vehicles = cars_collection.count_documents({"status": "Available"})
        
        # Dashboard Cards
        stats_frame = ctk.CTkFrame(self.main)
        stats_frame.pack(pady=20)

        ctk.CTkLabel(stats_frame, text=f"Your Active Rentals\n{active_rentals}", width=200, height=100, fg_color="gray25", corner_radius=10).grid(row=0, column=0, padx=20)
        ctk.CTkLabel(stats_frame, text=f"Available for Booking\n{available_vehicles}", width=200, height=100, fg_color="gray25", corner_radius=10).grid(row=0, column=1, padx=20)

        # Quick Action Area
        action_label = ctk.CTkLabel(self.main, text="Quick Actions", font=("Arial", 18, "bold"))
        action_label.pack(pady=(30, 10))

        ctk.CTkButton(self.main, text="Browse and Book a Car", width=300, height=40).pack(pady=10)
        

        search_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        search_frame.pack(pady=10)
        ctk.CTkEntry(search_frame, placeholder_text="Search by car model...", width=250).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Search", width=80).pack(side="left")

    def logout(self):
        self.destroy()
        messagebox.showinfo("Logout", "Logged out successfully")