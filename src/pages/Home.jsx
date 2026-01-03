import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import LanguageSelector from '../components/LanguageSelector';
import ModernTechniquesCarousel from '../components/ModernTechniquesCarousel';
import { marketService } from '../services/marketService';
import {
    Leaf, Store, Tractor, CloudSun, MapPin, Search,
    ChevronRight, Package, Plus, User, Settings, Droplets
} from 'lucide-react';
import './Home.css';

const Home = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { user, isLoggedIn } = useAuth() || {};
    const lang = i18n.language; // 'en', 'te', or 'hi'

    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);

    // Helper function for 3-language text
    const txt = (en, hi, te) => {
        if (lang === 'te') return te;
        if (lang === 'hi') return hi;
        return en;
    };

    // Localized strings
    const L = {
        greeting: txt('Namaste', 'नमस्ते', 'నమస్కారం'),
        welcome: txt('Welcome to KisanMitra', 'किसान मित्र में आपका स्वागत है', 'కిసాన్ మిత్ర లో స్వాగతం'),
        subtitle: txt('Your Farming Companion', 'आपका खेती साथी', 'మీ వ్యవసాయ సహాయకుడు'),
        cropAdvisory: txt('Crop Advisory', 'फसल सलाह', 'పంట సలహా'),
        cropAdvisoryDesc: txt('AI-powered crop recommendations', 'AI आधारित फसल सिफारिशें', 'AI ఆధారిత పంట సిఫారసులు'),
        marketplace: txt('Marketplace', 'मार्केटप्लेस', 'మార్కెట్‌ప్లేస్'),
        marketplaceDesc: txt('Sell your produce', 'अपनी फसल बेचें', 'మీ పంటలను అమ్మండి'),
        rentals: txt('Equipment Rental', 'उपकरण किराया', 'ట్రాక్టర్ అద్దె'),
        rentalsDesc: txt('Rent farming equipment', 'खेती उपकरण किराए पर लें', 'వ్యవసాయ పరికరాలు అద్దెకు'),
        techniques: txt('Modern Techniques', 'आधुनिक तकनीक', 'ఆధునిక పద్ధతులు'),
        weatherUpdate: txt('Weather', 'मौसम', 'వాతావరణం'),
        recentListings: txt('Recent Listings', 'नई लिस्टिंग', 'తాజా లిస్టింగ్‌లు'),
        viewAll: txt('View All', 'सभी देखें', 'అన్నీ చూడండి'),
        createListing: txt('New Listing', 'नई लिस्टिंग', 'కొత్త లిస్టింగ్'),
        myDashboard: txt('My Dashboard', 'मेरा डैशबोर्ड', 'నా డాష్‌బోర్డ్'),
        login: txt('Login', 'लॉगिन', 'లాగిన్'),
        search: txt('Search...', 'खोजें...', 'శోధించండి...'),
        perQuintal: txt('Quintal', 'क्विंटल', 'క్వింటాల్'),
        myCrops: txt('My Crops', 'मेरी फसलें', 'నా పంటలు'),
        myCropsDesc: txt('Daily monitoring & plan', 'दैनिक मॉनिटरिंग और प्लान', 'రోజువారీ మానిటరింగ్ & ప్లాన్'),
        irrigation: txt('Smart Irrigation', 'स्मार्ट सिंचाई', 'స్మార్ట్ నీటిపారుదల'),
        irrigationDesc: txt('IoT-based automation', 'IoT आधारित ऑटोमेशन', 'IoT ఆధారిత ఆటోమేషన్'),
        farmer: txt('Farmer', 'किसान', 'రైతు'),
        home: txt('Home', 'होम', 'హోమ్'),
        market: txt('Market', 'मार्केट', 'మార్కెట్'),
        advisory: txt('Advisory', 'सलाह', 'సలహా'),
        profile: txt('Profile', 'प्रोफ़ाइल', 'ప్రొఫైల్')
    };

    useEffect(() => {
        loadListings();
    }, []);

    const loadListings = async () => {
        try {
            const data = await marketService.getListings();
            setListings(data.slice(0, 4));
        } catch (error) {
            console.error('Error loading listings:', error);
        } finally {
            setLoading(false);
        }
    };

    const getLocationString = (loc) => {
        if (!loc) return 'India';
        if (typeof loc === 'string') return loc;
        if (typeof loc === 'object') return loc.district || loc.city || 'India';
        return 'India';
    };

    return (
        <div className="home-page">
            {/* Header */}
            <header className="app-header">
                <div className="header-left">
                    <span className="app-logo">🌾</span>
                    <div className="app-title">
                        <span className="title-main">KisanMitra</span>
                        <span className="title-sub">{L.subtitle}</span>
                    </div>
                </div>
                <div className="header-right">
                    <LanguageSelector />
                    {isLoggedIn ? (
                        <button className="profile-btn" onClick={() => navigate('/profile')}>
                            <User size={20} />
                        </button>
                    ) : (
                        <button className="login-btn-small" onClick={() => navigate('/login')}>
                            {L.login}
                        </button>
                    )}
                </div>
            </header>

            {/* Welcome Section */}
            <section className="welcome-section">
                <div className="welcome-content">
                    <h1>{L.greeting}, {user?.name || L.farmer}! 👋</h1>
                    <p>{L.welcome}</p>
                </div>
                <div className="search-bar">
                    <Search size={18} className="search-icon" />
                    <input type="text" placeholder={L.search} />
                </div>
            </section>

            {/* Quick Actions */}
            <section className="quick-actions">
                <div className="action-card primary" onClick={() => navigate('/my-crops')}>
                    <div className="action-icon" style={{ background: '#DCFCE7' }}>
                        <span style={{ fontSize: '24px' }}>🌾</span>
                    </div>
                    <div className="action-content">
                        <h3>{L.myCrops}</h3>
                        <p>{L.myCropsDesc}</p>
                    </div>
                    <ChevronRight size={20} className="action-arrow" />
                </div>

                <div className="action-card" onClick={() => navigate('/recommend')}>
                    <div className="action-icon" style={{ background: '#E8F5E9' }}>
                        <Leaf size={24} color="#4CAF50" />
                    </div>
                    <div className="action-content">
                        <h3>{L.cropAdvisory}</h3>
                        <p>{L.cropAdvisoryDesc}</p>
                    </div>
                    <ChevronRight size={20} className="action-arrow" />
                </div>

                <div className="action-card" onClick={() => navigate('/market')}>
                    <div className="action-icon" style={{ background: '#FFF3E0' }}>
                        <Store size={24} color="#FF9800" />
                    </div>
                    <div className="action-content">
                        <h3>{L.marketplace}</h3>
                        <p>{L.marketplaceDesc}</p>
                    </div>
                    <ChevronRight size={20} className="action-arrow" />
                </div>

                <div className="action-card" onClick={() => navigate('/rentals')}>
                    <div className="action-icon" style={{ background: '#E3F2FD' }}>
                        <Tractor size={24} color="#2196F3" />
                    </div>
                    <div className="action-content">
                        <h3>{L.rentals}</h3>
                        <p>{L.rentalsDesc}</p>
                    </div>
                    <ChevronRight size={20} className="action-arrow" />
                </div>

                <div className="action-card" onClick={() => navigate('/irrigation')}>
                    <div className="action-icon" style={{ background: '#E0F7FA' }}>
                        <Droplets size={24} color="#00BCD4" />
                    </div>
                    <div className="action-content">
                        <h3>{L.irrigation}</h3>
                        <p>{L.irrigationDesc}</p>
                    </div>
                    <ChevronRight size={20} className="action-arrow" />
                </div>
            </section>

            {/* Techniques Carousel */}
            <ModernTechniquesCarousel />

            {/* Dashboard Access */}
            {isLoggedIn && (
                <section className="dashboard-access">
                    <button className="dashboard-btn" onClick={() => navigate('/farmer/dashboard')}>
                        <Package size={20} />
                        {L.myDashboard}
                        <ChevronRight size={18} />
                    </button>
                </section>
            )}

            {/* Bottom Navigation */}
            <nav className="bottom-nav">
                <button className="nav-item active" onClick={() => navigate('/')}>
                    <span className="nav-icon">🏠</span>
                    <span>{L.home}</span>
                </button>
                <button className="nav-item" onClick={() => navigate('/market')}>
                    <span className="nav-icon">🛒</span>
                    <span>{L.market}</span>
                </button>
                <button className="nav-item" onClick={() => navigate('/recommend')}>
                    <span className="nav-icon">🌱</span>
                    <span>{L.advisory}</span>
                </button>
                <button className="nav-item" onClick={() => navigate('/techniques')}>
                    <span className="nav-icon">📚</span>
                    <span>{L.techniques}</span>
                </button>
                <button className="nav-item" onClick={() => navigate(isLoggedIn ? '/profile' : '/login')}>
                    <span className="nav-icon">👤</span>
                    <span>{L.profile}</span>
                </button>
            </nav>
        </div>
    );
};

export default Home;
