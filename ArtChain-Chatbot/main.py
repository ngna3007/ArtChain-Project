from atoma_sdk import AtomaSDK
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
import re
import json
import os
from io import BytesIO
from PIL import Image
from fastapi import Request
from typing import Optional, Dict, Any

# Initialize Stable Diffusion Client
from sd_client import StableDiffusionClient
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    message: str

class SD_Agent:
    def __init__(self, bearer_auth: str):
        self.sdk = AtomaSDK(bearer_auth=bearer_auth)
        self.history = []
        self.current_prompt = None
        self.current_config = self.load_session()

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
    
    async def ask_llm(self, prompt: str) -> str:
        """Use Atoma SDK to get LLM response"""
        try:
            # Assuming self.sdk.chat.create is synchronous
            completion = self.sdk.chat.create(
                messages=[
                    {"role": "developer", "content": "You are a Stable Diffusion assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="meta-llama/Llama-3.3-70B-Instruct"
            )
            # Extract the response content
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in ask_llm: {e}")
            return "Sorry, I encountered an error while processing your request."
    
    async def handle_message(self, message: Dict[str, str]) -> str:
        user_input = message["content"].strip().lower()

        # Check for greetings or general inquiries
        if re.search(r"\b(hi|hello|hey|what can you do|how can you help)\b", user_input):
            return await self.describe_capabilities()

        if re.search(r"\b(current|show|display|what are my)\b.*\b(settings|configuration|parameters)\b", user_input):
            return await self.list_available_settings()

        intent_prompt = f"""
        Determine the intent of the user's input below.

        User Input: "{user_input}"

        Choose one of the following categories:
        - "explain" → If the user asks about a setting
        - "settings_change" → If the user wants to change a setting
        - "generate" → If the user explicitly asks to generate an image
        - "modify" → If the user wants to modify a previous image
        - "idle" → If the user input does not request any of the above

        Respond with just the category.
        """
        intent = (await self.ask_llm(intent_prompt)).lower()

        if intent == "explain":
            return await self.explain_setting(user_input)
        elif intent == "settings_change":
            return await self.change_setting(user_input)
        elif intent == "generate":
            return await self.generate_image(user_input)
        elif intent == "modify":
            return await self.modify_prompt(user_input)
        elif intent == "idle":
            return "How can I assist you today?"
        else:
            return "I'm not sure what you mean. Try asking about settings, generating an image, or modifying one."

    async def describe_capabilities(self) -> str:
        capabilities = """
        Hi! I'm your Stable Diffusion assistant. Here's what I can do:
        
        1. **Generate Images**: I can create images based on your prompts. Just ask me to generate something, like "Generate an image of a futuristic city."
        
        2. **Modify Images**: I can tweak previous images based on your feedback. For example, "Make the previous image more vibrant."
        
        3. **Change Settings**: I can adjust Stable Diffusion settings like CFG scale, steps, width, height, sampler, and seed. For example, "Set CFG scale to 10."
        
        4. **Explain Settings**: I can explain what each setting does. For example, "What does CFG scale do?"
        
        5. **Show Current Settings**: I can display the current configuration. Just ask, "What are my current settings?"
        
        """
        return await self.ask_llm(f"Format these settings in a clear way:\n{capabilities}")

    async def list_available_settings(self) -> str:
        settings_summary = f"""
        Current Stable Diffusion settings:

        - CFG Scale: {self.current_config.get("cfg_scale", default_config["cfg_scale"])}
        - Steps: {self.current_config.get("steps", default_config["steps"])}
        - Width: {self.current_config.get("width", default_config["width"])}
        - Height: {self.current_config.get("height", default_config["height"])}
        - Sampler: {self.current_config.get("sampler", default_config["sampler"])}
        - Seed: {self.current_config.get("seed", 'Random')}
        """

        return await self.ask_llm(f"Format these settings in a clear way:\n{settings_summary}")

    async def explain_setting(self, user_input: str) -> str:
        return await self.ask_llm(f"Explain this Stable Diffusion setting: {user_input}")

    async def change_setting(self, user_input: str) -> str:
        setting_response = await self.ask_llm(
            f'Extract the setting and new value from: "{user_input}"\nRespond in format: "setting=value"'
        )

        if "=" in setting_response:
            key, value = setting_response.split("=")
            key = key.strip().lower()
            value = value.strip()

            setting_aliases = {
                "guidance scale": "cfg_scale",
                "cfg scale": "cfg_scale",
                "sampling method": "sampler",
                "sampling steps": "steps"
            }
            
            key = setting_aliases.get(key, key)

            if key in self.current_config:
                try:
                    if key in ["width", "height", "steps"]:
                        value = int(value)
                    elif key == "cfg_scale":
                        value = float(value)
                    
                    self.current_config[key] = value
                    self.save_session()
                    return f"Updated {key} to {value}."
                except ValueError:
                    return f"Invalid value for {key}. Must be a number."
            return "Invalid setting name."
        return "Could not understand the setting change request."

# API routes
@app.post("/chat/")
async def chat(input_data: UserInput):
    agent = SD_Agent(os.getenv("ATOMASDK_BEARER_AUTH", ""))
    response = await agent.handle_message({"content": input_data.message})
    return {"response": response}

@app.get("/chat/")
async def chat_get(request: Request):
    agent = SD_Agent(os.getenv("ATOMASDK_BEARER_AUTH", ""))
    prompt = request.query_params.get("prompt", "")
    response = await agent.handle_message({"content": prompt})
    
    if response.startswith("Image saved as"):
        filename = response.split("Image saved as ")[1].strip()
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Image file not found.")
        
        with open(filename, "rb") as image_file:
            image_data = image_file.read()
        return Response(content=image_data, media_type="image/png")
    
    return {"response": response}