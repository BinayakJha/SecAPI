import os
import yaml

CONFIG_FILE = "secapi_config.yaml"

def load_config():
    """Load configuration from secapi_config.yaml if it exists."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Failed to parse config file: {e}")
    return config

def get_ai_config():
    """
    Get AI configuration from config file, environment variables, or vault.
    Returns a dict with provider, model, api_key, and endpoint.
    """
    config = load_config()
    ai_section = config.get("ai", {})

    # 1. Provider (default: gemini)
    provider = ai_section.get("provider") or os.environ.get("SECAPI_AI_PROVIDER", "gemini").lower()

    # 2. Model
    default_model = "gemini-2.5-flash"
    if provider == "openai":
        default_model = "gpt-4o-mini"
    elif provider == "azure":
        default_model = "gpt-4"
    model = ai_section.get("model") or os.environ.get("SECAPI_AI_MODEL", default_model)

    # 3. Endpoint
    endpoint = ai_section.get("endpoint")
    if not endpoint:
        if provider == "openai":
            endpoint = os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        elif provider == "azure":
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        elif provider == "gemini":
            endpoint = "https://generativelanguage.googleapis.com/v1beta/openai"
        else:
            endpoint = os.environ.get("SECAPI_AI_ENDPOINT")

    # 4. API Key
    api_key_setting = ai_section.get("api_key")
    api_key = None
    if api_key_setting:
        if api_key_setting in os.environ:
            api_key = os.environ[api_key_setting]
        else:
            api_key = api_key_setting

    if not api_key:
        if provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif provider == "azure":
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        elif provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")

    # Fallback to secure vault if still not found
    if not api_key:
        try:
            from secapi.secure import load_key
            if provider == "openai":
                api_key = load_key("openai_api_key")
            elif provider == "azure":
                api_key = load_key("azure_api_key")
            elif provider == "gemini":
                api_key = load_key("gemini_api_key")
        except Exception:
            pass

    return {
        "provider": provider,
        "model": model,
        "endpoint": endpoint,
        "api_key": api_key
    }

def get_rotation_interval_days():
    """Retrieve key expiration interval in days from configuration."""
    config = load_config()
    security = config.get("security", {})
    return security.get("rotate_interval_days", 30)

