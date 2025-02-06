import autogen
import re
from sd_client import StableDiffusionClient

# Initialize Stable Diffusion Client
sd_client = StableDiffusionClient()

# Default Configuration
default_config = {
    "cfg_scale": 8.5,
    "steps": 50,
    "width": 512,
    "height": 512,
    "sampler": "Euler a",
    "seed": None
}

# List of Available Sampling Methods
available_samplers = [
    "Euler a", "Euler", "LMS", "Heun", "DPM2", "DPM2 a", 
    "DPM++ 2S a", "DPM++ 2M", "DPM++ SDE", "DPM++ 2M SDE",
    "DPM fast", "DPM adaptive", "LMS Karras", "DPM2 Karras",
    "DPM2 a Karras", "DPM++ 2S a Karras", "DPM++ 2M Karras",
    "DPM++ SDE Karras", "DPM++ 2M SDE Karras"
]

# AI Agent Definition
class SD_Agent(autogen.AssistantAgent):
    def __init__(self, name="StableDiffusionAgent"):
        super().__init__(name=name, llm_config={"model": "llama-3.5", "temperature": 0.7})
        self.prompt = None  # The prompt is now dynamically set based on user input.

    def extract_prompt_and_config(self, text):
        """Extracts the Stable Diffusion prompt and configuration values from the user's input."""
        config_pattern = r"(\b(cfg_scale|steps|width|height|sampler|seed)\s*:\s*[\w.]+)"
        configs = re.findall(config_pattern, text)

        # Extract settings from input
        for full_match, key in configs:
            value = full_match.split(":")[1].strip()
            if key in ["steps", "width", "height", "seed"]:
                default_config[key] = int(value)
            elif key in ["cfg_scale"]:
                default_config[key] = float(value)
            elif key == "sampler" and value in available_samplers:
                default_config[key] = value
            else:
                return f"Invalid value for {key}."

            # Remove config from input text to leave only the prompt
            text = text.replace(full_match, "").strip()

        return text  # This is the cleaned prompt

    def handle_message(self, message):
        text = message["content"].lower()  # Normalize the text to lowercase

        # Greeting & Sample Prompt
        if "hello" in text or "hi" in text:
            return "Hello! Enter a prompt to generate an image. You can also modify settings like cfg_scale, steps, width, height, sampler, or seed."

        # List available configurations if user only types "change" or "set"
        if text.strip() in ["change", "set"]:
            return "Available settings: cfg_scale, steps, width, height, sampler, seed."

        # Handle changing the sampler
        if "change sampler" in text or "set sampler" in text:
            # Check if the input matches any available sampler
            for available_sampler in available_samplers:
                if available_sampler.lower() in text:
                    default_config["sampler"] = available_sampler
                    return f"Updated sampler to {available_sampler}."

            return f"Available sampling methods: {', '.join(available_samplers)}. Please choose one."

        # Modify Configuration Only
        if "change" in text or "set" in text:
            for key in default_config.keys():
                if key in text:
                    try:
                        value = text.split(key)[1].strip()
                        if key in ["steps", "width", "height", "seed"]:
                            default_config[key] = int(value)
                        elif key in ["cfg_scale"]:
                            default_config[key] = float(value)
                        else:
                            return f"Invalid value for {key}."
                            
                        return f"Updated {key} to {value}."
                    except ValueError:
                        return f"Invalid value for {key}. Please specify a number."

        # Generate Image with Extracted Prompt and Config
        if "generate" in text or "create" in text:
            self.prompt = self.extract_prompt_and_config(text)
            if not self.prompt:
                return "Please provide a prompt to generate an image."

            return sd_client.generate_image(prompt=self.prompt, **default_config)

        return "I didn't understand that. You can ask me to 'Generate' or 'Create' an image and 'Change' or 'Set' settings!"



# Run the AI Agent
if __name__ == "__main__":
    agent = SD_Agent()
    print("AI Agent is running. Type 'hello' to start.")
    
    while True:
        user_input = input("You: ")
        response = agent.handle_message({"content": user_input})
        print("Agent:", response)
