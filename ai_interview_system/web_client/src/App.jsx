import { useState, useRef, useEffect } from 'react'
import { Mic, Square, Loader2, Volume2, MessageSquare, Activity } from 'lucide-react'

function App() {
    const [isRecording, setIsRecording] = useState(false)
    const [isProcessing, setIsProcessing] = useState(false)
    const [messages, setMessages] = useState([
        { role: 'ai', text: "Hello! I'm your AI Interviewer. Click the microphone to start our session." }
    ])
    const [aiAudioUrl, setAiAudioUrl] = useState(null)
    const [metrics, setMetrics] = useState(null)

    const mediaRecorderRef = useRef(null)
    const audioChunksRef = useRef([])
    const audioPlayerRef = useRef(null)
    const videoRef = useRef(null)
    const messagesEndRef = useRef(null)

    // Initialize Camera
    useEffect(() => {
        async function setupCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true })
                if (videoRef.current) {
                    videoRef.current.srcObject = stream
                }
            } catch (err) {
                console.error("Camera access denied:", err)
            }
        }
        setupCamera()
    }, [])

    // Auto-scroll chat
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    // Start Recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            mediaRecorderRef.current = new MediaRecorder(stream)
            audioChunksRef.current = []

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data)
                }
            }

            mediaRecorderRef.current.onstop = handleStopRecording
            mediaRecorderRef.current.start()
            setIsRecording(true)
            setAiAudioUrl(null)
        } catch (err) {
            console.error("Error accessing microphone:", err)
            alert("Could not access microphone.")
        }
    }

    // Stop Recording
    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop()
            setIsRecording(false)
        }
    }

    // Process Recording
    const handleStopRecording = async () => {
        setIsProcessing(true)
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const formData = new FormData()
        formData.append('file', audioBlob, 'recording.wav')

        try {
            // Optimistic Update
            setMessages(prev => [...prev, { role: 'user', text: "..." }]) // Placeholder

            const response = await fetch('http://localhost:8000/process_audio', {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) throw new Error('Backend processing failed')

            const data = await response.json()

            // Update Chat
            setMessages(prev => {
                const newMsgs = [...prev]
                newMsgs.pop() // Remove placeholder
                newMsgs.push({ role: 'user', text: data.transcript }) // Real text
                newMsgs.push({ role: 'ai', text: data.ai_response_text })
                return newMsgs
            })

            // Update Metrics
            if (data.vocal_metrics) {
                setMetrics(data.vocal_metrics)
            }

            // Play Audio
            if (data.ai_audio_filename) {
                const audioRes = await fetch(`http://localhost:8000/audio/${data.ai_audio_filename}`)
                const audioBlob = await audioRes.blob()
                const url = URL.createObjectURL(audioBlob)
                setAiAudioUrl(url)
            }

        } catch (error) {
            console.error(error)
            setMessages(prev => [...prev, { role: 'system', text: "Error processing audio." }])
        } finally {
            setIsProcessing(false)
        }
    }

    // Auto-play audio
    useEffect(() => {
        if (aiAudioUrl && audioPlayerRef.current) {
            audioPlayerRef.current.volume = 0.8
            audioPlayerRef.current.play().catch(e => console.error("Playback failed", e))
        }
    }, [aiAudioUrl])

    return (
        <div className="min-h-screen bg-zinc-950 text-white font-sans flex flex-col md:flex-row p-4 gap-4">

            {/* LEFT: Focus Area (Video + Visualizer) */}
            <div className="flex-1 flex flex-col gap-4">

                {/* Main "Call" Window */}
                <div className="flex-1 bg-zinc-900 rounded-2xl border border-zinc-800 relative overflow-hidden flex flex-col items-center justify-center min-h-[400px]">

                    {/* User Video (PiP) */}
                    <div className="absolute top-4 right-4 w-48 h-36 bg-black rounded-xl overflow-hidden shadow-2xl border border-zinc-700 z-10 group">
                        <video ref={videoRef} autoPlay muted className="w-full h-full object-cover transform scale-x-[-1]" />
                        <div className="absolute bottom-2 left-2 bg-black/50 px-2 rounded text-xs select-none">You</div>

                        {/* Metrics Overlay */}
                        {metrics && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-2 opacity-0 group-hover:opacity-100 transition-opacity p-2 text-center">
                                <div className="text-xs text-zinc-400 font-mono uppercase tracking-widest">Confidence</div>
                                <div className="text-2xl font-bold text-green-400">{metrics.confidence_score.toFixed(0)}%</div>

                                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[10px] w-full mt-2">
                                    <div className="text-zinc-500 text-right">Pitch</div>
                                    <div className="text-zinc-300 text-left">{metrics.avg_pitch.toFixed(0)} Hz</div>
                                    <div className="text-zinc-500 text-right">Tempo</div>
                                    <div className="text-zinc-300 text-left">{metrics.speech_rate.toFixed(0)} BPM</div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* AI Presence Center */}
                    <div className="relative z-0 flex flex-col items-center">
                        {isRecording ? (
                            <div className="relative">
                                <div className="w-32 h-32 bg-red-500 rounded-full animate-pulse blur-xl absolute opacity-20"></div>
                                <div className="w-32 h-32 bg-zinc-800 rounded-full flex items-center justify-center border-4 border-red-500 relative z-10">
                                    <Mic size={48} className="text-white" />
                                </div>
                                <p className="mt-6 text-red-400 tracking-widest uppercase font-bold animate-pulse">Listening...</p>
                            </div>
                        ) : isProcessing ? (
                            <div className="flex flex-col items-center">
                                <Loader2 size={64} className="text-violet-500 animate-spin" />
                                <p className="mt-6 text-violet-400 tracking-widest uppercase font-bold">Thinking...</p>
                            </div>
                        ) : aiAudioUrl ? (
                            <div className="relative">
                                <div className="w-32 h-32 bg-violet-600 rounded-full animate-pulse blur-xl absolute opacity-20"></div>
                                <div className="w-32 h-32 bg-zinc-800 rounded-full flex items-center justify-center border-4 border-violet-500 relative z-10 shadow-[0_0_50px_rgba(139,92,246,0.5)]">
                                    <Volume2 size={48} className="text-white" />
                                </div>
                                <p className="mt-6 text-violet-400 tracking-widest uppercase font-bold">Speaking</p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center opacity-50">
                                <div className="w-32 h-32 rounded-full border-4 border-dashed border-zinc-700 flex items-center justify-center">
                                    <div className="text-zinc-600 font-bold text-xl">AI</div>
                                </div>
                                <p className="mt-6 text-zinc-600 uppercase font-bold">Idling</p>
                            </div>
                        )}
                    </div>

                    {/* Primary Metrics Badge (Bottom Center) - Only if score > 0 */}
                    {metrics && metrics.confidence_score > 0 && !isRecording && !isProcessing && (
                        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-zinc-950/80 backdrop-blur border border-zinc-800 px-6 py-2 rounded-full flex items-center gap-4 animate-in fade-in slide-in-from-bottom-4">
                            <div className="flex items-center gap-2">
                                <Activity size={16} className="text-green-500" />
                                <span className="text-sm font-medium text-zinc-300">Vocal Confidence:</span>
                            </div>
                            <span className="text-lg font-bold text-white">{metrics.confidence_score.toFixed(0)}%</span>
                        </div>
                    )}

                </div>

                {/* Controls Bar */}
                <div className="h-24 bg-zinc-900 rounded-2xl border border-zinc-800 flex items-center justify-center gap-6 shadow-xl">
                    {!isRecording ? (
                        <button
                            onClick={startRecording}
                            disabled={isProcessing}
                            className="flex flex-col items-center gap-1 group disabled:opacity-50"
                        >
                            <div className="w-14 h-14 bg-zinc-800 rounded-full flex items-center justify-center group-hover:bg-violet-600 transition-colors">
                                <Mic size={24} />
                            </div>
                            <span className="text-xs text-zinc-400">Start</span>
                        </button>
                    ) : (
                        <button
                            onClick={stopRecording}
                            className="flex flex-col items-center gap-1 group"
                        >
                            <div className="w-14 h-14 bg-red-500/10 rounded-full flex items-center justify-center group-hover:bg-red-500 transition-colors border border-red-500">
                                <Square size={24} className="text-red-500 group-hover:text-white" />
                            </div>
                            <span className="text-xs text-red-500">Stop</span>
                        </button>
                    )}
                </div>
            </div>

            {/* RIGHT: Chat / Transcript History */}
            <div className="w-full md:w-96 bg-zinc-900 rounded-2xl border border-zinc-800 flex flex-col overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur">
                    <h2 className="text-lg font-bold flex items-center gap-2">
                        <MessageSquare size={20} className="text-violet-400" />
                        History
                    </h2>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.role === 'user'
                                ? 'bg-violet-600 text-white rounded-tr-none'
                                : 'bg-zinc-800 text-zinc-200 rounded-tl-none border border-zinc-700'
                                }`}>
                                {msg.text}
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Hidden Audio */}
            <audio ref={audioPlayerRef} src={aiAudioUrl} className="hidden" onEnded={() => setAiAudioUrl(null)} />
        </div>
    )
}

export default App
