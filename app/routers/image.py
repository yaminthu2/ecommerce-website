from fastapi import APIRouter,File,Form,UploadFile,HTTPException,status
import os
from ..database.mongodb import image_collection
import hashlib
from datetime import datetime


route=APIRouter()

file_dir="static"
category_dir="assets/category"
product_dir="assets/product"

@route.post("/")
async def upload_image(name:str=Form(...),file:UploadFile=File(...),category:str=Form(None),product:str=Form(None)):
    image_format=["image/jpeg","image/png"]
    file_format=file.headers.get("content-type")
    if  file_format not in image_format:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Upload valid image file type")
    
    file_read=await file.read()
    checksum=hashlib.md5(file_read).hexdigest()
    image_document=image_collection.find_one({"checksum":checksum})
    if image_document:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate image file")
    
    if category:
        file_path=category_dir
    elif product:
        file_path=product_dir
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify either 'category' or 'product'")
    
    path=os.path.join(file_dir,file_path)
    os.makedirs(path,exist_ok=True)
    
    current_time=datetime.now().strftime("%d-%b-%Y-%I:%M%p")#create datetime
    file_name,extension=os.path.splitext(file.filename)#split the file name 
    new_filename = f"{file_name}-{current_time}{extension}"#create new file name {origin name}{datetime}{.jpeg or .png}
    file_location=os.path.join(path,new_filename)
    with open(file_location,"wb") as f:
        f.write(file_read)
    database_path=os.path.join(file_path,new_filename)
    image_collection.insert_one({"name":name,"checksum":checksum,"img_url":database_path})
    return{"detail":"Successful image upload"}
   
   



   
        

    
