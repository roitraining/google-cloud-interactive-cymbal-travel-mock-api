import traceback
import vertexai
from app import config
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_agent_name() -> str:
    """Returns the fully-qualified Agent Engine resource name."""
    return (
        f"projects/{config.PROJECT_ID}"
        f"/locations/{config.AGENT_LOCATION}"
        f"/reasoningEngines/{config.AGENT_ENGINE_RESOURCE_ID}"
    )


async def create_session(user_id: str) -> str:
    """
    Creates a new Agent Engine session for the given user and returns the session ID.
    """
    if not config.PROJECT_ID:
        raise RuntimeError("AI agent is not configured (PROJECT_ID missing).")

    client = vertexai.Client(
        project=config.PROJECT_ID,
        location=config.AGENT_LOCATION,
    )
    remote_agent = client.agent_engines.get(name=_build_agent_name())
    session = await remote_agent.async_create_session(user_id=user_id)
    session_id = session["id"]
    logger.info(json.dumps({"event": "session_created", "user_id": user_id, "session_id": session_id}))
    return session_id


async def process_message(user_id: str, message: str, session_id: str) -> str:
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

        remote_agent = client.agent_engines.get(name=_build_agent_name())

        last_event = None

        async for event in remote_agent.async_stream_query(
            user_id=user_id,
            session_id=session_id,
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
            "session_id": session_id,
            "message": message,
            "response": response_text if not error_msg else None,
            "error": error_msg,
            "duration_seconds": round(duration, 3),
        }
        logger.info(json.dumps(log_entry))
