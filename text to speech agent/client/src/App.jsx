import { useState, useRef } from 'react'

function App() {
    const [text, setText] = useState('Hello! This is the React frontend for your AI Agent.')
    const [loading, setLoading] = useState(false)
    const [audioUrl, setAudioUrl] = useState(null)
    const audioRef = useRef(null)

    const handleSpeak = async () => {
        if (!text) return;
        setLoading(true);
        setAudioUrl(null);

        try {
            const response = await fetch('http://localhost:8000/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            if (!response.ok) {
                throw new Error('Speech generation failed');
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);

            // Auto-play
            setTimeout(() => {
                if (audioRef.current) {
                    audioRef.current.volume = 0.5;
                    audioRef.current.play().catch(e => console.error("Playback failed:", e));
                }
            }, 100);

        } catch (error) {
            console.error(error);
            alert('Error extracting audio');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={styles.title}>🎙️ Piper TTS Agent</h1>
                <p style={styles.subtitle}>Local Neural Text-to-Speech</p>

                <textarea
                    style={styles.textarea}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Type something..."
                />

                <div style={styles.controls}>
                    <button
                        style={{ ...styles.button, opacity: loading ? 0.7 : 1 }}
                        onClick={handleSpeak}
                        disabled={loading}
                    >
                        {loading ? 'Synthesizing...' : 'Speak Now'}
                    </button>
                </div>

                {audioUrl && (
                    <div style={styles.playerContainer}>
                        <audio ref={audioRef} controls src={audioUrl} style={styles.audio} />
                        <div style={styles.status}>Ready to play</div>
                    </div>
                )}
            </div>
        </div>
    )
}

const styles = {
    container: {
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#0f0f13',
        color: '#fff',
        fontFamily: '"Inter", sans-serif',
    },
    card: {
        width: '100%',
        maxWidth: '500px',
        backgroundColor: '#1c1c21',
        padding: '2rem',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        border: '1px solid #333',
        textAlign: 'center',
    },
    title: {
        margin: 0,
        fontSize: '2rem',
        background: 'linear-gradient(90deg, #bb86fc, #9b59b6)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
    },
    subtitle: {
        color: '#888',
        marginBottom: '2rem',
    },
    textarea: {
        width: '90%',
        height: '120px',
        backgroundColor: '#2b2b30',
        border: '1px solid #444',
        borderRadius: '8px',
        padding: '1rem',
        color: '#eee',
        fontSize: '1rem',
        resize: 'none',
        marginBottom: '1.5rem',
        outline: 'none',
    },
    button: {
        backgroundColor: '#bb86fc',
        color: '#000',
        border: 'none',
        padding: '12px 32px',
        fontSize: '1rem',
        fontWeight: 'bold',
        borderRadius: '50px',
        cursor: 'pointer',
        transition: 'transform 0.2s',
    },
    playerContainer: {
        marginTop: '2rem',
        animation: 'fadeIn 0.5s ease',
    },
    audio: {
        width: '100%',
        outline: 'none',
    },
    status: {
        marginTop: '0.5rem',
        fontSize: '0.8rem',
        color: '#4caf50',
    },
}

export default App
