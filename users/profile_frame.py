import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection

class ProfileFrame(ctk.CTkFrame):
    def __init__(self, master, username):
        # We use fg_color="transparent" so it blends into the main dashboard area
        super().__init__(master, fg_color="transparent")
        self.username = username
        self.load_profile_data()

    def load_profile_data(self):
        """Fetches user data from MongoDB and builds the UI"""
        try:
            # Finding the user document where first_name matches the logged-in username
            user_data = users_collection.find_one({"first_name": self.username})

            if not user_data:
                ctk.CTkLabel(self, text="User profile not found.", font=("Arial", 16)).pack(pady=50)
                return

            # Header
            ctk.CTkLabel(self, text="My Profile", font=("Arial", 28, "bold")).pack(pady=(20, 30))

            # Main Card Container
            profile_card = ctk.CTkFrame(self, corner_radius=15)
            profile_card.pack(pady=10, padx=40, fill="x")

            # Data mapping for display
            # These keys match the fields used during registration
            info_to_display = [
                ("First Name", user_data.get("first_name", "N/A")),
                ("Last Name", user_data.get("last_name", "N/A")),
                ("Email Address", user_data.get("email", "N/A")),
                ("ID Number", user_data.get("id_number", "N/A")),
                ("Phone Number", user_data.get("phone", "N/A")),
                ("Account Role", user_data.get("role", "user").upper())
            ]

            # Dynamically create rows for each piece of information
            for label_text, value_text in info_to_display:
                row = ctk.CTkFrame(profile_card, fg_color="transparent")
                row.pack(fill="x", pady=12, padx=25)
                
                ctk.CTkLabel(row, text=f"{label_text}:", font=("Arial", 14, "bold"), width=150, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=str(value_text), font=("Arial", 14)).pack(side="left", padx=10)

            # Footer Action Button
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