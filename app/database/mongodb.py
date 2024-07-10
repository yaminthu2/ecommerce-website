from pymongo import MongoClient
from fastapi import HTTPException,status
try:
    client=MongoClient("mongodb+srv://yaminthu2:Abc666%40%40@cluster0.yw8wpik.mongodb.net/")

    db=client["ecommerce"]

    collection=db["users"]
    
    category_collection=db["categories"]
    product_collection=db["products"]
    image_collection=db["images"]
    # checkout_collection=db["checkout"]
    checkout_collection=db["checkouts"]
   



except:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="database connection error")