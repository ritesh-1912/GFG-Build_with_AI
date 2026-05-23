import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card

app = FastAPI(title="GitHub Dev Card API")

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Static Files Setup
CARDS_DIR = "static/cards"
os.makedirs(CARDS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerateRequest(BaseModel):
    username: str

# 4. Endpoints
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    try:
        github_data = await scrape_github(username)
        if isinstance(github_data, dict) and github_data.get("error"):
            raise HTTPException(status_code=404, detail=github_data["error"])

        analysis = await analyze_profile(github_data)
        html_content = await generate_card_html(username, github_data, analysis)
        card_url = await save_card(username, html_content)

        return {
            "success": True,
            "card_url": card_url,
            "html": html_content,
            "message": "Card generated successfully."
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/card/{username}")
async def get_card(username: str):
    card_path = os.path.join(CARDS_DIR, f"{username}.html")
    if os.path.exists(card_path):
        return FileResponse(card_path)
    raise HTTPException(status_code=404, detail="Card not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
