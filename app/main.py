from fastapi import FastAPI,Request
from .routers import authentication,category,product,image
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app=FastAPI()

templates=Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="static"),name="static")

app.include_router(authentication.route,prefix="/api",tags=["/authentication"])
app.include_router(category.route,prefix="/api/category",tags=["category"])
app.include_router(product.route,prefix="/api/product",tags=["product"])
app.include_router(image.route,prefix="/api/image",tags=["image"])


app.get("/")
def root(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})

                                                                                                                                                                                                                           





    
    