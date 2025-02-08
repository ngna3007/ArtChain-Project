import React, { useState } from 'react';
import { Wand2, History, Save, Download, Share2, Sparkles, Palette, RefreshCw, Trash2, MessageSquare, Image } from 'lucide-react';
import axios from 'axios';
import { marked } from 'marked';

interface PromptHistory {
  id: string;
  prompt: string;
  timestamp: string;
  style: string;
  image?: string; // Add image URL or base64 data
}

export default function AIStudio() {
  const [prompt, setPrompt] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [simpleGeneratedImage, setSimpleGeneratedImage] = useState<string | null>(null);
  const [chatGeneratedImage, setChatGeneratedImage] = useState<string | null>(null);
  const [interfaceMode, setInterfaceMode] = useState<'simple' | 'chat'>('simple');
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([
    { role: 'assistant', content: 'Hello! I\'m your AI art assistant. I can help you generate images and adjust settings. What would you like to create today?' }
  ]);
  const [promptHistory, setPromptHistory] = useState<PromptHistory[]>([
    {
      id: '1',
      prompt: 'A cyberpunk city at night with neon signs and flying cars',
      timestamp: '2 minutes ago',
      style: 'Super Ani'
    },
    {
      id: '2',
      prompt: 'Abstract representation of human consciousness',
      timestamp: '15 minutes ago',
      style: 'Digital Surrealism'
    }
  ]);

  const unlockedStyles = [
    {
      id: '1',
      name: 'Super Ani',
      artist: 'Kim Jung Gi',
      thumbnail: '../../output.png' // Replace with the actual image URL
    },
    {
      id: '2',
      name: 'Digital Surrealism',
      artist: 'Emma Watson',
      thumbnail: 'https://images.unsplash.com/photo-1549490349-8643362247b5?auto=format&fit=crop&q=80'
    }
  ];

  const handleGenerate = async () => {
    if (!prompt || !selectedStyle) return;
    setIsGenerating(true);

    try {
      const response = await axios.get('http://127.0.0.1:8000/', {
        params: {
          prompt: prompt,
          style: selectedStyle
        },
        responseType: 'blob'
      });

      const imageUrl = URL.createObjectURL(response.data);
      setSimpleGeneratedImage(imageUrl); // Update to use simple mode state

      setPromptHistory(prev => [{
        id: Date.now().toString(),
        prompt,
        timestamp: 'Just now',
        style: selectedStyle,
        image: imageUrl
      }, ...prev]);
    } catch (error) {
      console.error('Error generating image:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClearHistory = () => {
    setPromptHistory([]);
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    // Add user message to chat
    setChatHistory(prev => [...prev, { role: 'user', content: prompt }]);
    const userPrompt = prompt;
    setPrompt('');
    setIsGenerating(true);

    try {
      const response = await axios.post('http://localhost:8001/chat/', {
        message: userPrompt
      }, {
        responseType: 'arraybuffer', // Handle both text and image responses
        headers: {
          'Accept': 'application/json, image/*' // Accept both JSON and image responses
        }
      });

      // Check if the response is an image (based on content-type header)
      const contentType = response.headers['content-type'];

      if (contentType.startsWith('image/')) {
        const blob = new Blob([response.data], { type: contentType });
        const imageUrl = URL.createObjectURL(blob);

        setChatGeneratedImage(imageUrl); // Update to use chat mode state

        setChatHistory(prev => [...prev, {
          role: 'assistant',
          content: 'I\'ve generated an image based on your request:'
        }]);

        setPromptHistory(prev => [{
          id: Date.now().toString(),
          prompt: userPrompt,
          timestamp: 'Just now',
          style: selectedStyle || 'Default',
          image: imageUrl
        }, ...prev]);

      } else {
        // Handle text response
        // Convert arraybuffer to text if it's a JSON response
        const textDecoder = new TextDecoder('utf-8');
        const responseData = JSON.parse(textDecoder.decode(response.data));

        setChatHistory(prev => [...prev, {
          role: 'assistant',
          content: responseData.response
        }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.'
      }]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white pt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Interface Mode Toggle */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => setInterfaceMode('simple')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${interfaceMode === 'simple' ? 'bg-purple-600' : 'bg-gray-700'
              }`}
          >
            <Image className="w-5 h-5" />
            <span>Simple Mode</span>
          </button>
          <button
            onClick={() => setInterfaceMode('chat')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${interfaceMode === 'chat' ? 'bg-purple-600' : 'bg-gray-700'
              }`}
          >
            <MessageSquare className="w-5 h-5" />
            <span>Chat Mode</span>
          </button>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Generation Area */}
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-gray-800/50 rounded-xl p-8">
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-2">
                <Wand2 className="w-8 h-8 text-purple-400" />
                AI Studio
              </h2>

              {/* Style Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">Select Style</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {unlockedStyles.map(style => (
                    <button
                      key={style.id}
                      onClick={() => setSelectedStyle(style.name)}
                      className={`relative rounded-lg overflow-hidden aspect-video group ${selectedStyle === style.name ? 'ring-2 ring-purple-500' : ''}`}
                    >
                      <img
                        src={style.thumbnail}
                        alt={style.name}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                        <div className="text-center">
                          <p className="font-semibold">{style.name}</p>
                          <p className="text-sm text-gray-400">{style.artist}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {interfaceMode === 'simple' ? (
                // Simple Mode Interface
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-300 mb-2">Prompt</label>
                  <div className="relative">
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Describe the artwork you want to generate..."
                      className="w-full h-32 bg-gray-900/50 rounded-lg p-4 text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    />
                    <div className="absolute right-2 bottom-2">
                      <button
                        onClick={handleGenerate}
                        disabled={!prompt || !selectedStyle || isGenerating}
                        className={`px-4 py-2 rounded-lg flex items-center gap-2 ${isGenerating ? 'bg-purple-600/50' : 'bg-purple-600 hover:bg-purple-700'
                          } transition-all`}
                      >
                        {isGenerating ? (
                          <>
                            <RefreshCw className="w-5 h-5 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-5 h-5" />
                            Generate
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                // Chat Mode Interface
                <div className="mb-6">
                  <div className="bg-gray-900/50 rounded-lg p-4 h-[50vh] mb-4 overflow-y-auto">
                    {chatHistory.map((message, index) => (
                      <div
                        key={index}
                        className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
                      >
                        <div
                          className={`
                            inline-block rounded-lg px-6 py-3 max-w-[90%]
                            ${message.role === 'user'
                              ? 'bg-purple-600 text-white'
                              : 'bg-gray-800 border border-gray-700 text-gray-100'
                            }
                            prose prose-invert prose-pre:bg-gray-900 prose-pre:border prose-pre:border-gray-700
                            ${message.role === 'assistant' ? 'prose-p:my-2 prose-code:text-purple-400 prose-code:bg-gray-900/50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded' : ''}
                          `}
                          style={{
                            lineHeight: '1.6',
                            fontFamily: message.role === 'assistant' ? 'system-ui, -apple-system, sans-serif' : 'inherit'
                          }}
                        >
                          {message.role === 'assistant'
                            ? <div dangerouslySetInnerHTML={{
                              __html: marked(message.content, { breaks: true })
                            }} />
                            : message.content
                          }
                        </div>
                      </div>
                    ))}
                  </div>
                  <form onSubmit={handleChatSubmit} className="relative">
                    <input
                      type="text"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Chat with AI assistant..."
                      className="w-full bg-gray-900/50 rounded-lg p-4 pr-24 text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    />
                    <button
                      type="submit"
                      disabled={!prompt.trim() || isGenerating}
                      className="absolute right-2 top-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-all flex items-center gap-2"
                    >
                      <MessageSquare className="w-5 h-5" />
                      Send
                    </button>
                  </form>
                </div>
              )}

              {/* Generated Image Display */}
              {interfaceMode === 'simple' ? (
                <div className="aspect-square rounded-lg bg-gray-900/50 flex items-center justify-center">
                  {isGenerating ? (
                    <div className="text-center">
                      <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-purple-400" />
                      <p className="text-gray-400">Creating your masterpiece...</p>
                    </div>
                  ) : simpleGeneratedImage ? (
                    <img src={simpleGeneratedImage} alt="Generated Artwork" className="w-full h-full object-cover rounded-lg" />
                  ) : (
                    <div className="text-center text-gray-400">
                      <Palette className="w-12 h-12 mx-auto mb-4" />
                      <p>Your generated artwork will appear here</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="aspect-square rounded-lg bg-gray-900/50 flex items-center justify-center">
                  {isGenerating ? (
                    <div className="text-center">
                      <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-purple-400" />
                      <p className="text-gray-400">AI is working on your request...</p>
                    </div>
                  ) : chatGeneratedImage ? (
                    <div className="relative">
                      <img src={chatGeneratedImage} alt="Generated Artwork" className="w-full h-full object-cover rounded-lg" />
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                        <p className="text-sm text-white">Generated image from our conversation</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-400">
                      <MessageSquare className="w-12 h-12 mx-auto mb-4" />
                      <p>Ask me to generate an image and it will appear here</p>
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4 mt-4">
                <button className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center justify-center gap-2 transition-all">
                  <Save className="w-5 h-5" />
                  Save
                </button>
                <button className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center justify-center gap-2 transition-all">
                  <Download className="w-5 h-5" />
                  Download
                </button>
                <button className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center justify-center gap-2 transition-all">
                  <Share2 className="w-5 h-5" />
                  Share
                </button>
              </div>
            </div>
          </div>

          {/* Prompt History Sidebar */}
          <div className="bg-gray-800/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <History className="w-5 h-5 text-purple-400" />
                Prompt History
              </h3>
              <button
                onClick={handleClearHistory}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              {promptHistory.map((item) => (
                <div key={item.id} className="bg-gray-900/50 rounded-lg p-4">
                  {item.image && <img src={item.image} alt="Generated Artwork" className="w-full h-32 object-cover rounded-lg mb-2" />}
                  <p className="text-sm mb-2">{item.prompt}</p>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>{item.style}</span>
                    <span>{item.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div >
  );
}