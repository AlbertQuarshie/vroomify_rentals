import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, rentals_collection, cars_collection
from bson.objectid import ObjectId

car_models_col = db["car_models"]

class RentalApprovalsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame, text="Pending Approval Requests", 
            font=("Arial", 26, "bold"), text_color="#3498DB"
        ).pack(side="left")

        # Scrollable area for cards
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_requests()

    def load_requests(self):
        """Clears and reloads the cards from the database"""
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        # Find only pending requests
        pending_rentals = list(rentals_collection.find({"status": "Pending"}).sort("booking_date", 1))

        if not pending_rentals:
            ctk.CTkLabel(
                self.scroll_container, 
                text="No pending requests at the moment.", 
                font=("Arial", 16), text_color="gray"
            ).pack(pady=50)
            return

        for request in pending_rentals:
            self.create_request_card(request)

    def create_request_card(self, r):
        """Creates an individual card for a rental request"""
        card = ctk.CTkFrame(self.scroll_container, corner_radius=15, border_width=1, border_color="#555")
        card.pack(fill="x", padx=20, pady=10)

        # Left Info Section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=20, pady=15)

        car_name = f"{r.get('brand')} {r.get('model')} ({r.get('year')})"
        ctk.CTkLabel(info_frame, text=car_name, font=("Arial", 18, "bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Customer: {r['username']}", text_color="#BDC3C7").pack(anchor="w")
        
        date_str = r['booking_date'].strftime("%Y-%m-%d %H:%M")
        ctk.CTkLabel(info_frame, text=f"Requested on: {date_str}", font=("Arial", 11)).pack(anchor="w")

        # Middle Price Section
        price_frame = ctk.CTkFrame(card, fg_color="transparent")
        price_frame.pack(side="left", padx=40)
        
        ctk.CTkLabel(price_frame, text=f"{r['days']} Days", font=("Arial", 14)).pack()
        ctk.CTkLabel(price_frame, text=f"Total: ${r['total_price']:.2f}", font=("Arial", 18, "bold"), text_color="#2ECC71").pack()

        # Right Action Section
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)

        ctk.CTkButton(
            btn_frame, text="Approve", fg_color="#1E8449", hover_color="#145A32", width=100,
            command=lambda rent=r: self.approve_request(rent)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Reject", fg_color="#922B21", hover_color="#641E16", width=100,
            command=lambda rent=r: self.reject_request(rent)
        ).pack(side="left", padx=5)

    def approve_request(self, rental):
        """Standard Approval Logic"""
        # Find an available car for this model
        car_unit = cars_collection.find_one({
            "model_id": rental["model_id"], 
            "status": "Available"
        })
        
        if not car_unit:
            messagebox.showerror("Inventory Error", f"No physical {rental['model']} units available to assign!")
            return

        # Update statuses in one go
        rentals_collection.update_one({"_id": rental["_id"]}, {
            "$set": {
                "status": "Active", 
                "car_id": car_unit["_id"], 
                "plate_number": car_unit["plate_number"]
            }
        })
        cars_collection.update_one({"_id": car_unit["_id"]}, {"$set": {"status": "Rented"}})
        car_models_col.update_one({"_id": rental["model_id"]}, {"$inc": {"available_count": -1}})

        messagebox.showinfo("Success", f"Approved! Assigned Plate: {car_unit['plate_number']}")
        self.load_requests()

    def reject_request(self, rental):
        """Standard Rejection Logic"""
        if messagebox.askyesno("Confirm", f"Reject {rental['username']}'s request?"):
            rentals_collection.update_one({"_id": rental["_id"]}, {"$set": {"status": "Rejected"}})
            self.load_requests()