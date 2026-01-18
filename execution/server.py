import os
import sys
import subprocess
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from execution.utils import get_blog_by_domain, get_blog_config, get_airtable_client, get_base_id

from execution.models import BlogConfig
from execution.admin_routes import router as admin_router

app = FastAPI()
# Reload for Admin Design
app.include_router(admin_router)

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

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Landing Page: Menu of every published blog on the platform.
    """
    from execution.utils import load_blogs_config
    
    # Check if we are on a specific custom domain (optional future-proofing)
    # host = request.headers.get("host", "").split(":")[0]
    # For now, per user instruction, the landing page is the Menu.
    
    all_blogs = load_blogs_config()
    
    return templates.TemplateResponse("platform_index.html", {
        "request": request,
        "blogs": all_blogs,
        "now": datetime.now()
    })

@app.get("/blogs/{blog_id}", response_class=HTMLResponse)
async def read_blog_index(blog_id: str, request: Request):
    """
    Blog Page: Displays published posts for a specific blog.
    """
    blog = get_blog_config(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

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
        # Note: Airtable formula string values should be single-quoted
        records = table.all(formula=f"{{Slug}}='{slug}'")
        if not records:
             # Try fallback for hash-based slugs if accidentally saved that way or URL encoding
             records = table.all(formula=f"{{Slug}}='{slug.replace('#', '')}'")

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
    """Executes the generate_post.py script as a subprocess."""
    print(f"Triggering generation for {blog_id}")
    try:
        # Check if blog has v2 default
        blog = get_blog_config(blog_id)
        # Use -m to ensure package imports work correctly
        cmd = [sys.executable, "-m", "execution.generate_post", "--blog-id", blog_id]
        
        if blog and blog.get("generation_contract_default") == "v2.0":
             cmd.append("--force-v2")
             
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Generation failed: {e}")

@app.get("/sitemap.xml", response_class=HTMLResponse)
async def sitemap(request: Request):
    """Generates a dynamic sitemap for the current blog."""
    blog = get_current_blog(request)
    try:
        airtable = get_airtable_client()
        base_id = get_base_id(blog)
        table = airtable.table(base_id, blog["airtable"]["table_name"])
        posts = table.all(sort=["-PublishedDate"], formula="{Status}='Published'")
    except:
        posts = []

    domain = f"https://{blog['domain']}"
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Home
    xml_content += f"  <url><loc>{domain}/</loc><changefreq>daily</changefreq></url>\n"
    
    # Posts
    for post in posts:
        slug = post.get('fields', {}).get('Slug')
        if slug:
            date = post.get('fields', {}).get('PublishedDate', datetime.now().strftime("%Y-%m-%d"))
            xml_content += f"  <url><loc>{domain}/post/{slug}</loc><lastmod>{date}</lastmod></url>\n"
            
    xml_content += "</urlset>"
    return HTMLResponse(content=xml_content, media_type="application/xml")

@app.get("/rss.xml", response_class=HTMLResponse)
async def rss(request: Request):
    """Generates an RSS feed for the current blog."""
    blog = get_current_blog(request)
    try:
        airtable = get_airtable_client()
        base_id = get_base_id(blog)
        table = airtable.table(base_id, blog["airtable"]["table_name"])
        posts = table.all(sort=["-PublishedDate"], formula="{Status}='Published'")
    except:
        posts = []

    domain = f"https://{blog['domain']}"
    rss_content = '<?xml version="1.0" encoding="UTF-8" ?>\n'
    rss_content += '<rss version="2.0">\n'
    rss_content += '  <channel>\n'
    rss_content += f"    <title>{blog['name']}</title>\n"
    rss_content += f"    <link>{domain}</link>\n"
    rss_content += f"    <description>Latest posts from {blog['name']}</description>\n"
    
    for post in posts:
        fields = post.get('fields', {})
        rss_content += "    <item>\n"
        rss_content += f"      <title>{fields.get('Title', 'Untitled')}</title>\n"
        rss_content += f"      <link>{domain}/post/{fields.get('Slug', '')}</link>\n"
        rss_content += f"      <description>{fields.get('MetaDescription', '')}</description>\n"
        rss_content += f"      <pubDate>{fields.get('PublishedDate', '')}</pubDate>\n"
        rss_content += "    </item>\n"
        
    rss_content += "  </channel>\n"
    rss_content += "</rss>"
    return HTMLResponse(content=rss_content, media_type="application/xml")
