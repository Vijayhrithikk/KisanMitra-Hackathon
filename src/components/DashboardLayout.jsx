import React from 'react';
import { Home, MessageSquare, Settings, LogOut, Menu } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import './DashboardLayout.css';

const DashboardLayout = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

    const menuItems = [
        { icon: Home, label: 'Overview', path: '/home' },
        { icon: MessageSquare, label: 'Kisan Chat', path: '/chat' },
        { icon: Settings, label: 'Settings', path: '/settings' },
    ];

    return (
        <div className="dashboard-container">
            {/* Sidebar */}
            <aside className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <div className="logo-icon">🌱</div>
                    {isSidebarOpen && <h2>KisanMitra</h2>}
                </div>

                <nav className="sidebar-nav">
                    {menuItems.map((item) => (
                        <button
                            key={item.path}
                            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                            onClick={() => navigate(item.path)}
                        >
                            <item.icon size={20} />
                            {isSidebarOpen && <span>{item.label}</span>}
                        </button>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <button className="nav-item logout">
                        <LogOut size={20} />
                        {isSidebarOpen && <span>Logout</span>}
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <header className="top-bar">
                    <button className="menu-toggle" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
                        <Menu size={24} />
                    </button>
                    <div className="user-profile">
                        <span className="user-name">Welcome, Farmer</span>
                        <div className="avatar">F</div>
                    </div>
                </header>

                <div className="content-area">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default DashboardLayout;
