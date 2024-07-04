# from fastapi import Request, APIRouter
# from models import CartItem
# from utils import find_product, initialize_session_cart, find_existing_item, update_existing_item_quantity, update_product_stock, remove_item_if_quantity_zero, add_new_item_to_cart

# route = APIRouter()

# @route.post("/add-to-cart")
# async def add_to_cart(cart: CartItem, request: Request):
#     product = await find_product(cart.product_id)
#     session = request.session
#     initialize_session_cart(session)

#     existing_item = find_existing_item(session, cart.product_id)
#     quantity_change = cart.quantity

#     if existing_item:
#         update_existing_item_quantity(existing_item, cart.quantity)
#         update_product_stock(cart.product_id, -cart.quantity)
#         remove_item_if_quantity_zero(session, existing_item)
#     else:
#         add_new_item_to_cart(session, cart.product_id, product['price'], cart.quantity)
#         update_product_stock(cart.product_id, -cart.quantity)

#     # Update total quantity in session
#     total_quantity = sum(item['quantity'] for item in session['cart'])
#     session['total_quantity'] = total_quantity

#     request.session.update(session)
#     return {"message": "Cart updated successfully", "total_quantity": total_quantity}






# document.addEventListener('DOMContentLoaded', (event) => {
#     const addToCartButtons = document.querySelectorAll('.add-to-cart');
#     addToCartButtons.forEach(button => {
#         button.addEventListener('click', async (event) => {
#             event.preventDefault();
#             const productId = button.dataset.productId;
#             const quantity = button.dataset.quantity;

#             const response = await fetch('/add-to-cart', {
#                 method: 'POST',
#                 headers: {
#                     'Content-Type': 'application/x-www-form-urlencoded'
#                 },
#                 body: new URLSearchParams({
#                     product_id: productId,
#                     quantity: quantity
#                 })
#             });

#             if (response.ok) {
#                 const data = await response.json();
#                 document.querySelector('#lg-bag .badge').textContent = data.total_quantity;
#             }
#         });
#     });
# });

