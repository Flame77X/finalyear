import React, { useState, useEffect, useRef } from 'react';
import {
    Mic,
    Square,
    User,
    Video,
    FolderOpen,
    FileText,
    ChevronUp,
    Send,
    VideoOff,
    MicOff
} from 'lucide-react';

/* --- COMPONENTS --- */

// 1. Sidebar Component
const Sidebar = () => {
    const activeTab = 'interview';
    const navItems = [
        { id: 'interview', icon: Video, label: 'Interview' },
    ];

    return (
        <div className="fixed left-0 top-0 h-full w-20 bg-[#272727] flex flex-col items-center py-8 border-r border-[#FFFFFF]/5 z-50">
            <div className="mb-12">
                <div className="w-10 h-10 bg-[#CCCCCC] rounded-full flex items-center justify-center">
                    <span className="font-serif text-black font-bold text-xl">V</span>
                </div>
            </div>

            <div className="flex-1 flex flex-col gap-8 w-full">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        className={`w-full flex justify-center py-3 transition-all duration-300 relative group
              ${activeTab === item.id ? 'text-[#00E5FF]' : 'text-[#CCCCCC]/60 hover:text-[#CCCCCC]'}`}
                    >
                        {activeTab === item.id && (
                            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[#00E5FF] rounded-r-full shadow-[0_0_10px_#00E5FF]" />
                        )}
                        <item.icon size={24} strokeWidth={1.5} />

                        {/* Tooltip */}
                        <span className="absolute left-full ml-4 bg-[#272727] px-3 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10 pointer-events-none">
                            {item.label}
                        </span>
                    </button>
                ))}
            </div>

            <div className="mt-auto">
                <button className="w-10 h-10 rounded-full bg-[#131313] flex items-center justify-center text-[#CCCCCC]/60 hover:text-[#CCCCCC] transition-colors">
                    <User size={20} />
                </button>
            </div>
        </div>
    );
};

// 2. AI Visualizer (The Orb)
const AIVisualizer = ({ state, lastMessage }) => {
    return (
        <div className="relative flex flex-col items-center justify-center w-full h-full">
            <div className="relative flex items-center justify-center w-64 h-64">
                {/* Outer Glow */}
                <div className={`absolute inset-0 rounded-full blur-[60px] transition-all duration-700
          ${state === 'listening' ? 'bg-[#00E5FF]/20' : 'bg-[#CCCCCC]/5'}`}
                />

                {/* Core Orb */}
                <div className={`w-32 h-32 rounded-full border flex items-center justify-center transition-all duration-500 relative
          ${state === 'listening'
                        ? 'border-[#00E5FF] shadow-[0_0_30px_#00E5FF] scale-110'
                        : 'border-[#CCCCCC]/30 scale-100'}`}
                >
                    <div className={`w-24 h-24 rounded-full bg-gradient-to-br from-[#272727] to-[#131313] flex items-center justify-center overflow-hidden relative`}>
                        {/* Animated Waveform Simulation */}
                        <div className="flex items-center gap-1 h-12">
                            {[1, 2, 3, 4, 5].map((i) => (
                                <div key={i}
                                    className={`w-1 bg-[#CCCCCC] rounded-full transition-all duration-150 ease-in-out
                     ${state === 'listening' || state === 'speaking' ? 'bg-[#00E5FF] animate-pulse' : 'bg-[#CCCCCC]/30'}`}
                                    style={{
                                        height: state === 'listening' || state === 'speaking' ? `${Math.random() * 100}%` : '20%',
                                        animationDelay: `${i * 0.1}s`
                                    }}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Status Text */}
                <div className="absolute -bottom-24 text-center w-full min-w-[300px]">
                    <h3 className="font-serif text-2xl text-[#CCCCCC] tracking-wide">
                        {state === 'listening' ? 'Listening...' : 'Voca AI'}
                    </h3>
                    <p className="text-sm text-[#CCCCCC]/50 font-light mt-1 uppercase tracking-widest text-[10px]">
                        {state === 'listening' ? 'Processing Audio' : state === 'speaking' ? 'Speaking...' : 'Ready'}
                    </p>
                    {state === 'speaking' && (
                        <p className="mt-2 text-[#CCCCCC]/80 italic text-sm line-clamp-2 px-4">
                            "{lastMessage}"
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

// 3. Interview Interface (Logic + UI merged)
const InterviewPage = () => {
    // --- LOGIC STATES ---
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'ai', text: "Hello! I'm Voca. Please introduce yourself." }
    ]);
    const [aiAudioUrl, setAiAudioUrl] = useState(null);

    // --- UI STATES ---
    const [timer, setTimer] = useState(0);
    const [showFiles, setShowFiles] = useState(false);
    const [textInput, setTextInput] = useState('');
    const [files] = useState([
        "Resume_JohnDoe_v2.pdf",
        "Portfolio_2024.pdf",
        "Cover_Letter.docx"
    ]);

    // --- REFS ---
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const audioPlayerRef = useRef(null);
    const videoRef = useRef(null);

    // --- EFFECTS ---

    // 1. Timer
    useEffect(() => {
        let interval;
        if (isRecording) {
            interval = setInterval(() => setTimer(t => t + 1), 1000);
        } else {
            setTimer(0);
        }
        return () => clearInterval(interval);
    }, [isRecording]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // 2. Camera Setup
    useEffect(() => {
        async function setupCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (err) {
                console.error("Camera access denied:", err);
            }
        }
        setupCamera();
    }, []);

    // 3. Auto-play Audio
    useEffect(() => {
        if (aiAudioUrl && audioPlayerRef.current) {
            audioPlayerRef.current.volume = 1.0;
            audioPlayerRef.current.play().catch(e => console.error(e));
        }
    }, [aiAudioUrl]);

    // --- HANDLERS ---

    const handleSend = () => {
        if (textInput.trim()) {
            console.log("Sending text (Connect to backend if needed):", textInput);
            setMessages(prev => [...prev, { role: 'user', text: textInput }]);
            setTextInput("");
            // NOTE: Current backend only processes audio. Text logic would go here.
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) audioChunksRef.current.push(event.data);
            };

            mediaRecorderRef.current.onstop = handleStopRecording;
            mediaRecorderRef.current.start();
            setIsRecording(true);
            setAiAudioUrl(null);
        } catch (err) {
            console.error(err);
            alert("Mic access denied.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const handleStopRecording = async () => {
        setIsProcessing(true);
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');

        // Capture Video Frame
        if (videoRef.current) {
            const canvas = document.createElement('canvas');
            canvas.width = videoRef.current.videoWidth;
            canvas.height = videoRef.current.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoRef.current, 0, 0);
            const videoBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
            if (videoBlob) formData.append('video_frame', videoBlob, 'frame.jpg');
        }

        try {
            const response = await fetch('http://localhost:8000/process_audio', {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error('Backend error');
            const data = await response.json();

            setMessages(prev => [
                ...prev,
                { role: 'user', text: data.transcript },
                { role: 'ai', text: data.ai_response_text }
            ]);

            if (data.ai_audio_filename) {
                const audioRes = await fetch(`http://localhost:8000/audio/${data.ai_audio_filename}`);
                const audioBlob = await audioRes.blob();
                const url = URL.createObjectURL(audioBlob);
                setAiAudioUrl(url);
            }
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'system', text: "Error processing audio." }]);
        } finally {
            setIsProcessing(false);
        }
    };

    // --- RENDER HELPERS ---
    const visualizerState = isRecording || isProcessing ? 'listening' : aiAudioUrl ? 'speaking' : 'idle';
    const lastUserMessage = messages.filter(m => m.role === 'user').slice(-1)[0]?.text;
    const lastAiMessage = messages.filter(m => m.role === 'ai').slice(-1)[0]?.text;

    return (
        <div className="flex bg-[#131313] text-[#CCCCCC] font-sans h-screen overflow-hidden">
            <Sidebar />

            <main className="flex-1 h-screen p-8 pl-28 overflow-hidden flex flex-col transition-opacity duration-500 ease-in-out">
                {/* Header */}
                <header className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-serif text-[#CCCCCC]">Voca AI</h1>
                    </div>
                </header>

                {/* Main Split Grid */}
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-0">

                    {/* Left Card: AI */}
                    <div className="relative rounded-[2rem] border border-[#CCCCCC]/10 bg-[#131313] flex flex-col items-center justify-center overflow-hidden group">
                        {/* Subtle Grid Background */}
                        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] opacity-20" />

                        <AIVisualizer state={visualizerState} lastMessage={lastAiMessage} />
                    </div>

                    {/* Right Card: User Camera + Transcript */}
                    <div className="flex flex-col rounded-[2rem] bg-[#131313] border border-[#CCCCCC]/10 overflow-hidden shadow-2xl">

                        {/* Video Feed (Top Section) */}
                        <div className="relative flex-1 bg-black min-h-0 overflow-hidden">
                            {/* Mock Camera Feed Background */}
                            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#131313]/90 z-10 pointer-events-none" />
                            <video ref={videoRef} autoPlay muted className="absolute inset-0 w-full h-full object-cover opacity-80" />

                            {/* Camera Status Overlay */}
                            <div className="absolute top-6 right-6 z-20 flex gap-3">
                                <div className="px-3 py-1 rounded-full bg-[#FF4444]/90 backdrop-blur-md text-white text-xs font-medium flex items-center gap-2 shadow-lg">
                                    <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                                    LIVE
                                </div>
                            </div>
                        </div>

                        {/* Transcript Box (Bottom Section) */}
                        <div className="bg-[#272727] border-t border-white/5 p-6 h-auto min-h-[140px] flex flex-col justify-center">
                            <p className="text-[#00E5FF] text-xs font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF]"></span>
                                Live Transcript
                            </p>
                            <p className="text-lg text-white font-light leading-relaxed line-clamp-3">
                                "{lastUserMessage || "Listening for your input..."}"
                            </p>
                        </div>
                    </div>
                </div>

                {/* Bottom Controls - Grid Layout to prevent Overlap */}
                <div className="h-32 grid grid-cols-[1fr_auto_1fr] items-center gap-4 mt-4">

                    {/* Left: Time */}
                    <div className="flex flex-col justify-center justify-self-start">
                        <span className="text-xs text-[#CCCCCC]/40 uppercase tracking-widest">Time Elapsed</span>
                        <span className="text-xl font-serif text-[#CCCCCC]">{formatTime(timer)}</span>
                    </div>

                    {/* Center: Input + Mic Group */}
                    <div className="flex items-center gap-4 justify-self-center">
                        {/* Typing Box */}
                        <div className="relative group hidden md:block">
                            <input
                                type="text"
                                value={textInput}
                                onChange={(e) => setTextInput(e.target.value)}
                                placeholder="Type your response..."
                                className="bg-[#272727] border border-[#CCCCCC]/10 rounded-full pl-6 pr-12 py-4 w-[300px] lg:w-[400px] text-white placeholder-[#CCCCCC]/30 focus:outline-none focus:border-[#00E5FF]/50 focus:bg-[#2a2a2a] transition-all shadow-lg text-sm"
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            />
                            <button
                                onClick={handleSend}
                                className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full transition-all duration-200
                  ${textInput ? 'text-[#00E5FF] hover:bg-[#00E5FF]/10 opacity-100' : 'text-[#CCCCCC]/20 opacity-0 pointer-events-none'}`}
                            >
                                <Send size={18} />
                            </button>
                        </div>

                        {/* Mic FAB */}
                        <button
                            onClick={!isRecording ? startRecording : stopRecording}
                            className={`w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 transform hover:scale-105 active:scale-95 border border-[#ffffff]/5
                ${isRecording ? 'bg-[#FF4444]' : 'bg-[#CCCCCC] hover:bg-white'}`}
                        >
                            {isRecording ? (
                                <Square className="text-white fill-current" size={24} />
                            ) : (
                                <Mic className="text-[#131313] group-hover:text-black transition-colors" size={28} strokeWidth={2} />
                            )}
                        </button>
                    </div>

                    {/* Right: Files & End Button */}
                    <div className="flex items-center gap-4 justify-self-end">

                        {/* Files Dropdown Container */}
                        <div className="relative hidden md:block">
                            {showFiles && (
                                <div className="absolute bottom-full mb-4 right-0 w-64 bg-[#272727] border border-[#CCCCCC]/10 rounded-xl p-4 shadow-2xl backdrop-blur-md animate-in fade-in slide-in-from-bottom-2 z-50">
                                    <div className="flex justify-between items-center mb-3 border-b border-[#FFFFFF]/5 pb-2">
                                        <h4 className="text-[#CCCCCC] font-serif text-sm">Uploaded Documents</h4>
                                        <span className="text-[10px] text-[#00E5FF] bg-[#00E5FF]/10 px-2 py-0.5 rounded-full">{files.length}</span>
                                    </div>
                                    <ul className="space-y-2">
                                        {files.map((file, i) => (
                                            <li key={i} className="flex items-center gap-3 text-xs text-[#CCCCCC]/70 p-2 hover:bg-[#131313] rounded-lg transition-colors cursor-pointer group">
                                                <div className="p-1.5 rounded bg-[#131313] group-hover:bg-[#272727] transition-colors">
                                                    <FileText size={14} className="text-[#00E5FF]" />
                                                </div>
                                                <span className="truncate">{file}</span>
                                            </li>
                                        ))}
                                        <li className="flex items-center gap-2 text-xs text-[#CCCCCC]/40 p-2 border border-dashed border-[#CCCCCC]/10 rounded-lg justify-center hover:border-[#00E5FF]/50 hover:text-[#00E5FF] transition-all cursor-pointer mt-2">
                                            + Upload New
                                        </li>
                                    </ul>
                                </div>
                            )}

                            {/* The "Small Box" Trigger */}
                            <button
                                onClick={() => setShowFiles(!showFiles)}
                                className={`h-12 px-5 rounded-full border flex items-center gap-3 transition-all duration-300 text-sm font-medium tracking-wide whitespace-nowrap
                  ${showFiles ? 'bg-[#CCCCCC] text-[#131313] border-[#CCCCCC]' : 'border-[#CCCCCC]/20 text-[#CCCCCC] hover:bg-[#272727]'}`}
                            >
                                <div className="relative">
                                    <FolderOpen size={18} />
                                    <div className="absolute -top-1 -right-1 w-2 h-2 bg-[#00E5FF] rounded-full border border-[#131313]" />
                                </div>
                                <span className="hidden md:inline">My Files</span>
                                {showFiles ? <ChevronUp size={16} /> : null}
                            </button>
                        </div>

                        <button className="h-12 px-8 rounded-full border border-[#CCCCCC]/20 text-[#CCCCCC] hover:bg-[#FF4444] hover:border-[#FF4444] hover:text-white transition-all font-medium text-sm tracking-wide">
                            End
                        </button>
                    </div>
                </div>

                {/* Hidden Audio */}
                <audio ref={audioPlayerRef} src={aiAudioUrl} className="hidden" onEnded={() => setAiAudioUrl(null)} />
            </main>
        </div>
    );
};

export default InterviewPage;
