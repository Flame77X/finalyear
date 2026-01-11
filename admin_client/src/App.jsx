import React, { useState, useEffect } from 'react';
import {
    LayoutDashboard, Settings, Activity, User, Play, MoreHorizontal,
    Clock, BarChart2, Search, LogOut, CheckCircle, AlertCircle, Shield, Lock, ArrowRight
} from 'lucide-react';

/* --- GLOBAL STYLES --- */
const GlobalStyles = () => (
    <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@400;600&display=swap');
    
    body {
      background-color: #131313;
      color: #CCCCCC;
      font-family: 'Inter', sans-serif;
    }
    
    /* Typography */
    .font-serif { font-family: 'Playfair Display', serif; }
    .font-sans { font-family: 'Inter', sans-serif; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #131313; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }

    /* Utilities */
    .glass-panel {
      background: rgba(39, 39, 39, 0.4);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .animate-in { animation: fadeIn 0.5s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
  `}</style>
);



/* -------------------------------------------------------------------------- */
/* 1. ADMIN LANDING (LOGIN)                                                  */
/* -------------------------------------------------------------------------- */

const AdminLanding = ({ onNavigate }) => {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-[#131313]">
            {/* Background Decor */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#FF4444]/5 rounded-full blur-[120px]" />

            <div className="relative z-10 text-center space-y-12 animate-in">
                <div className="space-y-4">
                    <div className="w-20 h-20 bg-[#CCCCCC] rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(255,255,255,0.1)]">
                        <span className="font-serif text-black font-bold text-4xl">V</span>
                    </div>
                    <h1 className="text-6xl font-serif text-white tracking-tight">Voca Admin</h1>
                    <p className="text-[#CCCCCC]/50 text-xl font-light tracking-wide">System Control Panel</p>
                </div>

                <div className="flex justify-center mt-12">
                    {/* Admin Card */}
                    <button
                        onClick={() => onNavigate('admin-dashboard')}
                        className="group relative w-80 p-8 rounded-3xl bg-[#1a1a1a] border border-white/5 hover:border-[#FF4444]/30 hover:bg-[#1a1a1a]/80 transition-all duration-300 text-left"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-[#FF4444]/0 to-[#FF4444]/5 opacity-0 group-hover:opacity-100 rounded-3xl transition-opacity" />
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-2xl bg-[#131313] border border-white/10 flex items-center justify-center mb-6 text-[#CCCCCC] group-hover:text-[#FF4444] group-hover:scale-110 transition-all">
                                <Shield size={24} />
                            </div>
                            <h3 className="text-2xl font-serif text-white mb-2">Admin Console</h3>
                            <p className="text-sm text-[#CCCCCC]/40 mb-6">Restricted access for system administrators.</p>
                            <div className="flex items-center text-[#CCCCCC] group-hover:text-[#FF4444] text-sm font-medium gap-2 group-hover:gap-4 transition-all">
                                Login <Lock size={16} />
                            </div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    );
};

/* -------------------------------------------------------------------------- */
/* 2. ADMIN INTERFACE                                                         */
/* -------------------------------------------------------------------------- */

const AdminSidebar = ({ activePage, onNavigate }) => {
    const menu = [
        { id: 'admin-dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'admin-sessions', label: 'Interview Logs', icon: Activity },
        { id: 'admin-settings', label: 'System Settings', icon: Settings },
    ];

    return (
        <div className="w-64 bg-[#272727] border-r border-[#FFFFFF]/5 flex flex-col h-full flex-shrink-0">
            <div className="p-8 border-b border-[#FFFFFF]/5 flex items-center gap-3 cursor-pointer" onClick={() => onNavigate('landing')}>
                <div className="w-8 h-8 bg-[#CCCCCC] rounded-full flex items-center justify-center text-black font-serif font-bold text-lg">V</div>
                <div>
                    <h2 className="font-serif text-xl text-white">Voca Admin</h2>
                    <p className="text-[10px] text-[#CCCCCC]/50 uppercase tracking-widest">v2.4 Control</p>
                </div>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {menu.map(item => (
                    <button
                        key={item.id}
                        onClick={() => onNavigate(item.id)}
                        className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all text-sm font-medium ${activePage === item.id
                            ? 'bg-[#131313] text-[#00E5FF] border-r-2 border-[#00E5FF]'
                            : 'text-[#CCCCCC]/60 hover:bg-[#131313]/50 hover:text-white'
                            }`}
                    >
                        <item.icon size={18} />
                        {item.label}
                    </button>
                ))}
            </nav>

            <div className="p-4 border-t border-[#FFFFFF]/5">
                <button
                    onClick={() => onNavigate('landing')}
                    className="w-full flex items-center gap-3 px-4 py-3 text-[#CCCCCC]/60 hover:text-[#FF4444] transition-colors text-sm"
                >
                    <LogOut size={18} />
                    Logout
                </button>
            </div>
        </div>
    );
};

/* --- HELPER COMPONENTS --- */
const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-4">
        <div className="h-32 bg-[#272727] rounded-2xl w-full"></div>
        <div className="h-64 bg-[#272727] rounded-2xl w-full"></div>
    </div>
);

const ErrorBanner = ({ message, onRetry }) => (
    <div className="bg-[#FF4444]/10 border border-[#FF4444]/20 rounded-xl p-4 flex items-center gap-3 text-[#FF4444] animate-in">
        <AlertCircle size={20} />
        <div className="flex-1 text-sm font-medium">{message}</div>
        {onRetry && <button onClick={onRetry} className="underline hover:text-white text-xs">Retry</button>}
    </div>
);

const DashboardPage = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStats = async (isSilent = false) => {
        if (!isSilent) setLoading(true);
        try {
            setError(null);
            const res = await fetch('http://localhost:8000/admin/stats');
            if (!res.ok) throw new Error("Failed to connect to server");
            const data = await res.json();
            setStats(data);
        } catch (err) {
            console.error("Stats fetch error:", err);
            setError("Could not load system metrics. Backend might be offline.");
        } finally {
            if (!isSilent) setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        // Poll every 10 seconds for dashboard stats
        const interval = setInterval(() => fetchStats(true), 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading && !stats) return <LoadingSkeleton />;
    if (error && !stats) return <ErrorBanner message={error} onRetry={() => fetchStats()} />;

    return (
        <div className="space-y-8 animate-in">
            <header>
                <h2 className="text-3xl font-serif text-white">System Overview</h2>
                <p className="text-[#CCCCCC]/50">Real-time metrics and health status.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    { label: "Total Interactions", val: stats?.total_interviews || 0, icon: User, color: "text-[#00E5FF]", bg: "bg-[#00E5FF]/10" },
                    { label: "Avg. Score", val: `${stats?.avg_score || 0}`, icon: BarChart2, color: "text-emerald-400", bg: "bg-emerald-500/10" },
                    { label: "System Health", val: stats?.health_status || "Unknown", icon: Activity, color: "text-purple-400", bg: "bg-purple-500/10" },
                    { label: "Active Nodes", val: "3", icon: Clock, color: "text-amber-400", bg: "bg-amber-500/10" },
                ].map((stat, i) => (
                    <div key={i} className="bg-[#1a1a1a] p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-all">
                        <div className="flex justify-between items-start mb-4">
                            <div className={`p-3 rounded-xl ${stat.bg} ${stat.color}`}>
                                <stat.icon size={20} />
                            </div>
                            <MoreHorizontal size={16} className="text-[#CCCCCC]/20 cursor-pointer" />
                        </div>
                        <h3 className="text-3xl font-serif text-white mb-1">{stat.val}</h3>
                        <p className="text-xs uppercase tracking-wider text-[#CCCCCC]/40 font-medium">{stat.label}</p>
                    </div>
                ))}
            </div>

            <div className="bg-[#1a1a1a] rounded-2xl border border-white/5 p-8 h-80 flex items-center justify-center relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-t from-[#131313] to-transparent opacity-50" />
                <div className="text-center relative z-10">
                    <BarChart2 size={48} className="text-[#CCCCCC]/10 mx-auto mb-4 group-hover:text-[#00E5FF]/20 transition-colors" />
                    <p className="text-[#CCCCCC]/40">Analytics Visualization</p>
                    <p className="text-xs text-[#CCCCCC]/20 mt-1">Real-time data stream active</p>
                </div>
            </div>
        </div>
    );
};

const SessionsPage = () => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchSessions = async (isSilent = false) => {
        if (!isSilent) setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/admin/sessions');
            if (!res.ok) throw new Error("Failed to fetch sessions");
            const data = await res.json();
            setSessions(data);
            if (!isSilent) setError(null); // Clear error on success
        } catch (err) {
            console.error("Sessions fetch error:", err);
            // Only show error banner if we have no data
            if (sessions.length === 0) setError("Connection lost. Retrying...");
        } finally {
            if (!isSilent) setLoading(false);
        }
    };

    useEffect(() => {
        fetchSessions();
        const interval = setInterval(() => fetchSessions(true), 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading && sessions.length === 0) return <LoadingSkeleton />;

    return (
        <div className="space-y-8 animate-in">
            <header className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-serif text-white">Interview Logs</h2>
                    <p className="text-[#CCCCCC]/50">History of all candidate interactions.</p>
                </div>
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#CCCCCC]/40" size={16} />
                    <input type="text" placeholder="Search logs..." className="bg-[#1a1a1a] border border-white/10 rounded-full pl-10 pr-4 py-2 text-sm text-[#CCCCCC] focus:outline-none focus:border-[#00E5FF]/50 w-64" />
                </div>
            </header>

            {error && <ErrorBanner message={error} onRetry={() => fetchSessions()} />}

            <div className="bg-[#1a1a1a] rounded-2xl border border-white/5 overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-[#272727]/50 text-[#CCCCCC]/40 text-xs uppercase tracking-widest">
                        <tr>
                            <th className="p-4 font-medium">Session ID</th>
                            <th className="p-4 font-medium">Date</th>
                            <th className="p-4 font-medium">Transcript Snippet</th>
                            <th className="p-4 font-medium">Score</th>
                            <th className="p-4 font-medium text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {sessions.map((sess) => {
                            const score = sess.interview_score?.grand_total || 0;
                            return (
                                <tr key={sess.session_id} className="hover:bg-white/5 transition-colors group">
                                    <td className="p-4">
                                        <div className="font-medium text-white font-mono text-xs">{sess.session_id.slice(0, 8)}...</div>
                                        <div className="text-xs text-[#CCCCCC]/40">Guest User</div>
                                    </td>
                                    <td className="p-4 text-sm text-[#CCCCCC]/60">{sess.date}</td>
                                    <td className="p-4 text-sm text-[#CCCCCC]/60 italic">"{sess.transcript ? sess.transcript.slice(0, 30) : '...'}..."</td>
                                    <td className="p-4">
                                        <span className={`font-serif text-lg ${score >= 80 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-[#FF4444]'}`}>
                                            {score.toFixed(1)}
                                        </span>
                                    </td>
                                    <td className="p-4 text-right">
                                        <button className="p-2 rounded-full hover:bg-[#00E5FF]/10 hover:text-[#00E5FF] text-[#CCCCCC]/40 transition-colors" title="View Details">
                                            <Play size={16} fill="currentColor" />
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                        {sessions.length === 0 && !loading && (
                            <tr><td colSpan="5" className="p-8 text-center text-[#CCCCCC]/30 ">No sessions recorded yet. API is waiting.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const SettingsPage = () => {
    const [systemPrompt, setSystemPrompt] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [status, setStatus] = useState(null);

    useEffect(() => {
        fetch('http://localhost:8000/admin/settings')
            .then(res => res.json())
            .then(data => {
                setSystemPrompt(data.system_prompt || "");
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load settings:", err);
                setStatus({ type: 'error', msg: "Failed to load current settings." });
                setLoading(false);
            });
    }, []);

    const handleSave = async () => {
        setSaving(true);
        setStatus(null);
        try {
            const res = await fetch('http://localhost:8000/admin/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ system_prompt: systemPrompt })
            });
            if (!res.ok) throw new Error("Save failed");
            setStatus({ type: 'success', msg: "Settings saved successfully." });
        } catch (err) {
            setStatus({ type: 'error', msg: "Failed to save settings. Server might be offline." });
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <LoadingSkeleton />;

    return (
        <div className="space-y-8 animate-in max-w-4xl">
            <header>
                <h2 className="text-3xl font-serif text-white">System Settings</h2>
                <p className="text-[#CCCCCC]/50">Configure AI personality and strictness.</p>
            </header>

            {status && (
                <div className={`p-4 rounded-xl border flex items-center gap-2 ${status.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                    {status.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                    {status.msg}
                </div>
            )}

            <div className="grid gap-6">
                <div className="bg-[#272727] p-8 rounded-2xl shadow-xl border border-white/5">
                    <h3 className="text-xl font-medium text-white mb-6 flex items-center gap-2">
                        <Settings size={20} className="text-[#00E5FF]" /> AI Persona Definition
                    </h3>
                    <div className="space-y-4">
                        <label className="text-sm text-[#CCCCCC]/60 uppercase tracking-widest block">System Prompt</label>
                        <textarea
                            className="w-full h-32 bg-[#131313] border border-white/10 rounded-xl p-4 text-[#CCCCCC] focus:outline-none focus:border-[#00E5FF] font-mono text-sm leading-relaxed"
                            value={systemPrompt}
                            onChange={(e) => setSystemPrompt(e.target.value)}
                            placeholder="Loading system prompt..."
                        />
                        <div className="flex justify-end">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className={`px-6 py-2 bg-[#00E5FF] text-black font-medium rounded-lg hover:bg-[#00E5FF]/90 transition-colors text-sm flex items-center gap-2 ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {saving ? "Saving..." : "Save Changes"}
                                {!saving && <ArrowRight size={16} />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const AdminLayout = ({ activePage, onNavigate }) => (
    <div className="flex h-screen bg-[#131313] overflow-hidden">
        <AdminSidebar activePage={activePage} onNavigate={onNavigate} />
        <main className="flex-1 overflow-y-auto p-12 bg-[#131313]">
            {activePage === 'admin-dashboard' && <DashboardPage />}
            {activePage === 'admin-sessions' && <SessionsPage />}
            {activePage === 'admin-settings' && <SettingsPage />}
        </main>
    </div>
);

/* -------------------------------------------------------------------------- */
/* ROOT COMPONENT                              */
/* -------------------------------------------------------------------------- */

const App = () => {
    const [currentView, setCurrentView] = useState('landing'); // Default to Gateway

    return (
        <div className="min-h-screen bg-[#131313] text-[#CCCCCC] font-sans selection:bg-[#00E5FF] selection:text-black">
            <GlobalStyles />

            {currentView === 'landing' && <AdminLanding onNavigate={setCurrentView} />}

            {currentView.startsWith('admin') && (
                <AdminLayout activePage={currentView} onNavigate={setCurrentView} />
            )}
        </div>
    );
};

export default App;
