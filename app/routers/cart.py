from fastapi import APIRouter,HTTPException,status,Depends,Request
from pydantic import BaseModel
from ..database.mongodb import product_collection,collection,checkout_collection
from bson import ObjectId
from .authentication import user_data
from fastapi.responses import HTMLResponse,JSONResponse
from bson.dbref import DBRef
import jwt

route=APIRouter()


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
def add_to_cart(cart: CartItem, request: Request,depend=Depends(user_data)):
    product = find_product(cart.product_id)
    session = request.session
    initialize_session_cart(session)

    existing_item = find_existing_item(session, cart.product_id)
    quantity_change = cart.quantity

    if existing_item:
        update_existing_item_quantity(existing_item, quantity_change)
        update_product_stock(cart.product_id, -quantity_change)
        remove_item_if_quantity_zero(session, existing_item)
    else:
        add_new_item_to_cart(session, cart.product_id, product['price'], quantity_change)
        update_product_stock(cart.product_id,quantity_change)
   
    total_quantity=sum(item['quantity']for item in session['cart'])
   
    session['total_quantity']=total_quantity    
    
    

    request.session.update(session)
    return {"message": "Cart updated successfully","success":True,"total_quantiy":total_quantity}


# @route.get("/cart-items")
# def get_cart_items(request:Request):
#     session=request.session
#     cart_items=session.get('cart',[])
#     total_quantity=session.get('total_quantity',0)
#     return { "total_quantity":total_quantity,"cart_items":cart_items}


@route.get("/cart-items")
def get_cart(request: Request):
    
    cart = request.session.get('cart')  
    
    detailed_cart = []

    for item in cart:
        product = product_collection.find_one({"_id": ObjectId(item['product_id'])})
        if product:
            
            detailed_cart.append({
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "name": product['name'],
                "price": product['price'],
                "total_price": product['price'] * item['quantity'],
                
            })

    return{"cart":detailed_cart}

    # return JSONResponse(content={"cart": detailed_cart})

@route.post("/checkout")
def create_checkout(request: Request, user=Depends(user_data)):
    try:
            token = request.session.get("token")
            if not token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            payload = jwt.decode(token, "website", algorithms=["HS256"])
        
            user_id = payload.get("_id")
            
            user_document = collection.find_one({"_id": ObjectId(user_id), "is_login": True})
            cart = request.session.get('cart', [])
            if not cart:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
            

            cart_total = sum(item['quantity'] * item['price'] for item in cart)
    
            cart_document = {
                "user": DBRef("users", ObjectId(user_document["_id"]),"ecommerce"),
                "items": [
                    {
                        "product": DBRef("products", ObjectId(item["product_id"])),
                        "quantity": item["quantity"], 
                        "price": item["price"]} for item in cart],
                "total_price": cart_total
            }
            
            checkout_collection.insert_one(cart_document)
            request.session['cart'] = []
            request.session.update(request.session)
            return{"detail":'successful checkout',"success":True}
    except HTTPException as e:
        return{"detail":e.detail,"success":False}
       
























