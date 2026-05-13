import customtkinter as ctk
from mongodb import db
from PIL import Image
from users.checkout import CheckoutWindow
import os

car_models_col = db["car_models"]

class AvailableCarsFrame(ctk.CTkFrame): # Changed to Frame to allow for a top search bar
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username # Store username for the checkout process
        
        # --- TOP CONTROL BAR (Search & Sort) ---
        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(self.controls, placeholder_text="Search cars...", width=250)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_models())

        self.sort_var = ctk.StringVar(value="Price: Low to High")
        self.sort_dropdown = ctk.CTkComboBox(
            self.controls, 
            values=["Price: Low to High", "Price: High to Low", "Newest Year"],
            variable=self.sort_var, 
            command=lambda x: self.load_models()
        )
        self.sort_dropdown.pack(side="right", padx=5)

        # --- SCROLLABLE GRID ---
        self.scroll_container = ctk.CTkScrollableFrame(self, label_text="Available Vehicles")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.load_models()

    def load_models(self):
        # Clear existing cards
        for widget in self.scroll_container.winfo_children(): 
            widget.destroy()

        # 1. Build Query (Search)
        search_query = self.search_entry.get()
        filter_criteria = {"available_count": {"$gt": 0}}
        if search_query:
            filter_criteria["$or"] = [
                {"brand": {"$regex": search_query, "$options": "i"}},
                {"model": {"$regex": search_query, "$options": "i"}}
            ]

        # 2. Determine Sort
        sort_choice = self.sort_var.get()
        sort_field = "price"
        sort_direction = 1 # Ascending
        
        if sort_choice == "Price: High to Low":
            sort_direction = -1
        elif sort_choice == "Newest Year":
            sort_field = "year"
            sort_direction = -1

        # 3. Fetch Data
        models = list(car_models_col.find(filter_criteria).sort(sort_field, sort_direction))
        
        r, c = 0, 0
        for model in models:
            card = ctk.CTkFrame(self.scroll_container, corner_radius=15, border_width=1)
            card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")

            # Load Image
            path = model.get("image", "")
            if path and os.path.exists(path):
                try:
                    img = ctk.CTkImage(Image.open(path), size=(200, 120))
                    ctk.CTkLabel(card, image=img, text="").pack(pady=10)
                except:
                    ctk.CTkLabel(card, text="Image Error", height=120).pack(pady=10)
            else:
                ctk.CTkLabel(card, text="No Image", height=120, fg_color="gray20").pack(pady=10)

            # Labels - Added Year to Title
            ctk.CTkLabel(card, text=f"{model['brand']} {model['model']} ({model.get('year', 'N/A')})", font=("Arial", 15, "bold")).pack()
            
            stock_text = f"Only {model['available_count']} left!" if model['available_count'] < 3 else f"{model['available_count']} available"
            ctk.CTkLabel(card, text=stock_text, text_color="#E67E22", font=("Arial", 12)).pack()
            
            ctk.CTkLabel(card, text=f"${model['price']}/day", font=("Arial", 18), text_color="#2ECC71").pack(pady=5)
            
            # --- FIXED BUTTON ---
            # Now calls the checkout window passing the specific model and the logged-in user
            ctk.CTkButton(
                card, 
                text="Rent Now", 
                command=lambda m=model: self.open_checkout(m)
            ).pack(pady=10, padx=20)

            c += 1
            if c > 2: 
                c = 0
                r += 1

    def open_checkout(self, model_data):
        # Open the new Toplevel window
        CheckoutWindow(self, model_data, self.username)