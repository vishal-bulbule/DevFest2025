from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient

from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any, Optional
from google.adk.tools import ToolContext
import copy
import json

# Connect to MCP tool server
toolbox = ToolboxSyncClient("http://127.0.0.1:5000")

# Load BigQuery HR toolset
tools = toolbox.load_toolset("gcp_bq_employees")

def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Converts the 'Country' argument to Camel Case before the tool call.
    """
    tool_name = tool.name
    print(f"[Callback] Before tool call for '{tool_name}'")
    print(f"[Callback] Original args: {args}")

    # Only modify args for this specific tool
    if tool_name == "search_employees_by_country":
        country = args.get("Country", "")
        if country:
            # Convert to Camel Case
            args["Country"] = " ".join(word.capitalize() for word in country.split())
            print(f"[Callback] Converted Country to Camel Case: {args['Country']}")

    print("[Callback] Proceeding with normal tool call")
    return None

def after_tool_callback(tool, args, tool_context, tool_response: str) -> list:
    """
    Filters tool response rows based on user's department.
    Handles tool_response as a string that needs to be parsed into a list.
    """
    # 1. Get user department
    # Note: I am assuming the user_id is 'vishal' for testing this specific outcome.
    session = tool_context._invocation_context.session
    try:
        user_id = session.user_id.strip().lower()
    except AttributeError:
        # Fallback if session.user_id is not set
        user_id = "user" 

    USER_DEPARTMENT_MAP = {
        "vishal": "Finance",  # Vishal's department
        "alice": "Marketing",
        "user": "IT",
    }
    department = USER_DEPARTMENT_MAP.get(user_id)
    
    # 2. No mapping → access denied
    if not department:
        return [{"Department": None, "message": "You do not have access to department-specific data."}]

    # 3. Parse the string response into a Python list of dictionaries
    if isinstance(tool_response, str):
        try:
            # The critical change: Use json.loads() to parse the string
            data_list = json.loads(tool_response)
        except json.JSONDecodeError as e:
            print(f"Error: Tool response string could not be parsed as JSON: {e}")
            return [{"Department": None, "message": "Tool response was malformed and could not be filtered."}]
    elif isinstance(tool_response, list):
        # Handle the case where it's already a list (no parsing needed)
        data_list = tool_response
    else:
        # Handle any other unexpected type
        print(f"Error: Unexpected tool_response type: {type(tool_response)}")
        return [{"Department": None, "message": "Unexpected tool response format."}]
    
    # 4. Filter the data
    # Filter only dicts and by department (case-insensitive check)
    filtered_result = [
        row for row in data_list
        if isinstance(row, dict) and str(row.get("Department", "")).strip().lower() == department.lower()
    ]

    # Optional: Return a message if the filter yielded no results
    if not filtered_result:
        return [{"Department": department, "message": f"No data found for department: {department}."}]

    return filtered_result

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=(
        "You are an HR Data Analyst.\n"
        "Use the tools to answer questions about employees, countries, and workforce stats.\n\n"
        "→ Use `search_users_by_id` for EmployeeID.\n"
        "→ Use `search_users_by_country` for country-based queries.\n"
        "Respond clearly and concisely — no SQL, no tool names, just insights."
    ),
    tools=tools,
    after_tool_callback=after_tool_callback,
    before_tool_callback=before_tool_callback,
)
