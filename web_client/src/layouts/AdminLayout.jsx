import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Activity, Settings, LogOut } from 'lucide-react';

const AdminSidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const menu = [
        { id: '/admin', label: 'Dashboard', icon: LayoutDashboard },
        { id: '/admin/sessions', label: 'Interview Logs', icon: Activity },
        { id: '/admin/settings', label: 'System Settings', icon: Settings },
    ];

    return (
        <div className="w-64 bg-[#272727] border-r border-[#FFFFFF]/5 flex flex-col h-full flex-shrink-0">
            <div
                className="p-8 border-b border-[#FFFFFF]/5 flex items-center gap-3 cursor-pointer"
                onClick={() => navigate('/')}
            >
                <div className="w-8 h-8 bg-[#CCCCCC] rounded-full flex items-center justify-center text-black font-serif font-bold text-lg">V</div>
                <div>
                    <h2 className="font-serif text-xl text-white">Voca Admin</h2>
                    <p className="text-[10px] text-[#CCCCCC]/50 uppercase tracking-widest">v2.4 Control</p>
                </div>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {menu.map(item => {
                    const isActive = location.pathname === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => navigate(item.id)}
                            className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all text-sm font-medium ${isActive
                                    ? 'bg-[#131313] text-[#00E5FF] border-r-2 border-[#00E5FF]'
                                    : 'text-[#CCCCCC]/60 hover:bg-[#131313]/50 hover:text-white'
                                }`}
                        >
                            <item.icon size={18} />
                            {item.label}
                        </button>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-[#FFFFFF]/5">
                <button
                    onClick={() => navigate('/')}
                    className="w-full flex items-center gap-3 px-4 py-3 text-[#CCCCCC]/60 hover:text-[#FF4444] transition-colors text-sm"
                >
                    <LogOut size={18} />
                    Logout
                </button>
            </div>
        </div>
    );
};

const AdminLayout = () => {
    return (
        <div className="flex h-screen bg-[#131313] overflow-hidden font-sans text-[#CCCCCC]">
            <AdminSidebar />
            <main className="flex-1 overflow-y-auto p-12 bg-[#131313]">
                <Outlet />
            </main>
        </div>
    );
};

export default AdminLayout;
