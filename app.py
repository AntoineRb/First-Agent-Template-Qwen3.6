from smolagents import CodeAgent, LiteLLMModel,load_tool,tool
from ddgs import DDGS
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

@tool
def search_web(query: str) -> str:
    """Searches the web with DuckDuckGo and returns the top results with title, link and snippet.
    Args:
        query: The search query, for example 'météo Lille'.
    """
    try:
        results = DDGS().text(query, region="fr-fr", max_results=5)
    except Exception as e:
        return f"Search error: {e}"
    if not results:
        return "No results found for this query."
    return "\n\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in results)
final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = LiteLLMModel(
    model_id="ollama_chat/qwen3.6",
    api_base="http://localhost:11434",
    num_ctx=16384,
    temperature=0.5,
)


# Import tool from Hub
# image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, get_current_time_in_timezone, search_web],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()