from fastapi import HTTPException,status,APIRouter,Request,Depends,Form
from pydantic import BaseModel,field_validator,Field
from app.database.mongodb import collection
import re
from argon2 import PasswordHasher
import jwt
from bson import ObjectId
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.templating import Jinja2Templates

route=APIRouter()
templates=Jinja2Templates(directory="app/templates")


# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin*123"

class Register(BaseModel):
    username:str
    email:str
    password:str
    is_admin:bool=False
    is_login:bool=True
    @field_validator("username","password","email")
    def get_strip(cls,value):
        return value.strip()
    @classmethod
    def register_form_data(cls,username: str = Form(...), email: str = Form(...), password: str = Form(...)):\
        return cls(username=username, email=email, password=password)
        
        # return{
        #     "username":username,
        #     "email":email,
        #     "password":password
        # }
   

class Login(BaseModel):
    email:str
    password:str

    @field_validator("*")
    def login_strip(cls,value):
        return value.strip()
    @classmethod
    def login_form_data(cls,email: str = Form(...), password: str = Form(...)):
        return cls(email=email,password=password)
        # return{
        #     "email":email,
        #     "password":password
        # }


class ChangePassword(BaseModel):
    email:str 
    password:str 
    new_password:str 

    @field_validator("*")
    def change_password_strip(cls,value):
        return value.strip()
    @classmethod
    def change_password_form_data(cls,email: str = Form(...), password: str = Form(...), new_password: str = Form(...)):
        
         return{
            "email":email,
            "password":password,
            "new_password":new_password
        }

def check_email(email):
    regex='[\w\.-]+@[\w\.-]+\.\w{2,4}'
    ch_email=re.match(regex,email)
    return ch_email
   

def valid_password(password):
    upper_letter = r'(?=.*?[A-Z])'
    lower_letter = r'(?=.*?[a-z])'
    digit = r'(?=.*?[0-9])'
    special_character = r'(?=.*?[#?!@$%^&*-])'

    if not re.search(upper_letter, password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Enter at least one upper case for password")

    if not re.search(lower_letter, password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Enter at least one lower case for password")

    if not re.search(digit, password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Enter at least one digit for password")

    if not re.search(special_character, password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Enter at least one special character for password")

    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Enter at least eight characters for password")


#middleware   
def user_data(request:Request):
    bearer_token=request.cookies.get("Authorization")or request.headers.get("Authorization")

    if bearer_token==None:  #bearer token include key and value
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Need to Bearer token ")
    
    token=bearer_token.strip().split(" ")
    if len(token)==1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized ")
    token_type=token[0]
    token_value=token[1]
    
    if token_type!="Bearer": # check the type /that mean Bearer instand of another token/ this error occur
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized token")
    payload=jwt.decode(token_value,"website",algorithms=["HS256"]) #jwt decode 
    user_data=collection.find_one({"_id":ObjectId(payload.get("_id"))}) #from users database

    if not user_data or not user_data.get("is_login") : #not user or  login is false /this error occur
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user")
    return payload


# Middleware to check the method override
async def check_method(request: Request):
    form_data = await request.form()
    method = form_data.get('_method')
    if method:
        request._method = method.upper()
    return request


# find all users
@route.get("/",status_code=status.HTTP_200_OK)
def get_all_users():
    cursor_obj=collection.find({})
    users_documents=[]
    for document in cursor_obj:
        document["_id"]=str(document["_id"])
        users_documents.append(document)
    return users_documents

        
@route.post("/register")
async def registration(request: Request, register: Register):
    try:
        if not register.username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid username")

        if len(register.username.split()) > 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username error")

        is_user = collection.find_one({"username": register.username})
        if is_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Existing username")

        is_email = check_email(register.email)
        if not is_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Please enter the email format")

        is_email = collection.find_one({"email": register.email})
        if is_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Existing email")

        valid_password(register.password)
        pass_hash = PasswordHasher()
        register.password = pass_hash.hash(register.password)
        user_document = collection.insert_one(register.model_dump())
        payload = {"_id": str(user_document.inserted_id)}
        token = jwt.encode(payload, "website", algorithm="HS256")
        request.session["token"]=token
        return {"detail":"successful register","success":True}
    except HTTPException as e:
        return{"detail":e.detail,"success":False}
        
@route.post("/login")   
def login(request:Request,login:Login):
    try:
        user_document=collection.find_one({"email":login.email})
      
        if user_document==None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=" Invalid email")
        try:
            PasswordHasher().verify(user_document['password'],login.password)
        except: 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid password")
        
        collection.update_one({"_id":user_document["_id"]},{"$set":{"is_login":True}})
        payload={"_id":str(user_document["_id"])}
        token=jwt.encode(payload,"website",algorithm="HS256")
        request.session["token"]=token
        url="/"
        if user_document["is_admin"]:
            url="/orders"
        return {"detail":"successful register","success":True,"url":url}
       
    except HTTPException as e:
         return{"detail":e.detail,"success":False}
    
@route.post("/change-password", dependencies=[Depends(check_method)])
async def change_password(request: Request,changePassword:ChangePassword.change_password_form_data=Depends(),user_id=Depends(user_data)):
    try:
        if request._method != "PATCH":
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Method not allowed")
    
        valid_password(changePassword["new_password"])
        user_document = collection.find_one({"email": changePassword["email"]})
        if user_document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )

        try:
            PasswordHasher().verify(user_document["password"], changePassword["password"])
            new_hashed_password = PasswordHasher().hash(changePassword["new_password"])
            collection.update_one({"email": changePassword["email"]}, {"$set": {"password": new_hashed_password}})
            # return {"message": "Successful change password"}
            html_content = f"""
            <html>
            <meta http-equiv="refresh" content="0;url=http://localhost:8000/login"">
            </html>
            """
            response = HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)
            # response.set_cookie(key="message",value="successful change password",httponly=True)
            return response

        except:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid password"
            )
    except HTTPException as e:
        return templates.TemplateResponse("changepassword.html", {"request":request,"error_message": e.detail})
    
@route.get("/logout",status_code=status.HTTP_200_OK)
def logout(user_id=Depends(user_data)):
    collection.update_one({"_id":ObjectId(user_id["_id"])},{"$set":{"is_login":False}})
    html_content = f"""
    <html>
        <meta http-equiv="refresh" content="0;url=http://localhost:8000/">
    </html>
    """
    response = HTMLResponse(content=html_content, status_code=status.HTTP_200_OK) 
    return response
    


    


