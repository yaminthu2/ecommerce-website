from fastapi import FastAPI,Request

from .routers import cart
from .routers import authentication,category,product,image,cart
from .routers.product import get_all_products,get_one_product
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
from starlette.middleware.sessions import SessionMiddleware


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
                                                                                            

# @app.get("/",response_class=HTMLResponse)
# def root(request:Request):
#     return templates.TemplateResponse("base.html",{"request":request})

   
@app.get("/",response_class=HTMLResponse)
def index(request:Request):
    products=get_all_products()
    return templates.TemplateResponse("index.html",{"request":request,"products":products})
    
@app.get("/login",response_class=HTMLResponse)   
def get_login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})  

@app.get("/register")   
def get_register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})  

@app.get("/change-password")
def change_password(request:Request):
    return templates.TemplateResponse('changepassword.html',{"request":request})
    

@app.get("/products/{id}")  
def get_product(request:Request,id:str):
    product=get_one_product(id)
    return templates.TemplateResponse("product.html",{"request":request,"product":product})

@app.get("/cart")
def get_cart(request:Request):
    return templates.TemplateResponse("cart.html",{"request":request})

                                                                                                                                                    
json_format=app.openapi()
filename="data.json"
with open(filename,'w') as json_file:
    json.dump(json_format,json_file)


    
    