import os
import subprocess
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from execution.utils import get_blog_by_domain, get_blog_config, get_airtable_client, get_base_id

app = FastAPI()

# Setup Templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

def get_current_blog(request: Request):
    """Resolves the current blog configuration from the Host header."""
    host = request.headers.get("host", "").split(":")[0] # Remove port if present
    
    # Check for exact domain match
    blog = get_blog_by_domain(host)
    if blog:
        return blog
    
    # Fallback/Default for development (take the first one if no match)
    # WARNING: In production, you might want to return 404 or a landing page
    from execution.utils import load_blogs_config
    blogs = load_blogs_config()
    if blogs:
        return blogs[0]
        
    raise HTTPException(status_code=404, detail="Blog not found")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    blog = get_current_blog(request)
    if not blog:
        return templates.TemplateResponse("base.html", {"request": request, "blog": {"name": "Not Found"}, "now": datetime.now()})

    try:
        airtable = get_airtable_client()
        base_id = get_base_id(blog)
        table = airtable.table(base_id, blog["airtable"]["table_name"])
        # Fetch only published posts
        records = table.all(sort=["-PublishedDate"], formula="{Status}='Published'")
    except Exception as e:
        print(f"Airtable Error: {e}")
        records = []

    return templates.TemplateResponse("index.html", {
        "request": request,
        "blog": blog,
        "posts": records,
        "now": datetime.now()
    })

@app.get("/post/{slug}", response_class=HTMLResponse)
async def read_post(slug: str, request: Request):
    blog = get_current_blog(request)
    
    try:
        airtable = get_airtable_client()
        base_id = get_base_id(blog)
        table = airtable.table(base_id, blog["airtable"]["table_name"])
        # Find record by slug
        records = table.all(formula=f"{{Slug}}='{slug}'")
        if not records:
             raise HTTPException(status_code=404, detail="Post not found")
        post = records[0]
    except Exception as e:
        print(f"Error fetching post: {e}")
        raise HTTPException(status_code=500, detail="Database Error")

    return templates.TemplateResponse("post.html", {
        "request": request,
        "blog": blog,
        "post": post,
        "now": datetime.now()
    })

@app.post("/api/cron/generate")
async def trigger_generation(request: Request, background_tasks: BackgroundTasks, blog_id: str, token: str):
    """
    Webhook to trigger post generation.
    Usage: POST /api/cron/generate?blog_id=example_blog&token=SECRET
    """
    secret = os.environ.get("CRON_SECRET")
    if token != secret:
        raise HTTPException(status_code=403, detail="Invalid Request")
        
    blog = get_blog_config(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog ID not found")
        
    # Run generation in background so webhook returns fast
    background_tasks.add_task(run_generation_script, blog_id)
    
    return {"status": "queued", "blog": blog["name"]}

def run_generation_script(blog_id: str):
    """Helper to run the CLI script."""
    print(f"Starting background generation for {blog_id}")
    script_path = os.path.join(os.path.dirname(__file__), "generate_post.py")
    subprocess.run(["python", script_path, "--blog-id", blog_id])
