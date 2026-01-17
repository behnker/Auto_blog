from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from execution.utils import load_blogs_config, get_airtable_client

router = APIRouter(prefix="/admin", tags=["admin"])

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
    
    # Fetch Blogs from Config
    blogs = load_blogs_config()
    
    # Fetch Stats (Simulated or Lightweight)
    metrics = {
        "agencies": 1, 
        "blogs": len(blogs),
        "posts": "..." 
    }
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "metrics": metrics,
        "blogs": blogs
    })

@router.get("/blogs/{blog_id}", response_class=HTMLResponse)
async def blog_detail(request: Request, blog_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Fetch Posts from Airtable
    posts = []
    try:
        api = get_airtable_client()
        # Fix: Helper get_base_id is in utils, but we can access config dict directly safely 
        # or reimplement the lookup to handle the env var indirection
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        if base_id:
             table = api.table(base_id, blog["airtable"]["table_name"])
             # Fetch generic view
             posts = table.all(sort=["-PublishedDate"])
        else:
             print(f"Base ID not found for env var: {env_var_name}")
    except Exception as e:
        print(f"Error fetching posts: {e}")

    # Helper for template to render base_id string safely
    blog_view = blog.copy()
    blog_view['airtable']['base_id_resolved'] = os.environ.get(blog["airtable"]["base_id_env"], "Not Set")

    return templates.TemplateResponse("admin/blog_detail.html", {
        "request": request,
        "blog": blog_view,
        "posts": posts
    })
