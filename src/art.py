import os
from openai import AsyncOpenAI
from g4f.client import AsyncClient as G4FClient
from g4f.Provider import BingCreateImages, Gemini, OpenaiChat

# initialize your OpenAI client once
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))


def get_image_provider(provider_name: str):
    """
    Map a string to a g4f image provider.
    Defaults to BingCreateImages if the name isn't recognized.
    """
    providers = {
        "Gemini": Gemini,
        "openai": OpenaiChat,         # g4f’s OpenAI wrapper
        "BingCreateImages": BingCreateImages,
    }
    return providers.get(provider_name, BingCreateImages)


async def draw(
    model: str,
    prompt: str,
    size: str = "1024x1024",
    n: int = 1
) -> list[str]:
    """
    Generate image(s) from a text prompt.

    If OPENAI_ENABLED="False", uses g4f for a single URL (ignores size/n).
    Otherwise calls the official OpenAI Images API.

    Returns a list of image URLs.
    """
    enabled = os.getenv("OPENAI_ENABLED", "True").lower() != "false"

    if not enabled:
        # g4f path (only supports one image at a time)
        provider = get_image_provider(model)
        client   = G4FClient(image_provider=provider)
        url      = await client.images.generate(prompt=prompt)
        return [url]

    # official OpenAI images endpoint
    resp = await openai_client.images.generate(
        model=model,   # e.g. "dall-e-2" or "dall-e-3"
        prompt=prompt,
        n=n,            # number of images
        size=size       # "256x256","512x512","1024x1024","1792x1024"
    )

    # resp.data is a list of objects with .url
    return [d.url for d in resp.data]
