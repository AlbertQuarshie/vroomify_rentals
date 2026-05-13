import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from mongodb import db, rentals_collection, cars_collection

# Collection Reference
car_models_col = db["car_models"]

class CheckoutWindow(ctk.CTkToplevel):
    def __init__(self, master, model_data, username):
        super().__init__(master)
        self.model_data = model_data
        self.username = username
        
        # Window Setup
        self.title("Secure Checkout - Vroomify")
        self.geometry("450x550")
        self.attributes('-topmost', True)
        self.configure(fg_color="#1B1B1B") # Darker theme for checkout

        # Header
        ctk.CTkLabel(
            self, text="Finalize Rental", 
            font=("Arial", 24, "bold"), text_color="#3498DB"
        ).pack(pady=(30, 10))
        
        # Car Summary Box
        summary_box = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        summary_box.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(
            summary_box, 
            text=f"{model_data['brand']} {model_data['model']} ({model_data['year']})", 
            font=("Arial", 16, "bold")
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            summary_box, 
            text=f"Rate: ${model_data['price']}/day", 
            text_color="gray"
        ).pack(pady=(0, 15))

        # Input Area
        ctk.CTkLabel(self, text="Rental Duration (Days):", font=("Arial", 13)).pack(pady=(20, 5))
        self.days_entry = ctk.CTkEntry(self, placeholder_text="Enter number of days", width=200, justify="center")
        self.days_entry.pack(pady=5)
        self.days_entry.bind("<KeyRelease>", self.calculate_total)

        # Total Display
        self.total_label = ctk.CTkLabel(
            self, text="Total: $0.00", 
            font=("Arial", 22, "bold"), text_color="#2ECC71"
        ).pack(pady=30)

        # Action Buttons
        ctk.CTkButton(
            self, text="Confirm & Book", 
            height=45, fg_color="#28B463", hover_color="#1D8348",
            command=self.complete_transaction
        ).pack(pady=10, padx=60, fill="x")

        ctk.CTkButton(
            self, text="Cancel", 
            height=40, fg_color="transparent", border_width=1,
            command=self.destroy
        ).pack(pady=5, padx=60, fill="x")

    def calculate_total(self, event=None):
        try:
            days = int(self.days_entry.get())
            if days < 0: raise ValueError
            total = days * self.model_data['price']
            # Re-finding the label to update text
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and "Total:" in widget.cget("text"):
                    widget.configure(text=f"Total: ${total:,.2f}")
        except:
            pass # Keep previous total if input is invalid

    def complete_transaction(self):
        try:
            days = int(self.days_entry.get())
            if days <= 0: raise ValueError
            
            # Find an available physical unit
            car_unit = cars_collection.find_one({
                "model_id": self.model_data["_id"],
                "status": "Available"
            })

            if not car_unit:
                messagebox.showerror("No Inventory", "No specific units of this model are currently available.")
                self.destroy()
                return

            # Record the Rental
            rental_entry = {
                "username": self.username,
                "model_id": self.model_data["_id"],
                "car_id": car_unit["_id"],
                "plate_number": car_unit["plate_number"],
                "days": days,
                "total_price": days * self.model_data['price'],
                "booking_date": datetime.now(),
                "status": "Active"
            }
            rentals_collection.insert_one(rental_entry)

            # Update DB States
            cars_collection.update_one({"_id": car_unit["_id"]}, {"$set": {"status": "Rented"}})
            car_models_col.update_one({"_id": self.model_data["_id"]}, {"$inc": {"available_count": -1}})

            messagebox.showinfo("Success", f"Booking Confirmed!\nYour car (Plate: {car_unit['plate_number']}) is ready.")
            self.master.load_models() # Refresh the car grid
            self.destroy()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of days.")