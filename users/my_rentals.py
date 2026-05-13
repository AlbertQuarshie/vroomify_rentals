import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, rentals_collection, cars_collection
from datetime import datetime

car_models_col = db["car_models"]

class MyRentalsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, username):
        super().__init__(master, label_text="My Rental History")
        self.username = username
        self.load_rentals()

    def load_rentals(self):
        for widget in self.winfo_children(): widget.destroy()

        # Fetch everything except 'Completed' or 'Rejected' if you want a clean list
        rentals = list(rentals_collection.find({"username": self.username}).sort("booking_date", -1))

        if not rentals:
            ctk.CTkLabel(self, text="No rental records found.", pady=40).pack()
            return

        for r in rentals:
            status = r.get("status", "Pending")
            
            # Color coding based on status
            color = "#E67E22" if status == "Pending" else "#2ECC71"
            if status == "Rejected": color = "#C0392B"
            if status == "Completed": color = "gray"

            card = ctk.CTkFrame(self, border_width=1, border_color=color)
            card.pack(fill="x", padx=10, pady=5)

            # Labels
            info = f"{r['brand']} {r['model']} ({r['year']}) | {r['days']} Days | Total: ${r['total_price']}"
            ctk.CTkLabel(card, text=info, font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
            
            status_label = ctk.CTkLabel(card, text=status.upper(), text_color=color, font=("Arial", 12, "bold"))
            status_label.pack(side="right", padx=20)

            # Only show Return button for Active rentals
            if status == "Active":
                ctk.CTkButton(
                    card, text="Return Car", width=100, fg_color="#C0392B",
                    command=lambda rent=r: self.return_process(rent)
                ).pack(side="right", padx=10)
            
            # Show Plate Number only if Assigned
            if "plate_number" in r:
                ctk.CTkLabel(card, text=f"Plate: {r['plate_number']}", text_color="#3498DB").pack(side="right", padx=10)

    def return_process(self, rental):
        if messagebox.askyesno("Return", "Are you returning this vehicle now?"):
            # 1. Complete Rental
            rentals_collection.update_one({"_id": rental["_id"]}, {"$set": {"status": "Completed"}})
            # 2. Make Car Available
            cars_collection.update_one({"_id": rental["car_id"]}, {"$set": {"status": "Available"}})
            # 3. Restock Model
            car_models_col.update_one({"_id": rental["model_id"]}, {"$inc": {"available_count": 1}})
            
            self.load_rentals()