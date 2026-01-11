```
import React from 'react';
import { Settings } from 'lucide-react';

const AdminSettings = () => {
    return (
        <div className="space-y-8 animate-in max-w-4xl">
            <header>
                <h2 className="text-3xl font-serif text-white">System Settings</h2>
                <p className="text-[#CCCCCC]/50">Configure AI personality and strictness.</p>
            </header>

            <div className="grid gap-6">
                <div className="bg-[#272727] p-8 rounded-2xl shadow-xl border border-white/5">
                    <h3 className="text-xl font-medium text-white mb-6 flex items-center gap-2">
                        <Settings size={20} className="text-[#00E5FF]" /> AI Persona Definition
                    </h3>
                    <div className="space-y-4">
                        <label className="text-sm text-[#CCCCCC]/60 uppercase tracking-widest block">System Prompt</label>
                        <textarea
                            className="w-full h-32 bg-[#131313] border border-white/10 rounded-xl p-4 text-[#CCCCCC] focus:outline-none focus:border-[#00E5FF] font-mono text-sm leading-relaxed"
                            defaultValue="You are Voca, a senior technical interviewer. Be professional, concise, and probing. Ask follow-up questions if the candidate's answer is vague."
                        />
                        <div className="flex justify-end">
                            <button className="px-6 py-2 bg-[#00E5FF] text-black font-medium rounded-lg hover:bg-[#00E5FF]/90 transition-colors text-sm">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminSettings;
```
