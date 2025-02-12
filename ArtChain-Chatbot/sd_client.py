import requests
import aiohttp
import asyncio

class StableDiffusionClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url

    async def generate_image(self, prompt, cfg_scale=8.5, steps=50, width=512, height=512, sampler="Euler a", seed=None, output_file="output.png"):
        params = {
            "prompt": prompt,
            "cfg_scale": cfg_scale,
            "steps": steps,
            "width": width,
            "height": height,
            "sampler": sampler,
            "seed": seed
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/", params=params) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        with open(output_file, "wb") as f:
                            f.write(image_data)
                        return f"Image saved as {output_file}"
                    else:
                        return f"Error: {response.status}, {await response.text()}"
        except Exception as e:
            return f"Failed to generate image: {str(e)}"