from ..database.mongodb import db

#parent derefrence for category
def category_derefrence(data):
    data=db.dereference(data)
    
    if data:
        data["_id"]=str(data["_id"])
        if data["parent"]:
            data["parent"]=category_derefrence(data["parent"])
        data["image"]=image_derefrence(data["image"])
    return data
    

#image derefrence 
def image_derefrence(image):
    image=db.dereference(image)
    if image:    
        image["_id"]=str(image["_id"])
    return image
   