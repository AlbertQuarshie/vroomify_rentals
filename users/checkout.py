import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from mongodb import db, rentals_collection

class CheckoutWindow(ctk.CTkToplevel):
    def __init__(self, master, model_data, username):
        super().__init__(master)
        self.model_data = model_data
        self.username = username
        
        self.title("Request Rental - Vroomify")
        self.geometry("450x500")
        self.attributes('-topmost', True)

        ctk.CTkLabel(self, text="Rental Request", font=("Arial", 22, "bold")).pack(pady=20)
        
        # Summary
        summary = f"Car: {model_data['brand']} {model_data['model']}\nYear: {model_data['year']}\nRate: ${model_data['price']}/day"
        ctk.CTkLabel(self, text=summary, justify="left").pack(pady=10)

        self.days_entry = ctk.CTkEntry(self, placeholder_text="Number of days")
        self.days_entry.pack(pady=20, padx=60, fill="x")

        self.total_label = ctk.CTkLabel(self, text="Estimated Total: $0.00", font=("Arial", 16, "bold"))
        self.total_label.pack(pady=10)
        self.days_entry.bind("<KeyRelease>", self.update_total)

        ctk.CTkButton(self, text="Send Request for Approval", fg_color="#2874A6", command=self.submit_request).pack(pady=20, padx=60, fill="x")

    def update_total(self, event=None):
        try:
            days = int(self.days_entry.get())
            total = days * self.model_data['price']
            self.total_label.configure(text=f"Estimated Total: ${total:,.2f}")
        except: self.total_label.configure(text="Estimated Total: $0.00")

    def submit_request(self):
        try:
            days = int(self.days_entry.get())
            if days <= 0: raise ValueError

            rental_request = {
                "username": self.username,
                "model_id": self.model_data["_id"],
                "brand": self.model_data["brand"],
                "model": self.model_data["model"],
                "year": self.model_data["year"],
                "days": days,
                "total_price": days * self.model_data['price'],
                "booking_date": datetime.now(),
                "status": "Pending" # Essential for admin filtering
            }
            
            rentals_collection.insert_one(rental_request)
            messagebox.showinfo("Success", "Request sent! Please wait for Admin approval.")
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")