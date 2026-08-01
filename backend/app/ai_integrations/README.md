# Module 3 — AI Integrations

Part of **Team B2 – Service Execution & Marketplace Operations** for Aegis AI Router.

Connects OpenAI, Gemini, Claude, Groq, Ollama, HuggingFace, and Azure OpenAI
behind one common interface so the **Execution Engine** can call any
ranked/selected agent identically, and **Self-Healing** can fail over
between providers without provider-specific branching.

## Structure

```
integrations/
  __init__.py        # public exports
  base.py             # AIProvider ABC, AIResponse, AIProviderError, TokenUsage
  factory.py          # get_provider(name, **kwargs) registry
  openai.py
  gemini.py
  claude.py
  groq.py
  ollama.py
  huggingface.py
  azure_openai.py
example_usage.py      # Execution Engine + Self-Healing style failover demo
requirements.txt
```

## Common interface

```python
class AIProvider(abc.ABC):
    def generate(self, prompt: str, **kwargs) -> AIResponse: ...
    async def agenerate(self, prompt: str, **kwargs) -> AIResponse: ...
    def health_check(self) -> bool: ...
```

Every provider returns the same `AIResponse` shape:

```python
@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    latency_ms: float
    usage: TokenUsage
    finish_reason: str | None
    raw: Any
```

And every failure — bad key, timeout, rate limit, malformed vendor
response — is normalized into a single `AIProviderError(retryable: bool)`,
so Self-Healing only has to catch one exception type to decide whether to
retry the same provider or fail over to the next backup agent.

## Usage

```python
from integrations import get_provider

provider = get_provider("claude", api_key=os.environ["ANTHROPIC_API_KEY"])
response = provider.generate("Summarize x402 in one sentence.")
print(response.content, response.usage, response.latency_ms)
```

Switching providers is a one-line change — same call shape for every one:

```python
provider = get_provider("groq", api_key=os.environ["GROQ_API_KEY"])
provider = get_provider("ollama")  # local, no key needed
provider = get_provider("azure", api_key=..., endpoint="https://my-resource.openai.azure.com", deployment="gpt-4o")
```

## Per-provider config

| Provider | Required | Notes |
|---|---|---|
| `openai` | `api_key` | optional `base_url` for proxies |
| `gemini` | `api_key` | model defaults to `gemini-1.5-flash` |
| `claude` | `api_key` | model defaults to `claude-sonnet-4-6` |
| `groq` | `api_key` | OpenAI-compatible API |
| `ollama` | — | local server, defaults to `http://localhost:11434` |
| `huggingface` / `hf` | `api_key` | 503 (model loading) is marked retryable |
| `azure_openai` / `azure` | `api_key`, `endpoint`, `deployment` | deployment name, not model name, drives routing |

## Adding a new provider

Subclass `AIProvider`, implement `_call(self, prompt, **kwargs) -> AIResponse`,
then register it:

```python
from integrations.factory import register_provider
register_provider("my_provider", MyProviderClass)
```

## Where this fits in the pipeline

```
Selected AI Agent → Payment Service → Execution Engine → AI Integration Layer (this module)
   → Receive Response → History / Reputation / Analytics
   → Self-Healing (only if execution fails, using AIProviderError.retryable)
```
