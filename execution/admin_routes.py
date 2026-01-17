from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os

router = APIRouter(prefix="/admin", tags=["admin"])

# Quick & Dirty Session Auth (MVP)
# In production, use a proper session library (e.g. starsessions)
# For now, we use a simple signed cookie or just a plain cookie with a "secret" check.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin") 

templates = Jinja2Templates(directory="templates")

def is_authenticated(request: Request) -> bool:
    return request.cookies.get("admin_session") == "authenticated"

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="admin_session", value="authenticated", httponly=True)
        return response
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": "Invalid Password"})

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_session")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    
    # Placeholder: Fetch metrics from Airtable later
    metrics = {
        "agencies": 0,
        "blogs": 0,
        "posts": 0
    }
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "metrics": metrics
    })
