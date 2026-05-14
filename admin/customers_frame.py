import customtkinter as ctk
from tkinter import messagebox
from mongodb import users_collection

class CustomersFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Header
        ctk.CTkLabel(self, text="Enrolled Customers", font=("Arial", 32, "bold")).pack(pady=(10, 20))
        
        # Container for the grid
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20)

        # 1. Table Header (Fixed at the top)
        self.create_table_header()

        # 2. Scrollable Area for Data
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Configure columns for the scroll frame to match header
        self.scroll_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="column")

        self.load_customers()

    def create_table_header(self):
        header_frame = ctk.CTkFrame(self.main_container, fg_color="gray20", height=45)
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Column weights must match the rows below for alignment
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="column")

        headers = ["Full Name", "Email Address", "ID Number", "Phone", "Status"]
        for i, text in enumerate(headers):
            lbl = ctk.CTkLabel(header_frame, text=text, font=("Arial", 14, "bold"), text_color="#3498DB")
            lbl.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

    def load_customers(self):
        """Fetches all users with the 'user' role and displays them in a grid"""
        try:
            # Clear existing data
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()

            # Query database
            customers = list(users_collection.find({"role": "user"}))

            if not customers:
                ctk.CTkLabel(self.scroll_frame, text="No registered customers found.", font=("Arial", 16)).grid(row=0, column=0, columnspan=5, pady=50)
                return

            for i, user in enumerate(customers):
                # Zebra striping for readability
                bg_color = "#2E2E2E" if i % 2 == 0 else "transparent"
                
                row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, corner_radius=0)
                row_frame.pack(fill="x")
                row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="column")

                # Data extraction
                name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
                email = user.get("email", "N/A")
                id_no = user.get("id_number", "N/A")
                phone = user.get("phone", "N/A")

                # Grid items
                ctk.CTkLabel(row_frame, text=name, font=("Arial", 13)).grid(row=0, column=0, padx=10, pady=12)
                ctk.CTkLabel(row_frame, text=email, font=("Arial", 13)).grid(row=0, column=1, padx=10, pady=12)
                ctk.CTkLabel(row_frame, text=id_no, font=("Arial", 13)).grid(row=0, column=2, padx=10, pady=12)
                ctk.CTkLabel(row_frame, text=phone, font=("Arial", 13)).grid(row=0, column=3, padx=10, pady=12)
                
                status_lbl = ctk.CTkLabel(row_frame, text="● Active", text_color="#2ecc71", font=("Arial", 13, "bold"))
                status_lbl.grid(row=0, column=4, padx=10, pady=12)

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve customers: {e}")