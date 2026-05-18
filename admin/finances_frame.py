import customtkinter as ctk
from tkinter import messagebox
from mongodb import rentals_collection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FinancesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Header matching your layout
        ctk.CTkLabel(self, text="Financial Analytics", font=("Arial", 32, "bold")).pack(pady=(10, 20))
        
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_dashboard()

    def load_dashboard(self):
        try:
            # Clear old elements if reloading
            for widget in self.container.winfo_children():
                widget.destroy()

            # Fetch only completed rentals
            completed_rentals = list(rentals_collection.find({"status": "Completed"}))
            
            total_revenue = sum(float(r.get("total_price", 0)) for r in completed_rentals)
            total_count = len(completed_rentals)
            avg_rev = total_revenue / total_count if total_count > 0 else 0

            # Building KPI Section
            kpi_frame = ctk.CTkFrame(self.container, fg_color="transparent")
            kpi_frame.pack(fill="x", pady=10)

            self.create_kpi_card(kpi_frame, "Total Revenue", f"KES {total_revenue:,.2f}", "#239B56", 0)
            self.create_kpi_card(kpi_frame, "Avg. Per Rental", f"KES {avg_rev:,.2f}", "#2E86C1", 1)
            self.create_kpi_card(kpi_frame, "Completed Deals", str(total_count), "#D35400", 2)

            # Process chart data with correct database key mappings
            model_data = {}
            for r in completed_rentals:
                # Expands fallback chain to explicitly check for the key 'model' first
                model = r.get("model") or r.get("car_model") or r.get("model_name") or "Unknown Model"
                model_data[model] = model_data.get(model, 0) + float(r.get("total_price", 0))

            if model_data:
                charts_frame = ctk.CTkFrame(self.container, fg_color="transparent")
                charts_frame.pack(fill="both", expand=True, pady=20)
                charts_frame.columnconfigure((0, 1), weight=1)

                # Bar Chart Container
                bar_con = ctk.CTkFrame(charts_frame, fg_color="#2B2B2B", corner_radius=15)
                bar_con.grid(row=0, column=0, padx=10, sticky="nsew")
                self.create_bar_chart(bar_con, list(model_data.keys()), list(model_data.values()))

                # Pie Chart Container
                pie_con = ctk.CTkFrame(charts_frame, fg_color="#2B2B2B", corner_radius=15)
                pie_con.grid(row=0, column=1, padx=10, sticky="nsew")
                self.create_pie_chart(pie_con, list(model_data.keys()), list(model_data.values()))
            else:
                ctk.CTkLabel(self.container, text="No completed sales found to chart.").pack(pady=50)

        except Exception as e:
            messagebox.showerror("Finance Error", f"Could not load sales data: {e}")

    def create_kpi_card(self, master, title, value, color, col):
        card = ctk.CTkFrame(master, fg_color=color, corner_radius=12, height=100)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        master.columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=title, font=("Arial", 14)).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold")).pack(pady=(0, 15))

    def create_bar_chart(self, master, labels, values):
        clean_labels = [str(l) for l in labels]
        clean_values = [float(v) for v in values]

        # Explicitly close previous active global plots to stop Tk memory leaks
        plt.close('all')

        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax.set_facecolor('#2B2B2B')
        
        ax.bar(clean_labels, clean_values, color='#3498DB')
        ax.set_title("Revenue by Model", color="white", fontsize=12, pad=10)
        
        ax.tick_params(colors='white', labelsize=8)
        for s in ax.spines.values(): 
            s.set_color('white')
            
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_pie_chart(self, master, labels, values):
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        ax.set_facecolor('#2B2B2B')
        
        ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%', 
            textprops={'color': "w"}, 
            colors=['#1ABC9C', '#3498DB', '#9B59B6', '#E67E22', '#F1C40F']
        )
        ax.set_title("Market Share", color="white", fontsize=12, pad=10)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)