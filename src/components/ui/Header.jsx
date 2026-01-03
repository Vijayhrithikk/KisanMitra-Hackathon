import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import { ShoppingCart, User, Menu, X, Home, Store, Leaf, LogOut, Droplets } from 'lucide-react';
import './Header.css';

const Header = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const auth = useAuth() || {};
    const cart = useCart() || {};

    const { user, isLoggedIn, logout } = auth;
    const cartCount = cart.cartCount || 0;
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navLinks = [
        { path: '/', label: 'Home', icon: Home },
        { path: '/market', label: 'Shop', icon: Store },
        { path: '/recommend', label: 'Advisory', icon: Leaf },
        { path: '/irrigation', label: 'Irrigation', icon: Droplets },
    ];

    const isActive = (path) => location.pathname === path;

    const handleLogout = () => {
        if (logout) logout();
        navigate('/');
        setMobileMenuOpen(false);
    };

    const closeMobileMenu = () => setMobileMenuOpen(false);

    return (
        <header className="header">
            <div className="header-container">
                {/* Logo */}
                <Link to="/" className="header-logo" onClick={closeMobileMenu}>
                    <span className="logo-icon">🌾</span>
                    <span className="logo-text">KisanMitra</span>
                </Link>

                {/* Mobile Nav Icons */}
                <div className="header-actions">
                    {/* Cart */}
                    <button className="icon-btn cart-btn" onClick={() => navigate('/cart')}>
                        <ShoppingCart size={22} />
                        {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
                    </button>

                    {/* Profile/Login */}
                    {isLoggedIn ? (
                        <button className="icon-btn profile-btn" onClick={() => navigate('/profile')}>
                            <div className="profile-avatar">{user?.name?.charAt(0) || '👤'}</div>
                        </button>
                    ) : (
                        <button className="icon-btn login-btn" onClick={() => navigate('/login')}>
                            <User size={22} />
                        </button>
                    )}

                    {/* Menu Toggle */}
                    <button className="icon-btn menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            <div className={`mobile-menu ${mobileMenuOpen ? 'open' : ''}`}>
                <nav className="mobile-nav">
                    {navLinks.map(({ path, label, icon: Icon }) => (
                        <Link
                            key={path}
                            to={path}
                            className={`mobile-nav-link ${isActive(path) ? 'active' : ''}`}
                            onClick={closeMobileMenu}
                        >
                            <Icon size={20} />
                            <span>{label}</span>
                        </Link>
                    ))}

                    {/* Additional Links */}
                    <div className="mobile-nav-divider" />
                    <Link to="/cart" className="mobile-nav-link" onClick={closeMobileMenu}>
                        <ShoppingCart size={20} />
                        <span>Cart {cartCount > 0 && `(${cartCount})`}</span>
                    </Link>

                    {isLoggedIn ? (
                        <>
                            <Link to="/profile" className="mobile-nav-link" onClick={closeMobileMenu}>
                                <User size={20} />
                                <span>My Profile</span>
                            </Link>
                            <button className="mobile-nav-link logout-btn" onClick={handleLogout}>
                                <LogOut size={20} />
                                <span>Logout</span>
                            </button>
                        </>
                    ) : (
                        <Link to="/login" className="mobile-nav-link" onClick={closeMobileMenu}>
                            <User size={20} />
                            <span>Login</span>
                        </Link>
                    )}
                </nav>
            </div>

            {/* Overlay */}
            {mobileMenuOpen && <div className="menu-overlay" onClick={closeMobileMenu} />}
        </header>
    );
};

export default Header;
