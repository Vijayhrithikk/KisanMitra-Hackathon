import React from 'react';
import { Link } from 'react-router-dom';
import { Phone, Mail, MapPin, Facebook, Twitter, Instagram } from 'lucide-react';
import './Footer.css';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-container">
                {/* Brand */}
                <div className="footer-brand">
                    <div className="footer-logo">
                        <span className="logo-icon">🌾</span>
                        <span className="logo-text">KisanMitra</span>
                    </div>
                    <p className="footer-tagline">
                        Empowering farmers with AI-driven insights and direct market access.
                    </p>
                    <div className="footer-social">
                        <a href="#" className="social-link"><Facebook size={20} /></a>
                        <a href="#" className="social-link"><Twitter size={20} /></a>
                        <a href="#" className="social-link"><Instagram size={20} /></a>
                    </div>
                </div>

                {/* Quick Links */}
                <div className="footer-links">
                    <h4>Quick Links</h4>
                    <Link to="/">Home</Link>
                    <Link to="/market">Marketplace</Link>
                    <Link to="/recommend">Crop Advisory</Link>
                    <Link to="/techniques">Farming Techniques</Link>
                </div>

                {/* For Farmers */}
                <div className="footer-links">
                    <h4>For Farmers</h4>
                    <Link to="/farmer/register">Register as Farmer</Link>
                    <Link to="/farmer/dashboard">Seller Dashboard</Link>
                    <Link to="/market/create">List Your Crop</Link>
                    <Link to="/farmer/orders">Order Management</Link>
                </div>

                {/* Contact */}
                <div className="footer-contact">
                    <h4>Contact Us</h4>
                    <div className="contact-item">
                        <Phone size={16} />
                        <span>1800-XXX-XXXX</span>
                    </div>
                    <div className="contact-item">
                        <Mail size={16} />
                        <span>support@kisanmitra.in</span>
                    </div>
                    <div className="contact-item">
                        <MapPin size={16} />
                        <span>Hyderabad, Telangana</span>
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="footer-bottom">
                <p>© 2024 KisanMitra. All rights reserved.</p>
                <div className="footer-bottom-links">
                    <a href="#">Privacy Policy</a>
                    <a href="#">Terms of Service</a>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
