import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    Leaf, Plus, AlertTriangle, Calendar, MapPin, Droplets,
    ChevronRight, RefreshCw, Loader2, Bell, Search, TrendingUp, Trash2, ArrowLeft
} from 'lucide-react';
import './MyCrops.css';

const API_BASE = import.meta.env.VITE_ML_API_URL || 'http://localhost:8001';

const MyCrops = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language; // 'en', 'te', or 'hi'

    const [loading, setLoading] = useState(true);
    const [subscriptions, setSubscriptions] = useState([]);
    const [error, setError] = useState(null);
    const [deleting, setDeleting] = useState(null); // Track which subscription is being deleted

    // Get farmer ID from localStorage
    const farmerId = localStorage.getItem('farmerPhone') || '7330671778';

    // Crop icons mapping
    const cropIcons = {
        'Paddy': '🌾', 'Rice': '🌾', 'Cotton': '🧶', 'Maize': '🌽',
        'Chilli': '🌶️', 'Groundnut': '🥜', 'Ground Nuts': '🥜',
        'Wheat': '🌾', 'Sugarcane': '🎋', 'Tomato': '🍅',
        'Pulses': '🫘', 'Turmeric': '🟡', 'Banana': '🍌'
    };

    // Helper function for 3-language text
    const txt = (en, hi, te) => {
        if (lang === 'te') return te;
        if (lang === 'hi') return hi;
        return en;
    };

    // Labels
    const L = {
        title: txt('🌾 My Crops', '🌾 मेरी फसलें', '🌾 నా పంటలు'),
        subtitle: txt('Daily monitoring for your crops', 'आपकी फसलों की दैनिक निगरानी', 'మీ పంటల రోజువారీ మానిటరింగ్'),
        addCrop: txt('+ Add New Crop', '+ नई फसल जोड़ें', '+ కొత్త పంట జోడించండి'),
        noCrops: txt('No crops added yet', 'अभी तक कोई फसल नहीं जोड़ी', 'ఇంకా పంటలు జోడించలేదు'),
        addFirst: txt('Add your first crop to start monitoring', 'निगरानी शुरू करने के लिए अपनी पहली फसल जोड़ें', 'మీ మొదటి పంటను జోడించండి'),
        day: txt('Day', 'दिन', 'రోజు'),
        stage: txt('Stage', 'चरण', 'దశ'),
        alerts: txt('Alerts', 'अलर्ट', 'హెచ్చరికలు'),
        viewPlan: txt('View Daily Plan', 'दैनिक प्लान देखें', 'రోజు ప్లాన్ చూడండి'),
        refresh: txt('Refresh', 'रिफ्रेश', 'రిఫ్రెష్'),
        area: txt('Area', 'क्षेत्र', 'విస్తీర్ణం'),
        acres: txt('acres', 'एकड़', 'ఎకరాలు'),
        delete: txt('Delete', 'हटाएं', 'తొలగించు'),
        confirmDelete: txt('Really delete?', 'वाकई हटाना है?', 'నిజంగా తొలగించాలా?'),
        yes: txt('Yes', 'हाँ', 'అవును'),
        no: txt('No', 'नहीं', 'కాదు'),
        loading: txt('Loading your crops...', 'आपकी फसलें लोड हो रही हैं...', 'మీ పంటలు లోడ్ అవుతున్నాయి...'),
        goodCondition: txt('Good condition', 'अच्छी स्थिति', 'మంచి పరిస్థితి'),
        cropRecommend: txt('Crop Recommendation', 'फसल सिफारिश', 'పంట సిఫార్సు'),
        cropAdvisory: txt('Crop Advisory', 'फसल सलाह', 'పంట సలహా')
    };

    useEffect(() => {
        fetchSubscriptions();
    }, []);

    const fetchSubscriptions = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/my-crops/${farmerId}`);
            const data = await res.json();
            if (data.success) {
                setSubscriptions(data.subscriptions);
            } else {
                setError('Failed to load crops');
            }
        } catch (err) {
            console.error(err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (e, subscriptionId) => {
        e.stopPropagation(); // Prevent card click
        if (deleting === subscriptionId) {
            // Already confirming - do the delete
            try {
                const res = await fetch(`${API_BASE}/subscription/${subscriptionId}`, {
                    method: 'DELETE'
                });
                if (res.ok) {
                    setSubscriptions(prev => prev.filter(s => s.subscriptionId !== subscriptionId));
                }
            } catch (err) {
                console.error('Delete failed:', err);
            }
            setDeleting(null);
        } else {
            // First click - show confirmation
            setDeleting(subscriptionId);
            setTimeout(() => setDeleting(null), 3000); // Auto-cancel after 3s
        }
    };

    const getProgressColor = (percent) => {
        if (percent < 30) return '#22c55e';
        if (percent < 60) return '#eab308';
        if (percent < 85) return '#f97316';
        return '#ef4444';
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString(lang === 'te' ? 'te-IN' : lang === 'hi' ? 'hi-IN' : 'en-IN', {
            day: 'numeric', month: 'short'
        });
    };

    if (loading) {
        return (
            <div className="mycrops-container">
                <div className="loading-state">
                    <Loader2 className="spinner" size={40} />
                    <p>{L.loading}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="mycrops-container">
            {/* Header */}
            <div className="mycrops-header">
                <button className="back-btn" onClick={() => navigate('/home')}>
                    <ArrowLeft size={20} />
                </button>
                <div className="header-content">
                    <h1>{L.title}</h1>
                    <p>{L.subtitle}</p>
                </div>
                <button className="refresh-btn" onClick={fetchSubscriptions}>
                    <RefreshCw size={18} />
                </button>
            </div>

            {/* Add New Crop Button */}
            <button
                className="add-crop-btn"
                onClick={() => navigate('/subscribe-crop')}
            >
                <Plus size={20} />
                {L.addCrop}
            </button>

            {/* Crops List */}
            {subscriptions.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">🌱</div>
                    <h3>{L.noCrops}</h3>
                    <p>{L.addFirst}</p>
                    <button
                        className="start-btn"
                        onClick={() => navigate('/subscribe-crop')}
                    >
                        <Plus size={20} />
                        {L.addCrop}
                    </button>
                </div>
            ) : (
                <div className="crops-list">
                    {subscriptions.map((sub) => {
                        const stageInfo = sub.stage_info || {};
                        const progress = stageInfo.progress_percent || 0;
                        const hasAlerts = sub.has_urgent_alerts;
                        const alertCount = sub.alert_count || 0;

                        return (
                            <div
                                key={sub.subscriptionId}
                                className={`crop-card ${hasAlerts ? 'has-alerts' : ''}`}
                                onClick={() => navigate(`/monitor/${sub.subscriptionId}`)}
                            >
                                {/* Alert Badge */}
                                {alertCount > 0 && (
                                    <div className="alert-badge">
                                        <Bell size={14} />
                                        {alertCount}
                                    </div>
                                )}

                                {/* Crop Header */}
                                <div className="crop-header">
                                    <div className="crop-icon">
                                        {cropIcons[sub.crop] || '🌱'}
                                    </div>
                                    <div className="crop-info">
                                        <h3>{sub.crop}</h3>
                                        <div className="crop-meta">
                                            <span><MapPin size={14} /> {sub.location?.name || sub.locationName}</span>
                                            <span><Droplets size={14} /> {sub.areaAcres} {L.acres}</span>
                                        </div>
                                    </div>
                                    <ChevronRight size={24} className="chevron" />
                                </div>

                                {/* Progress Bar */}
                                <div className="progress-section">
                                    <div className="progress-header">
                                        <span className="stage-name">
                                            {stageInfo.stage_name || 'Growing'}
                                        </span>
                                        <span className="day-count">
                                            {L.day} {stageInfo.days_after_sowing || 0}
                                        </span>
                                    </div>
                                    <div className="progress-bar">
                                        <div
                                            className="progress-fill"
                                            style={{
                                                width: `${progress}%`,
                                                backgroundColor: getProgressColor(progress)
                                            }}
                                        />
                                    </div>
                                    <div className="progress-labels">
                                        <span>{formatDate(sub.sowingDate)}</span>
                                        <span>{progress}%</span>
                                        <span>{formatDate(stageInfo.harvest_expected)}</span>
                                    </div>
                                </div>

                                {/* Quick Stats */}
                                <div className="quick-stats">
                                    {hasAlerts ? (
                                        <div className="stat alert">
                                            <AlertTriangle size={16} />
                                            <span>{alertCount} {L.alerts}</span>
                                        </div>
                                    ) : (
                                        <div className="stat success">
                                            <TrendingUp size={16} />
                                            <span>{L.goodCondition}</span>
                                        </div>
                                    )}
                                    <button className="view-plan-btn">
                                        {L.viewPlan}
                                        <ChevronRight size={16} />
                                    </button>
                                    <button
                                        className={`delete-btn ${deleting === sub.subscriptionId ? 'confirming' : ''}`}
                                        onClick={(e) => handleDelete(e, sub.subscriptionId)}
                                    >
                                        <Trash2 size={16} />
                                        {deleting === sub.subscriptionId ? L.yes : ''}
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions">
                <button onClick={() => navigate('/recommend')}>
                    <Search size={20} />
                    <span>{L.cropRecommend}</span>
                </button>
                <button onClick={() => navigate('/advisory')}>
                    <Calendar size={20} />
                    <span>{L.cropAdvisory}</span>
                </button>
            </div>
        </div>
    );
};

export default MyCrops;
