import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection
from datetime import datetime

class SignupApp(ctk.CTk):
    def __init__(self, on_back_to_login):
        super().__init__()
        self.on_back_to_login = on_back_to_login

        self.title("Vroomify Rentals - Create Account")
        self.geometry("500x700")

        # Main Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=450, height=650)
        self.scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Sign Up", font=("Arial", 24, "bold")).pack(pady=20)

        # Input Fields
        self.first_name = ctk.CTkEntry(self.scroll_frame, placeholder_text="First Name", width=300)
        self.first_name.pack(pady=10)

        self.last_name = ctk.CTkEntry(self.scroll_frame, placeholder_text="Last Name", width=300)
        self.last_name.pack(pady=10)

        self.email = ctk.CTkEntry(self.scroll_frame, placeholder_text="Email Address", width=300)
        self.email.pack(pady=10)

        self.id_number = ctk.CTkEntry(self.scroll_frame, placeholder_text="Identification Number", width=300)
        self.id_number.pack(pady=10)

        self.phone = ctk.CTkEntry(self.scroll_frame, placeholder_text="Phone Number", width=300)
        self.phone.pack(pady=10)

        self.password = ctk.CTkEntry(self.scroll_frame, placeholder_text="Password", show="*", width=300)
        self.password.pack(pady=10)

        self.confirm_password = ctk.CTkEntry(self.scroll_frame, placeholder_text="Confirm Password", show="*", width=300)
        self.confirm_password.pack(pady=10)

        # Register Button
        self.register_btn = ctk.CTkButton(
            self.scroll_frame, 
            text="Create Account", 
            command=self.register_user, 
            width=300, 
            height=40
        )
        self.register_btn.pack(pady=20)

        # Back Button
        self.back_btn = ctk.CTkButton(
            self.scroll_frame, 
            text="Already have an account? Login", 
            fg_color="transparent", 
            command=self.go_back
        )
        self.back_btn.pack(pady=10)

    def register_user(self):
        # Gathering Data
        data = {
            "first_name": self.first_name.get(),
            "last_name": self.last_name.get(),
            "email": self.email.get(),
            "id_number": self.id_number.get(),
            "phone": self.phone.get(),
            "password": self.password.get(),
            "role": "user",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        confirm_pwd = self.confirm_password.get()

        # Validation
        if not all([data["first_name"], data["last_name"], data["email"], data["id_number"], data["phone"], data["password"]]):
            messagebox.showerror("Error", "All fields are required")
            return

        if data["password"] != confirm_pwd:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Check for existing email or ID
        if users_collection.find_one({"email": data["email"]}):
            messagebox.showerror("Error", "Email already registered")
            return
        
        if users_collection.find_one({"id_number": data["id_number"]}):
            messagebox.showerror("Error", "Identification Number already in use")
            return

        # Database Insertion
        try:
            users_collection.insert_one(data)
            messagebox.showinfo("Success", "Account created successfully!")
            self.go_back()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save user: {e}")

    def go_back(self):
        self.destroy()
        self.on_back_to_login()