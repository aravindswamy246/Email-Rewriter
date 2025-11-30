"""
OpenAI Model Pricing Configuration

This module maintains up-to-date pricing information for OpenAI models.
Prices are per 1,000 tokens (divide by 1000 from OpenAI's per-million pricing).

Last Updated: November 2025
Source: https://openai.com/api/pricing/
"""

# Pricing in USD per 1,000 tokens
PRICING_CONFIG = {
    'gpt-4o': {
        'input': 0.005,   # $5 per 1M tokens = $0.005 per 1K
        'output': 0.015,  # $15 per 1M tokens = $0.015 per 1K
        'description': 'GPT-4o - Fastest and most cost-effective GPT-4 model'
    },
    'gpt-4o-mini': {
        'input': 0.00015,  # $0.15 per 1M tokens
        'output': 0.0006,  # $0.60 per 1M tokens
        'description': 'GPT-4o Mini - Most affordable model'
    },
    'gpt-4-turbo': {
        'input': 0.01,    # $10 per 1M tokens
        'output': 0.03,   # $30 per 1M tokens
        'description': 'GPT-4 Turbo - High performance at lower cost'
    },
    'gpt-4': {
        'input': 0.03,    # $30 per 1M tokens
        'output': 0.06,   # $60 per 1M tokens
        'description': 'GPT-4 - Most capable model'
    },
    'gpt-3.5-turbo': {
        'input': 0.0015,  # $1.50 per 1M tokens
        'output': 0.002,  # $2.00 per 1M tokens
        'description': 'GPT-3.5 Turbo - Fast and affordable'
    }
}


def get_model_pricing(model_name: str) -> dict:
    """
    Get pricing for a specific model.

    Args:
        model_name: Name of the OpenAI model

    Returns:
        Dict with 'input' and 'output' pricing per 1K tokens
        Falls back to GPT-4o pricing if model not found
    """
    # Handle model name variations
    model_key = model_name.lower().strip()

    # Direct match
    if model_key in PRICING_CONFIG:
        return {
            'input': PRICING_CONFIG[model_key]['input'],
            'output': PRICING_CONFIG[model_key]['output']
        }

    # Partial match for versioned models (e.g., gpt-4-0613)
    for key in PRICING_CONFIG.keys():
        if model_key.startswith(key):
            return {
                'input': PRICING_CONFIG[key]['input'],
                'output': PRICING_CONFIG[key]['output']
            }

    # Default fallback to GPT-4o (most common/cost-effective)
    return {
        'input': PRICING_CONFIG['gpt-4o']['input'],
        'output': PRICING_CONFIG['gpt-4o']['output']
    }


def get_all_models() -> dict:
    """
    Get all available models with their pricing.

    Returns:
        Complete pricing configuration dictionary
    """
    return PRICING_CONFIG


def calculate_cost(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """
    Calculate total cost for a given token usage.

    Args:
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens used
        model_name: Name of the OpenAI model

    Returns:
        Total cost in USD
    """
    pricing = get_model_pricing(model_name)
    input_cost = (input_tokens / 1000) * pricing['input']
    output_cost = (output_tokens / 1000) * pricing['output']
    return round(input_cost + output_cost, 6)


def get_model_description(model_name: str) -> str:
    """
    Get description for a specific model.

    Args:
        model_name: Name of the OpenAI model

    Returns:
        Model description string
    """
    model_key = model_name.lower().strip()

    for key, config in PRICING_CONFIG.items():
        if model_key.startswith(key):
            return config.get('description', 'OpenAI model')

    return 'OpenAI model'
