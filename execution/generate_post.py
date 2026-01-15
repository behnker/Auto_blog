import argparse
import os
import sys
from datetime import datetime
import anthropic
from execution.utils import get_blog_config, get_airtable_client, get_base_id

# Initialize Anthropic Client
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("WARNING: ANTHROPIC_API_KEY is None")
else:
    print(f"DEBUG: ANTHROPIC_API_KEY loaded: {api_key[:5]}...{api_key[-4:]} (Length: {len(api_key)})")

client = anthropic.Anthropic(
    api_key=api_key
)

def generate_post_content(blog_config):
    """
    Generates blog post content using Claude.
    TODO: Implement "Deep Well" and "Knowledge Integration" logic here.
    For now, this is a placeholder implementation.
    """
    system_prompt = "You are an expert blogger. Write a short, engaging blog post about a random topic related to the blog's theme."
    
    # In a real implementation, we would fetch 'Knowledge' from Airtable here
    # and inject it into the prompt.
    
    user_message = f"Write a blog post for the blog named '{blog_config['name']}'. Include a Title and Content in Markdown format."

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
    except anthropic.APIError as e:
        print(f"Anthropic API Error: {e}")
        # Return dummy content for dry-run if API fails, so we can verify the rest of the flow
        return "Title: API Error Occurred\n\nContent could not be generated due to API error. Check logs."

    # Simple parsing (robust parsing would separate Title/Content better)
    response_text = message.content[0].text
    
    # Assumption: Claude returns "Title: ... \n\n Content..."
    # This needs refinement in the 'Directive' phase.
    return response_text

def save_to_airtable(blog_config, content, is_draft=True):
    """Saves the generated content to Airtable."""
    airtable = get_airtable_client()
    base_id = get_base_id(blog_config)
    table_name = blog_config["airtable"]["table_name"]
    table = airtable.table(base_id, table_name)
    
    # Parse title vs content (Placeholder logic)
    lines = content.strip().split('\n')
    title = lines[0].replace("Title:", "").strip()
    body = "\n".join(lines[1:]).strip()
    
    record = table.create({
        "Title": title,
        "Content": body,
        "Status": "Draft" if is_draft else "Published",
        "PublishedDate": datetime.now().isoformat(),
        "Slug": title.lower().replace(" ", "-") # Simple slugify
    })
    print(f"Created record: {record['id']}")
    return record

def main():
    parser = argparse.ArgumentParser(description="Generate a blog post.")
    parser.add_argument("--blog-id", required=True, help="ID of the blog to generate for")
    parser.add_argument("--dry-run", action="store_true", help="Print content instead of saving")
    
    args = parser.parse_args()
    
    blog_config = get_blog_config(args.blog_id)
    if not blog_config:
        print(f"Error: Blog ID '{args.blog_id}' not found in config.")
        sys.exit(1)
        
    print(f"Generating post for: {blog_config['name']}...")
    content = generate_post_content(blog_config)
    
    if args.dry_run:
        print("\n--- GENERATED CONTENT ---\n")
        print(content)
        print("\n--------------------------\n")
    else:
        save_to_airtable(blog_config, content)
        print("Post saved to Airtable.")

if __name__ == "__main__":
    main()
