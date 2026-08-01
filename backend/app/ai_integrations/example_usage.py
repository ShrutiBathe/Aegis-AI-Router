"""
example_usage.py

Demonstrates how downstream modules (Execution Engine, Self-Healing) are
expected to consume Module 3.
"""

import os

from integrations import get_provider, AIProviderError


def execute_with_failover(primary: str, backups: list[str], prompt: str, **provider_kwargs):
    """
    Toy version of what the Execution Engine + Self-Healing modules would
    do: try the selected agent's provider, and on a retryable failure,
    fail over to the next backup provider in the ranked list.
    """
    candidates = [primary] + backups
    last_error = None

    for name in candidates:
        try:
            provider = get_provider(name, **provider_kwargs.get(name, {}))
            response = provider.generate(prompt)
            print(f"[execution] succeeded with provider={name} model={response.model} "
                  f"latency_ms={response.latency_ms}")
            return response
        except AIProviderError as exc:
            print(f"[self-healing] provider={name} failed (retryable={exc.retryable}): {exc.message}")
            last_error = exc
            if not exc.retryable:
                # Non-retryable errors (bad config, missing key) still move
                # on to the next backup rather than aborting the whole task.
                continue
            continue

    raise last_error


if __name__ == "__main__":
    result = execute_with_failover(
        primary="claude",
        backups=["groq", "ollama"],
        prompt="In one sentence, what is x402?",
        provider_kwargs={
            "claude": {"api_key": os.environ.get("ANTHROPIC_API_KEY")},
            "groq": {"api_key": os.environ.get("GROQ_API_KEY")},
            "ollama": {},  # local, no key needed
        },
    )
    print(result.to_dict())
