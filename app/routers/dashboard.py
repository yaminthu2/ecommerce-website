from fastapi  import APIRouter


route=APIRouter()

@route.get("")
def dashboard():
    return{"message":"success"}