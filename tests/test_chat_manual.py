import asyncio
import logging
import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from app import chat
from app import config

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_chat_agent():
    print(f"Testing Chat Agent Integration...")
    print(f"Project ID: {config.PROJECT_ID}")
    print(f"Location: {config.AGENT_LOCATION}")
    print(f"Agent Engine ID: {config.AGENT_ENGINE_RESOURCE_ID}")
    
    # 1. Test Initialization
    print("\n--- Initializing Agent ---")
    
    # Try the high-level SDK directly to debug
    try:
        from vertexai.preview import reasoning_engines
        resource_name = f"projects/{config.PROJECT_ID}/locations/{config.AGENT_LOCATION}/reasoningEngines/{config.AGENT_ENGINE_RESOURCE_ID}"
        print(f"Attempting ReasoningEngine({resource_name})")
        agent = reasoning_engines.ReasoningEngine(resource_name)
        print("ReasoningEngine init success!")
        print(f"Attributes: {dir(agent)}")
        
        print(f"Schemas: {agent._operation_schemas}")
        print("Attempting _submit('query')...")
        try:
            response = agent._submit("query", message="Hello")
            print(f"Query response: {response}")
        except Exception as e:
            print(f"_submit failed: {e}") 

        
    except Exception as e:
        print(f"ReasoningEngine failed: {e}")
        import traceback
        traceback.print_exc()

    # chat.init_agent()
    # ...


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(test_chat_agent())
