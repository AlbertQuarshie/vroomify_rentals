import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from mongodb import db, rentals_collection

class CheckoutWindow(ctk.CTkToplevel):
    def __init__(self, master, model_data, username):
        super().__init__(master)
        self.model_data = model_data
        self.username = username
        
        # Root window geometry constraints
        self.title("Request Rental - Vroomify")
        self.geometry("460x520")  
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Color palette layout definitions
        self.font_family = "Arial"
        self.primary_blue = "#3498DB"
        self.dark_accent = "#2C3E50"

        # Frame section header text string
        ctk.CTkLabel(
            self, text="RENTAL REQUEST", 
            font=(self.font_family, 22, "bold"), 
            text_color=self.primary_blue
        ).pack(pady=(30, 15))
        
        # Selected vehicle details card layout block
        self.vehicle_card = ctk.CTkFrame(
            self, fg_color=("#F5F5F5", "#242424"), 
            corner_radius=12, border_width=1, border_color=("#E0E0E0", "#333333")
        )
        self.vehicle_card.pack(fill="x", padx=40, pady=5)

        card_content = ctk.CTkFrame(self.vehicle_card, fg_color="transparent")
        card_content.pack(padx=20, pady=15, fill="x")
        
        card_content.columnconfigure(0, weight=1)
        card_content.columnconfigure(1, weight=1)

        # Field property value arrays
        details = [
            ("Vehicle Brand", model_data['brand']),
            ("Model Name", model_data['model']),
            ("Model Year", str(model_data['year'])),
            ("Daily Rate", f"KES {model_data['price']:,.2f}")
        ]
        
        # Grid loop generation steps
        for idx, (lbl, val) in enumerate(details):
            ctk.CTkLabel(
                card_content, text=lbl, font=(self.font_family, 13), 
                text_color="#888888", anchor="w"
            ).grid(row=idx, column=0, pady=4, sticky="w")
            
            ctk.CTkLabel(
                card_content, text=val, font=(self.font_family, 14, "bold"), 
                text_color=("#222222", "#ECF0F1"), anchor="e"
            ).grid(row=idx, column=1, pady=4, sticky="e")

        # Input fields container elements
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=40, pady=20)

        ctk.CTkLabel(
            input_frame, text="How many days would you like to rent?", 
            font=(self.font_family, 13, "bold"), text_color=("#555555", "#AAAAAA")
        ).pack(anchor="w", pady=(0, 8))

        # Booking duration number field setup
        self.days_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Enter number of days (e.g. 5)",
            height=45, font=(self.font_family, 14),
            border_width=1, border_color=("#BDC3C7", "#444444"),
            corner_radius=8
        )
        self.days_entry.pack(fill="x", pady=(0, 15))
        self.days_entry.bind("<KeyRelease>", self.update_total)

        # Bottom estimated calculation panel wrapper
        self.total_bar = ctk.CTkFrame(input_frame, fg_color=("#EAEDED", "#1A1A1A"), corner_radius=8, height=50)
        self.total_bar.pack(fill="x")
        self.total_bar.pack_propagate(False)

        self.total_label = ctk.CTkLabel(
            self.total_bar, text="Estimated Total: KES 0.00", 
            font=(self.font_family, 15, "bold"), text_color=("#2E86C1", "#5DADE2")
        )
        self.total_label.pack(side="left", padx=15)

        # Primary transaction verification button setup
        self.submit_btn = ctk.CTkButton(
            self, text="SEND REQUEST FOR APPROVAL", 
            height=50, font=(self.font_family, 13, "bold"),
            fg_color=self.primary_blue, hover_color="#2980B9",
            corner_radius=8, command=self.submit_request
        )
        self.submit_btn.pack(fill="x", padx=40, pady=(5, 25))

    def update_total(self, event=None):
        """Recalculates pricing estimation summary figures reactively"""
        try:
            days_input = self.days_entry.get().strip()
            if not days_input:
                self.total_label.configure(text="Estimated Total: KES 0.00")
                return
                
            days = int(days_input)
            if days <= 0: raise ValueError
            
            total = days * self.model_data['price']
            self.total_label.configure(text=f"Estimated Total: KES{total:,.2f}")
        except ValueError: 
            self.total_label.configure(text="Estimated Total: KES--.-- (Invalid Day Count)")

    def submit_request(self):
        """Validates entry states and drops new transaction log records into MongoDB"""
        try:
            days_input = self.days_entry.get().strip()
            if not days_input:
                raise ValueError
                
            days = int(days_input)
            if days <= 0: raise ValueError

            # Transaction data initialization packet 
            rental_request = {
                "username": self.username,
                "model_id": self.model_data["_id"],
                "brand": self.model_data["brand"],
                "model": self.model_data["model"],
                "year": self.model_data["year"],
                "days": days,
                "total_price": days * self.model_data['price'],
                "booking_date": datetime.now(),
                "status": "Pending"
            }
            
            rentals_collection.insert_one(rental_request)
            messagebox.showinfo("Success", "Request sent! Please wait for Admin approval.")
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")