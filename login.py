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

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email Address", width=250)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(self, text="Login", command=self.login, width=250)
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
            command=self.on_signup_request
        )
        self.signup_btn.pack(pady=5)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password")
            return

        # Query using email
        user = users_collection.find_one({
            "email": email, 
            "password": password
        })

        if user:
            role = user.get("role", "user")

            display_name = user.get("first_name", "User")
            
            messagebox.showinfo("Success", f"Welcome back, {display_name}!")
            self.destroy()
            self.on_success(role, display_name)
        else:
            messagebox.showerror("Error", "Invalid email or password")