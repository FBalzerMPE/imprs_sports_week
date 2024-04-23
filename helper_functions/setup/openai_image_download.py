"""Small library to generate and download images using openai's dall-e-3 API.
None of this should be exported to not create openai dependencies.
"""

import base64
import io
import os
import random
import time
from pathlib import Path
from typing import Literal

import openai
from PIL import Image

from ..constants import DATAPATH


# define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.RateLimitError,),
):
    """Retry a function with exponential backoff.
    Adopted from https://cookbook.openai.com/examples/how_to_handle_rate_limits
    """

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


@retry_with_exponential_backoff
def generate_image_with_dall_e(
    prompt: str,
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
    dall_e_version: Literal[2, 3] = 3,
) -> Image.Image:
    """Generate and decode an image."""
    api_key = os.environ.get(
        "OPENAI_API_KEY", DATAPATH.joinpath("hidden/gpt_ai_key.txt").read_text()
    )
    client = openai.OpenAI(api_key=api_key)
    model = f"dall-e-{dall_e_version}"
    response = client.images.generate(
        prompt=prompt,
        model=model,
        size=size,
        response_format="b64_json",
        style="vivid",
    )
    return Image.open(
        io.BytesIO(base64.decodebytes(bytes(response.data[0].b64_json, "utf-8")))  # type: ignore
    )


def generate_all_images(animal_names: list[str], verbose=True, redo_anyways=False):
    """Generate an image for each animal in animal names."""
    prompt_base = "Create an avatar showing a {} with a white background."
    for animal_name in animal_names:
        prompt = prompt_base.format(animal_name)
        img_name = animal_name.replace(" ", "_").lower() + ".png"
        full_path = DATAPATH.joinpath(f"assets/animal_pics/full_size/{img_name}")
        if full_path.exists():
            if not redo_anyways:
                continue
            for i in range(10):
                full_path = Path(str(full_path).replace(".png", f"{i}.png"))
                if not full_path.exists():
                    if verbose:
                        print(
                            f"Initial path for {animal_name} already existed, writing to {full_path} instead."
                        )
                    break
        if verbose:
            print(prompt)
        img = generate_image_with_dall_e(prompt)
        img.save(full_path)


def save_resized_animal_images(new_size: int = 150):
    """Save all images in the full size directory with a new pixel size in
    the small size directory.
    150 seems to be a good size for all avatars to load if necessary.
    """
    assert 50 <= new_size < 1024, f"Please provide sensible new size, not {new_size}"
    base_dir = DATAPATH.joinpath("assets/animal_pics/full_size")
    for full_path in base_dir.iterdir():
        if full_path.is_dir():
            continue
        new_path = (
            DATAPATH.parent.joinpath("static/animal_pics/small_size/") / full_path.name
        )
        with open(full_path, "rb") as f:
            img = Image.open(f)
            img = img.resize((new_size, new_size))
            img.save(new_path)
