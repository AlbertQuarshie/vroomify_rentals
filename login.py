import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection
from admin.admin_dashboard import AdminDashboard

class LoginApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Vroomify Rentals - Login")
        self.geometry("400x450")

        # Title
        self.title_label = ctk.CTkLabel(self, text="Login", font=("Arial", 24))
        self.title_label.pack(pady=20)

        # Username
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        # Password
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        # Login Button
        self.login_btn = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_btn.pack(pady=20)

    def login(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "All fields are required")
            return

        # Check user in database
        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if user:
            role = user.get("role", "user")

            messagebox.showinfo("Success", "Login successful")

            self.destroy()

            if role == "admin":
                app = AdminDashboard()
                app.mainloop()
            else:
                app = UserDashboard(username)
                app.mainloop()

        else:
            messagebox.showerror("Error", "Invalid username or password")