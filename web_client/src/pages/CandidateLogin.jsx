import React, { useState } from 'react';
import { Upload, ArrowRight, Check, FileText, User, Mail, BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CandidateLogin = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        branch: '',
        resume: null
    });
    const [isLoading, setIsLoading] = useState(false);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        if (file.type === "application/pdf") {
            setFormData({ ...formData, resume: file });
        } else {
            alert("Please upload a PDF file.");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        const data = new FormData();
        data.append('name', formData.name);
        data.append('email', formData.email);
        data.append('branch', formData.branch);
        if (formData.resume) {
            data.append('resume', formData.resume);
        }

        try {
            // Dynamic backend URL
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const backendUrl = `${protocol}//${host}:8000/register_candidate`;

            const response = await fetch(backendUrl, {
                method: 'POST',
                body: data
            });

            const result = await response.json();

            if (response.ok) {
                localStorage.setItem('candidate_id', result.candidate_id);
                localStorage.setItem('candidate_name', formData.name);
                navigate('/interview');
            } else {
                alert("Registration failed. Please try again.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Server error. Ensure backend is running.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0F0F0F] text-[#E0E0E0] font-sans flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#00E5FF]/5 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[#00E5FF]/5 rounded-full blur-[120px]" />
            </div>

            <div className="w-full max-w-md bg-[#1A1A1A] rounded-2xl border border-[#333] shadow-2xl relative z-10 p-8">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00E5FF] to-[#00AACC] bg-clip-text text-transparent mb-2">
                        AI Interviewer
                    </h1>
                    <p className="text-[#888] text-sm">Enter your details to begin your personalized session.</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-4">
                        {/* Name Input */}
                        <div className="relative group">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-[#555] group-focus-within:text-[#00E5FF] transition-colors" size={18} />
                            <input
                                type="text"
                                placeholder="Full Name"
                                required
                                className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-[#00E5FF] transition-all"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>

                        {/* Email Input */}
                        <div className="relative group">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-[#555] group-focus-within:text-[#00E5FF] transition-colors" size={18} />
                            <input
                                type="email"
                                placeholder="Email Address"
                                required
                                className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-[#00E5FF] transition-all"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>

                        {/* Branch Selection */}
                        <div className="relative group">
                            <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 text-[#555] group-focus-within:text-[#00E5FF] transition-colors" size={18} />
                            <select
                                required
                                className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-[#00E5FF] transition-all appearance-none text-[#E0E0E0]"
                                value={formData.branch}
                                onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                            >
                                <option value="" disabled>Select Branch</option>
                                <option value="CSE">Computer Science (CSE)</option>
                                <option value="AI">Artificial Intelligence (AI)</option>
                                <option value="ISE">Information Science (ISE)</option>
                                <option value="EC">Electronics (EC)</option>
                                <option value="EEE">Electrical (EEE)</option>
                                <option value="MECHANICAL">Mechanical</option>
                                <option value="CIVIL">Civil</option>
                            </select>
                            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                                <svg className="w-4 h-4 text-[#555]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                            </div>
                        </div>
                    </div>

                    {/* Resume Upload Area */}
                    <div
                        className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl transition-all duration-300 cursor-pointer relative
                    ${dragActive ? 'border-[#00E5FF] bg-[#00E5FF]/5' : 'border-[#333] hover:border-[#555] bg-[#0A0A0A]'}`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            accept=".pdf"
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            onChange={handleFileChange}
                        />

                        {formData.resume ? (
                            <div className="flex flex-col items-center text-[#00E5FF]">
                                <Check className="mb-2" size={24} />
                                <span className="text-sm font-medium truncate max-w-[200px]">{formData.resume.name}</span>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center text-[#666]">
                                <Upload className="mb-2" size={24} />
                                <span className="text-sm">Drag & Drop Resume (PDF)</span>
                                <span className="text-xs text-[#444] mt-1">or click to browse</span>
                            </div>
                        )}
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-[#00E5FF] hover:bg-[#00cce6] text-black font-bold py-3 rounded-lg transition-all duration-300 transform hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <span className="animate-pulse">Starting Session...</span>
                        ) : (
                            <>
                                Start Interview <ArrowRight size={18} />
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CandidateLogin;
