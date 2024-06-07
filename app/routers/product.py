from fastapi import APIRouter,status,Depends,HTTPException
from pydantic import BaseModel,field_validator
from .authentication import user_data
from ..database.mongodb import product_collection
from bson import ObjectId

route=APIRouter()

class Products(BaseModel):
    name:str
    category_id:str
    description:str
    item:int
    price:int
    image_ids:list[str]
    feature_product:bool=False

    @field_validator("name","category_id","description")
    def get_strip(cls,value):
        return value.strip()
    
    @field_validator("name","description")
    def empty_str(cls,value):
        if not value:
           raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Please enter the data")
        
        return value
        

#create product data
@route.post("/",status_code=status.HTTP_201_CREATED)
def get_create_product(product:Products,user=Depends(user_data)):
    product=product.model_dump()
    product_collection.insert_one(product)
    return{"detail":"Successful create product"}

# get all products document
@route.get("/",status_code=status.HTTP_200_OK)
def get_all_products(user_id=Depends(user_data)):
   cursor_obj=product_collection.find({})
   products_document=[]
   for document in cursor_obj:
        document["_id"]=str(document["_id"])
        products_document.append(document)
   return products_document

#get one product document
@route.get("/{id}",status_code=status.HTTP_200_OK)  
def get_one_product(id:str):
    id=id.strip()
    document=product_collection.find_one({"_id":ObjectId(id)})
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid product id")
    document["_id"]=str(document["_id"])
    return document

#product update  
@route.put("/{id}",status_code=status.HTTP_200_OK)
def update(id:str,product:Products):
    document=product_collection.find_one_and_update({"_id":ObjectId(id.strip())},{"$set":product.model_dump()})
    if document==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid product Id")
    return{"detail":"Successful product update"}

#product delete
@route.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)  
def delete(id:str):
    document=product_collection.find_one_and_delete({"_id":ObjectId(id.strip())}) 
    if document==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Id")


        
        
    
    

       