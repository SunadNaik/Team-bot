import sys
import traceback
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity
from bot import MyBot
from config import DefaultConfig

# Load configuration
CONFIG = DefaultConfig()

# Initialize web app
APP = web.Application(middlewares=[aiohttp_error_middleware])

# Initialize adapter
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Initialize bot
BOT = MyBot()

# Error handler
async def on_error(context: TurnContext, error: Exception):
    print(f"[on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity("Please fix the bot source code to continue.")

ADAPTER.on_turn_error = on_error

# Handle bot messages
async def messages(req: web.Request) -> web.Response:
    if req.content_type != "application/json":
        return web.Response(status=415)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)

# Admin dashboard route
async def admin_dashboard(req: web.Request) -> web.Response:
    points_table = BOT.points_table
    mentions_table = BOT.mentions_table

    print(f"Points Table: {points_table}")  # Add this line to log points data
    print(f"Mentions Table: {mentions_table}")  # Add this line to log mentions data

    # Generate HTML for the dashboard
    html = "<h1>Admin Dashboard</h1>"
    html += "<h2>Points Table</h2><table border='1'>"
    html += "<tr><th>Name</th><th>Points</th><th>Emojis Used</th></tr>"
    for user_id, data in points_table.items():
        emojis = " ".join(data["emojis"])  # Display emojis as a string
        html += f"<tr><td>{data['name']}</td><td>{data['points']}</td><td>{emojis}</td></tr>"
    html += "</table>"

    html += "<h2>Mention History</h2><ul>"
    for mention in mentions_table:
        html += f"<li>{mention['mentioned_by']} mentioned {mention['mentioned']}</li>"
    html += "</ul>"

    print("Dashboard generated successfully.")  # Add this line to confirm if this part works

    return web.Response(text=html, content_type="text/html")

# Define routes
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/admin/dashboard", admin_dashboard)

# Run app
if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
