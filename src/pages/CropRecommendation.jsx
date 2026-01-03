import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MapPin, ArrowRight, Loader2, ArrowLeft, Camera, Upload, CheckCircle, X, Navigation, MapPinned } from 'lucide-react';
import LanguageSelector from '../components/LanguageSelector';
import './CropRecommendation.css';
import './SoilUpload.css';
import '../styles/DecisionIntelligence.css';
import {
    RiskIndicator,
    ConfidenceBadge,
    RiskBreakdown,
    DecisionGradeBanner,
    ExplanationCard,
    WhatIfDropdown,
    ScenarioResult,
    ConfidenceMetadata
} from '../components/DecisionIntelligence';
import { ML_API_URL } from '../config/api';

const CropRecommendation = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const [locationQuery, setLocationQuery] = React.useState('');
    const [recommendations, setRecommendations] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [weather, setWeather] = React.useState(null);
    const [manualSoilType, setManualSoilType] = React.useState('');
    const [showSoilSelector, setShowSoilSelector] = React.useState(false);

    // Soil Image Upload States
    const [showSoilUpload, setShowSoilUpload] = React.useState(false);
    const [soilImage, setSoilImage] = React.useState(null);
    const [soilImagePreview, setSoilImagePreview] = React.useState(null);
    const [classifyingImage, setClassifyingImage] = React.useState(false);
    const [classificationResult, setClassificationResult] = React.useState(null);
    const [showSoilCorrection, setShowSoilCorrection] = React.useState(false);
    const [correctedSoilType, setCorrectedSoilType] = React.useState('');
    const fileInputRef = React.useRef(null);

    // HACKATHON: What-if scenario states
    const [selectedScenario, setSelectedScenario] = React.useState(null);
    const [scenarioResult, setScenarioResult] = React.useState(null);
    const [loadingScenario, setLoadingScenario] = React.useState(false);

    // NPK Input from Soil Report
    const [showNPKInput, setShowNPKInput] = React.useState(false);
    const [customNPK, setCustomNPK] = React.useState({ n: '', p: '', k: '', ph: '' });

    // GPS Location State
    const [gettingLocation, setGettingLocation] = React.useState(false);
    const [gpsAccuracy, setGpsAccuracy] = React.useState(null);
    const [gpsCoords, setGpsCoords] = React.useState(null);

    const lang = i18n.language === 'te' ? 'te' : 'en';

    // Restore recommendations when navigating back from advisory
    React.useEffect(() => {
        if (location.state?.recommendations) {
            setRecommendations(location.state.recommendations);
            if (location.state.locationQuery) {
                setLocationQuery(location.state.locationQuery);
            }
        }
    }, [location.state]);

    const cropNamesTe = {
        'Rice': 'వరి',
        'Cotton': 'పత్తి',
        'Maize': 'మొక్కజొన్న',
        'Groundnut': 'వేరుశెనగ',
        'Chilli': 'మిర్చి',
        'Sugarcane': 'చెరకు',
        'Turmeric': 'పసుపు',
        'Tobacco': 'పొగాకు',
        'Pulses': 'పప్పులు',
        'Sorghum': 'జొన్న',
        'Millets': 'చిరుధాన్యాలు',
        'Sunflower': 'సూర్యకాంతం',
        'Sesame': 'నువ్వులు',
        'Castor': 'ఆముదం',
        'Bengal Gram': 'శెనగలు',
        'Red Gram': 'కందులు',
        'Black Gram': 'మినుములు',
        'Green Gram': 'పెసలు',
        'Onion': 'ఉల్లి',
        'Tomato': 'టమాటో',
        'Banana': 'అరటి',
        'Mango': 'మామిడి',
        'Coconut': 'కొబ్బరి',
        'Wheat': 'గోధుమ'
    };

    const labels = {
        yieldHigh: lang === 'te' ? 'దిగుబడి: అధికం' : 'Yield: High',
        yieldMedium: lang === 'te' ? 'దిగుబడి: మధ్యస్థం' : 'Yield: Medium',
        yieldLow: lang === 'te' ? 'దిగుబడి: తక్కువ' : 'Yield: Low',
        riskLow: lang === 'te' ? 'రిస్క్: తక్కువ' : 'Risk: Low',
        riskMedium: lang === 'te' ? 'రిస్క్: మధ్యస్థం' : 'Risk: Medium',
        riskHigh: lang === 'te' ? 'రిస్క్: అధికం' : 'Risk: High',
        water: lang === 'te' ? 'నీరు' : 'Water',
        confidence: lang === 'te' ? 'విశ్వాసం' : 'Confidence',
        season: lang === 'te' ? 'సీజన్' : 'Season',
        location: lang === 'te' ? 'ప్రాంతం' : 'Location',
        soilType: lang === 'te' ? 'మట్టి రకం' : 'Soil Type',
        edit: lang === 'te' ? 'మార్చండి' : 'Edit',
        uploadSoilImage: lang === 'te' ? 'మట్టి ఫోటో అప్‌లోడ్ చేయండి' : 'Upload Soil Photo',
        takePhoto: lang === 'te' ? 'ఫోటో తీయండి' : 'Take Photo',
        chooseFile: lang === 'te' ? 'ఫైల్ ఎంచుకోండి' : 'Choose File',
        analyzing: lang === 'te' ? 'విశ్లేషిస్తోంది...' : 'Analyzing...',
        useThisSoil: lang === 'te' ? 'ఈ మట్టిని ఉపయోగించండి' : 'Use This Soil',
        retake: lang === 'te' ? 'మళ్ళీ తీయండి' : 'Retake',
        wrongPrediction: lang === 'te' ? 'తప్పు అంచనా?' : 'Wrong prediction?',
        selectCorrectSoil: lang === 'te' ? 'సరైన మట్టి ఎంచుకోండి' : 'Select correct soil',
        reAnalyze: lang === 'te' ? 'మళ్ళీ విశ్లేషించండి' : 'Re-analyze'
    };

    // Soil types with bilingual names
    const soilTypes = [
        { en: 'Alluvial', te: 'ఒండ్ర మట్టి' },
        { en: 'Black Cotton', te: 'నల్ల పత్తి మట్టి' },
        { en: 'Clay', te: 'బంక మట్టి' },
        { en: 'Laterite', te: 'జల్లి మట్టి' },
        { en: 'Loamy', te: 'లోమీ మట్టి' },
        { en: 'Red Sandy Loam', te: 'ఎర్ర ఇసుక మట్టి' },
        { en: 'Saline', te: 'ఉప్పు మట్టి' },
        { en: 'Sandy', te: 'ఇసుక మట్టి' }
    ];

    // Fetch weather for minimal display
    React.useEffect(() => {
        navigator.geolocation.getCurrentPosition(
            (pos) => fetchWeather(pos.coords.latitude, pos.coords.longitude),
            () => fetchWeather(17.3850, 78.4867)
        );
    }, []);

    const fetchWeather = async (lat, lon) => {
        try {
            const API_KEY = 'dd587855fbdac207034b854ea3e03c00';
            const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`);
            const data = await res.json();
            setWeather(data);
        } catch (e) { console.error(e); }
    };

    // Get accurate GPS location with reverse geocoding
    const getGPSLocation = () => {
        if (!navigator.geolocation) {
            alert(lang === 'te' ? 'మీ బ్రౌజర్ GPS సపోర్ట్ చేయదు' : 'GPS not supported in your browser');
            return;
        }

        setGettingLocation(true);
        setGpsAccuracy(null);

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const accuracy = Math.round(position.coords.accuracy);

                setGpsCoords({ lat, lon });
                setGpsAccuracy(accuracy);
                setCoords({ lat, lon });

                // Reverse geocode to get place name
                try {
                    const API_KEY = 'dd587855fbdac207034b854ea3e03c00';
                    const geoUrl = `https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lon}&limit=1&appid=${API_KEY}`;
                    console.log('[GPS] Fetching reverse geocode:', geoUrl);

                    const res = await fetch(geoUrl);
                    const data = await res.json();
                    console.log('[GPS] Reverse geocode response:', data);

                    if (data && Array.isArray(data) && data.length > 0) {
                        const place = data[0];
                        // Always use the name - it's always present
                        const placeName = place.name || 'Unknown';
                        const stateName = place.state || '';
                        const fullLocation = stateName ? `${placeName}, ${stateName}` : placeName;

                        console.log('[GPS] Setting location to:', fullLocation);
                        setLocationQuery(fullLocation);

                        // Auto-search after a short delay
                        setTimeout(() => {
                            handleSearch(null, fullLocation, null, { lat, lon });
                        }, 200);
                    } else {
                        // API returned but no results - use friendly name
                        console.warn('[GPS] No geocode results, showing generic location');
                        const genericName = lang === 'te' ? 'మీ ప్రాంతం' : 'Your Location';
                        setLocationQuery(genericName);
                        setTimeout(() => {
                            handleSearch(null, genericName, null, { lat, lon });
                        }, 200);
                    }
                } catch (err) {
                    console.error('[GPS] Reverse geocoding error:', err);
                    // On error, still show a friendly name, not coordinates
                    const fallback = lang === 'te' ? 'మీ ప్రాంతం' : 'Your Location';
                    setLocationQuery(fallback);
                }

                setGettingLocation(false);
            },
            (error) => {
                setGettingLocation(false);
                console.error('GPS Error:', error);
                if (error.code === 1) {
                    alert(lang === 'te' ? 'లొకేషన్ పర్మిషన్ ఇవ్వండి' : 'Please allow location permission');
                } else if (error.code === 2) {
                    alert(lang === 'te' ? 'GPS అందుబాటులో లేదు' : 'GPS not available');
                } else {
                    alert(lang === 'te' ? 'లొకేషన్ పొందలేకపోయాము' : 'Could not get location');
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    };

    const getCropName = (cropName) => {
        if (lang === 'te' && cropNamesTe[cropName]) {
            return cropNamesTe[cropName];
        }
        return cropName;
    };

    const getYieldLabel = (yield_potential) => {
        if (lang === 'te') {
            if (yield_potential === 'High') return 'దిగుబడి: అధికం';
            if (yield_potential === 'Medium') return 'దిగుబడి: మధ్యస్థం';
            return 'దిగుబడి: తక్కువ';
        }
        return `Yield: ${yield_potential}`;
    };

    const getRiskLabel = (risk_factor) => {
        if (lang === 'te') {
            if (risk_factor === 'Low') return 'రిస్క్: తక్కువ';
            if (risk_factor === 'Medium') return 'రిస్క్: మధ్యస్థం';
            return 'రిస్క్: అధికం';
        }
        return `Risk: ${risk_factor}`;
    };

    // Soil Image Upload Handlers
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSoilImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setSoilImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
            setClassificationResult(null);
        }
    };

    const handleCameraCapture = () => {
        if (fileInputRef.current) {
            fileInputRef.current.setAttribute('capture', 'environment');
            fileInputRef.current.click();
        }
    };

    const handleFileSelect = () => {
        if (fileInputRef.current) {
            fileInputRef.current.removeAttribute('capture');
            fileInputRef.current.click();
        }
    };

    const classifySoilImage = async () => {
        if (!soilImage) return;

        setClassifyingImage(true);
        try {
            const formData = new FormData();
            formData.append('file', soilImage);

            const res = await fetch(`${ML_API_URL}/classify-soil`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            console.log('Classification result:', data);

            // Ensure confidence is a valid number
            if (data && typeof data.confidence === 'number') {
                setClassificationResult(data);
            } else {
                // If confidence is missing or invalid, set a default
                setClassificationResult({
                    ...data,
                    confidence: data.confidence || 0.7,
                    top_3: data.top_3 || []
                });
            }
        } catch (err) {
            console.error('Classification error:', err);
            alert(lang === 'te' ? 'వర్గీకరణలో లోపం. దయచేసి మళ్ళీ ప్రయత్నించండి.' : 'Classification failed. Please try again.');
        } finally {
            setClassifyingImage(false);
        }
    };

    const useSoilClassification = () => {
        if (classificationResult) {
            setManualSoilType(classificationResult.soil_type);
            setShowSoilUpload(false);
            setShowSoilSelector(false);
        }
    };

    const resetSoilUpload = () => {
        setSoilImage(null);
        setSoilImagePreview(null);
        setClassificationResult(null);
    };

    const [coords, setCoords] = React.useState(null);

    // ... (existing code)

    const handleSearch = async (e, overrideQuery = null, overrideSoil = null, overrideCoords = null) => {
        if (e) e.preventDefault();
        const query = overrideQuery || locationQuery;
        if (!query.trim()) return;

        setLoading(true);
        setRecommendations(null);
        try {
            const payload = { location_name: query };
            // Use classified soil or manual selection
            if (overrideSoil) {
                payload.manual_soil_type = overrideSoil;
            } else if (manualSoilType) {
                payload.manual_soil_type = manualSoilType;
            }

            // Handle coordinates
            // Always fetch fresh coordinates for the searched location
            let lat = overrideCoords?.lat || null;
            let lon = overrideCoords?.lon || null;

            // Geocode the location name to get coordinates
            if (!lat || !lon) {
                try {
                    const API_KEY = 'dd587855fbdac207034b854ea3e03c00';
                    const geoRes = await fetch(`https://api.openweathermap.org/geo/1.0/direct?q=${query}&limit=1&appid=${API_KEY}`);
                    const geoData = await geoRes.json();
                    if (geoData && geoData.length > 0) {
                        lat = geoData[0].lat;
                        lon = geoData[0].lon;
                        console.log(`Geocoded ${query} to:`, { lat, lon });
                    }
                } catch (e) {
                    console.error("Geocoding failed", e);
                }
            }

            if (lat && lon) {
                payload.lat = lat;
                payload.lon = lon;
                setCoords({ lat, lon });
            }

            // Add custom NPK from soil report if provided
            if (customNPK.n || customNPK.p || customNPK.k || customNPK.ph) {
                payload.custom_npk = {};
                if (customNPK.n) payload.custom_npk.n = parseFloat(customNPK.n);
                if (customNPK.p) payload.custom_npk.p = parseFloat(customNPK.p);
                if (customNPK.k) payload.custom_npk.k = parseFloat(customNPK.k);
                if (customNPK.ph) payload.custom_npk.ph = parseFloat(customNPK.ph);
            }

            console.log("Sending Payload:", payload); // DEBUG PAYLOAD

            const res = await fetch(`${ML_API_URL}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Server error (${res.status}): ${errorText.substring(0, 100)}`);
            }

            const data = await res.json();
            console.log("Recommend Response:", data);
            setRecommendations(data);

            // Trigger unknown soil card only if explicitly unknown zone
            if (data.context.soil_zone === 'Unknown Region' && !overrideSoil && !manualSoilType) {
                setShowSoilSelector(true);
            } else {
                setShowSoilSelector(false);
            }

        } catch (err) {
            console.error("Search Error:", err);
            const msg = lang === 'te'
                ? "సేవ అందుబాటులో లేదు. సలహా: దయచేసి 1 నిమిషం ఆగి మళ్ళీ ప్రయత్నించండి (సర్వర్ నిద్రలేస్తోంది)."
                : `Service unavailable: ${err.message || 'Check connection'}. Tip: Wait 1 min for server to wake up.`;
            alert(msg);
        } finally {
            setLoading(false);
        }
    };

    // HACKATHON: Handle what-if scenario simulation
    const handleScenarioSimulation = async (crop, recommendation, scenarioType, params) => {
        setLoadingScenario(true);
        setSelectedScenario({ crop, scenarioType, params });

        try {
            const payload = {
                crop: crop,
                current_recommendation: recommendation,
                scenario_type: scenarioType,
                season: recommendations?.context?.season || 'Kharif',
                ...params
            };

            const res = await fetch(`${ML_API_URL}/whatif-scenario`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            console.log('Scenario result:', data);

            if (data.success) {
                setScenarioResult(data.simulated);
            } else {
                alert(lang === 'te' ? 'దోషం సంభవించింది' : 'Error occurred');
            }
        } catch (err) {
            console.error('Scenario simulation error:', err);
            alert(lang === 'te' ? 'దోషం సంభవించింది' : 'Error occurred');
        } finally {
            setLoadingScenario(false);
        }
    };

    // ... existing handlers ...

    return (
        <div className="min-app">
            <header className="min-header">
                <div className="header-left">
                    <button onClick={() => navigate('/home')}>
                        <ArrowLeft size={20} />
                    </button>
                    <span className="min-brand">{t('cropRecommend', 'Crop Recommend')}</span>
                </div>
                {weather && (
                    <div className="min-weather">
                        <span>{Math.round(weather.main.temp)}°</span>
                        <span className="sep">•</span>
                        <span>{weather.weather[0].main}</span>
                    </div>
                )}
            </header>

            <main className="min-main">
                <section className="min-hero">
                    <h1 className="hero-title">{t('findBestCrops', 'Find Best Crops')}</h1>
                    <p className="hero-sub">{t('aiBased', 'AI-based recommendations for your soil')}</p>


                    <form className="min-search-form" onSubmit={(e) => handleSearch(e)}>
                        <div className="input-wrapper">
                            <MapPin size={18} className="icon-grey" />
                            <input
                                type="text"
                                value={locationQuery}
                                onChange={(e) => setLocationQuery(e.target.value)}
                                placeholder={t('enterLocation', 'Enter village or mandal...')}
                            />
                        </div>
                        <button
                            type="button"
                            className="gps-btn"
                            onClick={getGPSLocation}
                            disabled={gettingLocation}
                            title={lang === 'te' ? 'GPS లొకేషన్ పొందండి' : 'Get GPS Location'}
                        >
                            {gettingLocation ? <Loader2 className="animate-spin" size={20} /> : <Navigation size={20} />}
                        </button>
                        <button type="submit" disabled={loading}>
                            {loading ? <Loader2 className="animate-spin" size={20} /> : <ArrowRight size={20} />}
                        </button>
                    </form>

                    {/* GPS Accuracy Indicator */}
                    {gpsCoords && gpsAccuracy && (
                        <div className="gps-accuracy-badge">
                            <MapPinned size={14} />
                            <span>{lang === 'te' ? `GPS: ±${gpsAccuracy}మీ ఖచ్చితత్వం` : `GPS: ±${gpsAccuracy}m accuracy`}</span>
                            {gpsAccuracy < 50 && <span className="accuracy-good">✓</span>}
                        </div>
                    )}

                    {/* Soil Upload Trigger if explicitly unknown or requested */}
                    {showSoilSelector && (
                        <div className="soil-upload-trigger">
                            <button className="soil-upload-btn" onClick={() => setShowSoilUpload(true)}>
                                <Camera size={16} />
                                {t('identifySoil', 'Identify Soil from Photo')}
                            </button>
                        </div>
                    )}
                </section>

                {/* Soil Context Card */}
                {recommendations && recommendations.context && (
                    <div className="context-card">
                        <div className="context-header">
                            <div className="ctx-main">
                                <span className="ctx-label">{t('soilType', 'SOIL TYPE')}</span>
                                <div className="ctx-value" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    {manualSoilType || recommendations.context.soil_type}
                                    {recommendations.context.soil_source === 'user_selected' && (
                                        <span className="badge badge-neutral" style={{ fontSize: '10px' }}>Manual</span>
                                    )}
                                    <button className="edit-soil-btn" onClick={() => setShowSoilUpload(true)}>
                                        {t('change', 'Change')}
                                    </button>
                                </div>
                            </div>
                            <div className="ctx-weather">
                                <span className="weather-temp">{recommendations.context.weather.temp}°</span>
                                <span className="weather-desc">{recommendations.context.weather.forecast_summary?.split('.')[0]}</span>
                            </div>
                        </div>

                        <div className="soil-metrics">
                            <div className="metric">
                                <span className="m-label">pH</span>
                                <span className="m-value">{recommendations.context.soil_params.ph}</span>
                            </div>
                            <div className="metric">
                                <span className="m-label">N</span>
                                <span className="m-value">{recommendations.context.soil_params.n}</span>
                            </div>
                            <div className="metric">
                                <span className="m-label">P</span>
                                <span className="m-value">{recommendations.context.soil_params.p}</span>
                            </div>
                            <div className="metric">
                                <span className="m-label">K</span>
                                <span className="m-value">{recommendations.context.soil_params.k}</span>
                            </div>
                        </div>

                        {/* Have Soil Report - Edit NPK */}
                        <div style={{
                            marginTop: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px'
                        }}>
                            <button
                                onClick={() => setShowNPKInput(!showNPKInput)}
                                style={{
                                    background: showNPKInput ? '#16A34A' : 'transparent',
                                    color: showNPKInput ? 'white' : '#16A34A',
                                    border: '1px solid #16A34A',
                                    borderRadius: '8px',
                                    padding: '8px 16px',
                                    fontSize: '12px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}
                            >
                                📋 {lang === 'te' ? 'మట్టి రిపోర్ట్ ఉంది?' : 'Have Soil Report?'}
                            </button>
                            {(customNPK.n || customNPK.p || customNPK.k) && (
                                <span style={{
                                    fontSize: '10px',
                                    background: '#DCFCE7',
                                    color: '#166534',
                                    padding: '4px 8px',
                                    borderRadius: '4px'
                                }}>
                                    ✓ Custom NPK Set
                                </span>
                            )}
                        </div>

                        {/* NPK Input Form */}
                        {showNPKInput && (
                            <div style={{
                                marginTop: '16px',
                                padding: '16px',
                                background: 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
                                borderRadius: '12px',
                                border: '1px solid #86EFAC'
                            }}>
                                <div style={{
                                    fontSize: '13px',
                                    fontWeight: '600',
                                    color: '#166534',
                                    marginBottom: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}>
                                    📊 {lang === 'te' ? 'మట్టి రిపోర్ట్ విలువలు నమోదు చేయండి' : 'Enter Soil Report Values'}
                                </div>

                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(4, 1fr)',
                                    gap: '10px',
                                    marginBottom: '12px'
                                }}>
                                    {['n', 'p', 'k', 'ph'].map(field => (
                                        <div key={field} style={{ textAlign: 'center' }}>
                                            <label style={{
                                                display: 'block',
                                                fontSize: '11px',
                                                fontWeight: '600',
                                                color: '#166534',
                                                marginBottom: '4px'
                                            }}>
                                                {field === 'ph' ? 'pH' : field.toUpperCase()}
                                                <span style={{ color: '#6B7280', fontWeight: '400' }}>
                                                    {field !== 'ph' ? ' (kg/ha)' : ''}
                                                </span>
                                            </label>
                                            <input
                                                type="number"
                                                step={field === 'ph' ? '0.1' : '1'}
                                                min={field === 'ph' ? '4' : '0'}
                                                max={field === 'ph' ? '10' : '500'}
                                                value={customNPK[field]}
                                                onChange={(e) => setCustomNPK({ ...customNPK, [field]: e.target.value })}
                                                placeholder={field === 'ph' ? '7.0' : '150'}
                                                style={{
                                                    width: '100%',
                                                    padding: '8px',
                                                    borderRadius: '8px',
                                                    border: '1px solid #86EFAC',
                                                    fontSize: '14px',
                                                    fontWeight: '600',
                                                    textAlign: 'center',
                                                    background: 'white'
                                                }}
                                            />
                                        </div>
                                    ))}
                                </div>

                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button
                                        onClick={() => {
                                            setShowNPKInput(false);
                                            handleSearch(null, locationQuery);
                                        }}
                                        disabled={loading}
                                        style={{
                                            flex: 1,
                                            background: 'linear-gradient(135deg, #16A34A 0%, #15803D 100%)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '8px',
                                            padding: '12px',
                                            fontSize: '13px',
                                            fontWeight: '600',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '6px'
                                        }}
                                    >
                                        🔄 {lang === 'te' ? 'మళ్ళీ విశ్లేషించు' : 'Re-Analyze with Report'}
                                    </button>
                                    <button
                                        onClick={() => {
                                            setCustomNPK({ n: '', p: '', k: '', ph: '' });
                                        }}
                                        style={{
                                            background: 'white',
                                            color: '#DC2626',
                                            border: '1px solid #DC2626',
                                            borderRadius: '8px',
                                            padding: '12px 16px',
                                            fontSize: '13px',
                                            fontWeight: '600',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        ✕
                                    </button>
                                </div>

                                <p style={{
                                    fontSize: '10px',
                                    color: '#6B7280',
                                    marginTop: '8px',
                                    textAlign: 'center'
                                }}>
                                    {lang === 'te'
                                        ? 'మీ మట్టి పరీక్ష నివేదిక నుండి విలువలను నమోదు చేయండి'
                                        : 'Enter values from your soil test report for accurate recommendations'}
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Inline Soil Analyzer - no overlay */}
                {showSoilUpload && recommendations && (
                    <div className="soil-analyzer-inline-card">
                        <div className="soil-upload-content">
                            <div className="soil-upload-header">
                                <h3>{labels.uploadSoilImage}</h3>
                                <button className="close-btn" onClick={() => { setShowSoilUpload(false); resetSoilUpload(); }}>
                                    <X size={20} />
                                </button>
                            </div>

                            {!soilImagePreview ? (
                                <div className="upload-options">
                                    <div className="upload-option" onClick={handleCameraCapture}>
                                        <Camera size={32} />
                                        <span>{labels.takePhoto}</span>
                                    </div>
                                    <div className="upload-option" onClick={handleFileSelect}>
                                        <Upload size={32} />
                                        <span>{labels.chooseFile}</span>
                                    </div>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        style={{ display: 'none' }}
                                        accept="image/*"
                                        onChange={handleImageUpload}
                                    />
                                </div>
                            ) : (
                                <div>
                                    <div className="image-preview">
                                        <img src={soilImagePreview} alt="Soil Preview" />
                                    </div>

                                    {classificationResult ? (
                                        <div className="soil-result">
                                            <div className="icon">
                                                <CheckCircle size={40} color="#2E7D32" />
                                            </div>
                                            <h4>{classificationResult.soil_type}</h4>
                                            <p className="confidence">
                                                {Math.round(classificationResult.confidence * 100)}% Confidence
                                            </p>
                                            <button className="use-soil-btn" onClick={() => {
                                                setManualSoilType(classificationResult.soil_type);
                                                setShowSoilUpload(false);
                                                setShowSoilSelector(false);
                                                handleSearch(null, locationQuery, classificationResult.soil_type, coords);
                                            }}>
                                                {labels.useThisSoil}
                                            </button>

                                            {!showSoilCorrection ? (
                                                <button
                                                    className="wrong-prediction-btn"
                                                    onClick={() => {
                                                        setShowSoilCorrection(true);
                                                        setCorrectedSoilType(classificationResult.soil_type);
                                                    }}
                                                    style={{
                                                        marginTop: '8px',
                                                        width: '100%',
                                                        padding: '10px',
                                                        background: 'white',
                                                        color: '#16A34A',
                                                        border: '2px solid #16A34A',
                                                        borderRadius: '10px',
                                                        fontSize: '14px',
                                                        fontWeight: '600',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    {labels.wrongPrediction}
                                                </button>
                                            ) : (
                                                <>
                                                    <div style={{ marginTop: '12px', textAlign: 'left' }}>
                                                        <label style={{
                                                            display: 'block',
                                                            fontSize: '13px',
                                                            fontWeight: '600',
                                                            color: '#374151',
                                                            marginBottom: '8px'
                                                        }}>
                                                            {labels.selectCorrectSoil}
                                                        </label>
                                                        <select
                                                            value={correctedSoilType}
                                                            onChange={(e) => setCorrectedSoilType(e.target.value)}
                                                            style={{
                                                                width: '100%',
                                                                padding: '12px',
                                                                border: '2px solid #D1D5DB',
                                                                borderRadius: '8px',
                                                                fontSize: '14px',
                                                                fontWeight: '500',
                                                                color: '#111827',
                                                                background: 'white'
                                                            }}
                                                        >
                                                            {soilTypes.map((soil) => (
                                                                <option key={soil.en} value={soil.en}>
                                                                    {soil.en} / {soil.te}
                                                                </option>
                                                            ))}
                                                        </select>
                                                    </div>
                                                    <button
                                                        className="use-soil-btn"
                                                        onClick={() => {
                                                            setManualSoilType(correctedSoilType);
                                                            setShowSoilUpload(false);
                                                            setShowSoilSelector(false);
                                                            setShowSoilCorrection(false);
                                                            handleSearch(null, locationQuery, correctedSoilType, coords);
                                                        }}
                                                        style={{ marginTop: '12px' }}
                                                    >
                                                        {labels.reAnalyze}
                                                    </button>
                                                </>
                                            )}
                                        </div>
                                    ) : classifyingImage ? (
                                        <div className="analyzing-state">
                                            <div className="spinner"></div>
                                            <p>{labels.analyzing}</p>
                                        </div>
                                    ) : (
                                        <div className="preview-actions">
                                            <button onClick={() => { setSoilImagePreview(null); setSoilImage(null); }} className="retake-btn">
                                                {labels.retake}
                                            </button>
                                            <button onClick={classifySoilImage} className="analyze-btn">
                                                Analyze Soil
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {
                    recommendations && (
                        <section className="rec-section">
                            <div className="section-title">
                                {t('recommend.recommendedCrops', 'Recommended Crops')}
                                <span style={{ fontSize: '0.8em', color: '#6B7280', marginLeft: '0.5rem' }}>
                                    ({recommendations.recommendations?.length || 0})
                                </span>
                                {recommendations.model_type === 'ml_trained' && (
                                    <span style={{
                                        fontSize: '10px',
                                        background: '#16A34A',
                                        color: 'white',
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        fontWeight: 'normal',
                                        marginLeft: 'auto'
                                    }}>
                                        🤖 AI Model
                                    </span>
                                )}
                            </div>

                            {(!recommendations.recommendations || recommendations.recommendations.length === 0) ? (
                                <div className="empty-state" style={{ textAlign: 'center', padding: '2rem', color: '#4B5563' }}>
                                    <span className="empty-icon" style={{ fontSize: '2rem', display: 'block', marginBottom: '0.5rem' }}>🌾</span>
                                    <p style={{ fontWeight: 500 }}>{lang === 'te' ? 'పంటలు కనుగొనబడలేదు' : 'No crops found for this location'}</p>
                                    <p style={{ fontSize: '0.9rem', color: '#6B7280', margin: '0.5rem 0' }}>
                                        {lang === 'te' ? 'దయచేసి మట్టి రకం మార్చండి' : 'Try selecting a different soil type'}
                                    </p>
                                    <button className="soil-upload-btn" style={{ marginTop: '1rem', background: '#16A34A', border: 'none' }} onClick={() => setShowSoilUpload(true)}>
                                        {lang === 'te' ? 'మట్టి మార్చండి' : 'Change Soil'}
                                    </button>
                                </div>
                            ) : (
                                <>
                                    {/* Horizontal Carousel - One Crop Per Page */}
                                    <div className="rec-carousel-wrapper">
                                        <div className="rec-carousel" id="cropCarousel">
                                            {recommendations.recommendations.map((rec, idx) => (
                                                <div key={idx} className={`rec-card ${idx < 2 ? 'rank-1' : ''}`}>
                                                    <div className="rec-header">
                                                        <h3>{getCropName(rec.crop)}</h3>
                                                        <div className="rec-badges">
                                                            <span className={`badge ${rec.yield_potential === 'High' ? 'badge-success' : 'badge-neutral'}`}>
                                                                {getYieldLabel(rec.yield_potential)}
                                                            </span>
                                                            <span className={`badge ${rec.risk_factor === 'Low' ? 'badge-success' : 'badge-warning'}`}>
                                                                {getRiskLabel(rec.risk_factor)}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <p className="rec-reason">{rec.reason}</p>

                                                    {/* HACKATHON: Risk Analysis */}
                                                    {rec.risk_analysis && (
                                                        <>
                                                            <RiskIndicator
                                                                lossProbability={rec.risk_analysis.loss_probability}
                                                                riskLevel={rec.risk_analysis.risk_level}
                                                            />

                                                            {rec.risk_analysis.risk_breakdown && (
                                                                <RiskBreakdown riskBreakdown={rec.risk_analysis.risk_breakdown} />
                                                            )}

                                                            {rec.decision_grade && (
                                                                <DecisionGradeBanner decisionGrade={rec.decision_grade} />
                                                            )}
                                                        </>
                                                    )}

                                                    {/* HACKATHON: Telugu Explanation */}
                                                    {rec.explanation_te && (
                                                        <ExplanationCard
                                                            explanation={{ explanation_te: rec.explanation_te }}
                                                            language={lang}
                                                            title={lang === 'te' ? 'ఎందుకు?' : 'Why?'}
                                                        />
                                                    )}

                                                    {rec.fertilizer_recommendation && (
                                                        <div className="rec-tip" style={{
                                                            fontSize: '11px',
                                                            marginTop: '8px',
                                                            padding: '6px',
                                                            background: '#FEF3C7',
                                                            borderRadius: '6px',
                                                            color: '#B45309'
                                                        }}>
                                                            <span className="tip-icon">💡</span>
                                                            {rec.fertilizer_recommendation}
                                                        </div>
                                                    )}

                                                    {/* Smart Fertilizer Plan */}
                                                    {rec.fertilizer_plan && !rec.fertilizer_plan.error && (
                                                        <div className="fertilizer-plan" style={{
                                                            marginTop: '12px',
                                                            padding: '12px',
                                                            background: 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
                                                            borderRadius: '8px',
                                                            border: '1px solid #86EFAC'
                                                        }} onClick={(e) => e.stopPropagation()}>
                                                            <div style={{
                                                                display: 'flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'space-between',
                                                                marginBottom: '10px'
                                                            }}>
                                                                <div style={{
                                                                    fontSize: '13px',
                                                                    fontWeight: '600',
                                                                    color: '#166534',
                                                                    display: 'flex',
                                                                    alignItems: 'center',
                                                                    gap: '6px'
                                                                }}>
                                                                    🌱 Smart Fertilizer Plan
                                                                </div>
                                                                {rec.fertilizer_plan.cost_benefit_analysis && (
                                                                    <div style={{
                                                                        fontSize: '10px',
                                                                        background: rec.fertilizer_plan.cost_benefit_analysis.sustainable ? '#16A34A' : '#EA580C',
                                                                        color: 'white',
                                                                        padding: '2px 6px',
                                                                        borderRadius: '4px',
                                                                        display: 'flex',
                                                                        alignItems: 'center',
                                                                        gap: '3px'
                                                                    }}>
                                                                        ⭐ {rec.fertilizer_plan.cost_benefit_analysis.sustainability_score}/10
                                                                    </div>
                                                                )}
                                                            </div>

                                                            {/* NPK Status */}
                                                            {rec.fertilizer_plan.npk_analysis && (
                                                                <div style={{
                                                                    display: 'grid',
                                                                    gridTemplateColumns: 'repeat(3, 1fr)',
                                                                    gap: '6px',
                                                                    marginBottom: '10px'
                                                                }}>
                                                                    {['n', 'p', 'k'].map(nutrient => {
                                                                        const deficit = rec.fertilizer_plan.npk_analysis.deficit[nutrient];
                                                                        const status = rec.fertilizer_plan.npk_analysis.status[nutrient];
                                                                        const color = status === 'Deficit' ? '#DC2626' : status === 'Excess' ? '#2563EB' : '#16A34A';

                                                                        return (
                                                                            <div key={nutrient} style={{
                                                                                padding: '6px',
                                                                                background: 'white',
                                                                                borderRadius: '6px',
                                                                                textAlign: 'center'
                                                                            }}>
                                                                                <div style={{
                                                                                    fontSize: '10px',
                                                                                    color: '#6B7280',
                                                                                    fontWeight: '500',
                                                                                    marginBottom: '2px'
                                                                                }}>
                                                                                    {nutrient.toUpperCase()}
                                                                                </div>
                                                                                <div style={{
                                                                                    fontSize: '11px',
                                                                                    fontWeight: '600',
                                                                                    color: color
                                                                                }}>
                                                                                    {deficit > 0 ? '+' : ''}{Math.round(deficit)} kg
                                                                                </div>
                                                                                <div style={{
                                                                                    fontSize: '9px',
                                                                                    color: color
                                                                                }}>
                                                                                    {status}
                                                                                </div>
                                                                            </div>
                                                                        );
                                                                    })}
                                                                </div>
                                                            )}

                                                            {/* Fertilizer Products */}
                                                            {rec.fertilizer_plan.fertilizer_recommendations && rec.fertilizer_plan.fertilizer_recommendations.length > 0 && (
                                                                <div style={{ marginBottom: '10px' }}>
                                                                    <div style={{
                                                                        fontSize: '11px',
                                                                        fontWeight: '600',
                                                                        color: '#166534',
                                                                        marginBottom: '6px'
                                                                    }}>
                                                                        📦 Recommended Products:
                                                                    </div>
                                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                                                        {rec.fertilizer_plan.fertilizer_recommendations.slice(0, 3).map((fert, fidx) => (
                                                                            <div key={fidx} style={{
                                                                                padding: '6px 8px',
                                                                                background: 'white',
                                                                                borderRadius: '6px',
                                                                                display: 'flex',
                                                                                alignItems: 'center',
                                                                                justifyContent: 'space-between',
                                                                                fontSize: '10px'
                                                                            }}>
                                                                                <div style={{ flex: 1 }}>
                                                                                    <div style={{ fontWeight: '600', color: '#1F2937', marginBottom: '2px' }}>
                                                                                        {fert.product}
                                                                                    </div>
                                                                                    <div style={{ color: '#6B7280', fontSize: '9px' }}>
                                                                                        {fert.quantity_kg_per_acre} kg/acre • ₹{fert.cost_estimate}
                                                                                    </div>
                                                                                </div>
                                                                                {fert.type === 'organic' && (
                                                                                    <span style={{
                                                                                        fontSize: '8px',
                                                                                        background: '#16A34A',
                                                                                        color: 'white',
                                                                                        padding: '2px 4px',
                                                                                        borderRadius: '3px'
                                                                                    }}>
                                                                                        🌿 Organic
                                                                                    </span>
                                                                                )}
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}

                                                            {/* Cost-Benefit Summary */}
                                                            {rec.fertilizer_plan.cost_benefit_analysis && (
                                                                <div style={{
                                                                    display: 'grid',
                                                                    gridTemplateColumns: 'repeat(2, 1fr)',
                                                                    gap: '6px',
                                                                    padding: '8px',
                                                                    background: 'white',
                                                                    borderRadius: '6px'
                                                                }}>
                                                                    <div style={{ textAlign: 'center' }}>
                                                                        <div style={{ fontSize: '9px', color: '#6B7280' }}>Total Cost</div>
                                                                        <div style={{ fontSize: '12px', fontWeight: '700', color: '#DC2626' }}>
                                                                            ₹{rec.fertilizer_plan.cost_benefit_analysis.total_cost}
                                                                        </div>
                                                                    </div>
                                                                    <div style={{ textAlign: 'center' }}>
                                                                        <div style={{ fontSize: '9px', color: '#6B7280' }}>ROI</div>
                                                                        <div style={{ fontSize: '12px', fontWeight: '700', color: '#16A34A' }}>
                                                                            {rec.fertilizer_plan.cost_benefit_analysis.roi}x
                                                                        </div>
                                                                    </div>
                                                                    <div style={{ textAlign: 'center' }}>
                                                                        <div style={{ fontSize: '9px', color: '#6B7280' }}>Yield ↑</div>
                                                                        <div style={{ fontSize: '12px', fontWeight: '700', color: '#2563EB' }}>
                                                                            +{rec.fertilizer_plan.cost_benefit_analysis.expected_yield_increase_percent}%
                                                                        </div>
                                                                    </div>
                                                                    <div style={{ textAlign: 'center' }}>
                                                                        <div style={{ fontSize: '9px', color: '#6B7280' }}>Revenue ↑</div>
                                                                        <div style={{ fontSize: '12px', fontWeight: '700', color: '#16A34A' }}>
                                                                            +₹{Math.round(rec.fertilizer_plan.cost_benefit_analysis.expected_revenue_increase || 0)}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}

                                                    {/* HACKATHON: What-If Scenarios */}
                                                    {rec.risk_analysis && (
                                                        <div onClick={(e) => e.stopPropagation()}>
                                                            <WhatIfDropdown
                                                                crop={rec.crop}
                                                                recommendation={rec}
                                                                language={lang}
                                                                onScenarioSelect={(scenarioType, params) => {
                                                                    handleScenarioSimulation(rec.crop, rec, scenarioType, params);
                                                                }}
                                                            />

                                                            {/* Show scenario result if this crop is selected */}
                                                            {selectedScenario && selectedScenario.crop === rec.crop && scenarioResult && (
                                                                <ScenarioResult
                                                                    scenarioData={scenarioResult}
                                                                    language={lang}
                                                                />
                                                            )}

                                                            {loadingScenario && selectedScenario && selectedScenario.crop === rec.crop && (
                                                                <div className="risk-analysis-loading" style={{ padding: '20px' }}>
                                                                    <div className="loading-spinner"></div>
                                                                    <div className="loading-text">Simulating scenario...</div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}

                                                    {/* Navigation Button */}
                                                    <button
                                                        className="soil-upload-btn"
                                                        style={{
                                                            width: '100%',
                                                            marginTop: '12px',
                                                            background: 'linear-gradient(135deg, #16A34A 0%, #22C55E 100%)',
                                                            color: 'white',
                                                            border: 'none',
                                                            padding: '10px',
                                                            borderRadius: '10px',
                                                            fontSize: '13px',
                                                            fontWeight: '600',
                                                            cursor: 'pointer',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center',
                                                            gap: '6px'
                                                        }}
                                                        onClick={() => navigate('/advisory', {
                                                            state: {
                                                                crop: rec,
                                                                location: locationQuery || recommendations.location,
                                                                coords: coords,
                                                                recommendations: recommendations,
                                                                locationQuery: locationQuery
                                                            }
                                                        })}
                                                    >
                                                        {lang === 'te' ? 'పూర్తి సలహా చూడండి' : 'View Full Advisory'} →
                                                    </button>

                                                    <div className="rec-details">
                                                        {rec.market_price && (
                                                            <div className="detail-row" style={{
                                                                background: rec.market_price_live ? '#F0FDF4' : '#F9FAFB',
                                                                padding: '6px 8px',
                                                                borderRadius: '6px',
                                                                marginBottom: '4px'
                                                            }}>
                                                                <span className="icon">💰</span>
                                                                <div style={{ flex: 1 }}>
                                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                                        <span style={{ fontWeight: '600' }}>
                                                                            ₹{rec.market_price.price?.toLocaleString()}/{lang === 'te' ? 'క్వింటాల్' : 'Q'}
                                                                        </span>
                                                                        {rec.market_price.trend === 'up' && <span style={{ color: '#16A34A' }}>↑</span>}
                                                                        {rec.market_price.trend === 'down' && <span style={{ color: '#DC2626' }}>↓</span>}
                                                                        {rec.market_price.trend === 'volatile' && <span style={{ color: '#F59E0B' }}>⚡</span>}
                                                                        {rec.market_price_live && (
                                                                            <span style={{
                                                                                fontSize: '8px',
                                                                                background: '#16A34A',
                                                                                color: 'white',
                                                                                padding: '1px 4px',
                                                                                borderRadius: '3px'
                                                                            }}>LIVE</span>
                                                                        )}
                                                                        {rec.market_price.msp && (
                                                                            <span style={{
                                                                                fontSize: '8px',
                                                                                background: '#3B82F6',
                                                                                color: 'white',
                                                                                padding: '1px 4px',
                                                                                borderRadius: '3px'
                                                                            }}>MSP</span>
                                                                        )}
                                                                    </div>
                                                                    <div style={{ fontSize: '9px', color: '#6B7280' }}>
                                                                        {rec.market_price.source || 'Market Price'}
                                                                        {rec.market_price.min_price && rec.market_price.max_price && (
                                                                            <span> • ₹{rec.market_price.min_price}-{rec.market_price.max_price}</span>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}

                                                        {/* Water Adequacy (from weather history service) */}
                                                        {rec.water_adequacy && (
                                                            <div className="detail-row" style={{
                                                                background: rec.water_adequacy.adequacy === 'Adequate' ? '#F0FDF4' :
                                                                    rec.water_adequacy.adequacy === 'Inadequate' ? '#FEF2F2' : '#FFFBEB',
                                                                padding: '6px 8px',
                                                                borderRadius: '6px',
                                                                marginBottom: '4px'
                                                            }}>
                                                                <span className="icon">🌧️</span>
                                                                <div style={{ flex: 1 }}>
                                                                    <div style={{ fontSize: '11px', fontWeight: '500' }}>
                                                                        {lang === 'te' ? 'నీటి లభ్యత' : 'Water'}: {rec.water_adequacy.adequacy}
                                                                    </div>
                                                                    <div style={{ fontSize: '9px', color: '#6B7280' }}>
                                                                        {rec.water_adequacy.irrigation_advice}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}

                                                        <div className="detail-row">
                                                            <span className="icon">💧</span>
                                                            <span>{labels.water}: {rec.water_needs}</span>
                                                        </div>
                                                        <div className="detail-row">
                                                            <span className="icon">🧪</span>
                                                            <span>{labels.confidence}: {Math.round(rec.confidence)}%</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        {/* Page Indicator Dots */}
                                        <div className="carousel-dots">
                                            {recommendations.recommendations.map((_, idx) => (
                                                <button
                                                    key={idx}
                                                    className={`carousel-dot ${idx === 0 ? 'active' : ''}`}
                                                    onClick={() => {
                                                        const carousel = document.getElementById('cropCarousel');
                                                        const cardWidth = carousel?.firstChild?.offsetWidth || 380;
                                                        carousel?.scrollTo({ left: idx * (cardWidth + 16), behavior: 'smooth' });
                                                        // Update active dot
                                                        document.querySelectorAll('.carousel-dot').forEach((dot, i) => {
                                                            dot.classList.toggle('active', i === idx);
                                                        });
                                                    }}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                </>
                            )}

                            {/* HACKATHON: Confidence Metadata Display */}
                            {recommendations.context && recommendations.context.confidence && (
                                <ConfidenceMetadata
                                    confidenceData={recommendations.context.confidence}
                                    language={lang}
                                />
                            )}
                        </section>
                    )
                }
            </main>
        </div >
    );
};

export default CropRecommendation;
