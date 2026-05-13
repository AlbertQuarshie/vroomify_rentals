import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection
from datetime import datetime

class SignupApp(ctk.CTkFrame):
    def __init__(self, master, on_back_to_login):
        super().__init__(master) 
        self.on_back_to_login = on_back_to_login 

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=450, height=650) 
        self.scroll_frame.pack(pady=20, padx=20, fill="both", expand=True) 
        
        ctk.CTkLabel(self.scroll_frame, text="Sign Up", font=("Arial", 24, "bold")).pack(pady=20) 
        
        self.first_name = ctk.CTkEntry(self.scroll_frame, placeholder_text="First Name", width=300) 
        self.last_name = ctk.CTkEntry(self.scroll_frame, placeholder_text="Last Name", width=300) 
        self.email = ctk.CTkEntry(self.scroll_frame, placeholder_text="Email Address", width=300) 
        self.id_number = ctk.CTkEntry(self.scroll_frame, placeholder_text="Identification Number", width=300) 
        self.phone = ctk.CTkEntry(self.scroll_frame, placeholder_text="Phone Number", width=300) 
        self.password = ctk.CTkEntry(self.scroll_frame, placeholder_text="Password", show="*", width=300) 
        self.confirm_password = ctk.CTkEntry(self.scroll_frame, placeholder_text="Confirm Password", show="*", width=300) 
        
        self.register_btn = ctk.CTkButton(self.scroll_frame, text="Create Account", command=self.register_user, width=300, height=40) 
        self.register_btn.pack(pady=20)
        
        self.back_btn = ctk.CTkButton(self.scroll_frame, text="Already have an account? Login", fg_color="transparent", command=self.go_back) 
        self.back_btn.pack(pady=10)

    def register_user(self):
        data = {
            "first_name": self.first_name.get(), "last_name": self.last_name.get(),
            "email": self.email.get(), "id_number": self.id_number.get(),
            "phone": self.phone.get(), "password": self.password.get(),
            "role": "user", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        } 
        
        if not all([data["first_name"], data["last_name"], data["email"], data["id_number"], data["phone"], data["password"]]): 
            messagebox.showerror("Error", "All fields are required") 
            return 
        if data["password"] != self.confirm_password.get(): 
            messagebox.showerror("Error", "Passwords do not match") 
            return 
        if users_collection.find_one({"email": data["email"]}) or users_collection.find_one({"id_number": data["id_number"]}): 
            messagebox.showerror("Error", "User already exists") 
            return 
            
        try:
            users_collection.insert_one(data) 
            messagebox.showinfo("Success", "Account created successfully!") 
            self.go_back() 
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save user: {e}") 

    def go_back(self):
        self.on_back_to_login() 