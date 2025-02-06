import requests

class StableDiffusionClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url

    def generate_image(self, prompt, cfg_scale=8.5, steps=50, width=512, height=512, sampler="Euler a", seed=None):
        params = {
            "prompt": prompt,
            "cfg_scale": cfg_scale,
            "steps": steps,
            "width": width,
            "height": height,
            "sampler": sampler,
            "seed": seed
        }
        response = requests.get(f"{self.api_url}/", params=params)
        if response.status_code == 200:
            with open("output.png", "wb") as f:
                f.write(response.content)
            return "Image saved as output.png"
        return f"Error: {response.status_code}, {response.text}"
