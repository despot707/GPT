import os
from openai import AsyncOpenAI
from g4f.client import AsyncClient
from g4f.Provider import BingCreateImages, Gemini

# Initialize the official OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))


def get_image_provider(name: str):
    return {
        "Gemini": Gemini,
        "BingCreateImages": BingCreateImages,
    }.get(name, BingCreateImages)


async def draw(model: str, prompt: str, size: str = "1024x1024", n: int = 1) -> str:
    """
    Generate an image URL using either:
      • OpenAI Images API (models: dall-e-3, dall-e-2, gpt-image-1) if OPENAI_ENABLED=True
      • Free G4F providers (Gemini, BingCreateImages) otherwise
    """
    use_official = os.getenv("OPENAI_ENABLED", "False").lower() == "true"
    if use_official and model in ("dall-e-3", "dall-e-2", "gpt-image-1"):
        resp = await openai_client.images.generate(
            model=model,
            prompt=prompt,
            n=n,
            size=size,
        )
        return resp.data[0].url

    # fallback free provider
    provider = get_image_provider(model)
    client = AsyncClient(image_provider=provider)
    result = await client.images.generate(prompt=prompt)
    # g4f may return either a string or an object with .data[0].url
    if hasattr(result, "data"):
        return result.data[0].url
    return result
