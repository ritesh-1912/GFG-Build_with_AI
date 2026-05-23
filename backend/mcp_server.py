import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
import google.generativeai as genai
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("GitHub Card Generator")

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
model = genai.GenerativeModel(MODEL_NAME)

GITHUB_API_URL = "https://api.github.com"

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetch GitHub stats for a given username using GitHub REST API."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    async with httpx.AsyncClient(headers=headers) as client:
        # User details
        user_resp = await client.get(f"{GITHUB_API_URL}/users/{username}")
        if user_resp.status_code != 200:
            return {"error": f"User {username} not found"}
        user_data = user_resp.json()

        # Repositories
        repos_resp = await client.get(f"{GITHUB_API_URL}/users/{username}/repos?sort=stars&per_page=30")
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        # Sort and take top 6
        sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
        
        top_repos = []
        languages = {}
        for r in sorted_repos:
            lang = r.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            top_repos.append({
                "name": r.get("name"),
                "stars": r.get("stargazers_count"),
                "language": lang,
                "description": r.get("description")
            })

        # Sort languages by count
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "avatar_url": user_data.get("avatar_url"),
            "top_repos": top_repos,
            "most_used_languages": [l[0] for l in top_languages[:5]]
        }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Analyze GitHub data using Gemini to derive developer personality and theme."""
    prompt = f"""
    Analyze this GitHub developer profile data and return a JSON object with:
    - developer_vibe: A 1-sentence personality description.
    - top_skills: A list of exactly 3 technical skills or focus areas.
    - fun_fact: A clever inference or observation based on their repos/activity.
    - card_theme: Choose exactly one from ["hacker", "builder", "researcher", "designer", "open-source-hero"].

    GitHub Data:
    {json.dumps(github_data, indent=2)}

    JSON Output:
    """
    
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generate a self-contained HTML/CSS string for the dev card."""
    theme = analysis.get("card_theme", "builder")
    
    theme_styles = {
        "hacker": "background: #0d1117; color: #58a6ff; border: 1px solid #30363d;",
        "builder": "background: #f6f8fa; color: #24292f; border: 1px solid #d0d7de;",
        "researcher": "background: #ffffff; color: #1a7f37; border: 1px solid #1a7f37;",
        "designer": "background: linear-gradient(135deg, #ff0080, #7928ca); color: #fff; border: none;",
        "open-source-hero": "background: #f0f9ff; color: #0366d6; border: 1px solid #0366d6;"
    }
    
    style = theme_styles.get(theme, theme_styles["builder"])
    
    badge_style = "display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; background: rgba(0,0,0,0.1);"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; {style} border-radius: 12px; padding: 24px; max-width: 450px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src=\"{github_data.get('avatar_url')}\" style=\"width: 80px; height: 80px; border-radius: 50%; margin-right: 20px; border: 2px solid currentColor;\">
            <div>
                <h2 style=\"margin: 0;\">{github_data.get('name')}</h2>
                <p style=\"margin: 4px 0; opacity: 0.8; font-size: 14px;\">@{username}</p>
                <p style=\"margin: 0; font-style: italic; font-size: 14px;\">{analysis.get('developer_vibe')}</p>
            </div>
        </div>
        
        <div style=\"margin-bottom: 20px;\">
            <p style=\"font-size: 14px; margin-bottom: 8px;\"><b>Top Skills:</b></p>
            <div>
                {"".join([f'<span style=\"{badge_style}\">{skill}</span>' for skill in analysis.get('top_skills', [])])}
            </div>
        </div>

        <div style=\"display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; font-size: 14px;\">
            <div><b>Repos:</b> {github_data.get('public_repos')}</div>
            <div><b>Followers:</b> {github_data.get('followers')}</div>
        </div>

        <div style=\"margin-bottom: 20px;\">
            <p style=\"font-size: 14px; margin-bottom: 8px;\"><b>Featured Projects:</b></p>
            <ul style=\"list-style: none; padding: 0; margin: 0; font-size: 13px;\">
                {"".join([f'<li style=\"margin-bottom: 5px;\">• {repo["name"]} ({repo["stars"]} ★)</li>' for repo in github_data.get('top_repos', [])[:3]])}
            </ul>
        </div>

        <div style=\"font-size: 12px; opacity: 0.8; padding-top: 10px; border-top: 1px solid currentColor;\">
            <b>Fun Fact:</b> {analysis.get('fun_fact')}
        </div>
    </div>
    """
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Save the HTML dev card to a file and return the relative path."""
    os.makedirs("static/cards", exist_ok=True)
    file_path = f"static/cards/{username}.html"
    with open(file_path, "w") as f:
        f.write(html)
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
