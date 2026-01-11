import React, { useEffect, useState } from 'react';
import { Search, Play, CheckCircle, AlertCircle } from 'lucide-react';

const AdminSessions = () => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const res = await fetch('http://localhost:8000/admin/sessions');
                const data = await res.json();
                setSessions(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchSessions();
    }, []);

    const playAudio = (filename) => {
        if (!filename) return;
        const audio = new Audio(`http://localhost:8000/audio/${filename}`);
        audio.play();
    };

    if (loading) return <div className="text-[#CCCCCC]/40">Loading interview logs...</div>;

    return (
        <div className="space-y-8 animate-in">
            <header className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-serif text-white">Interview Logs</h2>
                    <p className="text-[#CCCCCC]/50">History of all candidate sessions.</p>
                </div>
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#CCCCCC]/40" size={16} />
                    <input
                        type="text"
                        placeholder="Search candidate..."
                        className="bg-[#1a1a1a] border border-white/10 rounded-full pl-10 pr-4 py-2 text-sm text-[#CCCCCC] focus:outline-none focus:border-[#00E5FF]/50 w-64"
                    />
                </div>
            </header>

            <div className="bg-[#1a1a1a] rounded-2xl border border-white/5 overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-[#272727]/50 text-[#CCCCCC]/40 text-xs uppercase tracking-widest">
                        <tr>
                            <th className="p-4 font-medium">Session ID</th>
                            <th className="p-4 font-medium">Date</th>
                            <th className="p-4 font-medium">Last Response</th>
                            <th className="p-4 font-medium">Score</th>
                            <th className="p-4 font-medium">Status</th>
                            <th className="p-4 font-medium text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {sessions.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="p-8 text-center text-[#CCCCCC]/40">No sessions recorded yet.</td>
                            </tr>
                        ) : (
                            sessions.map((sess, idx) => {
                                const score = sess.interview_score?.grand_total || 0;
                                return (
                                    <tr key={idx} className="hover:bg-white/5 transition-colors group">
                                        <td className="p-4">
                                            <div className="font-medium text-white">{sess.session_id ? sess.session_id.slice(0, 8) : "N/A"}</div>
                                            <div className="text-xs text-[#CCCCCC]/40">V2.4 Architecture</div>
                                        </td>
                                        <td className="p-4 text-sm text-[#CCCCCC]/60">{sess.date || "N/A"}</td>
                                        <td className="p-4 text-sm text-[#CCCCCC]/60 max-w-xs truncate">{sess.transcript || "-"}</td>
                                        <td className="p-4">
                                            <span className={`font-serif text-lg ${score >= 80 ? 'text-emerald-400' : score >= 70 ? 'text-amber-400' : 'text-[#FF4444]'}`}>
                                                {score.toFixed(0)}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {score < 50 ? (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-[#FF4444]/10 text-[#FF4444] text-xs font-bold uppercase"><AlertCircle size={12} /> Flagged</span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-[#CCCCCC]/10 text-[#CCCCCC] text-xs font-bold uppercase"><CheckCircle size={12} /> Done</span>
                                            )}
                                        </td>
                                        <td className="p-4 text-right">
                                            <button
                                                onClick={() => playAudio(sess.audio_filename)}
                                                className="p-2 rounded-full hover:bg-[#00E5FF]/10 hover:text-[#00E5FF] text-[#CCCCCC]/40 transition-colors"
                                                title="Play Response"
                                            >
                                                <Play size={16} fill="currentColor" />
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminSessions;
