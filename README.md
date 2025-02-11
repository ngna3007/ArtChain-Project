### Our web deployed on Vercel is frontend only. Due to the limit budget, we cannot deploy the AI API on render: https://art-chain-ai-delta.vercel.app/

Project from student team of Swinburne University from Vietnam:
- Nguyen Ngoc Anh
- Nguyen Thien Phuoc
- Le Hoang Long
- Huynh Hoang Minh

# ArtChain-Chatbot Setup Guide

Welcome to the ArtChain-Chatbot setup guide! This document will walk you through the installation and configuration of the necessary dependencies to get the project up and running.

## 📋 Prerequisites

Before you begin, ensure you have the following:

- **Ubuntu** (or a similar Linux distribution)
- **Administrative privileges** (to install packages)

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

### Step 3: Set Up a Virtual Environment

1. Navigate to your project directory:
   
   ```bash
   cd ~/ArtChain-Chatbot

2. Create a virtual environment:

   ```bash
   python3.10 -m venv venv

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   Tip: You should see (venv) at the beginning of your terminal prompt, indicating the virtual environment is active.
### Step 4 Install Dependencies
1. Install the required packages from requirements.txt:
   
   ```bash
    pip install -r requirements.txt
2. If you're using an AMD GPU, install the following additional package:

   ```bash
   pip install torch-directml

## Running the Application
1. To run the Stable Diffusion API, use the following command:

    ```bash
    uvicorn stable_diffusion_api:app --reload

2. To run the AutoGen AI Agent API, use the following command:

   ```bash
    uvicorn main:app --port 8001 --reload

# ArtChain-Website Setup Guide

```bash
    npm install
    npm install next
    npm run dev
