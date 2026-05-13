import customtkinter as ctk
from tkinter import messagebox
from mongodb import cars_collection, rentals_collection
from users.available_cars import AvailableCarsFrame

class UserDashboard(ctk.CTk):
    def __init__(self, username):
        super().__init__()

        self.username = username
        self.title(f"User Dashboard - {self.username}")
        self.geometry("1100x750")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="USER PANEL", font=("Arial", 20, "bold")).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_home).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Available Cars", command=self.show_available_cars).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="My Rentals", command=lambda: self.placeholder("My Rentals")).pack(pady=10, padx=20)
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

        active = rentals_collection.count_documents({"username": self.username, "status": "Active"})
        avail = cars_collection.count_documents({"status": "Available"})

        ctk.CTkLabel(stats_frame, text=f"Active Rentals\n{active}", width=200, height=100, fg_color="gray25", corner_radius=10).grid(row=0, column=0, padx=20)
        ctk.CTkLabel(stats_frame, text=f"Available Now\n{avail}", width=200, height=100, fg_color="gray25", corner_radius=10).grid(row=0, column=1, padx=20)

        ctk.CTkButton(self.main, text="Start Booking a Car", width=300, height=50, command=self.show_available_cars).pack(pady=30)

    def show_available_cars(self):
        self.clear_main_area()
        grid_view = AvailableCarsFrame(self.main, self.username)
        grid_view.pack(fill="both", expand=True)

    def placeholder(self, name):
        self.clear_main_area()
        ctk.CTkLabel(self.main, text=f"{name} Coming Soon", font=("Arial", 20)).pack(pady=50)

    def logout(self):
        self.destroy()
        messagebox.showinfo("Logout", "Logged out successfully")