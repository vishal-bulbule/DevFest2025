from google.adk.agents.llm_agent import Agent
from google.adk.tools import ToolContext
from typing import Dict, Any,Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import google_search

def before_model(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """
    Appends instructions to the last user message before sending to LLM.
    """
    agent_name = callback_context.agent_name

    # Find the last user message
    last_user_message = ""
    if llm_request.contents and len(llm_request.contents) > 0:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts and len(content.parts) > 0:
                if hasattr(content.parts[0], "text") and content.parts[0].text:
                    last_user_message = content.parts[0].text
                    break

    print("=== MODEL REQUEST STARTED ===")
    print(f"Agent: {agent_name}")
    if last_user_message:
        print(f"User message: {last_user_message[:100]}...")

        # Append instructions to the last user message
        content_part = content.parts[0]
        #content_part.text += "\nPlease respond politely and keep the answer under 50 words."
        content_part.text += "\nPlease respond politely and also only give answer in german language."


        # Log the modified text
        print(f"Modified user message: {content_part.text[:150]}...")
        print("=== MODEL REQUEST COMPLETED ===")


    return None  # Continue normal LLM execution

def after_model(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Converts all text in the LLM response to uppercase.
    """
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None

    for part in llm_response.content.parts:
        if hasattr(part, "text") and part.text:
            print(f"Original response part: {part.text}...")
            part.text = part.text.upper()  # convert to uppercase

    return llm_response  # return modified response
    


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for answering user questions.',
    instruction='Answer user questions ',
    before_model_callback=before_model,
    #after_model_callback=after_model,
    output_key="result",
    tools=[google_search],

)
