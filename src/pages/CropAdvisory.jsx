import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    MapPin, ArrowLeft, Loader2, AlertTriangle, Bug, Calendar,
    Thermometer, Droplets, Leaf, CheckCircle, Navigation, X, ArrowRight
} from 'lucide-react';
import LanguageSelector from '../components/LanguageSelector';
import './CropAdvisory.css';

import { ML_API_URL } from '../config/api';
const API_BASE = ML_API_URL;

const CropAdvisory = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    // States
    const [locationQuery, setLocationQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState(1); // 1: Enter location, 2: Show crops, 3: Show crop advice
    const [recommendations, setRecommendations] = useState(null);
    const [selectedCrop, setSelectedCrop] = useState(null);
    const [advisory, setAdvisory] = useState(null);
    const [coords, setCoords] = useState({ lat: 17.385, lon: 78.4867 });
    const [expandedWeeks, setExpandedWeeks] = useState({ 1: true });

    // Subscribe modal state
    const [showSubscribeModal, setShowSubscribeModal] = useState(false);
    const [subscribeData, setSubscribeData] = useState({
        sowingDate: new Date().toISOString().split('T')[0],
        areaAcres: 1
    });
    const [subscribing, setSubscribing] = useState(false);

    // Handle incoming navigation state from CropRecommendation
    React.useEffect(() => {
        if (location.state?.crop) {
            const { crop, location: locName, coords: locCoords } = location.state;
            if (locName) setLocationQuery(locName);
            if (locCoords) setCoords(locCoords);

            // Set crop and go directly to advisory view (step 3)
            setSelectedCrop(crop);
            setStep(3);

            // Auto-fetch advisory
            fetchAdvisory(crop);
        }
    }, [location.state]);

    // Crop translations
    const cropNames = {
        'Paddy': { en: 'Paddy (Rice)', te: 'వరి', icon: '🌾' },
        'Rice': { en: 'Rice', te: 'వరి', icon: '🌾' },
        'Cotton': { en: 'Cotton', te: 'పత్తి', icon: '🧶' },
        'Maize': { en: 'Maize', te: 'మొక్కజొన్న', icon: '🌽' },
        'Chilli': { en: 'Chilli', te: 'మిర్చి', icon: '🌶️' },
        'Ground Nuts': { en: 'Groundnut', te: 'వేరుశెనగ', icon: '🥜' },
        'Groundnut': { en: 'Groundnut', te: 'వేరుశెనగ', icon: '🥜' },
        'Pulses': { en: 'Pulses', te: 'పప్పులు', icon: '🫘' },
        'Wheat': { en: 'Wheat', te: 'గోధుమ', icon: '🌾' },
        'Sugarcane': { en: 'Sugarcane', te: 'చెరకు', icon: '🎋' },
        'Turmeric': { en: 'Turmeric', te: 'పసుపు', icon: '🟡' }
    };

    // Labels
    const L = {
        title: lang === 'te' ? '🌾 పంట సలహా' : '🌾 Crop Advisory',
        enterLocation: lang === 'te' ? 'మీ ఊరు/జిల్లా పేరు' : 'Enter your village/district',
        useGPS: lang === 'te' ? '📍 GPS' : '📍 GPS',
        search: lang === 'te' ? 'వెతుకు' : 'Search',
        loading: lang === 'te' ? 'వెతుకుతోంది...' : 'Searching...',
        bestCrops: lang === 'te' ? 'మీకు సరైన పంటలు' : 'Recommended Crops',
        tapForAdvice: lang === 'te' ? 'సలహా కోసం నొక్కండి' : 'Tap for detailed advice',
        backToCrops: lang === 'te' ? '← పంటలు' : '← Back to crops',
        advice: lang === 'te' ? 'సలహా' : 'Advisory',
        weather: lang === 'te' ? 'వాతావరణం' : 'Weather',
        alerts: lang === 'te' ? 'హెచ్చరికలు' : 'Alerts',
        pests: lang === 'te' ? 'తెగుళ్ళు' : 'Pest Risks',
        calendar: lang === 'te' ? 'విత్తే సమయం' : 'Planting Time',
        todayTask: lang === 'te' ? 'ఈరోజు చేయండి' : "Today's Task",
        noAlerts: lang === 'te' ? 'ప్రమాదాలు లేవు' : 'No Alerts',
        yield: lang === 'te' ? 'దిగుబడి' : 'Yield',
        risk: lang === 'te' ? 'రిస్క్' : 'Risk',
        water: lang === 'te' ? 'నీరు' : 'Water'
    };

    // Use GPS
    const handleGPS = () => {
        if (!navigator.geolocation) return;
        setLoading(true);
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
                try {
                    const res = await fetch(`https://api.openweathermap.org/geo/1.0/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&limit=1&appid=dd587855fbdac207034b854ea3e03c00`);
                    const data = await res.json();
                    if (data?.[0]?.name) {
                        setLocationQuery(data[0].name);
                        fetchCrops(data[0].name);
                    }
                } catch (e) {
                    setLoading(false);
                }
            },
            () => setLoading(false)
        );
    };

    // Handle search
    const handleSearch = (e) => {
        e.preventDefault();
        if (!locationQuery.trim()) return;
        fetchCrops(locationQuery);
    };

    // Step 2: Fetch crop recommendations
    const fetchCrops = async (location) => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ location_name: location })
            });
            const data = await res.json();
            setRecommendations(data);
            setStep(2);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Step 3: Fetch comprehensive advisory for selected crop (5-year historical data)
    const fetchAdvisory = async (crop) => {
        setSelectedCrop(crop);
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/crop-advisory`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop: crop.crop,
                    lat: coords.lat,
                    lon: coords.lon,
                    language: 'both'
                })
            });
            const data = await res.json();
            if (data.success) {
                setAdvisory(data.advisory);
                setStep(3);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Render Step 1: Enter Location
    const renderLocationInput = () => (
        <div className="step-container">
            <div className="step-icon">🌾</div>
            <h2>{lang === 'te' ? 'మీ ప్రాంతం ఎంచుకోండి' : 'Enter Your Location'}</h2>
            <p className="step-desc">
                {lang === 'te'
                    ? 'మీ ఊరు పేరు టైప్ చేస్తే, మీకు సరైన పంటలు చూపిస్తాము'
                    : 'Enter your village to see recommended crops'}
            </p>

            <form onSubmit={handleSearch} className="location-form">
                <div className="input-row">
                    <MapPin size={20} />
                    <input
                        type="text"
                        value={locationQuery}
                        onChange={(e) => setLocationQuery(e.target.value)}
                        placeholder={L.enterLocation}
                        autoFocus
                    />
                </div>
                <div className="button-row">
                    <button type="button" className="gps-btn" onClick={handleGPS}>
                        <Navigation size={16} />
                        {L.useGPS}
                    </button>
                    <button type="submit" className="search-btn" disabled={!locationQuery.trim()}>
                        {L.search}
                        <ArrowRight size={16} />
                    </button>
                </div>
            </form>
        </div>
    );

    // Render Step 2: Show Crop Recommendations
    const renderCrops = () => {
        const recs = recommendations?.recommendations || [];
        const context = recommendations?.context;
        const soilParams = context?.soil_params;

        return (
            <div className="step-container">
                {/* Soil Parameters Card - At Top */}
                {context && (
                    <div className="soil-params-card">
                        <div className="soil-header">
                            <span className="soil-type">🏔️ {context.soil_type}</span>
                            {context.soil_zone && (
                                <span className="soil-zone">{context.soil_zone}</span>
                            )}
                        </div>
                        {soilParams && (
                            <div className="params-row">
                                <div className="param-chip">
                                    <span className="label">pH </span>
                                    <span className="value">{soilParams.ph}</span>
                                </div>
                                <div className="param-chip">
                                    <span className="label">N </span>
                                    <span className="value">{soilParams.n}</span>
                                </div>
                                <div className="param-chip">
                                    <span className="label">P </span>
                                    <span className="value">{soilParams.p}</span>
                                </div>
                                <div className="param-chip">
                                    <span className="label">K </span>
                                    <span className="value">{soilParams.k}</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Weather & Season Row */}
                <div className="context-row">
                    <div className="context-chip">
                        <div className="icon">📍</div>
                        <div className="label">{lang === 'te' ? 'ప్రాంతం' : 'Location'}</div>
                        <div className="value">{recommendations?.location || locationQuery}</div>
                    </div>
                    <div className="context-chip">
                        <div className="icon">🌡️</div>
                        <div className="label">{lang === 'te' ? 'ఉష్ణోగ్రత' : 'Temp'}</div>
                        <div className="value">{context?.weather ? `${Math.round(context.weather.temp)}°C` : '--'}</div>
                    </div>
                    <div className="context-chip">
                        <div className="icon">📅</div>
                        <div className="label">{lang === 'te' ? 'సీజన్' : 'Season'}</div>
                        <div className="value">{context?.season || 'Rabi'}</div>
                    </div>
                </div>

                <h2>{L.bestCrops}</h2>
                <p className="step-desc">{L.tapForAdvice}</p>

                {/* Crop Cards */}
                {recs.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#6B7280' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🌾</div>
                        <p>{lang === 'te' ? 'పంటలు కనుగొనబడలేదు' : 'No crops found for this location'}</p>
                    </div>
                ) : (
                    <div className="crop-list">
                        {recs.map((rec, i) => (
                            <div
                                key={i}
                                className="crop-card"
                                onClick={() => fetchAdvisory(rec)}
                            >
                                <div className="crop-icon">
                                    {cropNames[rec.crop]?.icon || '🌱'}
                                </div>
                                <div className="crop-info">
                                    <div className="crop-name">
                                        {lang === 'te' ? cropNames[rec.crop]?.te || rec.crop : rec.crop}
                                    </div>
                                    <div className="crop-meta">
                                        <span className={`tag ${rec.yield_potential?.toLowerCase() === 'high' ? 'high' : 'medium'}`}>
                                            {L.yield}: {rec.yield_potential}
                                        </span>
                                        <span className={`tag ${rec.risk_factor?.toLowerCase() === 'low' ? 'low' : 'medium'}`}>
                                            {L.risk}: {rec.risk_factor}
                                        </span>
                                    </div>
                                    {rec.market_price?.price && (
                                        <div style={{
                                            marginTop: '0.5rem',
                                            fontSize: '0.85rem',
                                            color: '#16a34a',
                                            fontWeight: 600,
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.25rem'
                                        }}>
                                            💰 {rec.market_price.price} {rec.market_price.unit}
                                            {rec.market_price.msp && <span style={{ fontSize: '0.7rem', color: '#666' }}>(MSP)</span>}
                                            {rec.market_price.trend === 'up' && <span style={{ color: '#22c55e' }}>↑</span>}
                                            {rec.market_price.trend === 'down' && <span style={{ color: '#ef4444' }}>↓</span>}
                                        </div>
                                    )}
                                </div>
                                <div className="crop-score">{Math.round(rec.confidence)}%</div>
                                <ArrowRight size={20} className="arrow" />
                            </div>
                        ))}
                    </div>
                )}

                {/* Soil Info */}
                {context?.soil_type && (
                    <div className="soil-info">
                        <span>🏔️ {lang === 'te' ? 'మట్టి' : 'Soil'}: {context.soil_type}</span>
                        <span>📅 {context.season}</span>
                    </div>
                )}
            </div>
        );
    };

    // Toggle function for expandable weeks (defined at component level)
    const toggleWeek = (week) => setExpandedWeeks(prev => ({ ...prev, [week]: !prev[week] }));

    // Render Step 3: Comprehensive Crop Advisory with Week-by-Week Timeline
    const renderAdvisory = () => {
        const summary = advisory?.summary?.[lang] || advisory?.summary?.en || {};
        const alerts = advisory?.alerts || [];
        const weeks = advisory?.weekly_advisory || [];

        return (
            <div className="step-container">
                {/* Back Button */}
                <button className="back-link" onClick={() => navigate('/recommend', { state: { recommendations: location.state?.recommendations, locationQuery: location.state?.location } })}>
                    {L.backToCrops}
                </button>

                {/* Crop Header with Summary */}
                <div className="advisory-crop-header" style={{
                    background: 'linear-gradient(135deg, #16a34a, #15803d)',
                    color: 'white',
                    padding: '1rem',
                    borderRadius: '16px',
                    marginBottom: '1rem',
                    overflow: 'hidden',
                    display: 'block',
                    maxWidth: '100%',
                    boxSizing: 'border-box'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '2rem', flexShrink: 0 }}>
                            {cropNames[selectedCrop?.crop]?.icon || '🌱'}
                        </span>
                        <div style={{ minWidth: 0, flex: 1 }}>
                            <h2 style={{ margin: 0, fontSize: '1.1rem', wordBreak: 'break-word' }}>
                                {lang === 'te' ? cropNames[selectedCrop?.crop]?.te : selectedCrop?.crop}
                            </h2>
                            <div style={{ opacity: 0.9, fontSize: '0.8rem', wordBreak: 'break-word' }}>
                                {advisory?.sowing_date} → {advisory?.harvest_date}
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.4rem' }}>
                        <div style={{ textAlign: 'center', padding: '0.4rem', background: 'rgba(255,255,255,0.15)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>{lang === 'te' ? 'వ్యవధి' : 'Duration'}</div>
                            <div style={{ fontWeight: 600, fontSize: '0.75rem', wordBreak: 'break-word' }}>{summary.crop_duration || `${advisory?.crop?.duration_days || 120}d`}</div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '0.4rem', background: 'rgba(255,255,255,0.15)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>{lang === 'te' ? 'వర్షం' : 'Rain'}</div>
                            <div style={{ fontWeight: 600, fontSize: '0.75rem', wordBreak: 'break-word' }}>{summary.expected_rainfall || '--'}</div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '0.4rem', background: 'rgba(255,255,255,0.15)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>{lang === 'te' ? 'రిస్క్' : 'Risk'}</div>
                            <div style={{ fontWeight: 600, fontSize: '0.75rem', wordBreak: 'break-word' }}>{summary.main_risk || 'Low'}</div>
                        </div>
                    </div>

                    {summary.recommendation && (
                        <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: 'rgba(255,255,255,0.15)', borderRadius: '8px', fontSize: '0.8rem', wordBreak: 'break-word' }}>
                            💡 {summary.recommendation}
                        </div>
                    )}

                    {/* Subscribe to Monitor Button - Opens modal for sowing date */}
                    <button
                        onClick={() => setShowSubscribeModal(true)}
                        style={{
                            width: '100%',
                            marginTop: '0.75rem',
                            padding: '0.7rem',
                            background: 'rgba(255,255,255,0.95)',
                            color: '#16a34a',
                            border: 'none',
                            borderRadius: '10px',
                            fontSize: '0.9rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.4rem',
                            flexWrap: 'wrap'
                        }}
                    >
                        🔔 {lang === 'te' ? 'మానిటర్ చేయండి' : 'Monitor Crop'}
                    </button>
                </div>

                {/* Smart Fertilizer Plan - Detailed Section */}
                {selectedCrop?.fertilizer_plan && !selectedCrop.fertilizer_plan.error && (
                    <div style={{
                        background: 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
                        borderRadius: '16px',
                        padding: '1rem',
                        marginBottom: '1rem',
                        border: '2px solid #86EFAC',
                        maxWidth: '100%',
                        boxSizing: 'border-box',
                        overflow: 'hidden'
                    }}>
                        {/* Section Header */}
                        <div style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            justifyContent: 'space-between',
                            flexWrap: 'wrap',
                            gap: '0.5rem',
                            marginBottom: '0.75rem'
                        }}>
                            <h3 style={{ margin: 0, color: '#166534', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.4rem', flex: '1 1 auto' }}>
                                🌱 {lang === 'te' ? 'ఎరువుల సిఫారసు' : 'Fertilizer Plan'}
                            </h3>
                            {selectedCrop.fertilizer_plan.cost_benefit_analysis && (
                                <div style={{
                                    padding: '3px 8px',
                                    background: selectedCrop.fertilizer_plan.cost_benefit_analysis.sustainable ? '#16A34A' : '#EA580C',
                                    color: 'white',
                                    borderRadius: '6px',
                                    fontSize: '10px',
                                    fontWeight: '600',
                                    whiteSpace: 'nowrap'
                                }}>
                                    ⭐ {selectedCrop.fertilizer_plan.cost_benefit_analysis.sustainability_score}/10
                                </div>
                            )}
                        </div>

                        {/* NPK Analysis */}
                        {selectedCrop.fertilizer_plan.npk_analysis && (
                            <div style={{ marginBottom: '0.75rem' }}>
                                <h4 style={{ fontSize: '0.85rem', color: '#166534', marginBottom: '0.5rem' }}>
                                    📊 {lang === 'te' ? 'NPK స్థితి' : 'NPK Status'}
                                </h4>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(3, 1fr)',
                                    gap: '0.5rem'
                                }}>
                                    {['n', 'p', 'k'].map(nutrient => {
                                        const analysis = selectedCrop.fertilizer_plan.npk_analysis;
                                        const deficit = analysis.deficit[nutrient];
                                        const status = analysis.status[nutrient];
                                        const current = analysis.current[nutrient];
                                        const required = analysis.required[nutrient];
                                        const color = status === 'Deficit' ? '#DC2626' : status === 'Excess' ? '#2563EB' : '#16A34A';

                                        return (
                                            <div key={nutrient} style={{
                                                padding: '0.75rem',
                                                background: 'white',
                                                borderRadius: '10px',
                                                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                            }}>
                                                <div style={{
                                                    fontSize: '11px',
                                                    color: '#6B7280',
                                                    fontWeight: '600',
                                                    marginBottom: '6px'
                                                }}>
                                                    {nutrient.toUpperCase()} ({lang === 'te' ? 'కేజీ/ఎకరం' : 'kg/acre'})
                                                </div>
                                                <div style={{
                                                    fontSize: '20px',
                                                    fontWeight: '700',
                                                    color: color,
                                                    marginBottom: '4px'
                                                }}>
                                                    {deficit > 0 ? '+' : ''}{Math.round(deficit)}
                                                </div>
                                                <div style={{
                                                    fontSize: '10px',
                                                    color: '#6B7280',
                                                    marginBottom: '6px'
                                                }}>
                                                    {lang === 'te' ? 'ప్రస్తుతం' : 'Current'}: {current} | {lang === 'te' ? 'అవసరం' : 'Need'}: {required}
                                                </div>
                                                <div style={{
                                                    fontSize: '11px',
                                                    fontWeight: '600',
                                                    color: color,
                                                    textTransform: 'uppercase'
                                                }}>
                                                    {lang === 'te' ?
                                                        (status === 'Deficit' ? 'కొరత' : status === 'Excess' ? 'అధికం' : 'సరైనది')
                                                        : status
                                                    }
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Fertilizer  Products */}
                        {selectedCrop.fertilizer_plan.fertilizer_recommendations && selectedCrop.fertilizer_plan.fertilizer_recommendations.length > 0 && (
                            <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ fontSize: '0.95rem', color: '#166534', marginBottom: '0.75rem' }}>
                                    📦 {lang === 'te' ? 'సిఫార్సు చేసిన ఎరువులు' : 'Recommended Fertilizers'}
                                </h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                    {selectedCrop.fertilizer_plan.fertilizer_recommendations.map((fert, idx) => (
                                        <div key={idx} style={{
                                            padding: '1rem',
                                            background: 'white',
                                            borderRadius: '10px',
                                            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                                        }}>
                                            <div style={{
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'start',
                                                marginBottom: '0.5rem'
                                            }}>
                                                <div>
                                                    <div style={{
                                                        fontWeight: '700',
                                                        fontSize: '15px',
                                                        color: '#1F2937',
                                                        marginBottom: '4px'
                                                    }}>
                                                        {fert.product}
                                                    </div>
                                                    <div style={{
                                                        fontSize: '12px',
                                                        color: '#6B7280'
                                                    }}>
                                                        {fert.application_time}
                                                    </div>
                                                </div>
                                                {fert.type === 'organic' && (
                                                    <span style={{
                                                        fontSize: '10px',
                                                        background: '#16A34A',
                                                        color: 'white',
                                                        padding: '4px 8px',
                                                        borderRadius: '4px',
                                                        fontWeight: '600'
                                                    }}>
                                                        🌿 {lang === 'te' ? 'సేంద్రీయ' : 'Organic'}
                                                    </span>
                                                )}
                                            </div>
                                            <div style={{
                                                display: 'grid',
                                                gridTemplateColumns: 'repeat(2, 1fr)',
                                                gap: '0.5rem',
                                                marginTop: '0.75rem',
                                                paddingTop: '0.75rem',
                                                borderTop: '1px dashed #E5E7EB'
                                            }}>
                                                <div>
                                                    <div style={{ fontSize: '11px', color: '#6B7280' }}>
                                                        {lang === 'te' ? 'పరిమాణం' : 'Quantity'}
                                                    </div>
                                                    <div style={{ fontSize: '14px', fontWeight: '700', color: '#1F2937' }}>
                                                        {fert.quantity_kg_per_acre} {lang === 'te' ? 'కేజీ/ఎకరం' : 'kg/acre'}
                                                    </div>
                                                </div>
                                                <div>
                                                    <div style={{ fontSize: '11px', color: '#6B7280' }}>
                                                        {lang === 'te' ? 'ధర' : 'Cost'}
                                                    </div>
                                                    <div style={{ fontSize: '14px', fontWeight: '700', color: '#DC2626' }}>
                                                        ₹{fert.cost_estimate}
                                                    </div>
                                                </div>
                                            </div>
                                            {/* NPK Contribution */}
                                            <div style={{
                                                marginTop: '0.75rem',
                                                padding: '0.5rem',
                                                background: '#F9FAFB',
                                                borderRadius: '6px',
                                                fontSize: '11px'
                                            }}>
                                                <strong>{lang === 'te' ? 'NPK ఇస్తుంది' : 'NPK Contribution'}:</strong>{' '}
                                                N: {fert.npk_contribution.n}kg, P: {fert.npk_contribution.p}kg, K: {fert.npk_contribution.k}kg
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Application Schedule */}
                        {selectedCrop.fertilizer_plan.application_schedule && selectedCrop.fertilizer_plan.application_schedule.length > 0 && (
                            <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ fontSize: '0.95rem', color: '#166534', marginBottom: '0.75rem' }}>
                                    📅 {lang === 'te' ? 'వర్తింపు షెడ్యూల్' : 'Application Schedule'}
                                </h4>
                                <div style={{
                                    background: 'white',
                                    borderRadius: '10px',
                                    overflow: 'hidden'
                                }}>
                                    {selectedCrop.fertilizer_plan.application_schedule.map((stage, idx) => (
                                        <div key={idx} style={{
                                            padding: '0.875rem 1rem',
                                            borderBottom: idx < selectedCrop.fertilizer_plan.application_schedule.length - 1 ? '1px solid #E5E7EB' : 'none',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '1rem'
                                        }}>
                                            <div style={{
                                                minWidth: '60px',
                                                textAlign: 'center'
                                            }}>
                                                <div style={{
                                                    fontSize: '20px',
                                                    fontWeight: '700',
                                                    color: '#16A34A'
                                                }}>
                                                    {stage.day}
                                                </div>
                                                <div style={{
                                                    fontSize: '10px',
                                                    color: '#6B7280',
                                                    fontWeight: '600'
                                                }}>
                                                    {lang === 'te' ? 'రోజు' : 'DAY'}
                                                </div>
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{
                                                    fontSize: '11px',
                                                    color: '#16A34A',
                                                    fontWeight: '600',
                                                    marginBottom: '4px'
                                                }}>
                                                    {stage.stage}
                                                </div>
                                                <div style={{
                                                    fontSize: '13px',
                                                    color: '#1F2937',
                                                    fontWeight: '500'
                                                }}>
                                                    {stage.activity}
                                                </div>
                                            </div>
                                            <div style={{
                                                fontSize: '13px',
                                                fontWeight: '700',
                                                color: '#DC2626'
                                            }}>
                                                ₹{stage.cost}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Cost-Benefit Analysis */}
                        {selectedCrop.fertilizer_plan.cost_benefit_analysis && (
                            <div>
                                <h4 style={{ fontSize: '0.95rem', color: '#166534', marginBottom: '0.75rem' }}>
                                    💰 {lang === 'te' ? 'వ్యయ-లాభ విశ్లేషణ' : 'Cost-Benefit Analysis'}
                                </h4>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(2, 1fr)',
                                    gap: '0.75rem',
                                    background: 'white',
                                    padding: '1rem',
                                    borderRadius: '10px'
                                }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
                                            {lang === 'te' ? 'మొత్తం ఖర్చు' : 'Total Cost'}
                                        </div>
                                        <div style={{ fontSize: '20px', fontWeight: '700', color: '#DC2626' }}>
                                            ₹{selectedCrop.fertilizer_plan.cost_benefit_analysis.total_cost}
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
                                            ROI
                                        </div>
                                        <div style={{ fontSize: '20px', fontWeight: '700', color: '#16A34A' }}>
                                            {selectedCrop.fertilizer_plan.cost_benefit_analysis.roi}x
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
                                            {lang === 'te' ? 'దిగుబడి పెరుగుదల' : 'Yield Increase'}
                                        </div>
                                        <div style={{ fontSize: '20px', fontWeight: '700', color: '#2563EB' }}>
                                            +{selectedCrop.fertilizer_plan.cost_benefit_analysis.expected_yield_increase_percent}%
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
                                            {lang === 'te' ? 'రాబడి పెరుగుదల' : 'Revenue Increase'}
                                        </div>
                                        <div style={{ fontSize: '20px', fontWeight: '700', color: '#16A34A' }}>
                                            +₹{Math.round(selectedCrop.fertilizer_plan.cost_benefit_analysis.expected_revenue_increase || 0)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Sustainability Advice */}
                        {selectedCrop.fertilizer_plan.sustainability_advice && selectedCrop.fertilizer_plan.sustainability_advice.length > 0 && (
                            <div style={{
                                marginTop: '1rem',
                                padding: '0.875rem',
                                background: 'rgba(22, 101, 52, 0.1)',
                                borderRadius: '8px',
                                borderLeft: '4px solid #16A34A'
                            }}>
                                <div style={{
                                    fontSize: '12px',
                                    fontWeight: '600',
                                    color: '#166534',
                                    marginBottom: '0.5rem'
                                }}>
                                    🌿 {lang === 'te' ? 'స్థిరత్వ సలహా' : 'Sustainability Tips'}
                                </div>
                                <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '11px', color: '#166534' }}>
                                    {selectedCrop.fertilizer_plan.sustainability_advice.map((tip, idx) => (
                                        <li key={idx} style={{ marginBottom: '0.25rem' }}>{tip}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )
                }

                {/* Alerts */}
                {
                    alerts.length > 0 && (
                        <div className="info-card" style={{ marginBottom: '1rem' }}>
                            <div className="card-title">⚠️ {L.alerts}</div>
                            {alerts.map((alert, i) => (
                                <div key={i} style={{
                                    padding: '0.75rem',
                                    background: alert.severity === 'warning' ? '#fef3c7' : '#fce7f3',
                                    borderRadius: '8px',
                                    marginBottom: '0.5rem',
                                    borderLeft: `4px solid ${alert.severity === 'warning' ? '#f59e0b' : '#ec4899'}`
                                }}>
                                    <strong>{alert[`name_${lang}`] || alert.name_en}</strong>
                                    <div style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
                                        {alert[`message_${lang}`] || alert.message_en}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )
                }

                {/* Week-by-Week Timeline */}
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                    <Leaf size={20} color="#16a34a" />
                    {lang === 'te' ? 'వారాల వారీ సలహా' : 'Week-by-Week Guide'}
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {weeks.slice(0, 12).map((week, idx) => (
                        <div key={idx} style={{
                            background: '#fff',
                            borderRadius: '12px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                            overflow: 'hidden'
                        }}>
                            {/* Week Header - Clickable */}
                            <div
                                onClick={() => toggleWeek(week.week)}
                                style={{
                                    padding: '1rem',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    background: expandedWeeks[week.week] ? '#f0fdf4' : 'white'
                                }}
                            >
                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                                        {lang === 'te' ? `వారం ${week.week}` : `Week ${week.week}`}
                                        <span style={{ marginLeft: '0.5rem', fontSize: '0.85rem', fontWeight: 400, color: '#16a34a' }}>
                                            {week.stage?.[`name_${lang}`] || week.stage?.name_en}
                                        </span>
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: '#666' }}>
                                        {week.date_range?.start} → {week.date_range?.end}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.8rem' }}>
                                        <span style={{ background: '#fef3c7', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                                            🌡️ {week.weather?.temp_max}°
                                        </span>
                                        <span style={{ background: '#dbeafe', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                                            🌧️ {week.weather?.rainfall_mm}mm
                                        </span>
                                    </div>
                                    {expandedWeeks[week.week] ? '▲' : '▼'}
                                </div>
                            </div>

                            {/* Week Details - Expandable */}
                            {expandedWeeks[week.week] && (
                                <div style={{ padding: '1rem', borderTop: '1px solid #e5e7eb' }}>
                                    {/* Tasks */}
                                    <div style={{ marginBottom: '1rem' }}>
                                        <h4 style={{ fontSize: '0.9rem', color: '#16a34a', marginBottom: '0.5rem' }}>
                                            📋 {lang === 'te' ? 'పనులు' : 'Tasks'}
                                        </h4>
                                        <ul style={{ paddingLeft: '1.5rem', margin: 0 }}>
                                            {week.tasks?.filter(t => t.lang === lang).map((task, tidx) => (
                                                <li key={tidx} style={{ marginBottom: '0.25rem' }}>{task.text}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Irrigation */}
                                    <div style={{ marginBottom: '1rem' }}>
                                        <h4 style={{ fontSize: '0.9rem', color: '#3b82f6', marginBottom: '0.5rem' }}>
                                            💧 {lang === 'te' ? 'నీటిపారుదల' : 'Irrigation'}
                                        </h4>
                                        <p style={{ margin: 0 }}>{week.irrigation?.[lang] || week.irrigation?.en}</p>
                                    </div>

                                    {/* Weather Notes */}
                                    {week.weather_notes?.filter(n => n.lang === lang).length > 0 && (
                                        <div style={{ background: '#f0fdf4', padding: '0.75rem', borderRadius: '8px', fontSize: '0.9rem' }}>
                                            {week.weather_notes.filter(n => n.lang === lang).map((note, nidx) => (
                                                <div key={nidx} style={{ marginBottom: nidx < week.weather_notes.length - 1 ? '0.5rem' : 0 }}>
                                                    {note.text}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Data Source */}
                <div style={{ marginTop: '1.5rem', textAlign: 'center', color: '#666', fontSize: '0.85rem' }}>
                    📊 {lang === 'te'
                        ? `డేటా: ${advisory?.weather_source} (5 సంవత్సరాల చరిత్ర)`
                        : `Source: ${advisory?.weather_source} (5-year historical)`}
                </div>
            </div >
        );
    };

    return (
        <div className="advisory-app minimal">
            {/* Header */}
            <header className="advisory-header">
                <div className="header-left">
                    <button className="back-btn" onClick={() => {
                        console.log('Back clicked!', location.state);
                        navigate('/recommend');
                    }}>
                        <ArrowLeft size={24} />
                    </button>
                    <h1>{L.title}</h1>
                </div>
                <LanguageSelector />
            </header>

            {/* Content */}
            <div className="content-area">
                {loading ? (
                    <div className="loading-state">
                        <Loader2 className="spinner" size={40} />
                        <p>{L.loading}</p>
                    </div>
                ) : (
                    <>
                        {/* Show advisory directly if crop passed from recommendation */}
                        {location.state?.crop ? (
                            renderAdvisory()
                        ) : (
                            <>
                                {step === 1 && renderLocationInput()}
                                {step === 2 && renderCrops()}
                                {step === 3 && renderAdvisory()}
                            </>
                        )}
                    </>
                )}
            </div>

            {/* Subscribe Modal */}
            {showSubscribeModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '1rem'
                }}>
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '1.5rem',
                        maxWidth: '400px',
                        width: '100%',
                        boxShadow: '0 10px 50px rgba(0,0,0,0.25)'
                    }}>
                        <h3 style={{ margin: '0 0 1rem', color: '#1f2937', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            🔔 {lang === 'te' ? 'మానిటరింగ్ ప్రారంభించండి' : 'Start Monitoring'}
                        </h3>

                        <div style={{ marginBottom: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#16a34a', fontWeight: 600 }}>
                                <span style={{ fontSize: '1.5rem' }}>{cropNames[selectedCrop?.crop]?.icon || '🌱'}</span>
                                <span>{selectedCrop?.crop}</span>
                            </div>
                            <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                                📍 {locationQuery}
                            </div>
                        </div>

                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, color: '#374151' }}>
                                📅 {lang === 'te' ? 'విత్తన తేదీ ఎప్పుడు?' : 'When do you plan to sow?'}
                            </label>
                            <input
                                type="date"
                                value={subscribeData.sowingDate}
                                onChange={(e) => setSubscribeData(prev => ({ ...prev, sowingDate: e.target.value }))}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '10px',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, color: '#374151' }}>
                                🌾 {lang === 'te' ? 'ఎన్ని ఎకరాలు?' : 'How many acres?'}
                            </label>
                            <input
                                type="number"
                                min="0.1"
                                step="0.5"
                                value={subscribeData.areaAcres}
                                onChange={(e) => setSubscribeData(prev => ({ ...prev, areaAcres: e.target.value }))}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '10px',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '0.75rem' }}>
                            <button
                                onClick={() => setShowSubscribeModal(false)}
                                style={{
                                    flex: 1,
                                    padding: '0.75rem',
                                    background: '#f3f4f6',
                                    border: 'none',
                                    borderRadius: '10px',
                                    fontSize: '1rem',
                                    fontWeight: 600,
                                    cursor: 'pointer'
                                }}
                            >
                                {lang === 'te' ? 'రద్దు' : 'Cancel'}
                            </button>
                            <button
                                onClick={async () => {
                                    setSubscribing(true);
                                    const farmerId = localStorage.getItem('farmerPhone') || '7330671778';
                                    const requestBody = {
                                        farmerId: farmerId,
                                        farmerPhone: farmerId,
                                        crop: selectedCrop?.crop || 'Paddy',
                                        sowingDate: subscribeData.sowingDate,
                                        areaAcres: parseFloat(subscribeData.areaAcres) || 1,
                                        locationName: locationQuery || 'Unknown',
                                        lat: coords?.lat || 17.385,
                                        lon: coords?.lon || 78.487,
                                        irrigationType: 'canal'
                                    };
                                    try {
                                        console.log('[Subscribe] API_BASE:', API_BASE);
                                        console.log('[Subscribe] Request:', requestBody);
                                        const res = await fetch(`${API_BASE}/subscribe-crop`, {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify(requestBody)
                                        });
                                        console.log('[Subscribe] Response status:', res.status);
                                        const data = await res.json();
                                        console.log('[Subscribe] Response data:', data);
                                        if (data.success) {
                                            setShowSubscribeModal(false);
                                            navigate(`/monitor/${data.subscription.subscriptionId}`);
                                        } else {
                                            alert(lang === 'te' ? `సమస్య: ${data.detail || 'Error'}` : `Error: ${data.detail || 'Please try again.'}`);
                                        }
                                    } catch (err) {
                                        console.error('[Subscribe] Error:', err);
                                        alert(lang === 'te' ? `కనెక్షన్ సమస్య: ${err.message}` : `Connection error: ${err.message}`);
                                    } finally {
                                        setSubscribing(false);
                                    }
                                }}
                                disabled={subscribing}
                                style={{
                                    flex: 2,
                                    padding: '0.75rem',
                                    background: 'linear-gradient(135deg, #16a34a, #15803d)',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '10px',
                                    fontSize: '1rem',
                                    fontWeight: 600,
                                    cursor: subscribing ? 'not-allowed' : 'pointer',
                                    opacity: subscribing ? 0.7 : 1
                                }}
                            >
                                {subscribing
                                    ? (lang === 'te' ? 'ప్రారంభిస్తోంది...' : 'Starting...')
                                    : (lang === 'te' ? 'మానిటరింగ్ ప్రారంభించండి' : 'Start Monitoring')
                                }
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CropAdvisory;
