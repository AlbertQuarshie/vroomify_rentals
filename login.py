import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection

class LoginApp(ctk.CTk):
    def __init__(self, on_success, on_signup_request):
        super().__init__()
        self.on_success = on_success
        self.on_signup_request = on_signup_request

        self.title("Vroomify Rentals - Login")
        self.geometry("400x500")

        self.title_label = ctk.CTkLabel(self, text="Login", font=("Arial", 24))
        self.title_label.pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=200)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=200)
        self.password_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_btn.pack(pady=20)

        # Signup Link
        self.signup_label = ctk.CTkLabel(self, text="Don't have an account?")
        self.signup_label.pack(pady=(10, 0))
        
        self.signup_btn = ctk.CTkButton(
            self, 
            text="Create Account", 
            fg_color="transparent", 
            text_color=("black", "white"),
            hover_color=("gray70", "gray30"),
            command=self.on_signup_request # Triggers the switch in app.py
        )
        self.signup_btn.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required")
            return

        user = users_collection.find_one({"username": username, "password": password})

        if user:
            role = user.get("role", "user")
            messagebox.showinfo("Success", "Login successful")
            self.destroy()
            self.on_success(role, username)
        else:
            messagebox.showerror("Error", "Invalid username or password")