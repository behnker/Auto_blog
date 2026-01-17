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
        
    agencies = []
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Agencies")
            records = table.all()
            for r in records:
                f = r["fields"]
                agencies.append({
                    "id": r["id"],
                    "name": f.get("Name", "Unnamed"),
                    "blogs_count": 0, # TODO: Phase 5 - Implement Rollup in Airtable
                    "posts_7d": 0,    # TODO: Phase 5
                    "avg_qa": 0       # TODO: Phase 5
                })
    except Exception as e:
        print(f"Error fetching agencies: {e}")
        
    return templates.TemplateResponse("admin/agencies.html", {"request": request, "agencies": agencies})

@router.get("/authors", response_class=HTMLResponse)
async def authors_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    authors = []
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            # Fetch Voices first for Lookup
            voices_table = api.table(base_id, "Voice_Profiles")
            voices_all = voices_table.all()
            voice_map = {v["id"]: v["fields"].get("Name", "Unknown") for v in voices_all}

            # Fetch Agencies for Lookup (Optional, if we want to show Agency per author)
            agencies_table = api.table(base_id, "Agencies")
            agencies_all = agencies_table.all()
            agency_map = {a["id"]: a["fields"].get("Name", "Unknown") for a in agencies_all}

            table = api.table(base_id, "Author_Profile")
            records = table.all()
            for r in records:
                f = r["fields"]
                
                # Resolve Voice Name
                voice_ids = f.get("Voice_Profile", [])
                voice_name = "None"
                if voice_ids:
                     # Get first voice name
                     voice_name = voice_map.get(voice_ids[0], "Unknown Voice")

                # Resolve Agency Name
                agency_ids = f.get("Agencies", [])
                agency_name = "None"
                if agency_ids:
                    agency_name = agency_map.get(agency_ids[0], "Unknown Agency")
                
                authors.append({
                    "id": r["id"],
                    "name": f.get("Author_Name", "Unnamed"),
                    "bio": f.get("Author_Bio", ""),
                    "voice": voice_name,
                    "agency": agency_name
                })
    except Exception as e:
        print(f"Error fetching authors: {e}")

    return templates.TemplateResponse("admin/authors.html", {"request": request, "authors": authors})

@router.get("/voices", response_class=HTMLResponse)
async def voices_list(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    voices = []
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Voice_Profiles")
            records = table.all()
            for r in records:
                f = r["fields"]
                voices.append({
                    "id": r["id"],
                    "name": f.get("Name", "Unnamed"),
                    "desc": f.get("Description", ""),
                    "tone": f.get("Tone_Instructions", "")
                })
    except Exception as e:
        print(f"Error fetching voices: {e}")

    return templates.TemplateResponse("admin/voices.html", {"request": request, "voices": voices})

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
