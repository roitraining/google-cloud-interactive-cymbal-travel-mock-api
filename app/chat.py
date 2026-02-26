import traceback
import vertexai
from app import config
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module-level agent instance
remote_agent = None


def init_agent():
    """
    Initialize the Agent Engine client. Called synchronously at module load
    (before the uvicorn event loop starts) so that the vertexai/aiohttp client
    is set up in the correct pre-loop context.
    """
    global remote_agent
    try:
        if not config.PROJECT_ID:
            logger.warning("PROJECT_ID not set. Chat agent will not be initialized.")
            return

        logger.info(
            f"Initializing Vertex AI with project={config.PROJECT_ID}, "
            f"location={config.AGENT_LOCATION}"
        )

        client = vertexai.Client(
            project=config.PROJECT_ID,
            location=config.AGENT_LOCATION,
        )

        agent_name = (
            f"projects/{config.PROJECT_ID}"
            f"/locations/{config.AGENT_LOCATION}"
            f"/reasoningEngines/{config.AGENT_ENGINE_RESOURCE_ID}"
        )
        logger.info(f"Connecting to Agent Engine: {agent_name}")

        remote_agent = client.agent_engines.get(name=agent_name)
        logger.info("Successfully connected to Agent Engine.")

    except Exception as e:
        logger.error(f"Failed to initialize Agent Engine: {e}")
        remote_agent = None


async def process_message(user_id: str, message: str) -> str:
    """
    Sends a message to the Agent Engine agent and returns the response text.
    Streams all events and extracts text from the final content-bearing event.
    """
    start_time = time.time()
    response_text = ""
    error_msg = None

    try:
        if not remote_agent:
            logger.warning("Agent not initialized. Re-attempting initialization...")
            init_agent()
            if not remote_agent:
                error_msg = "Sorry, the AI agent is not currently available."
                return error_msg

        last_event = None

        async for event in remote_agent.async_stream_query(
            user_id=user_id,
            message=message,
        ):
            last_event = event

        # Extract text from the last event, mirroring the working notebook pattern
        if last_event is not None and "content" in last_event:
            try:
                parts = last_event["content"]["parts"]
                response_text = "".join(
                    part["text"] for part in parts if "text" in part
                )
            except (KeyError, TypeError) as e:
                logger.warning(f"Could not extract text from last event: {e}. Event: {last_event}")
                response_text = str(last_event)
        elif last_event is not None:
            logger.warning(f"Last event had no 'content' key. Event: {last_event}")
            response_text = str(last_event)
        else:
            response_text = "No response received from the agent."

        return response_text

    except Exception as e:
        logger.error(f"Error during chat processing: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        error_msg = "I encountered an error processing your request."
        return error_msg

    finally:
        duration = time.time() - start_time
        log_entry = {
            "user_id": user_id,
            "message": message,
            "response": response_text if not error_msg else None,
            "error": error_msg,
            "duration_seconds": round(duration, 3),
        }
        logger.info(json.dumps(log_entry))


# Initialize synchronously at module load, before uvicorn starts its event loop.
# vertexai's internal aiohttp ClientSession must be created in a pre-loop context.
init_agent()
