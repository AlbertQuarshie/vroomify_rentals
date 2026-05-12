import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection

class SignupApp(ctk.CTk):
    def __init__(self, on_back_to_login):
        super().__init__()
        self.on_back_to_login = on_back_to_login

        self.title("Vroomify Rentals - Sign Up")
        self.geometry("400x500")

        ctk.CTkLabel(self, text="Create Account", font=("Arial", 24)).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Choose Username", width=200)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Choose Password", show="*", width=200)
        self.password_entry.pack(pady=10)

        # Register Button
        ctk.CTkButton(self, text="Register", command=self.register_user).pack(pady=20)

        # Back to Login
        ctk.CTkButton(
            self, 
            text="Back to Login", 
            fg_color="transparent",
            command=self.go_back
        ).pack(pady=10)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Fields cannot be empty")
            return

        # Check if user already exists
        if users_collection.find_one({"username": username}):
            messagebox.showerror("Error", "Username already taken")
            return

        # Insert new user with default 'user' role
        users_collection.insert_one({
            "username": username,
            "password": password,
            "role": "user"
        })

        messagebox.showinfo("Success", "Account created! Please login.")
        self.go_back()

    def go_back(self):
        self.destroy()
        self.on_back_to_login()