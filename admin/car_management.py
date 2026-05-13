import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from mongodb import db, cars_collection  # Assuming 'db' is your database object
from bson.objectid import ObjectId
from PIL import Image
import os

# Collection Reference for the Grouped Data
car_models_col = db["car_models"]

class CarManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.selected_car_id = None  # Stores the ID of the specific unit from 'cars'
        self.image_path = ""         # Stores the path for the car model image

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =========================
        # LEFT SIDE: FORM
        # =========================
        self.form_frame = ctk.CTkScrollableFrame(self, width=340, label_text="Vehicle Details")
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Input Fields
        self.brand_entry = self.create_input("Brand (e.g., Toyota)")
        self.model_entry = self.create_input("Model (e.g., Camry)")
        self.year_entry = self.create_input("Year")
        self.price_entry = self.create_input("Daily Price ($)")
        self.plate_entry = self.create_input("Specific Plate Number")

        # Image Display Area
        self.image_label = ctk.CTkLabel(
            self.form_frame, text="No Image Selected", 
            fg_color="gray25", height=120, corner_radius=10
        )
        self.image_label.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.form_frame, text="Import Image", command=self.import_image, fg_color="#2874A6").pack(pady=5, padx=20, fill="x")

        # Action Buttons
        self.add_btn = ctk.CTkButton(self.form_frame, text="Add New to Fleet", fg_color="#1E8449", command=self.save_car)
        self.add_btn.pack(pady=(20, 5), padx=20, fill="x")

        self.update_btn = ctk.CTkButton(self.form_frame, text="Update Selected", state="disabled", command=self.update_car)
        self.update_btn.pack(pady=5, padx=20, fill="x")

        self.clear_btn = ctk.CTkButton(self.form_frame, text="Clear Form", fg_color="gray", command=self.clear_entries)
        self.clear_btn.pack(pady=5, padx=20, fill="x")

        self.delete_btn = ctk.CTkButton(self.form_frame, text="Delete Vehicle", fg_color="#922B21", command=self.delete_car)
        self.delete_btn.pack(pady=(20, 5), padx=20, fill="x")

        # =========================
        # RIGHT SIDE: TABLE
        # =========================
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure Table Columns
        cols = ("Plate", "Brand", "Model", "Price", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show='headings')
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_car_select)
        
        self.load_table()

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.form_frame, placeholder_text=placeholder)
        entry.pack(pady=8, padx=20, fill="x")
        return entry

    # --- LOGIC ---

    def import_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.image_path = file_path
            self.image_label.configure(text="Image Selected ✅")

    def on_car_select(self, event):
        """Fetches data from BOTH collections when a row is clicked"""
        selected = self.tree.selection()
        if not selected: return

        plate = self.tree.item(selected[0])['values'][0]
        
        # 1. Get physical unit info
        car_unit = cars_collection.find_one({"plate_number": plate})
        if not car_unit: return
        self.selected_car_id = car_unit["_id"]

        # 2. Get model details info
        model_details = car_models_col.find_one({"_id": car_unit["model_id"]})
        
        if model_details:
            self.clear_entries(reset_id=False)
            self.brand_entry.insert(0, model_details.get('brand', ''))
            self.model_entry.insert(0, model_details.get('model', ''))
            self.year_entry.insert(0, model_details.get('year', ''))
            self.price_entry.insert(0, str(model_details.get('price', '')))
            self.plate_entry.insert(0, car_unit.get('plate_number', ''))
            
            self.image_path = model_details.get('image', '')
            self.image_label.configure(text="Image Loaded" if self.image_path else "No Image")
            
            # Switch to Edit Mode
            self.add_btn.configure(state="disabled")
            self.update_btn.configure(state="normal")

    def save_car(self):
        """Logic for adding a brand new car and checking if model exists"""
        brand, model, plate = self.brand_entry.get(), self.model_entry.get(), self.plate_entry.get()
        
        if not all([brand, model, plate]):
            messagebox.showerror("Error", "Brand, Model, and Plate are required")
            return

        try:
            # 1. Handle car_models
            model_record = car_models_col.find_one({"brand": brand, "model": model})
            if not model_record:
                model_id = car_models_col.insert_one({
                    "brand": brand, "model": model, "year": self.year_entry.get(),
                    "price": float(self.price_entry.get()), "image": self.image_path,
                    "total_stock": 1, "available_count": 1
                }).inserted_id
            else:
                model_id = model_record["_id"]
                car_models_col.update_one({"_id": model_id}, {"$inc": {"total_stock": 1, "available_count": 1}})

            # 2. Handle specific unit
            cars_collection.insert_one({
                "model_id": model_id, "plate_number": plate, "status": "Available"
            })
            
            messagebox.showinfo("Success", "New vehicle added to fleet")
            self.load_table()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def update_car(self):
        """Updates the model (for all units) and the plate (for this unit)"""
        if not self.selected_car_id: return
        
        unit = cars_collection.find_one({"_id": self.selected_car_id})
        model_id = unit["model_id"]

        try:
            # Update Model Details (Universal)
            car_models_col.update_one({"_id": model_id}, {"$set": {
                "brand": self.brand_entry.get(),
                "model": self.model_entry.get(),
                "year": self.year_entry.get(),
                "price": float(self.price_entry.get()),
                "image": self.image_path
            }})

            # Update Unit Details (Specific)
            cars_collection.update_one({"_id": self.selected_car_id}, {"$set": {
                "plate_number": self.plate_entry.get()
            }})

            messagebox.showinfo("Success", "Details updated successfully")
            self.load_table()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for car in cars_collection.find():
            m = car_models_col.find_one({"_id": car["model_id"]})
            if m:
                self.tree.insert("", "end", values=(
                    car.get("plate_number"), m.get("brand"), m.get("model"), 
                    f"${m.get('price')}", car.get("status")
                ))

    def delete_car(self):
        if not self.selected_car_id: return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this specific unit?"):
            # Find the model_id to decrement stock before deleting unit
            unit = cars_collection.find_one({"_id": self.selected_car_id})
            car_models_col.update_one({"_id": unit["model_id"]}, {"$inc": {"total_stock": -1, "available_count": -1}})
            
            cars_collection.delete_one({"_id": self.selected_car_id})
            self.load_table()
            self.clear_entries()

    def clear_entries(self, reset_id=True):
        if reset_id:
            self.selected_car_id = None
            self.add_btn.configure(state="normal")
            self.update_btn.configure(state="disabled")
        
        self.brand_entry.delete(0, 'end')
        self.model_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.plate_entry.delete(0, 'end')
        self.image_path = ""
        self.image_label.configure(text="No Image Selected")