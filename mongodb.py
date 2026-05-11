from pymongo import MongoClient

# Connection string
client = MongoClient("mongodb+srv://albejquarshie_db_user:bimVT2PLuZGLOtS8@vroomify.fzlbwnh.mongodb.net/?appName=vroomify")

# database
db = client["vroomify"]

# Collections
users_collection = db["users"]
cars_collection = db["cars"]
customers_collection = db["customers"]
rentals_collection = db["rentals"]

# Connection test
try:
    client.admin.command("ping")
    print("Connected to MongoDB successfully")
except Exception as e:
    print("MongoDB connection failed:", e)