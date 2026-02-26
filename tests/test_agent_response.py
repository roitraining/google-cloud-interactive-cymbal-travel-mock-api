"""
Simple integration test to verify the Agent Engine returns a response.
Run from the project root:
    python -m pytest tests/test_agent_response.py -v
or directly:
    python tests/test_agent_response.py
"""
import asyncio
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import chat


@pytest.mark.anyio
async def test_agent_returns_response():
    response = await chat.process_message(
        user_id="test-user",
        message="Hi, who are you?",
    )

    print(f"\nAgent response: {response}")

    assert response, "Expected a non-empty response from the agent"
    assert isinstance(response, str), "Expected response to be a string"
    assert response != "I encountered an error processing your request.", \
        f"Agent returned an error response: {response}"
    assert response != "Sorry, the AI agent is not currently available.", \
        "Agent was not initialized"


if __name__ == "__main__":
    asyncio.run(test_agent_returns_response())
