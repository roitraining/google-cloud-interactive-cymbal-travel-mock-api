import vertexai
from app import config
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vertex AI
remote_agent = None

def init_agent():
    global remote_agent
    try:
        # Check if PROJECT_ID is available
        if not config.PROJECT_ID:
            logger.warning("PROJECT_ID not set. Chat agent will not be initialized.")
            return

        vertexai.init(project=config.PROJECT_ID, location=config.AGENT_LOCATION)
        
        # Initialize the client
        # Note: In the notebook, the user uses client.agent_engines.get(...)
        # We need to replicate that.
        # The prompt uses:
        # client = vertexai.Client(...)
        # remote_agent = client.agent_engines.get(...)
        
        # However, vertexai.init sets the default project/location which might simplify things if using high-level SDK,
        # but for Agent Engine specific client, let's follow the notebook pattern exactly.
        
        client = vertexai.Client(
            project=config.PROJECT_ID,
            location=config.AGENT_LOCATION,
        )
        
        agent_name = f"projects/{config.PROJECT_ID}/locations/{config.AGENT_LOCATION}/reasoningEngines/{config.AGENT_ENGINE_RESOURCE_ID}"
        logger.info(f"Connecting to Agent Engine: {agent_name}")
        
        remote_agent = client.agent_engines.get(name=agent_name)
        logger.info(f"Connected to Agent Engine: {remote_agent.api_resource.display_name}")
        
    except Exception as e:
        logger.error(f"Failed to initialize Agent Engine: {e}")
        remote_agent = None

async def process_message(user_id: str, message: str):
    """
    Sends a message to the agent and returns the full response text.
    """
    start_time = time.time()
    full_text = ""
    error_msg = None

    try:
        if not remote_agent:
            logger.warning("Agent not initialized. Re-attempting initialization...")
            init_agent()
            if not remote_agent:
                error_msg = "Sorry, the AI agent is not currently available."
                return error_msg

        # The notebook uses async_stream_query
        async for event in remote_agent.async_stream_query(
            user_id=user_id,
            message=message
        ):
            # Checking structure from notebook: event["content"]["parts"][0]["text"]
            # But event might be an object, notebook access it as dict which implies it might be subscriptable 
            # or the notebook output shows it printed as dict. 
            # The SDK might return objects.
            # If it's a proto object, we access attributes. 
            # Notebook says: event["content"]["parts"][0]["text"]
            # This suggests it behaves like a dict or is a dict.
            # Let's try to handle both or assume dict as per notebook.
            
            # Defensive coding in case the structure varies
            try:
                # Check for explicit error in event (e.g. 429 Resource Exhausted)
                if isinstance(event, dict) and "error" in event:
                     logger.error(f"Received error from Agent: {event}")
                     raise Exception(f"Agent Error: {event.get('message', 'Unknown error')}")
                
                if hasattr(event, "content"):
                     # It's an object
                     # Check if parts exist
                     parts = event.content.parts
                     if parts:
                         full_text += parts[0].text
                else:
                    # Treat as dict
                    full_text += event["content"]["parts"][0]["text"]
            except (KeyError, IndexError, AttributeError) as e:
                logger.warning(f"Error parsing event: {e}, Event: {event}")
                continue
                
        return full_text
        
    except Exception as e:
        logger.error(f"Error during chat processing: {e}")
        error_msg = "I encountered an error processing your request."
        return error_msg

    finally:
        duration = time.time() - start_time
        log_entry = {
            "user_id": user_id,
            "message": message,
            "response": full_text if not error_msg else None, 
            "error": error_msg,
            "duration_seconds": duration
        }
        logger.info(json.dumps(log_entry))

# Initialize on module load or explicitly
init_agent()
