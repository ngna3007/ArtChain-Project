# ArtChain Architecture

## 1. Executive Summary

This project is an AI-powered NFT art platform that allows users to generate images based on an artist’s unique style using Stable Diffusion integrated with LoRA models. With the help of an AI agent, users can modify Stable Diffusion settings, request explanations, and refine their prompts for better results. Once satisfied, they can mint their AI-generated artwork as NFTs on the SUI blockchain. 

The platform ensures a seamless and intuitive creative process while leveraging smart contracts to manage transactions transparently. This includes handling minting fees, fund distributions, and—most importantly—automated royalty payments to artists who contribute their datasets, ensuring they are fairly compensated for their work.

## 2. Core Architecture Components

### 2.1. Frontend Architecture

#### 2.1.1. Tech Stack
- React.js for web applications and React Native for mobile platforms (optional).
- Web3.js and the SUI SDK to facilitate blockchain interactions.

#### 2.1.2. Features
- **User Authentication**: Web3-based wallet connections like Metamask, SUI Wallet, or custom wallets.
- **Gallery Interface**: Allows browsing art styles, filtering by artist names, genres, etc.
- **Minting Function**: Users can mint the generated image as an NFT after selecting an art style and configuring AI model parameters.
- **Transaction Monitoring**: Users can view transaction statuses and royalties received by artists.
- **On-Chain Verification**: Blockchain-based proof of ownership ensures authenticity and prevents unauthorized alterations to minted NFTs.
- **Real-Time Notifications**: Users receive updates on minting progress, transaction confirmations, and AI generation statuses.

### 2.2. Backend Infrastructure

#### 2.2.1. Tech Stack
- FastAPI for handling API requests efficiently.
- Python as the primary backend language for AI processing and API development.
- AutoGen to manage AI agent workflows, including self-reflection and iterative improvements.
- LLaMA 3.5 as the core large language model (LLM) for text-based interactions.
- Stable Diffusion for AI-generated image creation with configurable parameters.
- LoRA (Low-Rank Adaptation) to fine-tune Stable Diffusion models for customization.
- Sui Blockchain for NFT-related functionalities and Web3 interactions.
- Pinata - IPFS for decentralized storage of artwork.

#### 2.2.2. Features
- **Transaction Management**: Handle minting requests, royalties for artists, and smart contract calls.
- **Artwork Storage**: The backend triggers a minting transaction on the SUI blockchain, creating an NFT with metadata pointing to the generated image on IPFS.
- **Royalty Distribution**: Ensures that royalties are correctly distributed to the artist whenever their art style is used for minting.
- **AI-Powered Image Generation**: Users can generate art using Stable Diffusion with customizable parameters, including resolution, sampling method, and CFG scale.
- **Iterative Refinement**: The AI agent can add adjustments or improvements to generated images based on user feedback, adjusting prompts while preserving core concepts.
- **Configurable AI Settings**: Users can modify Stable Diffusion parameters such as sampling steps, width, height, and seed for precise image control.
- **AutoGen AI Agent**: An intelligent assistant guides users through AI-generated art creation, provides explanations of settings, and helps refine outputs.

### 2.3. Blockchain Layer

#### 2.3.1. Tech Stack
- **SUI blockchain**: Highly scalable and low latency.
- **The MOVE language**: Object-oriented programming language optimized for blockchain transactions.

#### 2.3.2. Features
- **NFT Smart Contract**: Manages minting, metadata (artist, style, etc.), and linking the NFT to the AI-generated image.
- **Payment Smart Contract**: Automates minting fee payments and royalty distributions when an NFT is minted.
- **Artist Registration Smart Contract** *(Planned)*: Enables artists to register their styles and track performance.

### 2.4. AI Diffusion Model

#### 2.4.1. Tech Stack
- **Stable Diffusion**
- **Hugging Face API**
- **LoRA Models**

#### 2.4.2. Features
- **Training Stage**: Fine-tunes models with specific styles of registered artists using LoRA.
- **Generation Stage**:
  - **Input**: User prompts for image generation.
  - **Output**: AI-generated images that users can mint as NFTs with embedded metadata on the SUI blockchain.

## 3. Interactions

### 3.1. Workflow Overview
![image](https://github.com/user-attachments/assets/8ebd8d45-967b-4faa-b8f0-cb840274fe4a)
|:---------------------------------:|
| *Figure 1: System Workflow* |

The workflow diagram outlines the AI-powered NFT image generator on the SUI blockchain, detailing the user journey from authentication to NFT creation and transactions.

Users begin by verifying their Web3 wallet or creating a new one. After logging in, they explore the Art Gallery and select between Premium Mode and Standard Mode for AI-generated artwork. In Premium Mode, users can refine prompts and adjust Stable Diffusion settings, while Standard Mode directly generates images with a LoRA-enhanced model.

Once artwork is created, users can mint it as an NFT. Premium users mint without extra charges, while others pay a generation fee. Approved NFTs are stored on Pinata (IPFS), with metadata passed to the smart contract for minting on SUI blockchain. The NFT is then sent to the user’s wallet.

Smart contracts handle transactions, including royalty distribution and payments. After minting, users can keep or trade their NFT, ensuring ongoing engagement.

![image](https://github.com/user-attachments/assets/c082ac8a-3158-41ea-8e0b-21e51bd85863)
|:---------------------------------:|
| *Figure 2: AI Agent System* |

This diagram illustrates an AI agent system that processes user input to generate images using Stable Diffusion. The workflow starts with the FastAPI Server, which receives user input and passes it to Intent Classification. Based on intent, the Action Type decision node directs the request:
-	Generate Image sends the request to Stable Diffusion, which uses a LoRA Model to produce the image.
- Explain Settings provides details about Stable Diffusion parameters.
-	Update Settings modifies stored user preferences.
-	Modify Previous Image refines existing outputs using LLaMA 3.5.
-	Handle Small Talk/Error responds to casual input.
  
The Response Handler delivers results back to the user, ensuring smooth interaction and iterative image refinement.


### 3.2. System Interaction

1. **Frontend (UI Layer)** → Users interact with the marketplace and send requests to:
   - Backend (API Server)
   - SUI Blockchain (for wallet interactions and minting)
2. **Backend API** → Handles requests:
   - Sends input to AI Diffusion Model & AutoGen AI agent.
   - Initiates minting requests on the SUI Blockchain.
   - Stores images on Pinata (IPFS).
3. **AI Diffusion Model** → Generates images based on user input.
4. **AutoGen AI Agent** → Assists with iterative refinements, explanations, and settings adjustments.
5. **SUI Blockchain** → Executes smart contracts for NFT minting and payment distribution.

## 4. Technical Considerations

### 4.1. Scalability & Performance
- Uses cloud computing (AWS, Google Cloud) with high-performance GPUs (AWS EC2 P4d, Google A100).
- Implements asynchronous processing with Redis-based job queues (Celery or RQ) to handle AI image generation efficiently.
- Plans to introduce Kubernetes for dynamic scaling and Cloudflare CDN for optimized content delivery.

### 4.2. Security
- **Wallet Authentication & Encryption**: Secure Web3 interactions with Metamask and SUI Wallet.
- **Smart Contract Security**: Best practices for preventing vulnerabilities (e.g., reentrancy attacks, access control mechanisms).
- **Data Integrity & IP Protection**: Metadata stored on IPFS ensures artwork authenticity.
- **API Security & DDoS Protection**: Implements rate limiting and Web Application Firewalls (WAF).

### 4.3. System Optimization & Feature Improvements
- **AI Model Optimization**: Fine-tuned LoRA models and model distillation for faster image generation.
- **AI Agent Enhancements**: Automates improved prompt suggestions and minting processes.
- **Gas Fee Optimization**: Smart contract optimizations to reduce transaction costs.
- **Parallel Processing & GPU Utilization**: Batch inference and mixed precision training for efficient AI task execution.
- **Marketplace Enhancements**: Optimized NFT listings, search functionality, and faster transactions.

---

This README provides a comprehensive overview of ArtChain's technical architecture, ensuring clarity and ease of implementation. 🚀
