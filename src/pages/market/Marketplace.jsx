import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import { marketService } from '../../services/marketService';
import { ArrowLeft, Search, Filter, MapPin, Plus, X, ShoppingCart } from 'lucide-react';
import './Marketplace.css';

const Marketplace = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { addToCart, cartCount } = useCart() || { cartCount: 0 };
    const { guestMode, isLoggedIn } = useAuth() || { guestMode: false, isLoggedIn: false };
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');

    // Localization
    const L = {
        title: lang === 'te' ? 'మార్కెట్‌ప్లేస్' : 'Marketplace',
        search: lang === 'te' ? 'పంటలు వెతకండి...' : 'Search crops...',
        all: lang === 'te' ? 'అన్నీ' : 'All',
        vegetables: lang === 'te' ? 'కూరగాయలు' : 'Vegetables',
        fruits: lang === 'te' ? 'పండ్లు' : 'Fruits',
        grains: lang === 'te' ? 'ధాన్యాలు' : 'Grains',
        pulses: lang === 'te' ? 'పప్పులు' : 'Pulses',
        noListings: lang === 'te' ? 'లిస్టింగ్‌లు లేవు' : 'No listings found',
        perQuintal: lang === 'te' ? 'క్వింటాల్' : 'Quintal',
        addListing: lang === 'te' ? 'కొత్త లిస్టింగ్' : 'Add Listing'
    };

    const categories = [
        { id: 'all', label: L.all, emoji: '🌾' },
        { id: 'vegetables', label: L.vegetables, emoji: '🥬' },
        { id: 'fruits', label: L.fruits, emoji: '🍎' },
        { id: 'grains', label: L.grains, emoji: '🌾' },
        { id: 'pulses', label: L.pulses, emoji: '🫘' }
    ];

    useEffect(() => {
        loadListings();
    }, []);

    const loadListings = async () => {
        try {
            const data = await marketService.getListings();
            console.log('Listings data:', data);
            console.log('First listing images:', data?.[0]?.images);
            setListings(data || []);
        } catch (error) {
            console.error('Error loading listings:', error);
            setListings([]);
        } finally {
            setLoading(false);
        }
    };

    const filteredListings = listings.filter(listing => {
        const matchesSearch = listing.crop?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || listing.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    const getLocationString = (loc) => {
        if (!loc) return 'India';
        if (typeof loc === 'string') return loc;
        if (typeof loc === 'object') return loc.district || loc.city || 'India';
        return 'India';
    };

    return (
        <div className="marketplace-page">
            {/* Header */}
            <header className="page-header">
                <button className="back-btn" onClick={() => navigate(guestMode ? '/login' : '/')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {/* Cart Icon with Badge */}
                    <button
                        className="cart-icon-btn"
                        onClick={() => navigate('/cart')}
                        style={{
                            position: 'relative',
                            width: '36px',
                            height: '36px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: '#F3F4F6',
                            border: 'none',
                            borderRadius: '10px',
                            cursor: 'pointer'
                        }}
                    >
                        <ShoppingCart size={20} />
                        {cartCount > 0 && (
                            <span style={{
                                position: 'absolute',
                                top: '-4px',
                                right: '-4px',
                                background: '#10b981',
                                color: 'white',
                                borderRadius: '50%',
                                width: '18px',
                                height: '18px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '11px',
                                fontWeight: '700'
                            }}>
                                {cartCount}
                            </span>
                        )}
                    </button>
                    {/* Farmer Dashboard Link */}
                    {isLoggedIn && (
                        <button
                            className="add-btn"
                            onClick={() => navigate('/farmer/dashboard')}
                            title={lang === 'te' ? 'నా డాష్‌బోర్డ్' : 'My Dashboard'}
                            style={{
                                background: '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: '10px',
                                width: '36px',
                                height: '36px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer'
                            }}
                        >
                            👨‍🌾
                        </button>
                    )}
                    {isLoggedIn && (
                        <button className="add-btn" onClick={() => navigate('/market/create')}>
                            <Plus size={20} />
                        </button>
                    )}
                </div>
            </header>

            {/* Search Bar */}
            <div className="search-section">
                <div className="search-bar">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        placeholder={L.search}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    {searchQuery && (
                        <button className="clear-btn" onClick={() => setSearchQuery('')}>
                            <X size={16} />
                        </button>
                    )}
                </div>
            </div>

            {/* Categories */}
            <div className="categories-scroll">
                {categories.map(cat => (
                    <button
                        key={cat.id}
                        className={`category-chip ${selectedCategory === cat.id ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(cat.id)}
                    >
                        <span>{cat.emoji}</span>
                        <span>{cat.label}</span>
                    </button>
                ))}
            </div>

            {/* Listings */}
            <div className="listings-container">
                {loading ? (
                    <div className="loading-grid">
                        {[1, 2, 3, 4, 5, 6].map(i => (
                            <div key={i} className="listing-skeleton">
                                <div className="skeleton-image" />
                                <div className="skeleton-content">
                                    <div className="skeleton-line" />
                                    <div className="skeleton-line short" />
                                </div>
                            </div>
                        ))}
                    </div>
                ) : filteredListings.length === 0 ? (
                    <div className="empty-state">
                        <span className="empty-icon">🌾</span>
                        <p>{L.noListings}</p>
                    </div>
                ) : (
                    <div className="listings-grid">
                        {filteredListings.map(listing => (
                            <div
                                key={listing.listingId}
                                className="listing-card"
                                onClick={() => navigate(`/market/${listing.listingId}`)}
                            >
                                <div className="listing-image">
                                    {(listing.images?.[0]?.data || listing.imageUrl) ? (
                                        <img
                                            src={listing.images?.[0]?.data || listing.imageUrl}
                                            alt={listing.crop}
                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                        />
                                    ) : (
                                        <div style={{ width: '100%', height: '100%', backgroundColor: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#9ca3af' }}>
                                            No Image
                                        </div>
                                    )}
                                    {listing.status === 'LISTED' && (
                                        <span className="fresh-badge">Fresh</span>
                                    )}
                                </div>
                                <div className="listing-info">
                                    <h4>{listing.crop}</h4>
                                    <p className="listing-variety">{listing.variety}</p>
                                    <p className="listing-price">
                                        ₹{listing.price}/{listing.unit || 'Quintal'}
                                    </p>
                                    <p className="listing-location">
                                        <MapPin size={12} />
                                        {getLocationString(listing.location)}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Marketplace;
