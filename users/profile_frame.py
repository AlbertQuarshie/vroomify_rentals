import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection

class ProfileFrame(ctk.CTkFrame):
    def __init__(self, master, username):
        super().__init__(master, fg_color="transparent")
        self.username = username
        self.load_profile_data()

    def load_profile_data(self):
        """Pulls metadata values linked to active user index profiles from MongoDB"""
        try:
            user_data = users_collection.find_one({"first_name": self.username})

            if not user_data:
                ctk.CTkLabel(self, text="User profile not found.", font=("Arial", 16)).pack(pady=50)
                return

            # Main header strings
            ctk.CTkLabel(self, text="My Profile", font=("Arial", 28, "bold")).pack(pady=(20, 30))

            # Display card shell wrapper
            profile_card = ctk.CTkFrame(self, corner_radius=15)
            profile_card.pack(pady=10, padx=40, fill="x")

            # Content keys row matrix declarations
            info_to_display = [
                ("First Name", user_data.get("first_name", "N/A")),
                ("Last Name", user_data.get("last_name", "N/A")),
                ("Email Address", user_data.get("email", "N/A")),
                ("ID Number", user_data.get("id_number", "N/A")),
                ("Phone Number", user_data.get("phone", "N/A")),
                ("Account Role", user_data.get("role", "user").upper())
            ]

            # Matrix loop display item injection steps
            for label_text, value_text in info_to_display:
                row = ctk.CTkFrame(profile_card, fg_color="transparent")
                row.pack(fill="x", pady=12, padx=25)
                
                ctk.CTkLabel(row, text=f"{label_text}:", font=("Arial", 14, "bold"), width=150, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=str(value_text), font=("Arial", 14)).pack(side="left", padx=10)

            # Form interaction console buttons widgets
            ctk.CTkButton(
                self, 
                text="Edit Profile Information", 
                width=200, 
                height=40,
                fg_color="#3498DB",
                command=lambda: messagebox.showinfo("Profile", "Edit feature coming soon!")
            ).pack(pady=40)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile: {e}")