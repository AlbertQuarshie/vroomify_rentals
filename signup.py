import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection
from datetime import datetime


class SignupApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Vroomify Rentals - Sign Up")
        self.geometry("400x650")

        self.title_label = ctk.CTkLabel(
            self,
            text="Create Account",
            font=("Arial", 24)
        )
        self.title_label.pack(pady=20)

        self.fullname_entry = ctk.CTkEntry(
            self,
            placeholder_text="Full Name",
            width=300
        )
        self.fullname_entry.pack(pady=10)

        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            width=300
        )
        self.username_entry.pack(pady=10)

        self.email_entry = ctk.CTkEntry(
            self,
            placeholder_text="Email",
            width=300
        )
        self.email_entry.pack(pady=10)

        # =========================
        # PHONE NUMBER
        # =========================
        self.phone_entry = ctk.CTkEntry(
            self,
            placeholder_text="Phone Number",
            width=300
        )
        self.phone_entry.pack(pady=10)

        # =========================
        # PASSWORD
        # =========================
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            width=300
        )
        self.password_entry.pack(pady=10)

        # =========================
        # CONFIRM PASSWORD
        # =========================
        self.confirm_password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Confirm Password",
            show="*",
            width=300
        )
        self.confirm_password_entry.pack(pady=10)

        self.signup_button = ctk.CTkButton(
            self,
            text="Sign Up",
            command=self.register_user,
            width=300
        )
        self.signup_button.pack(pady=20)


    def register_user(self):

        full_name = self.fullname_entry.get()
        username = self.username_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if (
            full_name == "" or
            username == "" or
            email == "" or
            phone == "" or
            password == "" or
            confirm_password == ""
        ):
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        existing_user = users_collection.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })

        if existing_user:
            messagebox.showerror(
                "Error",
                "Username or Email already exists"
            )
            return

        user_data = {
            "full_name": full_name,
            "username": username,
            "email": email,
            "phone": phone,
            "password": password,
            "role": "user",
            "created_at": datetime.now()
        }

        users_collection.insert_one(user_data)

        messagebox.showinfo(
            "Success",
            "Account created successfully"
        )

    
        self.fullname_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")



if __name__ == "__main__":
    app = SignupApp()
    app.mainloop()