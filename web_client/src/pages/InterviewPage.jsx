import React, { useRef, useEffect, useState, useCallback } from 'react';
import '../styles/InterviewPage.css';

const InterviewPage = () => {
    // ============ REFS ============
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const audioContextRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const wsRef = useRef(null);

    // ============ STATE ============
    const [isRecording, setIsRecording] = useState(false);
    const [liveScores, setLiveScores] = useState({
        verbal_score: 0,
        non_verbal_score: 0,
        vocal_score: 0,
        keyword_score: 0,
        final_score: 0,
    });
    const [transcript, setTranscript] = useState('');
    const [cameraActive, setCameraActive] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [framesSent, setFramesSent] = useState(0);
    const [aiMessage, setAiMessage] = useState('Hello! I am your AI Interview Coach. Click "Start Interview" to begin.');
    const [inputText, setInputText] = useState('');
    const [audioLevel, setAudioLevel] = useState(0); // For visualizing mic volume

    const handleSendMessage = () => {
        if (!inputText.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        // Send text to backend
        wsRef.current.send(JSON.stringify({
            type: 'text',
            text: inputText
        }));

        // Update local transcript immediately for better UX
        setTranscript(prev => prev + (prev ? ' ' : '') + inputText);
        setInputText('');
    };

    // ============ VIDEO FRAME CAPTURE & STREAMING ============

    /**
     * Initialize WebSocket connection
     */
    const initializeWebSocket = useCallback(() => {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const candidateId = localStorage.getItem('candidate_id');
            const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/interview?candidate_id=${candidateId || ''}`;

            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                console.log('✅ WebSocket connected');
                setConnectionStatus('connected');
            };

            wsRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data);

                // Handle different message types
                switch (data.type) {
                    case 'non_verbal_analysis':
                        // score is 0-1 in agent, 0-100 in message? check server. 
                        // Server sends 0-100 if nv_result is 0-1. 
                        // But let's assume it comes as 0-100 range from our server update.
                        let nv = data.confidence_score;
                        if (nv <= 1.0) nv *= 100;
                        setLiveScores(prev => ({
                            ...prev,
                            non_verbal_score: nv,
                        }));
                        break;

                    case 'audio_analysis':
                        setLiveScores(prev => ({
                            ...prev,
                            vocal_score: data.confidence_score || prev.vocal_score,
                        }));
                        break;

                    case 'keyword_analysis':
                        setLiveScores(prev => ({
                            ...prev,
                            keyword_score: data.keyword_score || prev.keyword_score,
                        }));
                        break;

                    case 'transcript':
                         if (data.text) {
                            // Only update if text is meaningful
                            if (data.text.trim().length > 0) {
                                setTranscript(data.text);
                            }
                         }
                         break;
                    
                    case 'text':
                        if (data.ai_text) {
                            setAiMessage(data.ai_text);
                        }
                        break;

                    case 'audio':
                        if (data.audio) {
                            try {
                                const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
                                audio.play();
                            } catch (e) {
                                console.error("Error playing audio:", e);
                            }
                        }
                        break;

                    case 'final_score':
                        setLiveScores(data.scores);
                        break;

                    case 'status':
                        console.log("Status:", data.message);
                        break;

                    case 'error':
                        console.error('Backend error:', data.message);
                        break;

                    default:
                        console.log('Unknown message type:', data.type);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionStatus('error');
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket closed');
                setConnectionStatus('disconnected');
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            setConnectionStatus('error');
        }
    }, []);

    /**
     * Initialize camera and start video streaming
     */
    const startCamera = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                },
                audio: false, // Audio handled separately
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setCameraActive(true);

                // Start frame capture loop
                startVideoFrameCapture();
            }
        } catch (error) {
            console.error('Failed to access camera:', error);
            alert('Camera access denied. Please enable camera permissions.');
        }
    }, []);

    /**
     * Capture video frames from canvas and send to backend
     * Runs every 500ms (2 FPS)
     */
    const startVideoFrameCapture = useCallback(() => {
        const frameInterval = setInterval(() => {
            if (!videoRef.current || !canvasRef.current || !cameraActive) return;

            try {
                const canvas = canvasRef.current;
                const ctx = canvas.getContext('2d');

                // Draw video frame to canvas
                ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

                // Convert canvas to base64 JPEG (lower bandwidth than PNG)
                const frameBase64 = canvas.toDataURL('image/jpeg', 0.7); // 70% quality

                // Extract just the base64 part
                const base64String = frameBase64.split(',')[1];

                // Send to backend via WebSocket
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({
                        type: 'video_frame',
                        frame: base64String,
                        timestamp: Date.now(),
                    }));

                    setFramesSent(prev => prev + 1);
                }
            } catch (error) {
                console.error('Error capturing video frame:', error);
            }
        }, 500); // 500ms

        // Store interval ID for cleanup
        videoRef.current._frameInterval = frameInterval;
    }, [cameraActive]);

    /**
     * Initialize audio recording and streaming using AudioContext (WAV)
     */
    const startAudioCapture = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Close existing context if any
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }

            // Create new context with 16kHz sample rate (match backend)
            // Browsers might ignore this and use hardware rate (e.g., 44.1k/48k)
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            audioContextRef.current = new AudioContextClass(); // Let browser decide rate for stability
            const context = audioContextRef.current;
            const actualSampleRate = context.sampleRate;
            console.log("Audio Sample Rate:", actualSampleRate);

            const source = context.createMediaStreamSource(stream);
            
            // Use ScriptProcessor for raw PCM access
            // Buffer size 4096, 1 input channel, 1 output channel
            const processor = context.createScriptProcessor(4096, 1, 1);
            
            source.connect(processor);
            processor.connect(context.destination);

            let audioBuffer = [];
            // Send smaller chunks (0.5s) for lower latency
            const BUFFER_SIZE = Math.floor(actualSampleRate / 2);

            processor.onaudioprocess = (e) => {
                const inputData = e.inputBuffer.getChannelData(0);
                audioBuffer.push(...inputData);
                
                // Calculate simple volume for visualization (Average Amplitude)
                let sum = 0;
                for (let i = 0; i < inputData.length; i++) {
                    sum += Math.abs(inputData[i]);
                }
                const avg = sum / inputData.length;
                setAudioLevel(Math.min(100, avg * 500)); // Amplify for visibility

                if (audioBuffer.length >= BUFFER_SIZE) {
                     // console.log("Sending Audio Chunk:", audioBuffer.length); // DEBUG
                    sendAudioChunk(new Float32Array(audioBuffer), actualSampleRate);
                    // Keep overlap? No, clear mostly.
                    audioBuffer = []; 
                }
            };

            // Helper to encode Float32 PCM to WAV (16-bit)
            const sendAudioChunk = (samples, sampleRate) => {
                const buffer = new ArrayBuffer(44 + samples.length * 2);
                const view = new DataView(buffer);

                // Write WAV Header
                const writeString = (view, offset, string) => {
                    for (let i = 0; i < string.length; i++) {
                        view.setUint8(offset + i, string.charCodeAt(i));
                    }
                };

                writeString(view, 0, 'RIFF');
                view.setUint32(4, 36 + samples.length * 2, true);
                writeString(view, 8, 'WAVE');
                writeString(view, 12, 'fmt ');
                view.setUint32(16, 16, true);
                view.setUint16(20, 1, true); // PCM
                view.setUint16(22, 1, true); // Mono
                view.setUint32(24, sampleRate, true); // Actual Sample Rate
                view.setUint32(28, sampleRate * 2, true); // Byte Rate
                view.setUint16(32, 2, true); // Block Align
                view.setUint16(34, 16, true); // Bits per Sample
                writeString(view, 36, 'data');
                view.setUint32(40, samples.length * 2, true);

                // Write Data (Float32 -> Int16)
                let offset = 44;
                for (let i = 0; i < samples.length; i++) {
                    let s = Math.max(-1, Math.min(1, samples[i]));
                    // Convert to 16-bit PCM
                    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                    offset += 2;
                }

                // Send to backend
                const bytes = new Uint8Array(buffer);
                let binary = '';
                const len = bytes.byteLength;
                for (let i = 0; i < len; i++) {
                    binary += String.fromCharCode(bytes[i]);
                }
                const base64Audio = btoa(binary);
                
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({
                        type: 'audio_chunk',
                        audio: base64Audio,
                        timestamp: Date.now(),
                    }));
                }
            };
            
            // Store reference for cleanup (mocking MediaRecorder interface for compatibility)
            mediaRecorderRef.current = {
                stop: () => {
                    processor.disconnect();
                    source.disconnect();
                    if (stream) stream.getTracks().forEach(track => track.stop());
                },
                state: 'recording'
            };

        } catch (error) {
            console.error('Failed to initialize audio recording:', error);
            alert('Microphone access denied.');
        }
    }, [isRecording]);

    /**
     * Start interview: Initialize WebSocket, camera, and audio
     */
    const handleStartInterview = useCallback(() => {
        setIsRecording(true);

        // 1. Initialize WebSocket connection
        initializeWebSocket();

        // 2. Start camera (sends frames every 500ms)
        startCamera();

        // 3. Start audio recording (sends chunks every 2s)
        setTimeout(() => {
            startAudioCapture();
        }, 1000);

        // Notify backend interview started
        setTimeout(() => {
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({
                    type: 'interview_event',
                    event: 'interview_started',
                    timestamp: Date.now(),
                }));
            }
        }, 1500);
    }, [initializeWebSocket, startCamera, startAudioCapture]);

    /**
     * Stop interview and cleanup
     */
    /**
     * Stop interview and cleanup (Audio Only)
     */
    const handleStopInterview = useCallback(() => {
        setIsRecording(false);

        // Stop video frame capture (sending to backend), BUT keep camera preview alive
        if (videoRef.current && videoRef.current._frameInterval) {
            clearInterval(videoRef.current._frameInterval);
        }

        // DO NOT STOP VIDEO TRACKS - User wants camera always on
        // if (videoRef.current && videoRef.current.srcObject) { ... }

        // Stop audio recording
        if (mediaRecorderRef.current) {
            if (mediaRecorderRef.current._interval) clearInterval(mediaRecorderRef.current._interval);
            if (mediaRecorderRef.current.state && mediaRecorderRef.current.state !== 'inactive') {
                 mediaRecorderRef.current.stop();
            }
        }
        
        // Close AudioContext if active
        if (audioContextRef.current) {
            audioContextRef.current.close().catch(e => console.error(e));
            audioContextRef.current = null;
        }

        // Notify backend
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'interview_event',
                event: 'interview_ended',
                timestamp: Date.now(),
            }));

            // Optional: Close WS or keep it open for "Pause"? 
            // For now, let's keep it open so we can resume easily, or close if "End" is clicked.
            // But user said "Mic off", implying toggle.
            // If it's a "Mute" toggle, we shouldn't close WS. 
            // If it's "End Call", we close. 
            // Let's assume the button wraps "End" functionality for now based on previous code.
            // But to fix "Listening", we might need to NOT close it if it's just a pause.
            // Let's stick to the previous behavior of closing for "Stop", but we'll ensure Camera stays.
            setTimeout(() => {
                wsRef.current.close();
            }, 1000);
        }
    }, []);

    // ============ LIFECYCLE ============
    useEffect(() => {
        // Start camera immediately on mount for preview
        startCamera();

        return () => {
            // Cleanup on unmount
            if (videoRef.current && videoRef.current._frameInterval) {
                clearInterval(videoRef.current._frameInterval);
            }
            if (mediaRecorderRef.current && mediaRecorderRef.current._interval) {
                clearInterval(mediaRecorderRef.current._interval);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    // ============ RENDER ============
    return (
        <div className="interview-container">
            {/* Sidebar */}
            <div className="sidebar">
                <div className="logo-icon">V</div>
                <div className="nav-item active"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 10l5 5-5 5" /><path d="M4 4v7a4 4 0 0 0 4 4h12" /></svg></div>
                <div className="nav-item"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" /></svg></div>
            </div>

            {/* Main Content */}
            <div className="main-content">
                {/* Top Bar */}
                <div className="top-bar">
                    Voca AI
                </div>

                {/* Split Pane */}
                <div className="split-pane">

                    {/* Left: AI Pane */}
                    <div className="ai-pane">
                        <div className="ai-container">
                            <div className="ai-avatar-placeholder">
                                <div style={{ width: 80, height: 2, background: 'white', marginBottom: 5 }}></div>
                                <div style={{ width: 50, height: 2, background: 'white' }}></div>
                            </div>
                            <div className="listening-indicator">
                                <div className="bar" style={{height: `${10 + audioLevel}%`, transition: 'height 0.1s', animation: 'none'}}></div>
                                <div className="bar" style={{height: `${10 + audioLevel * 1.5}%`, transition: 'height 0.1s', animation: 'none'}}></div>
                                <div className="bar" style={{height: `${10 + audioLevel * 2}%`, transition: 'height 0.1s', animation: 'none'}}></div>
                                <div className="bar" style={{height: `${10 + audioLevel * 1.5}%`, transition: 'height 0.1s', animation: 'none'}}></div>
                                <div className="bar" style={{height: `${10 + audioLevel}%`, transition: 'height 0.1s', animation: 'none'}}></div>
                            </div>
                            <div style={{ marginTop: 20, color: '#888', fontSize: '0.9rem', textAlign: 'center', padding: '0 40px' }}>
                                {aiMessage}
                            </div>
                        </div>
                    </div>

                    {/* Right: User Pane */}
                    <div className="user-pane">
                        <video ref={videoRef} autoPlay playsInline muted className="camera-feed" />
                        <canvas ref={canvasRef} width={640} height={480} style={{ display: 'none' }} />

                        <div className="live-badge">
                            <div className="live-dot"></div> LIVE
                        </div>

                        {/* Transcript Overlay */}
                        <div className="transcript-overlay">
                            <div className="transcript-label">TRANSCRIPT</div>
                            <div className="current-transcript">
                                {transcript ? transcript : (isRecording ? "Listening..." : "Ready")}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Control Bar */}
                <div className="bottom-controls">
                    <div className="timer">0:00</div>

                    <div className="chat-input-wrapper">
                        <input
                            type="text"
                            className="chat-input"
                            placeholder="Type response..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleSendMessage();
                            }}
                        />
                    </div>

                    <button className={`mic-btn ${isRecording ? 'active' : ''}`} onClick={isRecording ? handleStopInterview : handleStartInterview}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                            <line x1="12" y1="19" x2="12" y2="23" />
                            <line x1="8" y1="23" x2="16" y2="23" />
                        </svg>
                    </button>

                    <button className="files-btn">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" /><polyline points="13 2 13 9 20 9" /></svg>
                        Files
                    </button>

                    <button className="end-btn" onClick={handleStopInterview}>
                        End
                    </button>
                </div>
            </div>
        </div>
    );
};

export default InterviewPage;
