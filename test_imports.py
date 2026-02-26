 
import vertexai
from vertexai.preview import reasoning_engines
import inspect

try:
    print("ReasoningEngine imported successfully")
    print(dir(reasoning_engines.ReasoningEngine))
    if hasattr(reasoning_engines.ReasoningEngine, 'query'):
        print("ReasoningEngine has method 'query'")
    else:
        print("ReasoningEngine DOES NOT HAVE 'query'")
except Exception as e:
    print(f"Error: {e}")
