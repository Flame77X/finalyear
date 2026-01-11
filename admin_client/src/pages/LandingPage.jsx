import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#131313] font-sans text-white">
            <div className="text-center space-y-12">
                <div className="space-y-4">
                    <h1 className="text-6xl font-serif tracking-tight">Voca AI</h1>
                    <p className="text-[#CCCCCC]/50 text-xl font-light">Autonomous Technical Interview Platform</p>
                </div>

                <div className="flex gap-8 mt-12 justify-center">
                    {/* Candidate Card */}
                    <button
                        onClick={() => navigate('/interview')}
                        className="w-80 p-8 rounded-3xl bg-[#1a1a1a] border border-white/5 hover:bg-[#1a1a1a]/80 text-left transition-all"
                    >
                        <h3 className="text-2xl font-serif mb-2">Candidate</h3>
                        <p className="text-sm text-[#CCCCCC]/40 mb-6">Enter session ID to begin.</p>
                        <div className="text-[#00E5FF] text-sm font-medium">Start Session &rarr;</div>
                    </button>

                    {/* Admin Card */}
                    <button
                        onClick={() => navigate('/admin')}
                        className="w-80 p-8 rounded-3xl bg-[#1a1a1a] border border-white/5 hover:bg-[#1a1a1a]/80 text-left transition-all"
                    >
                        <h3 className="text-2xl font-serif mb-2">Admin</h3>
                        <p className="text-sm text-[#CCCCCC]/40 mb-6">Access system dashboard.</p>
                        <div className="text-[#FF4444] text-sm font-medium">Login &rarr;</div>
                    </button>
                </div>

                <p className="text-[#CCCCCC]/20 text-xs mt-12">System v2.4 • Secure Connection</p>
            </div>
        </div>
    );
};

export default LandingPage;
