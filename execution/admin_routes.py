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
    
    blogs = load_blogs_config()
    
    # In a real app, we'd query Airtable for these aggregated stats
    metrics = {
        "drafts": 18,
        "in_review": 7,
        "published_7d": 34,
        "avg_qa": 86
    }
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "metrics": metrics,
        "blogs": blogs
    })

@router.get("/agencies", response_class=HTMLResponse)
async def agencies_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    # Mock Agency Data for MVP (Phase 4 will link this to Airtable 'Agencies' table)
    agencies_mock = [
        {"id": "ag-1", "name": "Atlas Content Lab", "blogs_count": 3, "posts_7d": 18, "avg_qa": 88},
        {"id": "ag-2", "name": "Northstar Studio", "blogs_count": 2, "posts_7d": 10, "avg_qa": 91}
    ]
    return templates.TemplateResponse("admin/agencies.html", {"request": request, "agencies": agencies_mock})

@router.get("/authors", response_class=HTMLResponse)
async def authors_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    # Mock Author Data (Phase 4 will link to 'Author_Profile')
    authors_mock = [
        {"id": "au-1", "name": "R. Behnke", "bio": "AI transformation + operations automation.", "voice": "Professional"},
        {"id": "au-2", "name": "E. Ogier", "bio": "Witty analyst voice. Loves analogies.", "voice": "Witty"}
    ]
    return templates.TemplateResponse("admin/authors.html", {"request": request, "authors": authors_mock})

@router.get("/voices", response_class=HTMLResponse)
async def voices_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    # Mock Voice Data (Phase 4 'Voice_Profiles')
    voices_mock = [
        {"id": "vp-1", "name": "Professional", "desc": "Clear, executive, concise.", "tone": "Active voice, minimal jargon."},
        {"id": "vp-2", "name": "Witty", "desc": "Smart humor, sharp analogies.", "tone": "Playful, still professional."}
    ]
    return templates.TemplateResponse("admin/voices.html", {"request": request, "voices": voices_mock})

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("admin/settings.html", {"request": request})

@router.get("/blogs/{blog_id}", response_class=HTMLResponse)
async def blog_detail(request: Request, blog_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    posts = []
    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        if base_id:
             table = api.table(base_id, blog["airtable"]["table_name"])
             # Fetch generic view
             posts = table.all(sort=["-PublishedDate"], max_records=20)
    except Exception as e:
        print(f"Error fetching posts: {e}")

    blog_view = blog.copy()
    blog_view['airtable']['base_id_resolved'] = os.environ.get(blog["airtable"]["base_id_env"], "Not Set")

    return templates.TemplateResponse("admin/blog_detail.html", {
        "request": request,
        "blog": blog_view,
        "posts": posts
    })
