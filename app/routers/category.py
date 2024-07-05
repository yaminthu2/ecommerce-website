from fastapi import APIRouter,status,HTTPException,Depends
from pydantic import BaseModel,field_validator
from ..database.mongodb import category_collection
from bson import ObjectId,DBRef
from .authentication import user_data
from ..utilities.derefrence import category_derefrence,image_derefrence


route=APIRouter()

class Category(BaseModel):
    name:str
    parent:str=None
    image:str

    @field_validator("*")
    def get_strip(cls,value):
        return value.strip()
        
# create category data 
@route.post("/",status_code=status.HTTP_201_CREATED)
def carete_category(category:Category):
   category=category.model_dump()
   if category["parent"]:
       category["parent"]= DBRef("categories",ObjectId(category["parent"]),"ecommerce")
   category["image"]=DBRef("images",ObjectId(category["image"]),"ecommerce")
   
   result=category_collection.insert_one(category)
   category["_id"]=str(result.inserted_id)
   return{"detail":"Successful create category"}

#find all categories 
@route.get("/",status_code=status.HTTP_200_OK)
def get_all_categories(user=Depends(user_data)):
    cursor_obj=category_collection.find({})
    categories=[]
    for category in cursor_obj:
        category["_id"]=str(category["_id"])
        if category["parent"]:
            category["parent"]=category_derefrence(category["parent"])
        category["image"]=image_derefrence(category["image"])
        categories.append(category)
    return categories
  
#find parentId
@route.get("/parentId",status_code=status.HTTP_200_OK)
def get_parent(user=Depends(user_data)):
    cursor_obj=category_collection.find({"parent":None})
    categories=[]
    for category in cursor_obj:
        category["_id"]=str(category["_id"])
        category["image"]=image_derefrence(category["image"])
        categories.append(category)
    return categories
    
#find one data
@route.get("/{id}",status_code=status.HTTP_200_OK)
def get_one_category(id:str):
    id=id.strip()
    if len(id) !=24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please must be enter 24 character Id")
    category=category_collection.find_one({"_id":ObjectId(id)})
    if category==None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category object Id")
    category["_id"]=str(category["_id"])
    if category["parent"]:
        category["parent"]=category_derefrence(category["parent"])
    category["image"]=image_derefrence(category["image"])
    return category

#category update
@route.put("/{id}",status_code=status.HTTP_200_OK)
def update_category(id:str,data:Category):
    id=id.strip()
    if  len(id) !=24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please must be enter 24 character Id")
    data=data.model_dump()
    if data["parent"]:
        data["parent"]=DBRef("categories",ObjectId(data["parent"]),"ecommerce")
    data["image"]=DBRef("images",ObjectId(data["image"]),"ecommerce")
    update_data=category_collection.update_one({"_id":ObjectId(id)},{"$set":data})
    if update_data.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category object Id")
    return{"detail":"Successful update"}

#delete of category
@route.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete(id:str):
    category=category_collection.find_one({"_id":ObjectId(id.strip())})
    if category==None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Id")
    category_collection.delete_one({"_id":ObjectId(id.strip())})
    

    
    
   





    



    
    
    
