from fastapi import APIRouter,File,Form,UploadFile,HTTPException,status
import os
from ..database.mongodb import image_collection
import hashlib
# from datetime import datetime


route=APIRouter()

file_dir="static"
image_dir="assets"

@route.post("/")
async def upload_image(name:str=Form(...),file:UploadFile=File(...)):
  
    image_format=["image/jpeg","image/png"]
    file_format=file.headers.get("content-type")
    if  file_format not in image_format:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Enter the image file type")
    
    
    file_read=await file.read()
    checksum=hashlib.md5(file_read).hexdigest()
    document=image_collection.find_one({"checksum":checksum})
    if document:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Duplicate image file")
    file_path=os.path.join(file_dir,image_dir)
    os.makedirs(file_path,exist_ok=True)
    
    # current_time=datetime.now()
    # print(current_time)

    file_location=os.path.join(file_dir,image_dir,file.filename)
    with open(file_location,"wb") as f:
        f.write(file_read)
    database_path=os.path.join(image_dir,file.filename)
    image_collection.insert_one({"name":name,"checksum":checksum,"img_url":database_path})
    return{"detail":"Successful image upload"}
   



   
        

    
    
