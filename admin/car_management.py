import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from mongodb import cars_collection
from bson.objectid import ObjectId
from PIL import Image
import os

class CarManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.selected_car_id = None  # Tracks if we are editing an existing car
        self.image_path = ""         # Stores the path of the imported image

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

   
        self.form_frame = ctk.CTkScrollableFrame(self, width=320, label_text="Vehicle Details")
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.brand_entry = self.create_input("Brand")
        self.model_entry = self.create_input("Model")
        self.year_entry = self.create_input("Year")
        self.plate_entry = self.create_input("Plate Number")
        self.price_entry = self.create_input("Price per Day ($)")
        
        ctk.CTkLabel(self.form_frame, text="Status:").pack(pady=(10, 0), anchor="w", padx=20)
        self.status_var = ctk.StringVar(value="Available")
        self.status_dropdown = ctk.CTkComboBox(self.form_frame, values=["Available", "Rented", "Maintenance"], variable=self.status_var)
        self.status_dropdown.pack(pady=5, padx=20, fill="x")

        # Image Import Section
        self.image_label = ctk.CTkLabel(self.form_frame, text="No Image Selected", fg_color="gray30", height=100, corner_radius=10)
        self.image_label.pack(pady=15, padx=20, fill="x")
        
        self.import_btn = ctk.CTkButton(self.form_frame, text="Import Car Image", command=self.import_image, fg_color="#2874A6")
        self.import_btn.pack(pady=5, padx=20, fill="x")

        # Action Buttons
        self.add_btn = ctk.CTkButton(self.form_frame, text="Add New Car", command=self.save_car, fg_color="#1E8449")
        self.add_btn.pack(pady=(20, 5), padx=20, fill="x")

        self.update_btn = ctk.CTkButton(self.form_frame, text="Update Selected", command=self.update_car, state="disabled")
        self.update_btn.pack(pady=5, padx=20, fill="x")

        self.clear_btn = ctk.CTkButton(self.form_frame, text="Clear Form", command=self.clear_entries, fg_color="gray")
        self.clear_btn.pack(pady=5, padx=20, fill="x")

        self.delete_btn = ctk.CTkButton(self.form_frame, text="Delete Vehicle", fg_color="#922B21", command=self.delete_car)
        self.delete_btn.pack(pady=(20, 5), padx=20, fill="x")

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        cols = ("ID", "Brand", "Model", "Year", "Plate", "Price", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show='headings')
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "ID" else 50)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_car_select) # Bind selection event
        
        self.load_cars()

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.form_frame, placeholder_text=placeholder)
        entry.pack(pady=10, padx=20, fill="x")
        return entry

    # --- LOGIC ---

    def import_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.image_path = file_path
            filename = os.path.basename(file_path)
            self.image_label.configure(text=f"Image: {filename[:20]}...")

    def on_car_select(self, event):
        """Triggered when a row is clicked - fills the form for editing"""
        selected = self.tree.selection()
        if not selected: return

        values = self.tree.item(selected[0])['values']
        self.selected_car_id = values[0]
        
        # Find car in DB to get full data (like image path)
        car = cars_collection.find_one({"_id": ObjectId(self.selected_car_id)})
        
        if car:
            self.clear_entries(reset_id=False)
            self.brand_entry.insert(0, car.get('brand', ''))
            self.model_entry.insert(0, car.get('model', ''))
            self.year_entry.insert(0, car.get('year', ''))
            self.plate_entry.insert(0, car.get('plate_number', ''))
            self.price_entry.insert(0, str(car.get('price', '')))
            self.status_var.set(car.get('status', 'Available'))
            self.image_path = car.get('image', '')
            
            if self.image_path:
                self.image_label.configure(text=f"Existing Image Loaded")
            
            self.update_btn.configure(state="normal")
            self.add_btn.configure(state="disabled")

    def save_car(self):
        """Adds a new car to MongoDB"""
        data = self.get_form_data()
        if data:
            cars_collection.insert_one(data)
            messagebox.showinfo("Success", "New vehicle added")
            self.load_cars()
            self.clear_entries()

    def update_car(self):
        """Updates the currently selected car"""
        if not self.selected_car_id: return
        
        data = self.get_form_data()
        if data:
            cars_collection.update_one({"_id": ObjectId(self.selected_car_id)}, {"$set": data})
            messagebox.showinfo("Success", "Vehicle updated successfully")
            self.load_cars()
            self.clear_entries()

    def get_form_data(self):
        try:
            return {
                "brand": self.brand_entry.get(),
                "model": self.model_entry.get(),
                "year": self.year_entry.get(),
                "plate_number": self.plate_entry.get(),
                "price": float(self.price_entry.get()),
                "status": self.status_var.get(),
                "image": self.image_path
            }
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return None

    def load_cars(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for car in cars_collection.find():
            self.tree.insert("", "end", values=(
                str(car["_id"]), car.get("brand"), car.get("model"), 
                car.get("year"), car.get("plate_number"), f"${car.get('price')}", 
                car.get("status")
            ))

    def delete_car(self):
        if not self.selected_car_id: return
        if messagebox.askyesno("Confirm", "Delete this vehicle?"):
            cars_collection.delete_one({"_id": ObjectId(self.selected_car_id)})
            self.load_cars()
            self.clear_entries()

    def clear_entries(self, reset_id=True):
        if reset_id:
            self.selected_car_id = None
            self.update_btn.configure(state="disabled")
            self.add_btn.configure(state="normal")
        
        self.brand_entry.delete(0, 'end')
        self.model_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.plate_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.image_path = ""
        self.image_label.configure(text="No Image Selected")