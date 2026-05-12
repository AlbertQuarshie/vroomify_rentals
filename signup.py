import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection


class SignupApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Car Rental System - Sign Up")
        self.geometry("400x500")


        self.title_label = ctk.CTkLabel(
            self,
            text="Create Account",
            font=("Arial", 24)
        )
        self.title_label.pack(pady=20)


        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Username"
        )
        self.username_entry.pack(pady=10)

   
        self.email_entry = ctk.CTkEntry(
            self,
            placeholder_text="Email"
        )
        self.email_entry.pack(pady=10)

      
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*"
        )
        self.password_entry.pack(pady=10)

        self.confirm_password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Confirm Password",
            show="*"
        )
        self.confirm_password_entry.pack(pady=10)

 
        self.signup_button = ctk.CTkButton(
            self,
            text="Sign Up",
            command=self.register_user
        )
        self.signup_button.pack(pady=20)

    def register_user(self):

        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Empty field validation
        if username == "" or email == "" or password == "" or confirm_password == "":
            messagebox.showerror("Error", "All fields are required")
            return

        # Password match validation
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Check if username already exists
        existing_user = users_collection.find_one({
            "username": username
        })

        if existing_user:
            messagebox.showerror("Error", "Username already exists")
            return

        # Save user to MongoDB
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": "user"
        }

        users_collection.insert_one(user_data)

        messagebox.showinfo("Success", "Account created successfully")

        # Clear fields
        self.username_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")



if __name__ == "__main__":
    app = SignupApp()
    app.mainloop()