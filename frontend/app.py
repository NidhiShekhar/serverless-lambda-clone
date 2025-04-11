# Import streamlit & requests

# Setup Streamlit page config (title, layout)

# Define Sidebar Navigation
# Options:
# - Home
# - Deploy Function
# - Execute Function
# - View Logs
# - View Metrics Dashboard (Grafana iframe)

# If Deploy Function selected:
# - Form inputs:
#   - Function Name
#   - Language (Python / JS)
#   - Timeout
#   - Code Editor (multiline text area)
# - Submit button → calls FastAPI POST /functions/

# If Execute Function selected:
# - Enter function id or pick from dropdown
# - Execute button → calls POST /functions/{id}/execute
# - Display Output / Error / Execution Time

# If View Logs selected:
# - Enter function id
# - Fetch logs via GET /functions/{id}/logs
# - Display in table or text area

# If Metrics Dashboard selected:
# - Embed Grafana Panel iframe
# - URL like: http://localhost:3000/d/your_dashboard_id

