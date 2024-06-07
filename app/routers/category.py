from fastapi import APIRouter,status,HTTPException,Depends
from pydantic import BaseModel,field_validator
from ..database.mongodb import category_collection
from bson import ObjectId
from .authentication import user_data

route=APIRouter()

class ParentCategory(BaseModel):
    name:str
    parent_id:str=""
    image_id:str

    @field_validator("*")
    def get_strip(cls,value):
        return value.strip()
        
# create category data 
@route.post("/",status_code=status.HTTP_201_CREATED)
def parent_category(category:ParentCategory,user=Depends(user_data)):
   category=category.model_dump()
   category_collection.insert_one(category)
   return{"detail":"Successful insert data"}

#take all data 
@route.get("/",status_code=status.HTTP_200_OK)
def get_all_data(user_id=Depends(user_data)):
    cursor_obj=category_collection.find({})
    datas=[]
    for data in cursor_obj:
        data["_id"]=str(data["_id"])
        datas.append(data)
        print("Testing")
    return datas
    


@route.get("/parentId",status_code=status.HTTP_200_OK)
def get_parent_id(user_id=Depends(user_data)):
    cursor_obj=category_collection.find({"parent_id":""})
    datas=[]
    for data in cursor_obj:
        data["_id"]=str(data["_id"])
        datas.append(data)
    return datas
    
#take one data
@route.get("/{id}",status_code=status.HTTP_200_OK)
def get_one_data(id:str,user_id=Depends(user_data)):
    id=id.strip()
    if len(id) !=24:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please must be enter 24 character Id")

    object_id=category_collection.find_one({"_id":ObjectId(id)})
    if object_id==None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid category object Id")
    object_id["_id"]=str(object_id["_id"])
    return object_id

@route.put("/{id}",status_code=status.HTTP_200_OK)
def update(id:str,data:ParentCategory,user_id=Depends(user_data)):
    id=id.strip()
    if  len(id) !=24:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please must be enter 24 character Id")
    update_data=category_collection.update_one({"_id":ObjectId(id)},{"$set":data.model_dump()})
    if update_data.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid category object Id")
    return{"detail":"Successful update"}

#delete of category
@route.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete(id:str,user_id=Depends(user_data)):
    category=category_collection.find_one({"_id":ObjectId(id.strip())})

    if category==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Id")
    category_collection.delete_one({"_id":ObjectId(id.strip())})
    

    
    
   





    



    
    
    
