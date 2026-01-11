import React from 'react';
import { Video, Building2, GraduationCap, ArrowRight, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-[#050505] text-[#E0E0E0] font-sans flex flex-col items-center justify-center p-6 relative overflow-hidden">

            {/* 1. Grid Background */}
            <div className="absolute inset-0 z-0 opacity-10"
                style={{
                    backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)',
                    backgroundSize: '40px 40px'
                }}
            />

            {/* 2. Central Content */}
            <div className="relative z-10 flex flex-col items-center w-full max-w-6xl">

                {/* Logo Section */}
                <div className="mb-12 text-center flex flex-col items-center animate-fade-in-up">
                    <div className="w-20 h-20 bg-[#E0E0E0] rounded-full flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                        <span className="font-serif text-black font-bold text-4xl">V</span>
                    </div>
                    <h1 className="font-serif text-6xl tracking-tight mb-4 text-white">
                        Voca AI
                    </h1>
                    <p className="text-[#666] text-lg tracking-wide font-light uppercase">
                        Autonomous Technical Interview Platform
                    </p>
                </div>

                {/* Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">

                    {/* Candidate Card (Active) */}
                    <div
                        onClick={() => navigate('/candidate-login')}
                        className="group relative bg-[#0F0F0F] border border-[#222] hover:border-[#444] rounded-3xl p-8 cursor-pointer transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl hover:shadow-[#00E5FF]/10"
                    >
                        <div className="mb-6 w-12 h-12 rounded-xl bg-[#1A1A1A] flex items-center justify-center text-[#E0E0E0] group-hover:text-[#00E5FF] transition-colors">
                            <Video size={24} />
                        </div>

                        <h2 className="font-serif text-2xl mb-3 text-gray-100">Candidate</h2>
                        <p className="text-[#666] text-sm leading-relaxed mb-8 group-hover:text-[#888] transition-colors">
                            Register and begin your AI-driven technical assessment session immediately.
                        </p>

                        <div className="mt-auto flex items-center text-[#00E5FF] text-sm font-bold tracking-wide">
                            Start Session <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                        </div>
                    </div>

                    {/* College Card (Locked) */}
                    <div className="relative bg-[#0A0A0A] border border-[#1A1A1A] rounded-3xl p-8 opacity-60 cursor-not-allowed">
                        <div className="mb-6 w-12 h-12 rounded-xl bg-[#111] flex items-center justify-center text-[#444]">
                            <GraduationCap size={24} />
                        </div>

                        <div className="flex justify-between items-start mb-3">
                            <h2 className="font-serif text-2xl text-[#666]">College</h2>
                            <span className="bg-[#111] text-[#00E5FF] text-[10px] px-2 py-1 rounded border border-[#222]">SOON</span>
                        </div>

                        <p className="text-[#444] text-sm leading-relaxed mb-8">
                            Mass recruitment and placement assessment flows.
                        </p>

                        <div className="mt-auto flex items-center text-[#333] text-xs font-bold tracking-wide uppercase gap-2">
                            Access Locked <Lock size={12} />
                        </div>
                    </div>

                    {/* Enterprise Card (Locked) */}
                    <div className="relative bg-[#0A0A0A] border border-[#1A1A1A] rounded-3xl p-8 opacity-60 cursor-not-allowed">
                        <div className="mb-6 w-12 h-12 rounded-xl bg-[#111] flex items-center justify-center text-[#444]">
                            <Building2 size={24} />
                        </div>

                        <div className="flex justify-between items-start mb-3">
                            <h2 className="font-serif text-2xl text-[#666]">Enterprise</h2>
                            <span className="bg-[#111] text-[#00E5FF] text-[10px] px-2 py-1 rounded border border-[#222]">SOON</span>
                        </div>

                        <p className="text-[#444] text-sm leading-relaxed mb-8">
                            Custom pipelines for high-volume hiring teams.
                        </p>

                        <div className="mt-auto flex items-center text-[#333] text-xs font-bold tracking-wide uppercase gap-2">
                            Access Locked <Lock size={12} />
                        </div>
                    </div>

                </div>

                {/* Footer */}
                <div className="mt-16 text-[#333] text-[10px] tracking-widest uppercase">
                    System V2.4 • Secure Connection
                </div>

            </div>
        </div>
    );
};

export default LandingPage;
