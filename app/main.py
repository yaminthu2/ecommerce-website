from fastapi import FastAPI,Request,HTTPException,status,Depends
from .routers import cart
from .routers import authentication,category,product,image,cart
from .routers.product import get_all_products,get_one_product
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
import json
from starlette.middleware.sessions import SessionMiddleware
from .routers.cart import add_to_cart
from .routers import dashboard
from .routers.category import get_all_categories,get_one_category,update_category
from .routers.product import get_all_products,get_one_product
from .routers.image import get_all_images
from .routers.authentication import get_all_users,get_one_user
import jwt
from bson import ObjectId
from .database.mongodb import collection
from .routers.cart import get_cart


app=FastAPI()
#need to create sessionMiddleware using secret key  for using session to cart
app.add_middleware(SessionMiddleware, secret_key="website")

templates=Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="static"),name="static")

app.include_router(authentication.route,prefix="/api",tags=["/authentication"])
app.include_router(category.route,prefix="/api/category",tags=["category"])
app.include_router(product.route,prefix="/api/product",tags=["product"])
app.include_router(image.route,prefix="/api/image",tags=["image"])
app.include_router(cart.route,prefix="/api/cart",tags=["cart"])
# app.include_router(dashboard.route,prefix="/dashboard",tags=["cart"])
                                                                                            
# Dependency function to get current user from session token
def get_current_user(request: Request):
    try:
        token = request.session.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        payload = jwt.decode(token, "website", algorithms=["HS256"])
    
        user_id = payload.get("_id")
        
        user_document = collection.find_one({"_id": ObjectId(user_id), "is_login": True})
        
        if not user_document:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return {"is_admin":user_document["is_admin"],"success":True}


    except HTTPException as e:
        return{"detail":e.detail,"success":False,"is_admin":False}

 

   
@app.get("/",response_class=HTMLResponse)
def index(request:Request):
    products=get_all_products()
    token=request.session.get("token")
    return templates.TemplateResponse("index.html",{"request":request,"products":products,"session":request.session,"token":token})
    
@app.get("/login",response_class=RedirectResponse)   
def get_login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request,"session":request.session})  

@app.get("/register")   
def get_register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request,"session":request.session})  

@app.get("/change-password")
def change_password(request:Request):
    return templates.TemplateResponse('changepassword.html',{"request":request,"session":request.session})
    

@app.get("/products/{id}")  
def get_product(request:Request,id:str):
    product=get_one_product(id)
    token=request.session.get("token")
    return templates.TemplateResponse("product.html",{"request":request,"product":product,"session":request.session,"token":token})

@app.get("/cart")  
def get_product(request:Request):
    cart=get_cart(request)
    token=request.session.get("token")
    return templates.TemplateResponse("cart.html",{"request":request,"session":request.session,"token":token,"cart":cart})


# @app.get("/orders")
# def get_user_order(request: Request, current_user: dict = Depends(get_current_user)):
#     print(current_user)
#     if not current_user['is_admin'] and not current_user['success']:
#         return RedirectResponse("/")
#     return templates.TemplateResponse("dashboard/orders.html", {"request": request, "user": current_user})


#  start dashboard 
@app.get("/orders")
def get_user_order(request:Request,current_user:dict=Depends(get_current_user)):
    token=request.session.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
 
    return templates.TemplateResponse("dashboard/orders.html",{"request":request,"user":current_user,"token":token})

@app.get("/categories")
def get_user_order(request:Request,current_user:dict=Depends(get_current_user)):
    categories=get_all_categories()
    images=get_all_images()
    token=request.session.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard/categories.html",{"request":request,"categories":categories,"images":images,"token":token,"user":current_user})


@app.get("/categories/edit/{id}")
def category_edit(request:Request,id:str,current_user:dict=Depends(get_current_user)):
    category=get_one_category(id)
    categories=get_all_categories()
    images=get_all_images()
    token=request.session.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard/category_edit.html",{"request":request,"category":category,"categories":categories,"images":images,"token":token,"user":current_user})

@app.get("/products")
def get_user_order(request:Request,current_user:dict=Depends(get_current_user)):
    products=get_all_products()
    images=get_all_images()
    categories=get_all_categories()
    token=request.session.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard/products.html",{"request":request,"products":products,"images":images,"categories":categories,"token":token,"user":current_user})

@app.get("/products/edit/{id}")
def product_edit(request:Request,id:str,current_user:dict=Depends(get_current_user)):
    product=get_one_product(id)
    products=get_all_products()
    categories=get_all_categories()
    images=get_all_images()
    token=request.session.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard/product_edit.html",{"request":request,
                                                                     "product":product,
                                                                     "products":products,
                                                                     "categories":categories,
                                                                     "images":images,"token":token
                                                                     ,"user":current_user})
    

@app.get("/users")
def get_user_order(request:Request,current_user:dict=Depends(get_current_user)):
    users=get_all_users()
    token=request.sesson.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard/users.html",{"request":request,"users":users,"user":current_user,"token":token})


@app.get("/users/edit/{id}")
def user_edit(request:Request,id:str,current_user:dict=Depends(get_current_user)):
    users=get_all_users()
    user=get_one_user(id)
    # category=get_one_category(id)
    # categories=get_all_categories()
    # images=get_all_images()
    token=request.session.get("token")
    if not current_user['is_admin'] or  not current_user['success'] :
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard/user_edit.html",{"request":request,"current_user":current_user,"users":users,"user":user,"token":token})



# End dashboard

                                                                                                                                           
json_format=app.openapi()
filename="data.json"
with open(filename,'w') as json_file:
    json.dump(json_format,json_file)


    
    


    #  category = find_category(id)
#     categories = find_categories()
#     images = find_images()
#     token = request.session.get("token")
#     return templates.TemplateResponse(
#         "dashboard/edit_category.html",
#         {
#             "request": request,
#             "category": category,
#             "categories": categories,
#             "images": images,
#             "token": token,
#         },