import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Mic, User, Bot, Loader2 } from 'lucide-react';

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef(null);

    // Initial Greeting
    useEffect(() => {
        // Check if we need to start the interview or if history exists
        // For now, just show a welcome message locally
        setMessages([{
            role: 'bot',
            content: "Hello! I am your AI Interviewer. I'm ready to begin when you are. Type 'Start' to begin."
        }]);
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');

        // Add User Message
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            // Call Backend
            const response = await axios.post('http://localhost:8000/chat', {
                message: userMsg
            });

            const data = response.data;

            // Add Bot Message
            setMessages(prev => [...prev, { role: 'bot', content: data.dialogue }]);

            // If there are scores, maybe show them?
            if (data.scores) {
                console.log("Scores:", data.scores);
                // Optional: Add a system message with score
                // setMessages(prev => [...prev, { role: 'system', content: `Score: ${data.scores.score}/10` }]);
            }

        } catch (error) {
            console.error("Error:", error);
            setMessages(prev => [...prev, { role: 'error', content: "Error connecting to the AI. Is the backend running?" }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-gray-100 font-sans">
            {/* Header */}
            <header className="bg-gray-800 p-4 shadow-md border-b border-gray-700 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Bot className="w-6 h-6 text-blue-400" />
                    <h1 className="text-xl font-bold">AI Interviewer</h1>
                </div>
                <div className="text-sm text-gray-400">Powered by Groq</div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-br-none'
                                : msg.role === 'error'
                                    ? 'bg-red-900/50 text-red-200 border border-red-700'
                                    : 'bg-gray-800 text-gray-100 rounded-bl-none border border-gray-700'
                            }`}>
                            <div className="flex items-center gap-2 mb-1 opacity-50 text-xs uppercase tracking-wider font-bold">
                                {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                                {msg.role === 'user' ? 'You' : 'Interviewer'}
                            </div>
                            <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-800 rounded-2xl p-4 rounded-bl-none border border-gray-700 flex items-center gap-2 text-gray-400">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-4 bg-gray-800 border-t border-gray-700">
                <div className="flex gap-2 max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your answer..."
                        className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </form>
        </div>
    );
}

export default App;
