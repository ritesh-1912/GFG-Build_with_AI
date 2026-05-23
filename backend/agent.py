import os
import sys
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset, 
    StdioConnectionParams, 
    StdioServerParameters
)

# Define the path to the MCP server script relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(current_dir, "mcp_server.py")

# Configure the MCP Toolset using stdio transport
# This allows the ADK agent to call the tools defined in mcp_server.py
github_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable, 
            args=[mcp_server_path],
            env=os.environ.copy()
        ),
        timeout=60
    )
)

# System instruction as requested
SYSTEM_INSTRUCTION = (
    "You are a GitHub profile analyst and dev card generator. "
    "When a user gives you a GitHub username, you ALWAYS follow this exact sequence: "
    "first call scrape_github, then analyze_profile with the result, "
    "then generate_card_html with all three inputs, then save_card. "
    "Never skip steps. Be enthusiastic about developers' work. "
    "If the profile is private or doesn't exist, say so clearly."
)

# Initialize the agent with Gemini 2.5 Flash
github_card_agent = Agent(
    name="github_card_agent",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    tools=[github_toolset]
)

# Function to orchestrate the generation for the FastAPI app
async def run_agent_generation(username: str):
    """Run the agent to generate a dev card for the given username."""
    # We use the agent.run method which returns an async iterator of events
    # In a production scenario, we'd handle these events (tool calls, thoughts, etc.)
    # For the API, we'll collect the final response.
    try:
        response_text = ""
        async for event in github_card_agent.run(f"Generate a dev card for user: {username}"):
            # Depending on the ADK version, we collect text or the final result
            # Assuming 'event' has a text attribute or similar for the final response
            if hasattr(event, 'text'):
                response_text += event.text
            elif isinstance(event, str):
                response_text += event
        
        # We also need to extract the card_url which the agent should have generated and saved
        # The agent.run will execute the tool sequence and return the final confirmation.
        return {"success": True, "message": response_text, "username": username}
    except Exception as e:
        return {"success": False, "error": str(e)}
