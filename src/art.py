import os
from openai import AsyncOpenAI
from g4f.client import AsyncClient
from g4f.Provider import BingCreateImages, Gemini

# initialize the official OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))

async def draw(model: str, prompt: str) -> str:
    """
    Generate an image according to `model`:
      • "dall-e-3", "dall-e-2", "gpt-image-1" → official OpenAI Images API
      • "gemini"                         → free Gemini-Pro via g4f
      • "bing"                          → free Bing Images via g4f
    Returns the image URL.
    """
    # OFFICIAL OPENAI BRANCH
    if os.getenv("OPENAI_ENABLED", "False") == "True" and model in ("dall-e-3", "dall-e-2", "gpt-image-1"):
        resp = await openai_client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",  # or "1792x1024"
            n=1,
        )
        return resp.data[0].url

    # FREE G4F BRANCH
    # pick the provider class
    provider_cls = Gemini if model == "gemini" else BingCreateImages
    g4f_client = AsyncClient(image_provider=provider_cls)
    url = await g4f_client.images.generate(prompt=prompt)
    return url
