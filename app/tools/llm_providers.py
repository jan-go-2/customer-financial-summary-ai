import os
from typing import Optional

import requests

LOCAL_MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

_tokenizer = None
_model = None


# ---------- Shared HTTP caller for all cloud providers ----------

def _call_openai_compatible_chat(
    base_url: str,
    api_key_env_var: str,
    model: str,
    prompt: str,
    provider_label: str,
    extra_headers: Optional[dict] = None,
    timeout: int = 120,
) -> str:
    api_key = os.environ.get(api_key_env_var)
    if not api_key:
        raise EnvironmentError(
            f"{api_key_env_var} is not set. Export it before running, e.g.\n"
            f'  export {api_key_env_var}="your-key-here"'
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 1024,
    }

    print(f"Calling {provider_label} ({model})...")

    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=timeout)
        print("Status Code:", response.status_code)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"{provider_label} API call failed: {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(
            f"{provider_label} returned an unexpected response shape: {data}"
        ) from exc


PROVIDER_CONFIGS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
        "api_key_env_var": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
        "label": "Groq",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1/chat/completions",
        "api_key_env_var": "CEREBRAS_API_KEY",
        "default_model": "llama3.3-70b",
        "label": "Cerebras",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_env_var": "OPENROUTER_API_KEY",
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
        "label": "OpenRouter",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1/chat/completions",
        "api_key_env_var": "MISTRAL_API_KEY",
        "default_model": "mistral-small-latest",
        "label": "Mistral",
    },
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_key_env_var": "NVIDIA_API_KEY",
        "default_model": "meta/llama-3.1-70b-instruct",
        "label": "NVIDIA NIM",
    },
}


def call_cloud_provider(prompt: str, provider_name: str, model: Optional[str] = None) -> str:
    if provider_name not in PROVIDER_CONFIGS:
        raise ValueError(
            f"Unknown provider: {provider_name}. Supported: {list(PROVIDER_CONFIGS.keys())}"
        )
    config = PROVIDER_CONFIGS[provider_name]
    model = model or config["default_model"]
    return _call_openai_compatible_chat(
        base_url=config["base_url"],
        api_key_env_var=config["api_key_env_var"],
        model=model,
        prompt=prompt,
        provider_label=config["label"],
    )


# ---------- Local model (Qwen, runs on CPU) ----------

def _load_local_model():
    """Load the local tokenizer/model once, on first use, and cache them."""
    global _tokenizer, _model

    if _model is None:
        # Imported here so torch/transformers are only pulled in if the
        # local model path is actually used.
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        print(f"Loading tokenizer: {LOCAL_MODEL_NAME}")
        _tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME)

        print(f"Loading model: {LOCAL_MODEL_NAME}")
        _model = AutoModelForCausalLM.from_pretrained(
            LOCAL_MODEL_NAME, dtype=torch.float32, device_map="cpu"
        )
        print("Model loaded.\n")

    return _tokenizer, _model


def call_local_model(prompt: str) -> str:
    tokenizer, model = _load_local_model()
    messages = [{"role": "user", "content": prompt}]

    chat = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(chat, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs, max_new_tokens=512, do_sample=False, temperature=0.0
    )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )
    return response.strip()


def call_llm(prompt: str, provider: str) -> str:
    """
    Single entry point for entity_extractor.py -- it just calls this with
    a provider name and doesn't need to know which HTTP call happens under
    the hood.
    """
    if provider == "local":
        return call_local_model(prompt)
    return call_cloud_provider(prompt, provider)