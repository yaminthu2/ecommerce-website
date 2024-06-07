from fastapi import HTTPException,status,APIRouter,Request,Depends
from pydantic import BaseModel,field_validator
from app.database.mongodb import collection
# import email_validator
import re
from argon2 import PasswordHasher
import jwt
from bson import ObjectId
    

route=APIRouter()

class Register(BaseModel):
    username:str
    password:str
    email:str
    is_login:bool=True

    @field_validator("username","password","email")
    def get_strip(cls,value):
        return value.strip()

class Login(BaseModel):
    email:str
    password:str

    @field_validator("*")
    def login_strip(cls,value):
        return value.strip()


class ChangePassword(BaseModel):
    email:str
    password:str
    new_password:str

    @field_validator("*")
    def change_password_strip(cls,value):
        return value.strip()

def check_email(email):
    regex='[\w\.-]+@[\w\.-]+\.\w{2,4}'
    ch_email=re.match(regex,email)
    return ch_email
   

def valid_password(password):
    upper_letter='(?=.*?[A-Z])'
    search_password=re.search(upper_letter,password)
    if search_password==None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Enter at least one upper case for  password")
    
    lower_letter='(?=.*?[a-z])'
    search_password=re.search(lower_letter,password)
    if search_password==None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Enter at least one lower case for  password")
    
    digit='(?=.*?[0-9])'
    search_password=re.search(digit,password)
    if search_password==None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Enter at least one 0 to 9 for  password")


    special_chacter='(?=.*?[#?!@$%^&*-])'
    search_password=re.search(special_chacter,password)
    if search_password==None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Enter at least one special character for  password")
    
    if len(password)<8:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Enter at least eight character for  password")
    print("Testing")

#middleware   
def user_data(request:Request):
    bearer_token=request.headers.get("Authorization")

    if not bearer_token:  #bearer token include key and value
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Need to Bearer token ")
    
    token=bearer_token.strip().split(" ")
    if len(token)==1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized ")
    token_type=token[0]
    token_value=token[1]
    if token_type!="Bearer": # check the type /that mean Bearer instand of another token/ this error occur
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized token")

    payload=jwt.decode(token_value,"website",algorithms=["HS256"]) #jwt decode ss

    user_data=collection.find_one({"_id":ObjectId(payload.get("_id"))}) #from users database
    if not user_data or not user_data.get("is_login") : #not user or  login is false /this error occur
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized user")
    return payload

@route.post("/register")
def registration(register:Register):

    
    register=register.model_dump()
    if not register["username"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Invalid username")
    
    if len(register["username"].split())>1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="username error")


    is_user=collection.find_one({"username":register["username"]})
    if is_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Existing username")
    
    is_email=check_email(register["email"])

    if not is_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=" please enter the email format")
    
    is_email=collection.find_one({"email":register["email"]})

    if is_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=" existing email")
    
    valid_password(register["password"])

    pass_hash=PasswordHasher()
    register["password"]=pass_hash.hash(register["password"])
    user_document=collection.insert_one(register)
    payload={"_id":str(user_document.inserted_id)}
    token=jwt.encode(payload,"website",algorithm="HS256")
    return{"message":"Successful Register","token":token}


@route.post("/login")
def get_login(login:Login):   

    # login=get_strip(login)
    login=login.model_dump()
    user_document=collection.find_one({"email":login["email"]})
    if not user_document:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=" Invalid credentials")
    try:
        PasswordHasher().verify(user_document["password"],login["password"])
    except:  
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Invalid credentials")
    
    collection.update_one({"_id":user_document["_id"]},{"$set":{"is_login":True}})
    payload={"_id":str(user_document["_id"])}
    token=jwt.encode(payload,"website",algorithm="HS256")
    
    return {"detail":"Successful Login","token":token}


@route.patch("/change_password")
def change_password(changePassword:ChangePassword,user_id=Depends(user_data)):

    # changePassword=get_strip(changePassword)

    changePassword=changePassword.model_dump()
    
    valid_password(changePassword["new_password"])
    
    collect_user=collection.find_one({"_id":ObjectId(user_id["_id"])})
    
    if not changePassword["email"]==collect_user["email"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Invalid email")

    # if not collect_database:
        # raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Invalid Email")
        
    try:
        
        PasswordHasher().verify(collect_user["password"],changePassword["password"])
        changePassword["new_password"]=PasswordHasher().hash(changePassword["new_password"])
        collection.update_one({"email":changePassword["email"]},{"$set":{"password":changePassword["new_password"]}})
        return {"message":"Successful change password"}
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Invalid password")
    
@route.get("/logout",status_code=status.HTTP_200_OK)
def logout(user_id=Depends(user_data)):
    
    collection.update_one({"_id":ObjectId(user_id["_id"])},{"$set":{"is_login":False}})
    return{"detail":"Successful logout"}


    
    