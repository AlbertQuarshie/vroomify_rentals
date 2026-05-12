import customtkinter as ctk
from login import LoginApp
from signup import SignupApp 
from admin.admin_dashboard import AdminDashboard
from users.user_dashboard import UserDashboard

class VroomifyApp:
    def __init__(self):
        self.show_login()

    def show_login(self):
        # Pass both login success and signup request callbacks
        self.login_window = LoginApp(
            on_success=self.enter_dashboard,
            on_signup_request=self.show_signup
        )
        self.login_window.mainloop()

    def show_signup(self):
        self.login_window.destroy()
        self.signup_window = SignupApp(on_back_to_login=self.show_login)
        self.signup_window.mainloop()

    def enter_dashboard(self, role, username):
        if role == "admin":
            self.main_window = AdminDashboard()
        else:
            self.main_window = UserDashboard(username)
        self.main_window.mainloop()

if __name__ == "__main__":
    VroomifyApp()