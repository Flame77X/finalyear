import React, { useEffect, useState } from 'react';
import { User, Activity, BarChart2, Clock, MoreHorizontal } from 'lucide-react';

const AdminDashboard = () => {
    const [stats, setStats] = useState({
        total_interviews: 0,
        avg_score: 0,
        health_status: 'Checking...'
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch('http://localhost:8000/admin/stats');
                const data = await res.json();
                setStats(data);
            } catch (err) {
                console.error("Failed to fetch stats", err);
                setStats(prev => ({ ...prev, health_status: 'Offline' }));
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) return <div className="text-[#CCCCCC]/40">Loading system metrics...</div>;

    const statCards = [
        {
            label: "Total Candidates",
            val: stats.total_interviews.toString(),
            icon: User,
            color: "text-[#00E5FF]",
            bg: "bg-[#00E5FF]/10"
        },
        {
            label: "Avg. Score",
            val: `${stats.avg_score}%`,
            icon: BarChart2,
            color: "text-emerald-400",
            bg: "bg-emerald-500/10"
        },
        {
            label: "System Health",
            val: stats.health_status,
            icon: Activity,
            color: stats.health_status === 'Active' ? "text-purple-400" : "text-red-400",
            bg: stats.health_status === 'Active' ? "bg-purple-500/10" : "bg-red-500/10"
        },
        {
            label: "Uptime",
            val: "99.9%",
            icon: Clock,
            color: "text-amber-400",
            bg: "bg-amber-500/10"
        },
    ];

    return (
        <div className="space-y-8 animate-in">
            <header>
                <h2 className="text-3xl font-serif text-white">System Overview</h2>
                <p className="text-[#CCCCCC]/50">Real-time metrics and health status.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, i) => (
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
                    <p className="text-[#CCCCCC]/40">Analytics Visualization Placeholder</p>
                    <p className="text-xs text-[#CCCCCC]/20 mt-1">Chart.js / Recharts Implementation</p>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
