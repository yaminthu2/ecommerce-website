from fastapi import FastAPI
from .routers import authentication,category,product,image

app=FastAPI()

app.include_router(authentication.route,tags=["authentication"])
app.include_router(category.route,prefix="/category",tags=["category"])
app.include_router(product.route,prefix="/product",tags=["product"])
app.include_router(image.route,prefix="/image",tags=["image"])


                                                                                                                                                                                                                           





    
    