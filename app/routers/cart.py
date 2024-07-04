from fastapi import APIRouter,HTTPException,status,Depends,Request
from pydantic import BaseModel
from ..database.mongodb import product_collection
from bson import ObjectId
from .authentication import user_data
from fastapi.responses import HTMLResponse,JSONResponse
from ..database.mongodb import carts_collection
from bson.dbref import DBRef

route=APIRouter()

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from ..database.mongodb import product_collection
from bson import ObjectId
from .authentication import user_data
from fastapi.responses import JSONResponse
from ..database.mongodb import carts_collection
from bson.dbref import DBRef

route = APIRouter()

class CartItem(BaseModel):
    product_id: str
    quantity: int

def find_product(product_id):
    product = product_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

def initialize_session_cart(session):
    if 'cart' not in session:
        session['cart'] = []

def find_existing_item(session, product_id):
    for cart_item in session['cart']:
        if cart_item['product_id'] == product_id:
            return cart_item
    return None

def update_product_stock(product_id, quantity_change):
    product_collection.update_one({"_id": ObjectId(product_id)}, {"$inc": {"item": quantity_change}})

def add_new_item_to_cart(session, product_id, price, quantity):
    session['cart'].append({"product_id": product_id, "quantity": quantity, "price": price})

def update_existing_item_quantity(existing_item, quantity):
    existing_item['quantity'] += quantity

def remove_item_if_quantity_zero(session, existing_item):
    if existing_item['quantity'] <= 0:
        session['cart'].remove(existing_item)

@route.post("/add-to-cart")
def add_to_cart(cart: CartItem, request: Request):
    product = find_product(cart.product_id)
    session = request.session
    initialize_session_cart(session)

    existing_item = find_existing_item(session, cart.product_id)
    # quantity_change = cart.quantity

    if existing_item:
        update_existing_item_quantity(existing_item, cart.quantity)
        update_product_stock(cart.product_id, -cart.quantity)
        remove_item_if_quantity_zero(session, existing_item)
    else:
        add_new_item_to_cart(session, cart.product_id, product['price'], cart.quantity)
        update_product_stock(cart.product_id,cart.quantity)
   
    total_quantity=sum(item['quantity']for item in session['cart'])
    session['total_quantity']=total_quantity

    request.session.update(session)
    return {"message": "Cart updated successfully","success":True,"total_quantiy":total_quantity}


@route.get("/cart-items")
def get_cart_items(request:Request):
    session=request.session
    cart_items=session.get('cart',[])
    total_quantity=session.get('total_quantity',0)
    return { "total_quantity":total_quantity,"cart_items":cart_items}


# @route.get("/cart")
# def get_cart(request: Request, user=Depends(user_data)):
#     cart = request.session.get('cart', [])
#     detailed_cart = []

#     for item in cart:
#         product = product_collection.find_one({"_id": ObjectId(item['product_id'])})
#         if product:
#             detailed_cart.append({
#                 "product_id": item['product_id'],
#                 "quantity": item['quantity'],
#                 "name": product['name'],
#                 "price": product['price'],
#                 "total_price": product['price'] * item['quantity']
#             })

#     return JSONResponse(content={"cart": detailed_cart})

# @route.post("/checkout")
# def checkout(request: Request, user=Depends(user_data)):
#     cart = request.session.get('cart', [])
#     if not cart:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

#     cart_total = sum(item['quantity'] * item['price'] for item in cart)

#     cart_document = {
#         "user_id": DBRef("users", ObjectId(user["_id"])),
#         "items": [{"product_id": DBRef("products", ObjectId(item["product_id"])), "quantity": item["quantity"], "price": item["price"]} for item in cart],
#         "total_price": cart_total
#     }
#     carts_collection.insert_one(cart_document)
#     request.session['cart'] = []
#     request.session.update(request.session)

#     return JSONResponse(content={"message": "Checkout successful"})
























