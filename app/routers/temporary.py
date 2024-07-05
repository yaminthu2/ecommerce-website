# @router.get("/categories/{id}")
# def category_detail_page(
#     request: Request, id: str, result: dict = Depends(check_is_logged_in)
# ):
#     if not result["is_logged_in"]:
#         return RedirectResponse(result["redirect_url"])
#     if not result["is_admin"]:
#         return RedirectResponse("/")
#     category = find_category(id)
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
#     )