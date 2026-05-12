import customtkinter as ctk
from tkinter import messagebox, ttk
from mongodb import cars_collection
from bson.objectid import ObjectId

class CarManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.form_frame = ctk.CTkScrollableFrame(self, width=300)
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.form_frame, text="Manage Vehicle", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.brand_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Brand (e.g. Toyota)")
        self.brand_entry.pack(pady=5, padx=10, fill="x")
        
        self.model_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Model (e.g. Camry)")
        self.model_entry.pack(pady=5, padx=10, fill="x")

        self.year_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Year of Manufacture")
        self.year_entry.pack(pady=5, padx=10, fill="x")

        self.plate_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Plate Number")
        self.plate_entry.pack(pady=5, padx=10, fill="x")
        
        self.price_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Price per Day ($)")
        self.price_entry.pack(pady=5, padx=10, fill="x")

        self.image_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Image URL or Path")
        self.image_entry.pack(pady=5, padx=10, fill="x")
        
        self.status_var = ctk.StringVar(value="Available")
        self.status_dropdown = ctk.CTkComboBox(self.form_frame, values=["Available", "Rented", "Maintenance"], variable=self.status_var)
        self.status_dropdown.pack(pady=10, padx=10, fill="x")
        
        # Action Buttons
        self.add_btn = ctk.CTkButton(self.form_frame, text="Add New Car", command=self.add_car)
        self.add_btn.pack(pady=5, padx=10, fill="x")
        
        self.delete_btn = ctk.CTkButton(self.form_frame, text="Delete Selected", fg_color="#922b21", command=self.delete_car)
        self.delete_btn.pack(pady=5, padx=10, fill="x")

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Define Columns matching your MongoDB schema
        columns = ("ID", "Brand", "Model", "Year", "Plate", "Price", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True)
        self.load_cars()

    # --- CRUD OPERATIONS ---

    def load_cars(self):
        """Refreshes the table with data from MongoDB"""
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        cars = cars_collection.find()
        for car in cars:
            self.tree.insert("", "end", values=(
                str(car["_id"]), 
                car.get("brand", ""), 
                car.get("model", ""), 
                car.get("year", ""),
                car.get("plate_number", ""),
                f"${car.get('price', 0)}", 
                car.get("status", "Available")
            ))

    def add_car(self):
        data = {
            "brand": self.brand_entry.get(),
            "model": self.model_entry.get(),
            "year": self.year_entry.get(),
            "plate_number": self.plate_entry.get(),
            "price": self.price_entry.get(),
            "status": self.status_var.get(),
            "image": self.image_entry.get()
        }

        if not all([data["brand"], data["model"], data["plate_number"], data["price"]]):
            messagebox.showerror("Error", "Required fields: Brand, Model, Plate, and Price")
            return

        try:
            data["price"] = float(data["price"])
            cars_collection.insert_one(data)
            messagebox.showinfo("Success", f"Car {data['plate_number']} added successfully")
            self.clear_entries()
            self.load_cars()
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")

    def delete_car(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a car from the table first")
            return
            
        car_id = self.tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this vehicle?"):
            cars_collection.delete_one({"_id": ObjectId(car_id)})
            self.load_cars()

    def clear_entries(self):
        """Clears the form after submission"""
        self.brand_entry.delete(0, 'end')
        self.model_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.plate_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.image_entry.delete(0, 'end')