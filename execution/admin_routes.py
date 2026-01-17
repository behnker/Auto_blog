from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from datetime import datetime, timedelta
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
    
    metrics = {
        "drafts": 0,
        "in_review": 0,
        "published_7d": 0,
        "avg_qa": 0
    }
    
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Posts")
            # Fetch all posts to aggregate stats (optimized to fetch only needed fields)
            records = table.all(fields=["Status", "PublishedDate", "QA_Score_GEO_AEO"])
            
            now = datetime.now()
            qa_sum = 0
            qa_count = 0
            
            for r in records:
                f = r["fields"]
                status_val = f.get("Status", "")
                
                # Count Statuses
                if status_val == "Draft":
                    metrics["drafts"] += 1
                elif status_val in ["InReview", "NeedsReview"]:
                    metrics["in_review"] += 1
                elif status_val == "Published":
                    # Check 7-day window
                    pdate_str = f.get("PublishedDate")
                    if pdate_str:
                        try:
                            # Airtable dates are YYYY-MM-DD
                            pdate = datetime.fromisoformat(pdate_str)
                            if (now - pdate).days <= 7:
                                metrics["published_7d"] += 1
                        except ValueError:
                            pass # Ignore parse errors
                            
                # Sum QA Scores
                qa_score = f.get("QA_Score_GEO_AEO")
                if isinstance(qa_score, (int, float)):
                    qa_sum += qa_score
                    qa_count += 1
            
            if qa_count > 0:
                metrics["avg_qa"] = int(qa_sum / qa_count)
                
    except Exception as e:
        print(f"Error fetching dashboard metrics: {e}")
    
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
                    "website": f.get("Website", ""), # Added field
                    "blogs_count": 0, # TODO: Phase 5 - Implement Rollup in Airtable
                    "posts_7d": 0,    # TODO: Phase 5
                    "avg_qa": 0       # TODO: Phase 5
                })
    except Exception as e:
        print(f"Error fetching agencies: {e}")
        
    return templates.TemplateResponse("admin/agencies.html", {"request": request, "agencies": agencies})

    return templates.TemplateResponse("admin/agencies.html", {"request": request, "agencies": agencies})

@router.get("/agencies/new", response_class=HTMLResponse)
async def new_agency_page(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("admin/agency_form.html", {"request": request, "agency": None})

@router.get("/agencies/{agency_id}/edit", response_class=HTMLResponse)
async def edit_agency_page(request: Request, agency_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    
    agency = None
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Agencies")
            r = table.get(agency_id)
            agency = {
                "id": r["id"],
                "name": r["fields"].get("Name", ""),
                "website": r["fields"].get("Website", ""),
                "notes": r["fields"].get("Notes", "")
            }
    except Exception as e:
        print(f"Error fetching agency for edit: {e}")
        # In real app, flash error
    
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    return templates.TemplateResponse("admin/agency_form.html", {"request": request, "agency": agency})

@router.post("/agencies/save", response_class=RedirectResponse)
async def save_agency(request: Request, 
                      agency_id: Optional[str] = Form(None),
                      name: str = Form(...), 
                      website: Optional[str] = Form(None),
                      notes: Optional[str] = Form(None)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
        
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Agencies")
            fields = {"Name": name}
            if website:
                fields["Website"] = website
            if notes:
                fields["Notes"] = notes
            
            if agency_id:
                # Update
                table.update(agency_id, fields, typecast=True)
            else:
                # Create
                table.create(fields, typecast=True)
                
    except Exception as e:
        print(f"Error saving agency: {e}")
        
    return RedirectResponse(url="/admin/agencies", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/agencies/{agency_id}/delete", response_class=RedirectResponse)
async def delete_agency(request: Request, agency_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Agencies")
            table.delete(agency_id)
    except Exception as e:
        print(f"Error deleting agency: {e}")
        
    return RedirectResponse(url="/admin/agencies", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/agencies/{agency_id}", response_class=HTMLResponse)
async def agency_detail(request: Request, agency_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    
    agency = None
    blogs = []
    
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Agencies")
            record = table.get(agency_id)
            agency = {
                "id": record["id"],
                "name": record["fields"].get("Name", "Unnamed"),
                "website": record["fields"].get("Website", ""),
                "notes": record["fields"].get("Notes", "")
            }
            
            # TODO: Fetch linked blogs if we had that link easily available or query via formula
            
    except Exception as e:
        print(f"Error fetching agency detail: {e}")
        raise HTTPException(status_code=404, detail="Agency not found")
        
    return templates.TemplateResponse("admin/agency_detail.html", {
        "request": request, 
        "agency": agency,
        "blogs": blogs
    })

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

    return templates.TemplateResponse("admin/authors.html", {"request": request, "authors": authors, "voices": voices_all})

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

@router.post("/voices", response_class=RedirectResponse)
async def create_voice(request: Request, name: str = Form(...), desc: Optional[str] = Form(None), tone: Optional[str] = Form(None)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
        
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Voice_Profiles")
            fields = {"Name": name}
            if desc:
                fields["Description"] = desc
            if tone:
                fields["Tone_Instructions"] = tone
                
            table.create(fields, typecast=True)
    except Exception as e:
        print(f"Error creating voice: {e}")
        
    return RedirectResponse(url="/admin/voices", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("admin/settings.html", {"request": request})

@router.post("/authors", response_class=RedirectResponse)
async def create_author(request: Request, name: str = Form(...), bio: Optional[str] = Form(None), voice_id: Optional[str] = Form(None)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
        
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Author_Profile")
            fields = {"Author_Name": name}
            if bio:
                fields["Author_Bio"] = bio
            if voice_id:
                fields["Voice_Profile"] = [voice_id]
                
            table.create(fields, typecast=True)
    except Exception as e:
        print(f"Error creating author: {e}")
        
    return RedirectResponse(url="/admin/authors", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/authors/{author_id}", response_class=HTMLResponse)
async def author_detail(request: Request, author_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    
    author = None
    
    try:
        api = get_airtable_client()
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        if base_id:
            table = api.table(base_id, "Author_Profile")
            record = table.get(author_id)
            f = record["fields"]
            author = {
                "id": record["id"],
                "name": f.get("Author_Name", "Unnamed"),
                "bio": f.get("Author_Bio", ""),
                # Fetching voice/agency names would require extra lookups or passing them if we wanted to be fancy, 
                # but for now we'll show raw IDs or just the fields we have.
            }

    except Exception as e:
        print(f"Error fetching author detail: {e}")
        raise HTTPException(status_code=404, detail="Author not found")
        
    return templates.TemplateResponse("admin/author_detail.html", {
        "request": request, 
        "author": author
    })

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
    
    # Fetch voices for the modal dropdown
    voices = []
    try:
        api = get_airtable_client()
        # Voices are in the BASE defined by the blog? Or a central base?
        # Assuming all blogs share the SAME base for now as per env config, or at least we check the one configured.
        # But wait, voices might be global. Let's assume they are in the same base as the blog for this architecture.
        base_id = os.environ.get("AIRTABLE_BASE_ID") # Using the main base ID for voices
        if base_id:
            table = api.table(base_id, "Voice_Profiles")
            records = table.all()
            for r in records:
                voices.append({"id": r["id"], "name": r["fields"].get("Name", "Unnamed")})
    except:
        pass

    return templates.TemplateResponse("admin/blog_detail.html", {
        "request": request,
        "blog": blog_view,
        "posts": posts,
        "voices": voices
    })

@router.post("/blogs/{blog_id}/posts", response_class=RedirectResponse)
async def create_post(request: Request, blog_id: str, title: str = Form(...), voice_id: Optional[str] = Form(None)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
        
    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            fields = {
                "Title": title,
                "Status": "Draft",
                # "GenerationContractDefault": "v2.0" # Optional: set default
            }
            if voice_id:
                fields["Voice_Profile_Override"] = [voice_id]
                
            table.create(fields, typecast=True)
            
    except Exception as e:
        print(f"Error creating post: {e}")
        
    return RedirectResponse(url=f"/admin/blogs/{blog_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/blogs/{blog_id}/posts/{post_id}", response_class=HTMLResponse)
async def post_detail_editor(request: Request, blog_id: str, post_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    post = None
    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            r = table.get(post_id)
            f = r["fields"]
            post = {
                "id": r["id"],
                "title": f.get("Title", ""),
                "content": f.get("Content", ""),
                "slug": f.get("Slug", ""),
                "status": f.get("Status", "Draft"),
                "image": f.get("Image_URL", ""), # Assumes simple text field for now? Or Attachment? Let's assume URL string.
                "feedback": f.get("User_Feedback", "")
            }
    except Exception as e:
        print(f"Error fetching post: {e}")
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse("admin/post_detail.html", {
        "request": request,
        "blog": blog,
        "post": post
    })

@router.post("/posts/save", response_class=RedirectResponse)
async def save_post_content(request: Request,
                            blog_id: str = Form(...),
                            post_id: str = Form(...),
                            title: str = Form(...),
                            content: str = Form(...),
                            slug: Optional[str] = Form(None),
                            image: Optional[str] = Form(None)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            fields = {
                "Title": title,
                "Content": content
            }
            if slug:
                fields["Slug"] = slug
            if image:
                fields["Image_URL"] = image # Ensure this field exists in Airtable Schema
                
            table.update(post_id, fields, typecast=True)
            
    except Exception as e:
        print(f"Error saving post: {e}")
        
    return RedirectResponse(url=f"/admin/blogs/{blog_id}/posts/{post_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/posts/revise", response_class=RedirectResponse)
async def request_revision(request: Request, 
                           blog_id: str = Form(...), 
                           post_id: str = Form(...), 
                           feedback: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            fields = {
                "Status": "RevisionRequested",
                "User_Feedback": feedback
            }
            table.update(post_id, fields, typecast=True)
            
    except Exception as e:
        print(f"Error requesting revision: {e}")
        
    return RedirectResponse(url=f"/admin/blogs/{blog_id}/posts/{post_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/blogs/{blog_id}/posts/{post_id}", response_class=HTMLResponse)
async def post_detail_editor(request: Request, blog_id: str, post_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    post = None
    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            r = table.get(post_id)
            f = r["fields"]
            post = {
                "id": r["id"],
                "title": f.get("Title", ""),
                "content": f.get("Content", ""),
                "slug": f.get("Slug", ""),
                "status": f.get("Status", "Draft"),
                "image": f.get("Image_URL", ""),
                "feedback": f.get("User_Feedback", "")
            }
    except Exception as e:
        print(f"Error fetching post: {e}")
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse("admin/post_detail.html", {
        "request": request,
        "blog": blog,
        "post": post
    })

@router.post("/posts/save", response_class=RedirectResponse)
async def save_post_content(request: Request,
                            blog_id: str = Form(...),
                            post_id: str = Form(...),
                            title: str = Form(...),
                            content: str = Form(...),
                            slug: Optional[str] = Form(None),
                            image: Optional[str] = Form(None)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            fields = {
                "Title": title,
                "Content": content
            }
            if slug:
                fields["Slug"] = slug
            if image:
                fields["Image_URL"] = image
                
            table.update(post_id, fields, typecast=True)
            
    except Exception as e:
        print(f"Error saving post: {e}")
        
    return RedirectResponse(url=f"/admin/blogs/{blog_id}/posts/{post_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/posts/revise", response_class=RedirectResponse)
async def request_revision(request: Request, 
                           blog_id: str = Form(...), 
                           post_id: str = Form(...), 
                           feedback: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    blogs = load_blogs_config()
    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    try:
        api = get_airtable_client()
        env_var_name = blog["airtable"]["base_id_env"]
        base_id = os.environ.get(env_var_name)
        
        if base_id:
            table = api.table(base_id, blog["airtable"]["table_name"])
            fields = {
                "Status": "RevisionRequested",
                "User_Feedback": feedback
            }
            table.update(post_id, fields, typecast=True)
            
    except Exception as e:
        print(f"Error requesting revision: {e}")
        
    return RedirectResponse(url=f"/admin/blogs/{blog_id}/posts/{post_id}", status_code=status.HTTP_303_SEE_OTHER)
