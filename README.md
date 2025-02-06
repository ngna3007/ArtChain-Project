# 🚀 ArtChain-Chatbot Setup Guide

Welcome to the ArtChain-Chatbot setup guide! This document will help you install and configure the necessary dependencies to get the project up and running.

---

## 📋 Prerequisites

Before you begin, ensure you have the following:

- **Ubuntu** (or a similar Linux distribution)
- **Administrative privileges** (to install packages)

---

## 🛠 Installation Steps

### Step 1: Install Python 3.10.6

1. Update your package list and install required dependencies:

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install software-properties-common -y

2. Add the deadsnakes PPA (for updated Python versions):

   ```bash
   sudo add-apt-repository ppa:deadsnakes/ppa -y
   sudo apt update

3. Install Python 3.10.6:

   ```bash
   sudo apt install python3.10 python3.10-venv python3.10-dev python3.10-distutils -y

4. Verify the installation:
   ```bash
   python3.10 --version

### Step 2: Install pip for Python 3.10

1. Install pip for Python 3.10:
   
   ```bash
   curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

3. Verify pip installation:
   
   ```bash
    python3.10 -m pip --version
   
### Step 3: Set Up a Virtual Environment

1. Navigate to your project directory:
   
    ```bash
    cd ~/ArtChain-Chatbot

3. Create a virtual environment:
   
    ```bash
    python3.10 -m venv venv
  
Activate the virtual environment:

    source venv/bin/activate
    
Tip: You should see (venv) at the beginning of your terminal prompt, indicating the virtual environment is active.

Step 4: Install Dependencies
1. Install the required packages from requirements.txt:

    ```bash
    pip install -r requirements.txt

If you're using an AMD GPU, install the following additional package:
    
    pip install torch-directml
  
2.Install the peft package:

    pip install peft


## 🚀 Running the Application
# Running the Stable Diffusion API

To run the Stable Diffusion API, use the following command:

    uvicorn stable_diffusion_api:app --reload

# Running the AI Agent
To run the AI agent, use the following command:

    python main.py
    
🔑 OpenAI Token
For the OpenAI token, go to this site: https://platform.openai.com/.
And then type this cmd:

    export OPEN_API_KEY="your_api_key_here"

❓ Need Help?
If you encounter any issues during setup, feel free to open an issue on GitHub.
