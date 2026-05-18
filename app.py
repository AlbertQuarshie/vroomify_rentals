import customtkinter as ctk
from login import LoginApp
from signup import SignupApp
from admin.admin_dashboard import AdminDashboard
from users.user_dashboard import UserDashboard

class LandingPage(ctk.CTkFrame):
    def __init__(self, master, on_login, on_signup):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="VROOMIFY", font=("Arial", 40, "bold"), text_color="#3498DB").pack(pady=(120, 10))
        ctk.CTkLabel(self, text="Premium Car Rental Management System", font=("Arial", 16)).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=40)
        
        ctk.CTkButton(btn_frame, text="Login", width=180, height=45, command=on_login).grid(row=0, column=0, padx=15)
        ctk.CTkButton(btn_frame, text="Sign Up", width=180, height=45, fg_color="transparent", border_width=2, command=on_signup).grid(row=0, column=1, padx=15)

class VroomifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vroomify Car Rentals")
        self.current_page = None
        self.show_landing()

    def switch_page(self, page_class, is_auth_screen=False, *args, **kwargs):
        """Safely swaps frames, resizes the window, and toggles maximize functionality"""
        if self.current_page:
            self.current_page.destroy()

        # Target dimensions based on screen type
        if is_auth_screen:
            width, height = 520, 600
            self.resizable(False, False)  
        else:
            width, height = 1100, 750
            self.resizable(True, True)

        # Center the window on the user's screen monitor
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (width / 2))
        y_coordinate = int((screen_height / 2) - (height / 2))
        
        self.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

        # Mount the incoming view
        self.current_page = page_class(self, *args, **kwargs)
        self.current_page.pack(fill="both", expand=True)

    def show_landing(self):
        self.switch_page(LandingPage, is_auth_screen=True, on_login=self.show_login, on_signup=self.show_signup)

    def show_login(self):
        self.switch_page(LoginApp, is_auth_screen=True, on_success=self.enter_dashboard, on_signup_request=self.show_signup)

    def show_signup(self):
        self.switch_page(SignupApp, is_auth_screen=True, on_back_to_login=self.show_login)

    def enter_dashboard(self, role, username):
        if role == "admin":
            self.switch_page(AdminDashboard, is_auth_screen=False, on_logout=self.show_landing)
        else:
            self.switch_page(UserDashboard, is_auth_screen=False, username=username, on_logout=self.show_landing)

if __name__ == "__main__":
    app = VroomifyApp()
    app.mainloop()