import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, rentals_collection, cars_collection
from datetime import datetime, timedelta

# Collection for restocking logic
car_models_col = db["car_models"]

class MyRentalsFrame(ctk.CTkFrame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header, text="My Rental History", 
            font=("Arial", 26, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Refresh Status", 
            width=120, command=self.load_rentals, 
            fg_color="gray30", hover_color="gray20"
        ).pack(side="right")

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_rentals()

    def load_rentals(self):
        """Fetches and displays rental cards with dynamic deadline warnings"""
        # Clear current list
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        # Query all rentals for the user, sorted by newest booking date
        try:
            rentals = list(rentals_collection.find({"username": self.username}).sort("booking_date", -1))
        except Exception as e:
            ctk.CTkLabel(self.scroll_container, text=f"Database Connection Error: {e}").pack(pady=20)
            return

        if not rentals:
            ctk.CTkLabel(
                self.scroll_container, 
                text="No rental records found.\nVisit 'Available Cars' to start your first booking!", 
                pady=50, font=("Arial", 16), text_color="gray"
            ).pack()
            return

        now = datetime.now()

        for r in rentals:
            status = r.get("status", "Pending")
            brand = r.get("brand") if r.get("brand") is not None else "Unknown"
            model = r.get("model") if r.get("model") is not None else "Vehicle"
            year = r.get("year", "N/A")
            days = r.get("days", 0)
            total = r.get("total_price", 0.0)
            
            # Dynamic deadline warning checks for Active rentals
            deadline_warning = None
            warning_color = None
            
            if status == "Active" and "booking_date" in r:
                booking_date = r["booking_date"]
                deadline = booking_date + timedelta(days=days)
                
                if now > deadline:
                    # Car is overdue
                    overdue_delta = now - deadline
                    days_overdue = overdue_delta.days
                    if days_overdue == 0:
                        deadline_warning = "⚠️ OVERDUE: Return vehicle immediately!"
                    else:
                        deadline_warning = f"⚠️ OVERDUE BY {days_overdue} DAY(S)!"
                    warning_color = "#E74C3C"  # Crimson Red
                elif deadline - now <= timedelta(hours=24):
                    # Car is nearing the return deadline
                    time_left = deadline - now
                    hours_left = int(time_left.total_seconds() // 3600)
                    deadline_warning = f"⏳ Nearing Deadline: {hours_left} hour(s) remaining!"
                    warning_color = "#E67E22"  # Alert Orange

            # Logic-based Card Border Color Coding
            if status == "Pending":
                color = "#E67E22"  
            elif status == "Active":
                # Use warning color as the frame border if the contract is compromised or nearing expiry
                color = warning_color if warning_color else "#2ECC71"  
            elif status == "Rejected":
                color = "#C0392B"  
            else:
                color = "#7F8C8D"  

            # Create the Card UI
            card = ctk.CTkFrame(self.scroll_container, corner_radius=12, border_width=1, border_color=color)
            card.pack(fill="x", padx=15, pady=8)

            # --- LEFT SECTION: INFO AND REJECTION LOGIC ---
            text_container = ctk.CTkFrame(card, fg_color="transparent")
            text_container.pack(side="left", padx=20, pady=15, fill="both", expand=True)

            info_text = f"{brand} {model} ({year})\n{days} Days — Total: KES {total:,.2f}"
            ctk.CTkLabel(
                text_container, text=info_text, justify="left", 
                font=("Arial", 14, "bold")
            ).pack(anchor="w")
            
            # Visual Deadline Flag Placement
            if deadline_warning:
                warning_lbl = ctk.CTkLabel(
                    text_container, 
                    text=deadline_warning, 
                    justify="left",
                    font=("Arial", 12, "bold"), 
                    text_color=warning_color
                )
                warning_lbl.pack(anchor="w", pady=(5, 0))
            
            # Rejection Notice Output Container
            rejection_reason = r.get("rejection_reason")
            if status == "Rejected" and rejection_reason:
                reason_lbl = ctk.CTkLabel(
                    text_container, 
                    text=rejection_reason, 
                    justify="left",
                    wraplength=480,  
                    font=("Arial", 11, "italic"), 
                    text_color="#E74C3C"
                )
                reason_lbl.pack(anchor="w", pady=(6, 0))
            
            # --- RIGHT SECTION: STATUS & ACTIONS ---
            status_container = ctk.CTkFrame(card, fg_color="transparent")
            status_container.pack(side="right", padx=20)

            # Highlight status text with warning accent color if applicable
            display_color = warning_color if warning_color else color
            ctk.CTkLabel(
                status_container, text=status.upper(), 
                text_color=display_color, font=("Arial", 12, "bold")
            ).pack()

            # Show Plate Number only if Active/Completed and value exists
            plate = r.get("plate_number")
            if plate and status != "Rejected":
                ctk.CTkLabel(
                    status_container, 
                    text=f"Plate: {plate}", 
                    text_color="#3498DB", font=("Arial", 11, "italic")
                ).pack()

            # Return Button: Interactive only if status is Active
            if status == "Active":
                ctk.CTkButton(
                    card, text="Return Car", width=100, 
                    fg_color="#C0392B", hover_color="#922B21",
                    command=lambda rent=r: self.return_process(rent)
                ).pack(side="right", padx=10)

    def return_process(self, rental):
        """Processes the return by updating Rentals, Cars, and Model Stock"""
        v_name = rental.get('brand')
        if not v_name:
            v_name = "Vehicle"

        if messagebox.askyesno("Return Vehicle", f"Are you sure you want to return the {v_name}?"):
            try:
                # 1. Update Rental Status
                rentals_collection.update_one(
                    {"_id": rental["_id"]}, 
                    {"$set": {
                        "status": "Completed", 
                        "actual_return_date": datetime.now()
                    }}
                )
                
                # 2. Release physical car unit back to Available status
                if "car_id" in rental:
                    cars_collection.update_one(
                        {"_id": rental["car_id"]}, 
                        {"$set": {"status": "Available"}}
                    )
                
                # 3. Increment the global available count for the model
                if "model_id" in rental:
                    car_models_col.update_one(
                        {"_id": rental["model_id"]}, 
                        {"$inc": {"available_count": 1}}
                    )
                
                messagebox.showinfo("Success", "Car returned successfully. Thank you for using Vroomify!")
                self.load_rentals() # Refresh the view
            except Exception as e:
                messagebox.showerror("System Error", f"Failed to complete return: {e}")