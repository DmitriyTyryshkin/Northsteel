from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="",
    tags=["Pages"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/home")
def get_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
