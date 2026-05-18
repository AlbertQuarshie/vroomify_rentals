import customtkinter as ctk
from tkinter import messagebox
from mongodb import db, rentals_collection, cars_collection
from bson.objectid import ObjectId
import math

car_models_col = db["car_models"]

class RentalApprovalsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # --- PAGINATION & FILTER STATES ---
        self.current_page = 1
        self.items_per_page = 5  
        self.current_filter = "All"  # Default filter state

        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame, text="Rental History & Approvals", 
            font=("Arial", 26, "bold"), text_color="#3498DB"
        ).pack(side="left")

        # --- FILTER CONTROL BAR ---
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(filter_frame, text="Filter Status:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))

        self.filter_buttons = ctk.CTkSegmentedButton(
            filter_frame,
            values=["All", "Pending", "Active", "Completed", "Rejected"],
            command=self.change_filter
        )
        self.filter_buttons.set("All")  # Initialize with 'All' active
        self.filter_buttons.pack(side="left", fill="x", expand=True)

        # Scrollable container for cards
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # --- BOTTOM PAGINATION NAVIGATION BAR ---
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", side="bottom", pady=15, padx=20)

        self.prev_btn = ctk.CTkButton(
            self.pagination_frame, text="◀ Previous", width=100, command=self.prev_page
        )
        self.prev_btn.pack(side="left")

        self.page_label = ctk.CTkLabel(
            self.pagination_frame, text="Page 1 of 1", font=("Arial", 14, "bold")
        )
        self.page_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            self.pagination_frame, text="Next ▶", width=100, command=self.next_page
        )
        self.next_btn.pack(side="right")

        self.load_requests()

    def change_filter(self, selection):
        """Callback when an admin changes the segmented filter buttons"""
        self.current_filter = selection
        self.current_page = 1  # Reset to page 1 on filter switch to prevent boundary bugs
        self.load_requests()

    def load_requests(self):
        """Clears, filters, sorts, and paginates records dynamically"""
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        # 1. Fetch data based on the chosen filter
        if self.current_filter == "All":
            db_query = {}
        else:
            db_query = {"status": self.current_filter}

        all_rentals = list(rentals_collection.find(db_query))

        if not all_rentals:
            # Clear pagination UI if zero records match the active filter criteria
            self.page_label.configure(text="Page 1 of 1")
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            
            ctk.CTkLabel(
                self.scroll_container, 
                text=f"No {self.current_filter.lower()} rental records found.", 
                font=("Arial", 16), text_color="gray"
            ).pack(pady=50)
            return

        # 2. Map statuses to weights for global custom sorting logic
        status_order = {
            "Pending": 1,
            "Active": 2,
            "Completed": 3,
            "Rejected": 4
        }

        # 3. Python Stable Multi-Pass Sorting (Newest date first, then grouped by priority)
        all_rentals.sort(key=lambda x: x.get("booking_date") if x.get("booking_date") else "", reverse=True) 
        all_rentals.sort(key=lambda x: status_order.get(x.get("status", "Pending"), 5)) 

        # 4. Process Pagination Limits based on the FILTERED data size
        total_records = len(all_rentals)
        total_pages = max(1, math.ceil(total_records / self.items_per_page))
        
        if self.current_page > total_pages:
            self.current_page = total_pages

        # 5. Slice the record list array for the active page view
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        paginated_rentals = all_rentals[start_index:end_index]

        # 6. Update Bottom Navigation Layout
        self.page_label.configure(text=f"Page {self.current_page} of {total_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")

        # 7. Generate UI Cards
        for request in paginated_rentals:
            self.create_request_card(request)

    def create_request_card(self, r):
        """Creates an individual card for a rental request with context-aware actions"""
        status = r.get("status", "Pending")

        border_colors = {
            "Pending": "#F39C12",
            "Active": "#1E8449",
            "Rejected": "#922B21",
            "Completed": "#5D6D7E"
        }
        card_border = border_colors.get(status, "#555")

        card = ctk.CTkFrame(self.scroll_container, corner_radius=15, border_width=1, border_color=card_border)
        card.pack(fill="x", padx=20, pady=10)

        # Left Info Section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=20, pady=15)

        car_name = f"{r.get('brand', 'Unknown')} {r.get('model', 'Car')} ({r.get('year', 'N/A')})"
        ctk.CTkLabel(info_frame, text=car_name, font=("Arial", 18, "bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Customer: {r.get('username', 'N/A')}", text_color="#BDC3C7").pack(anchor="w")
        
        try:
            date_str = r['booking_date'].strftime("%Y-%m-%d %H:%M")
        except:
            date_str = str(r.get('booking_date', 'N/A'))
        ctk.CTkLabel(info_frame, text=f"Requested on: {date_str}", font=("Arial", 11)).pack(anchor="w")

        # Middle Price Section
        price_frame = ctk.CTkFrame(card, fg_color="transparent")
        price_frame.pack(side="left", padx=40)
        
        ctk.CTkLabel(price_frame, text=f"{r.get('days', 0)} Days", font=("Arial", 14)).pack()
        ctk.CTkLabel(price_frame, text=f"Total: KES {r.get('total_price', 0.0):.2f}", font=("Arial", 18, "bold"), text_color="#2ECC71").pack()

        # Right Action Section
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=20)

        if status == "Pending":
            ctk.CTkButton(
                right_frame, text="Approve", fg_color="#1E8449", hover_color="#145A32", width=100,
                command=lambda rent=r: self.approve_request(rent)
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                right_frame, text="Reject", fg_color="#922B21", hover_color="#641E16", width=100,
                command=lambda rent=r: self.reject_request(rent)
            ).pack(side="left", padx=5)
        else:
            badge_colors = {
                "Active": ("#E8F8F5", "#1E8449"),
                "Rejected": ("#FDEDEC", "#922B21"),
                "Completed": ("#EAECEE", "#2C3E50")
            }
            bg_c, text_c = badge_colors.get(status, ("gray20", "white"))

            ctk.CTkLabel(
                right_frame, 
                text=status.upper(), 
                font=("Arial", 12, "bold"),
                fg_color=text_c, 
                text_color="white",
                corner_radius=6,
                padx=15, 
                pady=6
            ).pack()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_requests()

    def next_page(self):
        self.current_page += 1
        self.load_requests()

    def approve_request(self, rental):
        """Standard Approval Logic"""
        car_unit = cars_collection.find_one({
            "model_id": rental["model_id"], 
            "status": "Available"
        })
        
        if not car_unit:
            messagebox.showerror("Inventory Error", "No physical assigned units available to allocate!")
            return

        rentals_collection.update_one({"_id": rental["_id"]}, {
            "$set": {
                "status": "Active", 
                "car_id": car_unit["_id"], 
                "plate_number": car_unit["plate_number"]
            }
        })
        cars_collection.update_one({"_id": car_unit["_id"]}, {"$set": {"status": "Rented"}})
        car_models_col.update_one({"_id": rental["model_id"]}, {"$inc": {"available_count": -1}})

        messagebox.showinfo("Success", f"Approved! Assigned Plate: {car_unit['plate_number']}")
        self.load_requests()

    def reject_request(self, rental):
        """Standard Rejection Logic"""
        if messagebox.askyesno("Confirm", f"Reject {rental['username']}'s request?"):
            rentals_collection.update_one({"_id": rental["_id"]}, {"$set": {"status": "Rejected"}})
            self.load_requests()