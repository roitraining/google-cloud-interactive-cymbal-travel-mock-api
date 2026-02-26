import traceback
import vertexai
from app import config
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_message(user_id: str, message: str) -> str:
    """
    Sends a message to the Agent Engine agent and returns the response text.

    A fresh vertexai.Client is created per call so its internal aiohttp
    ClientSession is always constructed inside the running uvicorn event loop.
    Caching the client across requests causes "client has been closed" errors
    on Cloud Run because the session gets bound to a pre-startup loop context.
    """
    start_time = time.time()
    response_text = ""
    error_msg = None

    try:
        if not config.PROJECT_ID:
            error_msg = "Sorry, the AI agent is not currently available."
            return error_msg

        client = vertexai.Client(
            project=config.PROJECT_ID,
            location=config.AGENT_LOCATION,
        )

        agent_name = (
            f"projects/{config.PROJECT_ID}"
            f"/locations/{config.AGENT_LOCATION}"
            f"/reasoningEngines/{config.AGENT_ENGINE_RESOURCE_ID}"
        )

        remote_agent = client.agent_engines.get(name=agent_name)

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
