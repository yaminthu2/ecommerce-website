from fastapi import APIRouter,status,HTTPException,Depends
from pydantic import BaseModel,field_validator
from ..database.mongodb import category_collection,image_collection
from bson import ObjectId,DBRef
from .authentication import user_data

route=APIRouter()

class ParentCategory(BaseModel):
    name:str
    parent:str=None
    image:str

    @field_validator("*")
    def get_strip(cls,value):
        return value.strip()
        
# create category data 
@route.post("/",status_code=status.HTTP_201_CREATED)
def carete_category(category:ParentCategory,user_id=Depends(user_data)):
   category=category.model_dump()
   if category["parent"]:
       category["parent"]= DBRef("categories",ObjectId(category["parent"]),"ecommerce")
   category["image"]=DBRef("images",ObjectId(category["image"]),"ecommerce")
   
   result=category_collection.insert_one(category)
   category["_id"]=str(result.inserted_id)
   return {"_id":category["_id"]}


    
#    return{"detail":"Successful insert data"}

#find all data 
@route.get("/",status_code=status.HTTP_200_OK)
def get_all_data(user_id=Depends(user_data)):
    cursor_obj=category_collection.find({})
    datas=[]
    for data in cursor_obj:
        data["_id"]=str(data["_id"])
       
        
        # derefrence the parent
        if isinstance(data.get("parent"), DBRef):
            parent_category = category_collection.find_one({"_id": data["parent"].id})
            data["parent"] = {"_id": str(parent_category["_id"]), "name": parent_category["name"]} if parent_category else None

        # Dereference the image field
        if isinstance(data.get("image"), DBRef):
            image_document = image_collection.find_one({"_id": data["image"].id})
            print(image_document)
           
            data["image"] = {"_id": str(image_document["_id"]),"name":image_document["name"], "checksum":image_document["checksum"],"img_url": image_document["img_url"]} if image_document else None

        datas.append(data)
    return datas
    


@route.get("/parentId",status_code=status.HTTP_200_OK)
def get_parent(user_id=Depends(user_data)):
    cursor_obj=category_collection.find({"parent":""})
    datas=[]
    for data in cursor_obj:
        data["_id"]=str(data["_id"])
        datas.append(data)
    return datas
    
#find one data
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


#product update
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
    

    
    
   





    



    
    
    
