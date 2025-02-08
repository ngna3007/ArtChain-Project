import autogen
import re
import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from sd_client import StableDiffusionClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import base64
from fastapi.responses import JSONResponse, Response
from io import BytesIO
from PIL import Image
from fastapi import Request




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

SESSION_FILE = "session_data.json"

# FastAPI App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific domains for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    message: str

class SD_Agent(autogen.AssistantAgent):
    def __init__(self, api_key):
        super().__init__(name="StableDiffusionAgent")  # Provide a name
        self.client = Groq(api_key=api_key)
        self.history = []  # Initialize history
        self.current_prompt = None  # Track the latest prompt
        self.current_config = self.load_session()  # Load saved settings

    
    def save_session(self):
        """Save current settings to a file."""
        session_data = {"config": self.current_config, "history": self.history}
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f)
    
    def load_session(self):
        """Load settings from a file if available."""
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                session_data = json.load(f)
                self.history = session_data.get("history", [])
                return session_data.get("config", default_config.copy())
        return default_config.copy()
    
    def ask_llm(self, prompt):
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,  # Set to True if you want streaming responses
        )
        return completion.choices[0].message.content
    
    def handle_message(self, message):
        user_input = message["content"].strip().lower()

        if re.search(r"\b(current|show|display|what are my)\b.*\b(settings|configuration|parameters)\b", user_input):
            return self.list_available_settings()

        intent_prompt = f"""
        Determine the intent of the user's input below.

        User Input: "{user_input}"

        Choose one of the following categories:
        - "explain" → If the user asks about a setting (e.g., "What is CFG scale?")
        - "settings_change" → If the user wants to change a setting (e.g., "Set steps to 100")
        - "generate" → If the user explicitly asks to generate an image (e.g., "Generate an image of a sunset")
        - "modify" → If the user wants to modify a previous image (e.g., "Make it less detailed")
        - "idle" → If the user input does not request any of the above (e.g., greetings, small talk)

        Respond with just the category.
        """
        intent = self.ask_llm(intent_prompt).lower()

        if intent == "explain":
            return self.explain_setting(user_input)
        elif intent == "settings_change":
            return self.change_setting(user_input)
        elif intent == "generate":
            return self.generate_image(user_input)
        elif intent == "modify":
            return self.modify_prompt(user_input)
        elif intent == "idle":
            return "How can I assist you today?"
        else:
            return "I'm not sure what you mean. Try asking about settings, generating an image, or modifying one."


    def list_available_settings(self):
        settings_summary = f"""
        Here are the current Stable Diffusion settings:

        - **CFG Scale** (`cfg_scale`): {self.current_config.get("cfg_scale", default_config["cfg_scale"])}  
        Controls how closely the image follows the prompt (higher values = more adherence).  

        - **Steps** (`steps`): {self.current_config.get("steps", default_config["steps"])}  
        Determines the number of refinement steps (higher = more detail).  

        - **Width** (`width`): {self.current_config.get("width", default_config["width"])}  
        Width of the generated image in pixels.  

        - **Height** (`height`): {self.current_config.get("height", default_config["height"])}  
        Height of the generated image in pixels.  

        - **Sampler** (`sampler`): {self.current_config.get("sampler", default_config["sampler"])}  
        The method used to generate the image.  

        - **Seed** (`seed`): {self.current_config.get("seed", 'Random')}  
        A fixed number for reproducibility.  
        """

        prompt = f"""
        The user wants to know the current Stable Diffusion settings. 
        Here is the extracted information:
        
        {settings_summary}
        
        Format the response in **bullet points**, highlighting each **parameter name in bold**.
        Ensure it's clear and structured, making it easy to read.
        """

        return self.ask_llm(prompt)


    def explain_setting(self, user_input):
        explain_prompt = f"""
        Explain the Stable Diffusion setting:
        
        {user_input}
        
        Keep it simple.
        """
        return self.ask_llm(explain_prompt)
    
    def change_setting(self, user_input):
        change_prompt = f"""
        Extract the setting and new value from the following user input:
        "{user_input}"
        Respond in format: "setting=value"
        """
        setting_response = self.ask_llm(change_prompt)

        if "=" in setting_response:
            key, value = setting_response.split("=")
            key = key.strip().lower()
            value = value.strip()

            # Map alternative names to actual parameter names
            setting_aliases = {
                "guidance scale": "cfg_scale",
                "cfg scale": "cfg_scale",
                "guild scale": "cfg_scale",
                "sampling method": "sampler",
                "sampling steps": "steps"
            }
            
            key = setting_aliases.get(key, key)  # Convert alias to correct key

            if key in self.current_config:
                if key in ["width", "height", "steps"]:
                    try:
                        value = int(value)
                    except ValueError:
                        return "Invalid value. Must be a number."
                elif key == "cfg_scale":
                    try:
                        value = float(value)
                    except ValueError:
                        return "Invalid value. Must be a number."

                self.current_config[key] = value
                self.save_session()
                return f"Updated {key} to {value}."
            else:
                return "Invalid setting name."
        else:
            return "Could not understand the setting change request."


    def process_user_input(self, user_input):
        """Extracts the main prompt and updates settings if specified."""
        
        setting_pattern = r"(cfg_scale|steps|width|height|sampler|seed)\s*of\s*(\d+|\w+)"
        matches = re.findall(setting_pattern, user_input, re.IGNORECASE)
        
        settings = {}
        for key, value in matches:
            key = key.lower()
            if key in ["width", "height", "steps", "seed"]:
                value = int(value)  # Convert to integer
            elif key == "cfg_scale":
                value = float(value)  # Convert to float
            settings[key] = value

        # Remove extracted settings from the prompt
        cleaned_prompt = re.sub(setting_pattern, "", user_input, flags=re.IGNORECASE).strip()

        # Remove extra words like "for me" if they don't impact the prompt meaning
        cleaned_prompt = re.sub(r"\b(for me|please)\b", "", cleaned_prompt, flags=re.IGNORECASE).strip()

        return cleaned_prompt, settings

    def generate_image(self, user_input):
        prompt, extracted_settings = self.process_user_input(user_input)
        
        # Update settings if any were extracted
        if extracted_settings:
            self.current_config.update(extracted_settings)
            self.save_session()

        # Generate image with cleaned-up prompt and updated settings
        output_message = sd_client.generate_image(prompt=prompt, **self.current_config)
        
        # Store the latest prompt
        self.current_prompt = prompt
        
        # Update history
        self.history.append({"prompt": prompt, "config": self.current_config.copy(), "output": output_message})
        self.save_session()
        
        # Return the output message (e.g., "Image saved as output.png")
        return output_message


    
    def modify_prompt(self, user_input):
        if not self.history:
            return "You haven't generated an image yet."

        last_entry = self.history[-1]  # Retrieve the last generated image
        original_prompt = last_entry["prompt"]

        # Ask LLM to refine the prompt intelligently
        refine_prompt = f"""
        Modify the following Stable Diffusion prompt based on the user's input:

        Original Prompt: "{original_prompt}"
        User Modification: "{user_input}"

        Generate a new prompt that maintains the core concept but integrates the requested change naturally.
        """

        new_prompt = self.ask_llm(refine_prompt).strip()

        # Generate the image with the refined prompt
        output = sd_client.generate_image(prompt=new_prompt, **last_entry["config"])

        # Store the modified prompt as the latest
        self.current_prompt = new_prompt

        # Update history
        self.history.append({"prompt": new_prompt, "config": last_entry["config"], "output": output})
        self.save_session()

        return f"Generated modified image:\n{output}"


api_key = "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"  # Replace with your actual API key
agent = SD_Agent(api_key)
    
@app.api_route("/chat/", methods=["GET", "POST"])
async def chat(request: Request, input_data: UserInput = None):
    # Extract query parameters from the GET request
    query_params = request.query_params

    # Update settings if query parameters are provided
    if "cfg_scale" in query_params:
        agent.current_config["cfg_scale"] = float(query_params["cfg_scale"])
    if "steps" in query_params:
        agent.current_config["steps"] = int(query_params["steps"])
    if "width" in query_params:
        agent.current_config["width"] = int(query_params["width"])
    if "height" in query_params:
        agent.current_config["height"] = int(query_params["height"])
    if "sampler" in query_params:
        agent.current_config["sampler"] = query_params["sampler"]

    # If it's a POST request, use the input_data
    if input_data:
        response = agent.handle_message({"content": input_data.message})
    else:
        # If it's a GET request, use the prompt from the query parameters
        prompt = query_params.get("prompt", "")
        response = agent.handle_message({"content": prompt})

    # Check if the response indicates an image was saved
    if response.startswith("Image saved as"):
        # Extract the filename from the response
        filename = response.split("Image saved as ")[1].strip()
        
        # Check if the file exists
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Image file not found.")
        
        # Read the image file as binary data
        with open(filename, "rb") as image_file:
            image_data = image_file.read()
        
        # Return the image as a binary response with the appropriate media type
        return Response(content=image_data, media_type="image/png")
    
    # Otherwise, return the text response
    return {"response": response}