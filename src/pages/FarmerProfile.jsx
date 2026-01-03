/**
 * Farmer Profile Page
 * Shows farmer details and their listings
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { marketService } from '../services/marketService';
import { useTranslation } from 'react-i18next';
import {
    User, MapPin, Phone, LogOut, Package,
    ShieldCheck, Edit2, ArrowLeft
} from 'lucide-react';
import './Login.css';
import './FarmerProfile.css';

const FarmerProfile = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { user, logout, isLoggedIn } = useAuth();

    const [myListings, setMyListings] = useState([]);

    useEffect(() => {
        const loadListings = async () => {
            try {
                if (isLoggedIn && user && user.id) {
                    // Get listings by this farmer - FIXED: Added await
                    const allListings = await marketService.getListings() || [];

                    // Defensive check
                    if (!Array.isArray(allListings)) {
                        console.warn('getListings did not return array:', allListings);
                        setMyListings([]);
                        return;
                    }

                    const filtered = allListings.filter(l => l.farmerId === user.id);
                    setMyListings(filtered);
                }
            } catch (err) {
                console.error('Error loading listings:', err);
                setMyListings([]);
            }
        };

        loadListings();
    }, [isLoggedIn, user]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!isLoggedIn || !user) {
        return (
            <div className="profile-page">
                <div className="profile-header">
                    <button
                        className="back-btn"
                        onClick={() => navigate('/')}
                        style={{ position: 'absolute', left: '1rem', top: '1rem', color: 'white', background: 'rgba(255,255,255,0.2)' }}
                    >
                        <ArrowLeft size={18} />
                    </button>
                    <div className="profile-avatar">👤</div>
                    <h2 className="profile-name">{t('profile.guest', 'Guest User')}</h2>
                </div>
                <div className="profile-content">
                    <div className="profile-card" style={{ textAlign: 'center', padding: '32px 16px' }}>
                        <p style={{ color: '#6B7280', marginBottom: '16px' }}>
                            {t('profile.loginRequired', 'Please login to view your profile')}
                        </p>
                        <button className="submit-btn" onClick={() => navigate('/login')}>
                            {t('profile.loginButton', 'Login / Register')}
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="profile-page">
            <div className="profile-header">
                <button
                    className="back-btn"
                    onClick={() => navigate('/home')}
                    style={{ position: 'absolute', left: '1rem', top: '1rem', color: 'white', background: 'rgba(255,255,255,0.2)' }}
                >
                    <ArrowLeft size={18} />
                </button>

                <div className="profile-avatar">
                    👨‍🌾
                </div>
                <h2 className="profile-name">{user.name || 'Farmer'}</h2>
                <p className="profile-phone">
                    <Phone size={14} /> {user.phone}
                </p>
                {user.verified && (
                    <div className="verified-badge">
                        <ShieldCheck size={14} /> Verified Farmer
                    </div>
                )}
            </div>

            <div className="profile-content">
                {/* Profile Details */}
                <div className="profile-card">
                    <h3>
                        <User size={18} />
                        {t('profile.details', 'Profile Details')}
                    </h3>
                    <div className="profile-info-row">
                        <label>{t('profile.id', 'Farmer ID')}</label>
                        <span>{user.id}</span>
                    </div>
                    <div className="profile-info-row">
                        <label>{t('profile.village', 'Village')}</label>
                        <span>{user.village || '-'}</span>
                    </div>
                    <div className="profile-info-row">
                        <label>{t('profile.district', 'District')}</label>
                        <span>{user.district || '-'}</span>
                    </div>
                    <div className="profile-info-row">
                        <label>{t('profile.state', 'State')}</label>
                        <span>{user.state || '-'}</span>
                    </div>
                    <div className="profile-info-row">
                        <label>{t('profile.joined', 'Joined')}</label>
                        <span>{user.createdAt ? new Date(user.createdAt).toLocaleDateString() : '-'}</span>
                    </div>
                </div>

                {/* My Listings */}
                <div className="profile-card">
                    <h3>
                        <Package size={18} />
                        {t('profile.myListings', 'My Listings')} ({myListings.length})
                    </h3>
                    {myListings.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '1rem', color: '#6b7280' }}>
                            <p>{t('profile.noListings', 'You have no listings yet')}</p>
                            <button
                                className="submit-btn"
                                onClick={() => navigate('/market/create')}
                                style={{ marginTop: '1rem' }}
                            >
                                + Create First Listing
                            </button>
                        </div>
                    ) : (
                        <div>
                            {myListings.map(listing => (
                                <div
                                    key={listing.listingId}
                                    onClick={() => navigate(`/market/${listing.listingId}`)}
                                    style={{
                                        padding: '0.75rem',
                                        borderBottom: '1px solid #f3f4f6',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center'
                                    }}
                                >
                                    <div>
                                        <strong>{listing.crop}</strong> - {listing.variety}
                                        <br />
                                        <small style={{ color: '#6b7280' }}>
                                            ₹{listing.price}/{listing.unit}
                                        </small>
                                    </div>
                                    <span className={`status-badge ${listing.status.toLowerCase()}`}>
                                        {listing.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="profile-card">
                    <button
                        onClick={() => navigate('/market/create')}
                        className="submit-btn"
                        style={{ marginBottom: '0.75rem' }}
                    >
                        <Package size={18} /> Create New Listing
                    </button>
                    <button onClick={handleLogout} className="logout-btn">
                        <LogOut size={18} /> Logout
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FarmerProfile;
