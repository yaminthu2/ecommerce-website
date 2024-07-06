from fastapi import FastAPI,Request
from .routers import cart
from .routers import authentication,category,product,image,cart
from .routers.product import get_all_products,get_one_product
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
from starlette.middleware.sessions import SessionMiddleware
from .routers.cart import add_to_cart
from .routers import dashboard
from .routers.category import get_all_categories,get_one_category,update_category
from .routers.product import get_all_products,get_one_product
from .routers.image import get_all_images


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
app.include_router(dashboard.route,prefix="/dashboard",tags=["cart"])
                                                                                            


# @app.middleware("http")
# async def add_dession_to_request(request:Request,call_next):
#     response=await call_next(request)
#     return response
   
@app.get("/",response_class=HTMLResponse)
def index(request:Request):
    products=get_all_products()
    return templates.TemplateResponse("index.html",{"request":request,"products":products,"session":request.session})
    
@app.get("/login",response_class=HTMLResponse)   
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
    return templates.TemplateResponse("product.html",{"request":request,"product":product,"session":request.session})




#  start dashboard 
@app.get("/orders")
def get_user_order(request:Request):
    return templates.TemplateResponse("dashboard/orders.html",{"request":request})

@app.get("/categories")
def get_user_order(request:Request):
    categories=get_all_categories()
    images=get_all_images()
    token=request.session.get("token")
    return templates.TemplateResponse("dashboard/categories.html",{"request":request,"categories":categories,"images":images,"token":token})

@app.get("/categories/edit/{id}")
def category_edit(request:Request,id:str):
    category=get_one_category(id)
    categories=get_all_categories()
    images=get_all_images()
    token=request.session.get("token")
    return templates.TemplateResponse("dashboard/category_edit.html",{"request":request,"category":category,"categories":categories,"images":images,"token":token})

@app.get("/products")
def get_user_order(request:Request):
    products=get_all_products()
    images=get_all_images()
    categories=get_all_categories()
    token=request.session.get("token")
    return templates.TemplateResponse("dashboard/products.html",{"request":request,"products":products,"images":images,"categories":categories,"token":token})

@app.get("/products/edit/{id}")
def product_edit(request:Request,id:str):
    product=get_one_product(id)
    products=get_all_products()
    categories=get_all_categories()
    images=get_all_images()
    token=request.session.get("token")
    return templates.TemplateResponse("dashboard/product_edit.html",{"request":request,
                                                                     "product":product,
                                                                     "products":products,
                                                                     "categories":categories,
                                                                     "images":images,"token":token})
    

@app.get("/users")
def get_user_order(request:Request):
    return templates.TemplateResponse("dashboard/users.html",{"request":request})

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