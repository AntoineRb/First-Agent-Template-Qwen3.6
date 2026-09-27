---
title: First Agent Template
emoji: ⚡
colorFrom: pink
colorTo: yellow
sdk: gradio
sdk_version: 5.23.1
app_file: app.py
pinned: false
tags:
- smolagents
- agent
- smolagent
- tool
- agent-course
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# First Agent — running locally with smolagents & Ollama

A local version of the **"Let's Create Our First Agent Using smolagents"** exercise from the [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit1/tutorial) (Unit 1).

The original template runs on a Hugging Face Space and calls a model through the Hugging Face Inference API, which quickly requires a paid plan once the free quota is used up. This version runs **entirely on your own machine**: the LLM is served locally by [Ollama](https://ollama.com), so no API key, token or credit card is needed.

## What the agent does

The agent is a smolagents `CodeAgent`: instead of calling tools through JSON, it writes and executes small Python snippets, following a *Thought → Action → Observation* loop until it can call `final_answer`. It comes with three tools:

- **`get_current_time_in_timezone`** returns the current time in any timezone (e.g. `Asia/Tokyo`).
- **`search_web`** searches the web with DuckDuckGo via the [`ddgs`](https://pypi.org/project/ddgs/) library and returns the top results (title, link, snippet).
- **`final_answer`** returns the final answer to the user.

A Gradio chat interface lets you talk to the agent in your browser, while the terminal shows each reasoning step, the generated code and its output.

## Changes from the original template

- **Local model**: `HfApiModel` (Hugging Face Inference API) replaced by `LiteLLMModel` pointing to a local Ollama server running `qwen3.6`.
- **New search tool**: the built-in `DuckDuckGoSearchTool` relies on the deprecated `duckduckgo_search` package, which no longer returns results. It is replaced by a custom `search_web` tool built on `ddgs`.
- **Fixed `prompts.yaml`**: added the missing `final_answer` section. Without it, the agent crashed with `KeyError: 'final_answer'` when it reached `max_steps`.
- **Completed `requirements.txt`**: added packages that are pre-installed on Hugging Face Spaces but missing on a local machine (`gradio`, `pytz`, `litellm`, `ddgs`).
- **No public link**: Gradio now launches with `share=False`, so the agent is only reachable from your machine.
- **Image generation tool disabled**: `agents-course/text-to-image` calls the paid Inference API.

## Requirements

- [uv](https://docs.astral.sh/uv/) (or plain `pip` + `venv`)
- Python **3.12** (3.14 fails: some pinned dependencies have no prebuilt wheels for it)
- [Ollama](https://ollama.com)
- Enough memory for the model: `qwen3.6` (35B-A3B MoE, Q4_K_M) takes about 23 GB, so 32 GB of RAM / unified memory is recommended. Smaller models such as `qwen2.5-coder:7b` also work, with lower quality.

Tested on a MacBook with an Apple M5 chip and 32 GB of unified memory.

## Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

uv venv --python 3.12
uv pip install -r requirements.txt

ollama pull qwen3.6
```

## Usage

Make sure Ollama is running (menu bar app or `ollama serve`), then:

```bash
uv run python app.py
```

Open http://127.0.0.1:7860 and try, for example:

- *What time is it in Tokyo?*
- *What's the weather like in Lille today?*
- *What time is it in New York, and what's the weather there?*

## Model configuration

The model is defined in `app.py`:

```python
model = LiteLLMModel(
    model_id="ollama_chat/qwen3.6",
    api_base="http://localhost:11434",
    num_ctx=16384,
    temperature=0.5,
)
```

- `model_id`: the `ollama_chat/` prefix tells LiteLLM to use Ollama, followed by the model name from `ollama list`.
- `num_ctx`: context window size. Ollama's default is too small for smolagents' system prompt, so it must be raised.
- `max_tokens` is intentionally omitted: `qwen3.6` reasons before answering, and a low limit can cut its answer short.

## Project structure

```
├── app.py              # Tools, model and agent definition
├── prompts.yaml        # System prompt and prompt templates for the CodeAgent
├── Gradio_UI.py        # Gradio chat interface
├── tools/
│   └── final_answer.py # FinalAnswerTool
└── requirements.txt
```

## Troubleshooting

- **`Failed to build pillow` / `libjpeg` not found**: you are on Python 3.14. Recreate the environment with `uv venv --python 3.12`.
- **`Failed to build tokenizers==0.13.3`**: the resolver picked an old version that must be compiled from source. Force a recent one with `uv pip install litellm "tokenizers>=0.21"`.
- **`Please install 'gradio' extra`**: install it with `uv pip install "gradio>=5,<6"`. `Gradio_UI.py` was written for Gradio 5.
- **`Import of X is not allowed`**: expected behaviour. The agent's generated code can only import a whitelist of modules. Add modules via `additional_authorized_imports` in `CodeAgent`, or better, wrap the functionality in a tool.

## Security note

A `CodeAgent` executes Python code generated by the model on your machine. smolagents restricts imports, but keep the interface local (`share=False`) and don't expose it publicly.

## Credits

Based on the [First_agent_template](https://huggingface.co/spaces/agents-course/First_agent_template) Space from the Hugging Face Agents Course, created by [Aymeric Roucher](https://huggingface.co/m-ric) and the Hugging Face team. Built with [smolagents](https://github.com/huggingface/smolagents), [Ollama](https://ollama.com), [LiteLLM](https://github.com/BerriAI/litellm), [ddgs](https://pypi.org/project/ddgs/) and [Gradio](https://www.gradio.app).