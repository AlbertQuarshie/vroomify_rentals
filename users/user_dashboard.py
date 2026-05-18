import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, rentals_collection
from users.available_cars import AvailableCarsFrame
from users.my_rentals import MyRentalsFrame
from users.profile_frame import ProfileFrame  
from datetime import datetime, timedelta

# Collection for accurate inventory stats
car_models_col = db["car_models"]

class UserDashboard(ctk.CTkFrame):
    def __init__(self, master, username, on_logout):
        super().__init__(master)
        self.username = username
        self.on_logout = on_logout

        # Navigation Sidebar UI (Your exact original styling configuration)
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
        ctk.CTkButton(self.sidebar, text="Profile", command=self.show_profile).pack(pady=10, padx=20)

        ctk.CTkButton(
            self.sidebar, 
            text="Logout", 
            fg_color="#922B21", 
            hover_color="#641E16",
            command=self.logout
        ).pack(side="bottom", pady=30, padx=20)

        # Main Workspace Canvas Viewport
        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        # Trigger Screen Build & Deadline Scanners
        self.show_home()
        self.check_rental_deadlines()

    def clear_main_area(self):
        """Clears the current view before loading a new frame"""
        for widget in self.main.winfo_children():
            widget.destroy()

    def check_rental_deadlines(self):
        """Scans active user rentals for imminent or overdue contract deadlines"""
        try:
            active_rentals = list(rentals_collection.find({"username": self.username, "status": "Active"}))
        except Exception:
            return  

        if not active_rentals:
            return

        now = datetime.now()
        overdue_cars = []
        nearing_deadline_cars = []

        for r in active_rentals:
            if "booking_date" in r:
                booking_date = r["booking_date"]
                days_allowed = r.get("days", 0)
                deadline = booking_date + timedelta(days=days_allowed)
                car_name = f"{r.get('brand', 'Unknown')} {r.get('model', 'Vehicle')}"
                
                if now > deadline:
                    overdue_cars.append(car_name)
                elif deadline - now <= timedelta(hours=24):
                    nearing_deadline_cars.append(car_name)

        if overdue_cars:
            cars_list = "\n- ".join(overdue_cars)
            messagebox.showwarning(
                "OVERDUE RENTAL NOTICE", 
                f"The following vehicle(s) are OVERDUE for return:\n- {cars_list}\n\n"
                f"Please return them immediately to avoid extra late penalty structures!"
            )
            return  

        if nearing_deadline_cars:
            cars_list = "\n- ".join(nearing_deadline_cars)
            messagebox.showinfo(
                "Rental Deadline Nearing", 
                f"Reminder: Your rental contract for the following vehicle(s) expires within 24 hours:\n- {cars_list}\n\n"
                f"Please ensure you plan to return the vehicle on time."
            )

    def show_home(self):
        """Calculates and displays user-specific metrics, card logs, and shortcuts"""
        self.clear_main_area()
        
        # Original Title Style
        ctk.CTkLabel(self.main, text=f"Welcome back, {self.username}!", font=("Arial", 28, "bold")).pack(pady=15)

        # ─── SECTION 1: TOP STATS ROW ───
        stats_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        stats_frame.pack(pady=5)

        active = rentals_collection.count_documents({"username": self.username, "status": "Active"})
        pending = rentals_collection.count_documents({"username": self.username, "status": "Pending"})
        
        try:
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$available_count"}}}]
            result = list(car_models_col.aggregate(pipeline))
            avail = result[0]['total'] if result else 0
        except Exception:
            avail = 0

        # Uniform structural cards matching your core layout parameters
        ctk.CTkLabel(stats_frame, text=f"Active Rentals\n{active}", width=210, height=100, fg_color="#2E86C1", corner_radius=12, font=("Arial", 15, "bold")).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Pending Approval\n{pending}", width=210, height=100, fg_color="#E67E22", corner_radius=12, font=("Arial", 15, "bold")).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(stats_frame, text=f"Available Fleet\n{avail}", width=210, height=100, fg_color="#239B56", corner_radius=12, font=("Arial", 15, "bold")).grid(row=0, column=2, padx=10)

        # ─── SECTION 2: RECENT RENTAL STATUS CARDS ───
        rentals_section = ctk.CTkFrame(self.main, fg_color="transparent")
        rentals_section.pack(pady=20, fill="x", padx=30)

        ctk.CTkLabel(rentals_section, text="⏱️ Recent Booking Applications", font=("Arial", 16, "bold"), text_color="#3498DB").pack(anchor="w", padx=10, pady=(0, 10))

        # Horizontal sub-grid to house booking item cards side-by-side
        cards_row = ctk.CTkFrame(rentals_section, fg_color="transparent")
        cards_row.pack(fill="x")

        try:
            # Fetch the 2 most recent applications submitted by the user
            recent_bookings = list(rentals_collection.find({"username": self.username}).sort("booking_date", -1).limit(2))
        except Exception:
            recent_bookings = []

        if recent_bookings:
            for i, r in enumerate(recent_bookings):
                brand = r.get("brand", "Unknown")
                model = r.get("model", "Vehicle")
                status = r.get("status", "Pending")
                days = r.get("days", 0)
                plate = r.get("plate_number", "Awaiting Assign")

                # Setup card layout container block
                card = ctk.CTkFrame(cards_row, fg_color=("#F2F4F4", "#2C3E50"), corner_radius=10, height=110)
                card.grid(row=0, column=i, padx=10, sticky="nsew")
                cards_row.grid_columnconfigure(i, weight=1) # Ensure cards take equal horizontal share

                # Vehicle Details
                ctk.CTkLabel(card, text=f"{brand} {model}", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(12, 2))
                ctk.CTkLabel(card, text=f"Duration: {days} Days  |  Plate: {plate}", font=("Arial", 12), text_color="gray").pack(anchor="w", padx=15, pady=2)

                # Status Badge styling definitions
                status_colors = {"Active": "#2E86C1", "Pending": "#E67E22", "Completed": "#239B56"}
                badge_bg = status_colors.get(status, "gray")

                badge = ctk.CTkLabel(
                    card, 
                    text=status.upper(), 
                    font=("Arial", 10, "bold"), 
                    text_color="white",
                    fg_color=badge_bg,
                    corner_radius=6,
                    width=90,
                    height=20
                )
                badge.pack(anchor="w", padx=15, pady=(6, 12))
        else:
            # Safe Fallback View card if no database records exist
            empty_card = ctk.CTkFrame(cards_row, fg_color=("#F2F4F4", "#2C3E50"), corner_radius=10, height=80)
            empty_card.pack(fill="x", padx=10)
            ctk.CTkLabel(empty_card, text="No previous bookings or rental requests tracked on this account node.", font=("Arial", 12, "italic"), text_color="gray").pack(pady=25)

        # ─── SECTION 3: QUICK OPERATIONS HUB (MULTIPLE CTAs) ───
        hub_container = ctk.CTkFrame(self.main, fg_color="transparent")
        hub_container.pack(pady=10)

        ctk.CTkLabel(hub_container, text="⚡ Quick Actions Console", font=("Arial", 15, "bold")).pack(pady=(0, 10))

        buttons_row = ctk.CTkFrame(hub_container, fg_color="transparent")
        buttons_row.pack()

        # Aligned primary entry points styled dynamically to preserve the main layout framework
        ctk.CTkButton(buttons_row, text="Browse Fleet Vehicles", width=190, height=40, command=self.show_available_cars).grid(row=0, column=0, padx=8)
        ctk.CTkButton(buttons_row, text="Manage Active Rentals", width=190, height=40, fg_color="gray30", hover_color="gray20", command=self.show_my_rentals).grid(row=0, column=1, padx=8)
        ctk.CTkButton(buttons_row, text="Edit Account Profile", width=190, height=40, fg_color="gray40", hover_color="gray30", command=self.show_profile).grid(row=0, column=2, padx=8)

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
        ProfileFrame(self.main, self.username).pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.on_logout()