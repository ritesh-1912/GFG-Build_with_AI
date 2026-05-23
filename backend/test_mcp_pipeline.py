import asyncio
import os
import json
from github_card_generator.backend.mcp_server import scrape_github, analyze_profile, generate_card_html, save_card

async def run_test():
    username = "torvalds"
    print(f"--- Starting E2E Test for {username} ---")

    # 1. Scrape
    print("Step 1: Scraping GitHub...")
    github_data = await scrape_github(username)
    if "error" in github_data:
        print(f"FAILED: scrape_github -> {github_data['error']}")
        return

    # 2. Analyze
    print("Step 2: Analyzing Profile with Gemini...")
    try:
        analysis = await analyze_profile(github_data)
        print(f"Analysis Results:")
        print(f" - Theme: {analysis.get('card_theme')}")
        print(f" - Vibe: {analysis.get('developer_vibe')}")
    except Exception as e:
        print(f"FAILED: analyze_profile -> {str(e)}")
        return

    # 3. Generate HTML
    print("Step 3: Generating HTML Card...")
    try:
        html = await generate_card_html(username, github_data, analysis)
        print("SUCCESS: HTML card generated.")
    except Exception as e:
        print(f"FAILED: generate_card_html -> {str(e)}")
        return

    # 4. Save (Optional but good for completeness)
    print("Step 4: Saving Card...")
    try:
        path = await save_card(username, html)
        print(f"SUCCESS: Card saved to {path}")
    except Exception as e:
        print(f"FAILED: save_card -> {str(e)}")
        return

    print("--- E2E Test Completed Successfully ---")

if __name__ == "__main__":
    asyncio.run(run_test())
