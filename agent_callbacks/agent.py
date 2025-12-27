from google.adk.agents.llm_agent import Agent
from google.adk.tools import ToolContext
from typing import Dict, Any,Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.tools import google_search

def check_access(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Checks if the user_id is in an allowed list.
    If yes -> allow agent/LLM execution (return None)
    If no  -> skip LLM and return a message
    """
    session = callback_context._invocation_context.session
    user_id = session.user_id
    allowed_users = ["user_123", "user_abc", "Vishal"]

    print(f"\n[Callback] Checking user: {user_id}")

    if user_id in allowed_users:
        print(f"[Callback] User allowed: {user_id} - proceeding with agent/LLM call.")
        return None  # Continue normal execution
    else:
        print(f"[Callback] User not allowed: {user_id} - skipping LLM call.")
        return types.Content(
            parts=[types.Part(text=f"Access denied for user: {user_id}. LLM call skipped.")],
            role="model"  # Optional: role can be 'system' or 'model'
        )

def log_completion(callback_context: CallbackContext) -> Optional[types.Content]:
    current_state = callback_context.state.to_dict()
    print(f"\n[Callback] state: {current_state}")
    print(f"========\n[Callback] Agent Execution Completed=======")



root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for answering user questions.',
    instruction='Answer user questions ',
    #tools=[get_session],
    before_agent_callback=check_access,
    after_agent_callback=log_completion,
    tools=[google_search],
    output_key="result"  
)
