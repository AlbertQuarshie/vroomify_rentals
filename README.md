# VROOMIFY RENTALS

## A. Contributor

- **Albert Junior Quarshie**

## B. Overview

- A car renting platform whereby users log in and proceed to rent a vehicle of their choosing at the selected duration and price


### C. Installation

- Follow these steps to set up and run the project locally:

1. Clone the Repository

```bash
git clone https://github.com/AlbertQuarshie/vroomify_rentals.git
cd vroomify_rentals
```
2. Install the following imports:

```bash
pip install customtkinter
pip install pymongo
pip install pillow
```

2. Run the Application

- The project requires Python 3.14 or later.

```bash
python app.py
```

### D. Usage

1. Launch the App
-  Run the Python file.
- You’ll be prompted to login and if you don't have an account you have to register

2. Browse a variety of available cars

- You can use the search query to search and also sort the cars by name, price, year of manufacture etc

3. Book the car of your choice

- After selecting the desired car you need you can proceed to place a rental request of which it will need the approval of the system admin.

### E. Features

1. Personalized  User Dashboard

- The client-facing side of VROOMIFY focuses on an intuitive, fluid interface for customers looking to discover and secure car bookings.

2. GUI Architecture

- Utilizes Python's customtkinter with an optimized, non-blocking single-window layout framework (VroomifyApp) swapping contextual instances of ctk.CTkFrame components to prevent desktop clutter or multiple window spawns.

3. Database Design

- NoSQL backend structure leveraging MongoDB aggregation pipelines to efficiently sum and group real-time metrics (like processing $sum conditions for active financial balances or counting targeted documentation states).

4. Rental Approvals Pipeline

- An administrative verification queue to safely audit incoming customer booking files and toggle statuses between pending flags and approved checkouts.

## F. Tech Stack

| Layer           | Technology     |
| ----------------| -------------- |
| Environment     | Python 3.14.4  |
| GUI             | Custom Tkinter |
| Database        | Mongodb        |
| Charts          | Matplottb      |
| Image Processing|  Pillow        |  
