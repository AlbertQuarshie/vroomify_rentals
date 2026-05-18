import customtkinter as ctk
from mongodb import db
from PIL import Image
from users.checkout import CheckoutWindow
import os

car_models_col = db["car_models"]

class AvailableCarsFrame(ctk.CTkFrame): 
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username 
        
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
        self.scroll_container = ctk.CTkScrollableFrame(self, label_text="Fleet Vehicles")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.load_models()

    def load_models(self):
        # Clear existing cards
        for widget in self.scroll_container.winfo_children(): 
            widget.destroy()

        # 1. Build Query (FIX: Removed the available_count constraint)
        filter_criteria = {}
        search_query = self.search_entry.get()
        if search_query:
            filter_criteria["$or"] = [
                {"brand": {"$regex": search_query, "$options": "i"}},
                {"model": {"$regex": search_query, "$options": "i"}}
            ]

        # 2. Determine Sort
        sort_choice = self.sort_var.get()
        sort_field = "price"
        sort_direction = 1 
        
        if sort_choice == "Price: High to Low":
            sort_direction = -1
        elif sort_choice == "Newest Year":
            sort_field = "year"
            sort_direction = -1

        # 3. Fetch Data
        models = list(car_models_col.find(filter_criteria).sort(sort_field, sort_direction))
        
        r, c = 0, 0
        for model in models:
            # Check if this model variant is currently available
            available_count = model.get('available_count', 0)
            is_available = available_count > 0

            # Dynamic styling options depending on availability
            border_color = "gray30" if is_available else "#922B21"
            card = ctk.CTkFrame(self.scroll_container, corner_radius=15, border_width=1, border_color=border_color)
            card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")

            # Load Image
            path = model.get("image", "")
            if path and os.path.exists(path):
                try:
                    img = ctk.CTkImage(Image.open(path), size=(200, 120))
                    lbl_img = ctk.CTkLabel(card, image=img, text="")
                    lbl_img.pack(pady=10)
                except:
                    ctk.CTkLabel(card, text="Image Error", height=120).pack(pady=10)
            else:
                ctk.CTkLabel(card, text="No Image", height=120, fg_color="gray20").pack(pady=10)

            # --- TITLE LABEL (With optional cross-out format) ---
            title_text = f"{model['brand']} {model['model']} ({model.get('year', 'N/A')})"
            if is_available:
                title_font = ("Arial", 15, "bold")
                title_color = ("black", "white")
            else:
                title_font = ("Arial", 15, "bold", "overstrike") # Standard Tkinter Strikethrough
                title_color = "gray50"

            ctk.CTkLabel(card, text=title_text, font=title_font, text_color=title_color).pack()
            
            # --- STOCK STATUS LABEL ---
            if is_available:
                stock_text = f"Only {available_count} left!" if available_count < 3 else f"{available_count} available"
                stock_color = "#E67E22"
            else:
                stock_text = "Unavailable (All Rented Out)"
                stock_color = "#922B21"
                
            ctk.CTkLabel(card, text=stock_text, text_color=stock_color, font=("Arial", 12, "bold")).pack()
            
            # --- PRICE LABEL ---
            price_color = "#2ECC71" if is_available else "gray50"
            ctk.CTkLabel(card, text=f"${model['price']}/day", font=("Arial", 18), text_color=price_color).pack(pady=5)
            
            # --- ACTION BUTTON ---
            if is_available:
                ctk.CTkButton(
                    card, 
                    text="Rent Now", 
                    command=lambda m=model: self.open_checkout(m)
                ).pack(pady=10, padx=20)
            else:
                ctk.CTkButton(
                    card, 
                    text="Unavailable", 
                    state="disabled",
                    fg_color="gray25",
                    text_color="gray50"
                ).pack(pady=10, padx=20)

            c += 1
            if c > 2: 
                c = 0
                r += 1

    def open_checkout(self, model_data):
        CheckoutWindow(self, model_data, self.username)