import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
    Package, BarChart3, Plus, Settings, LogOut,
    Menu, X, Home, CreditCard, Bell
} from 'lucide-react';
import './FarmerHeader.css';

const FarmerHeader = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const auth = useAuth() || {};
    const { user, logout } = auth;
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navLinks = [
        { path: '/farmer/dashboard', label: 'Dashboard', icon: BarChart3 },
        { path: '/market/create', label: 'New Listing', icon: Plus },
        { path: '/market/orders', label: 'Orders', icon: Package },
        { path: '/bank/verify', label: 'Bank Account', icon: CreditCard },
    ];

    const isActive = (path) => location.pathname === path;

    const handleLogout = () => {
        if (logout) logout();
        navigate('/login');
    };

    return (
        <>
            {/* Top Header */}
            <header className="farmer-header">
                <div className="farmer-header-left">
                    <button
                        className="sidebar-toggle"
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                    >
                        <Menu size={24} />
                    </button>
                    <Link to="/farmer/dashboard" className="farmer-logo">
                        <span className="logo-icon">🌾</span>
                        <div className="logo-text">
                            <span className="logo-title">KisanMitra</span>
                            <span className="logo-subtitle">Farmer Portal</span>
                        </div>
                    </Link>
                </div>

                <div className="farmer-header-right">
                    <button className="notification-btn">
                        <Bell size={20} />
                        <span className="notification-badge">3</span>
                    </button>
                    <div className="farmer-profile">
                        <div className="farmer-avatar">
                            {user?.name?.charAt(0) || '👨‍🌾'}
                        </div>
                        <div className="farmer-info">
                            <span className="farmer-name">{user?.name || 'Farmer'}</span>
                            <span className="farmer-role">Seller Account</span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Sidebar */}
            <aside className={`farmer-sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <Link to="/farmer/dashboard" className="sidebar-logo">
                        <span>🌾</span>
                        <span>KisanMitra</span>
                    </Link>
                    <button className="sidebar-close" onClick={() => setSidebarOpen(false)}>
                        <X size={24} />
                    </button>
                </div>

                <nav className="sidebar-nav">
                    {navLinks.map(({ path, label, icon: Icon }) => (
                        <Link
                            key={path}
                            to={path}
                            className={`sidebar-link ${isActive(path) ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <Icon size={20} />
                            <span>{label}</span>
                        </Link>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <Link to="/" className="sidebar-link">
                        <Home size={20} />
                        <span>Back to Store</span>
                    </Link>
                    <button className="sidebar-link logout" onClick={handleLogout}>
                        <LogOut size={20} />
                        <span>Logout</span>
                    </button>
                </div>
            </aside>

            {/* Overlay */}
            {sidebarOpen && (
                <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
            )}
        </>
    );
};

export default FarmerHeader;
