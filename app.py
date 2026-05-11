import customtkinter as ctk
from login import LoginApp

def start_app():
    app = LoginApp()
    app.mainloop()


if __name__ == "__main__":
    start_app()