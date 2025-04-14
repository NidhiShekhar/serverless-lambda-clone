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

import streamlit as st
import requests
import json
import asyncio

# Fix for the asyncio issue in Python 3.13
try:
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
except RuntimeError:
    pass

# Setup Streamlit page config
st.set_page_config(
    page_title="Serverless Functions Platform",
    layout="wide"
)

# Base URL for the API
API_BASE_URL = "http://backend:8000"


def main():
    st.title("Serverless Functions Platform")

    # Define Sidebar Navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Home", "Deploy Function", "Execute Function", "View Logs", "Metrics Dashboard"]
    )

    if page == "Home":
        show_home()
    elif page == "Deploy Function":
        deploy_function()
    elif page == "Execute Function":
        execute_function()
    elif page == "View Logs":
        view_logs()
    elif page == "Metrics Dashboard":
        show_metrics_dashboard()


def show_home():
    st.header("Welcome to Serverless Functions Platform")
    st.write("""
    This platform allows you to:
    - Deploy serverless functions in Python or JavaScript
    - Execute your functions in isolated containers
    - View execution logs and metrics

    Use the navigation menu on the left to get started.
    """)


def deploy_function():
    st.header("Deploy a New Function")

    # Form inputs
    with st.form("deploy_form"):
        name = st.text_input("Function Name")
        language = st.selectbox("Language", ["python", "javascript"])
        timeout = st.slider("Timeout (seconds)", 1, 30, 5)
        code = st.text_area("Code", height=300)

        submit_button = st.form_submit_button("Deploy Function")

    if submit_button:
        # Call FastAPI endpoint
        response = requests.post(
            f"{API_BASE_URL}/functions",
            json={"name": name, "code": code, "language": language, "timeout": timeout}
        )

        if response.status_code == 200:
            function_data = response.json()
            st.success(f"Function deployed successfully! Function ID: {function_data.get('id')}")
            st.json(function_data)
        else:
            st.error(f"Error deploying function: {response.text}")


def execute_function():
    st.header("Execute Function")

    # Get list of functions
    try:
        response = requests.get(f"{API_BASE_URL}/functions")
        functions = response.json()

        # Create a dictionary of function_id: function_name
        function_options = {f["id"]: f"{f['id']} - {f['name']} ({f['language']})"
                            for f in functions}

        # Allow user to select a function
        selected = st.selectbox(
            "Select a function to execute",
            options=list(function_options.keys()),
            format_func=lambda x: function_options[x]
        )

        if st.button("Execute"):
            with st.spinner("Executing function..."):
                exec_response = requests.post(f"{API_BASE_URL}/functions/{selected}/execute")

                if exec_response.status_code == 200:
                    result = exec_response.json()

                    st.success("Function executed successfully")

                    # Check if result contains output or error
                    if "result" in result:
                        result_data = result["result"]
                        if "output" in result_data:
                            st.subheader("Output")
                            st.code(result_data["output"])
                        elif "error" in result_data:
                            st.subheader("Error")
                            st.error(result_data["error"])

                    st.json(result)
                else:
                    st.error(f"Error executing function: {exec_response.text}")

    except Exception as e:
        st.error(f"Error loading functions: {str(e)}")


def view_logs():
    st.header("Function Execution Logs")

    # Get list of functions
    try:
        response = requests.get(f"{API_BASE_URL}/functions")
        functions = response.json()

        # Create a dictionary of function_id: function_name
        function_options = {f["id"]: f"{f['id']} - {f['name']} ({f['language']})"
                            for f in functions}

        # Allow user to select a function
        selected = st.selectbox(
            "Select a function to view logs",
            options=list(function_options.keys()),
            format_func=lambda x: function_options[x]
        )

        if st.button("View Logs"):
            logs_response = requests.get(f"{API_BASE_URL}/functions/{selected}/logs")

            if logs_response.status_code == 200:
                logs_data = logs_response.json()

                if "logs" in logs_data and logs_data["logs"]:
                    st.subheader("Execution History")

                    # Create a table with execution logs
                    for idx, log in enumerate(logs_data["logs"]):
                        with st.expander(f"Execution #{idx + 1} - {log.get('timestamp', 'Unknown date')}"):
                            if "result" in log:
                                result = log["result"]
                                if isinstance(result, str):
                                    try:
                                        result = json.loads(result)
                                    except:
                                        pass

                                if isinstance(result, dict):
                                    if "output" in result:
                                        st.success("Success")
                                        st.code(result["output"])
                                    elif "error" in result:
                                        st.error("Failed")
                                        st.code(result["error"])
                                else:
                                    st.write(result)
                else:
                    st.info("No logs found for this function")
            else:
                st.error(f"Error fetching logs: {logs_response.text}")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_metrics_dashboard():
    st.header("Metrics Dashboard")

    tab1, tab2 = st.tabs(["Grafana Dashboard", "Raw Metrics"])

    with tab1:
        st.subheader("Function Execution Metrics")

        # Replace with your actual dashboard ID from Grafana
        # You can find this ID in the URL after /d/ when viewing your dashboard
        dashboard_id = "lambda-metrics"

        # Embed the Grafana dashboard with proper parameters
        st.components.v1.iframe(
            f"http://localhost:3000/d/lambda-metrics/serverless-lambda-clone-full-metrics?orgId=1&from=now-6h&to=now&timezone=browser&refresh=10s",
            height=800,
            scrolling=True
        )

    with tab2:
        # Keep your existing raw metrics display code
        st.subheader("Raw Prometheus Metrics")
        metrics_response = requests.get(f"{API_BASE_URL}/metrics")
        if metrics_response.status_code == 200:
            # Rest of your existing metrics code
            metrics_text = metrics_response.text
            function_metrics = [line for line in metrics_text.split('\n')
                                if 'serverless_function' in line and not line.startswith('#')]

            if function_metrics:
                st.text('\n'.join(function_metrics))
            else:
                st.info("No function execution metrics found")
        else:
            st.error("Failed to load metrics")

if __name__ == "__main__":
    main()