import customtkinter as ctk
from mongodb import db
from PIL import Image
import os

car_models_col = db["car_models"]

class AvailableCarsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, username):
        super().__init__(master, label_text="Available Vehicles")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.load_models()

    def load_models(self):
        for widget in self.winfo_children(): widget.destroy()

        # Fetch models that actually have stock
        models = list(car_models_col.find({"available_count": {"$gt": 0}}))
        
        r, c = 0, 0
        for model in models:
            card = ctk.CTkFrame(self, corner_radius=15, border_width=1)
            card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")

            # Load Image from stored path
            path = model.get("image", "")
            if path and os.path.exists(path):
                img = ctk.CTkImage(Image.open(path), size=(200, 120))
                ctk.CTkLabel(card, image=img, text="").pack(pady=10)
            else:
                ctk.CTkLabel(card, text="No Image", height=120, fg_color="gray20").pack(pady=10)

            ctk.CTkLabel(card, text=f"{model['brand']} {model['model']}", font=("Arial", 16, "bold")).pack()
            
            # Show Stock Quantity
            stock_text = f"Only {model['available_count']} left!" if model['available_count'] < 3 else f"{model['available_count']} available"
            ctk.CTkLabel(card, text=stock_text, text_color="#E67E22").pack()
            
            ctk.CTkLabel(card, text=f"${model['price']}/day", font=("Arial", 18), text_color="#2ECC71").pack(pady=5)
            ctk.CTkButton(card, text="Rent Now").pack(pady=10, padx=20)

            c += 1
            if c > 2: c = 0; r += 1