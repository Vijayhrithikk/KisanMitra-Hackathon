import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    ArrowLeft, Leaf, Calendar, MapPin, Droplets, Check,
    Navigation, ChevronRight, Loader2, AlertCircle, Sprout, Phone, MessageSquare
} from 'lucide-react';
import './CropSubscribe.css';

import { ML_API_URL } from '../config/api';
const API_BASE = ML_API_URL;

const CropSubscribe = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    // Form state
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    // Form data
    const [formData, setFormData] = useState({
        crop: location.state?.crop || '',
        sowingDate: new Date().toISOString().split('T')[0],
        areaAcres: 1,
        previousCrop: '',
        locationName: '',
        lat: 17.385,
        lon: 78.487,
        district: '',
        soilType: '',
        irrigationType: 'canal',
        notifyPhone: '',
        enableSmsUpdates: true
    });

    const [subscriptionResult, setSubscriptionResult] = useState(null);

    // Get farmer info
    const farmerId = localStorage.getItem('farmerPhone') || '7330671778';
    const farmerPhone = farmerId;

    // Crop options
    const crops = [
        { name: 'Paddy', te: 'వరి', icon: '🌾' },
        { name: 'Cotton', te: 'పత్తి', icon: '🧶' },
        { name: 'Chilli', te: 'మిర్చి', icon: '🌶️' },
        { name: 'Maize', te: 'మొక్కజొన్న', icon: '🌽' },
        { name: 'Groundnut', te: 'వేరుశెనగ', icon: '🥜' },
        { name: 'Sugarcane', te: 'చెరకు', icon: '🎋' },
        { name: 'Tomato', te: 'టమాటో', icon: '🍅' },
        { name: 'Wheat', te: 'గోధుమ', icon: '🌾' },
        { name: 'Pulses', te: 'పప్పులు', icon: '🫘' }
    ];

    // Irrigation types
    const irrigationTypes = [
        { value: 'canal', label_en: 'Canal', label_te: 'కాలువ', icon: '🌊' },
        { value: 'borewell', label_en: 'Borewell', label_te: 'బోరు', icon: '💧' },
        { value: 'drip', label_en: 'Drip', label_te: 'డ్రిప్', icon: '💦' },
        { value: 'rainfed', label_en: 'Rainfed', label_te: 'వర్షాధారం', icon: '🌧️' }
    ];

    // Labels
    const L = {
        title: lang === 'te' ? 'పంట సబ్‌స్క్రిప్షన్' : 'Crop Subscription',
        step1: lang === 'te' ? 'పంట ఎంచుకోండి' : 'Select Crop',
        step2: lang === 'te' ? 'వివరాలు' : 'Details',
        step3: lang === 'te' ? 'ధృవీకరించండి' : 'Confirm',
        selectCrop: lang === 'te' ? 'మీ పంటను ఎంచుకోండి' : 'Select your crop',
        sowingDate: lang === 'te' ? 'విత్తిన తేదీ' : 'Sowing Date',
        area: lang === 'te' ? 'విస్తీర్ణం (ఎకరాల్లో)' : 'Area (in acres)',
        previousCrop: lang === 'te' ? 'గత పంట (వైకల్పికం)' : 'Previous Crop (optional)',
        location: lang === 'te' ? 'స్థానం' : 'Location',
        useGPS: lang === 'te' ? 'GPS ఉపయోగించండి' : 'Use GPS',
        irrigation: lang === 'te' ? 'నీటి వనరు' : 'Irrigation Type',
        next: lang === 'te' ? 'తదుపరి' : 'Next',
        back: lang === 'te' ? 'వెనుకకు' : 'Back',
        subscribe: lang === 'te' ? 'సబ్‌స్క్రైబ్ చేయండి' : 'Subscribe',
        subscribing: lang === 'te' ? 'సబ్‌స్క్రైబ్ అవుతోంది...' : 'Subscribing...',
        success: lang === 'te' ? 'విజయవంతం!' : 'Success!',
        successMsg: lang === 'te' ? 'మీ పంట మానిటరింగ్ ప్రారంభమైంది' : 'Your crop monitoring has started',
        viewPlan: lang === 'te' ? 'రోజు ప్లాన్ చూడండి' : 'View Daily Plan',
        goToMyCrops: lang === 'te' ? 'నా పంటలకు వెళ్ళండి' : 'Go to My Crops',
        phoneNumber: lang === 'te' ? 'ఫోన్ నంబర్ (SMS అప్‌డేట్స్ కోసం)' : 'Phone Number (for SMS updates)',
        enableSms: lang === 'te' ? 'SMS అప్‌డేట్స్ కావాలి' : 'Enable SMS Updates',
        smsNote: lang === 'te' ? 'రోజువారీ ప్లాన్ మీ ఫోన్‌కు వస్తుంది' : 'Daily plan will be sent to your phone'
    };

    const handleGPS = () => {
        if (!navigator.geolocation) return;
        setLoading(true);
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                setFormData(prev => ({
                    ...prev,
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                }));
                // Reverse geocode
                try {
                    const res = await fetch(
                        `https://api.openweathermap.org/geo/1.0/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&limit=1&appid=dd587855fbdac207034b854ea3e03c00`
                    );
                    const data = await res.json();
                    if (data?.[0]) {
                        setFormData(prev => ({
                            ...prev,
                            locationName: data[0].name,
                            district: data[0].state || ''
                        }));
                    }
                } catch (e) {
                    console.error(e);
                }
                setLoading(false);
            },
            () => setLoading(false)
        );
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE}/subscribe-crop`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    farmerId,
                    farmerPhone,
                    crop: formData.crop,
                    sowingDate: formData.sowingDate,
                    areaAcres: parseFloat(formData.areaAcres),
                    previousCrop: formData.previousCrop,
                    locationName: formData.locationName,
                    lat: formData.lat,
                    lon: formData.lon,
                    district: formData.district,
                    soilType: formData.soilType,
                    irrigationType: formData.irrigationType,
                    notifyPhone: formData.enableSmsUpdates ? formData.notifyPhone : null,
                    enableSmsUpdates: formData.enableSmsUpdates
                })
            });

            const data = await res.json();

            if (data.success) {
                setSubscriptionResult(data);
                setSuccess(true);
            } else {
                setError(data.detail || 'Subscription failed');
            }
        } catch (err) {
            console.error(err);
            setError('Connection error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Step 1: Select Crop
    const renderStep1 = () => (
        <div className="step-content">
            <h2>{L.selectCrop}</h2>
            <div className="crop-grid">
                {crops.map((crop) => (
                    <button
                        key={crop.name}
                        className={`crop-option ${formData.crop === crop.name ? 'selected' : ''}`}
                        onClick={() => setFormData(prev => ({ ...prev, crop: crop.name }))}
                    >
                        <span className="crop-icon">{crop.icon}</span>
                        <span className="crop-name">{lang === 'te' ? crop.te : crop.name}</span>
                        {formData.crop === crop.name && <Check className="check-icon" size={20} />}
                    </button>
                ))}
            </div>
            <button
                className="next-btn"
                disabled={!formData.crop}
                onClick={() => setStep(2)}
            >
                {L.next}
                <ChevronRight size={20} />
            </button>
        </div>
    );

    // Step 2: Enter Details
    const renderStep2 = () => (
        <div className="step-content">
            <h2>{L.step2}</h2>

            {/* Sowing Date */}
            <div className="form-group">
                <label>
                    <Calendar size={18} />
                    {L.sowingDate}
                </label>
                <input
                    type="date"
                    value={formData.sowingDate}
                    onChange={(e) => setFormData(prev => ({ ...prev, sowingDate: e.target.value }))}
                />
            </div>

            {/* Area */}
            <div className="form-group">
                <label>
                    <Sprout size={18} />
                    {L.area}
                </label>
                <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={formData.areaAcres}
                    onChange={(e) => setFormData(prev => ({ ...prev, areaAcres: e.target.value }))}
                />
            </div>

            {/* Previous Crop */}
            <div className="form-group">
                <label>
                    <Leaf size={18} />
                    {L.previousCrop}
                </label>
                <select
                    value={formData.previousCrop}
                    onChange={(e) => setFormData(prev => ({ ...prev, previousCrop: e.target.value }))}
                >
                    <option value="">{lang === 'te' ? 'ఎంచుకోండి' : 'Select'}</option>
                    {crops.map((crop) => (
                        <option key={crop.name} value={crop.name}>
                            {lang === 'te' ? crop.te : crop.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Location */}
            <div className="form-group">
                <label>
                    <MapPin size={18} />
                    {L.location}
                </label>
                <div className="location-input">
                    <input
                        type="text"
                        value={formData.locationName}
                        onChange={(e) => setFormData(prev => ({ ...prev, locationName: e.target.value }))}
                        placeholder={lang === 'te' ? 'ఊరు/జిల్లా' : 'Village/District'}
                    />
                    <button className="gps-btn" onClick={handleGPS} disabled={loading}>
                        <Navigation size={18} />
                        {L.useGPS}
                    </button>
                </div>
            </div>

            {/* Irrigation Type */}
            <div className="form-group">
                <label>
                    <Droplets size={18} />
                    {L.irrigation}
                </label>
                <div className="irrigation-options">
                    {irrigationTypes.map((type) => (
                        <button
                            key={type.value}
                            className={`irrigation-btn ${formData.irrigationType === type.value ? 'selected' : ''}`}
                            onClick={() => setFormData(prev => ({ ...prev, irrigationType: type.value }))}
                        >
                            <span>{type.icon}</span>
                            <span>{lang === 'te' ? type.label_te : type.label_en}</span>
                        </button>
                    ))}
                </div>
            </div>
            {/* SMS Updates */}
            <div className="form-group sms-section">
                <label className="sms-toggle">
                    <input
                        type="checkbox"
                        checked={formData.enableSmsUpdates}
                        onChange={(e) => setFormData(prev => ({ ...prev, enableSmsUpdates: e.target.checked }))}
                    />
                    <MessageSquare size={18} />
                    {L.enableSms}
                </label>
                {formData.enableSmsUpdates && (
                    <>
                        <div className="phone-input">
                            <Phone size={18} />
                            <input
                                type="tel"
                                value={formData.notifyPhone}
                                onChange={(e) => setFormData(prev => ({ ...prev, notifyPhone: e.target.value }))}
                                placeholder={lang === 'te' ? '10 అంకెల నంబర్' : '10 digit number'}
                                maxLength={10}
                            />
                        </div>
                        <p className="sms-note">📱 {L.smsNote}</p>
                    </>
                )}
            </div>

            <div className="button-row">
                <button className="back-btn" onClick={() => setStep(1)}>
                    <ArrowLeft size={18} />
                    {L.back}
                </button>
                <button
                    className="next-btn"
                    disabled={!formData.locationName}
                    onClick={() => setStep(3)}
                >
                    {L.next}
                    <ChevronRight size={20} />
                </button>
            </div>
        </div>
    );

    // Step 3: Confirm
    const renderStep3 = () => (
        <div className="step-content">
            <h2>{L.step3}</h2>

            <div className="summary-card">
                <div className="summary-header">
                    <span className="summary-icon">
                        {crops.find(c => c.name === formData.crop)?.icon || '🌱'}
                    </span>
                    <div>
                        <h3>{formData.crop}</h3>
                        <p>{formData.locationName}</p>
                    </div>
                </div>

                <div className="summary-details">
                    <div className="detail-row">
                        <Calendar size={16} />
                        <span>{lang === 'te' ? 'విత్తిన తేదీ' : 'Sowing Date'}</span>
                        <strong>{formData.sowingDate}</strong>
                    </div>
                    <div className="detail-row">
                        <Sprout size={16} />
                        <span>{lang === 'te' ? 'విస్తీర్ణం' : 'Area'}</span>
                        <strong>{formData.areaAcres} {lang === 'te' ? 'ఎకరాలు' : 'acres'}</strong>
                    </div>
                    <div className="detail-row">
                        <Droplets size={16} />
                        <span>{lang === 'te' ? 'నీటి వనరు' : 'Irrigation'}</span>
                        <strong>
                            {irrigationTypes.find(t => t.value === formData.irrigationType)?.[lang === 'te' ? 'label_te' : 'label_en']}
                        </strong>
                    </div>
                    {formData.previousCrop && (
                        <div className="detail-row">
                            <Leaf size={16} />
                            <span>{lang === 'te' ? 'గత పంట' : 'Previous Crop'}</span>
                            <strong>{formData.previousCrop}</strong>
                        </div>
                    )}
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <AlertCircle size={18} />
                    {error}
                </div>
            )}

            <div className="button-row">
                <button className="back-btn" onClick={() => setStep(2)}>
                    <ArrowLeft size={18} />
                    {L.back}
                </button>
                <button
                    className="subscribe-btn"
                    onClick={handleSubmit}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <Loader2 className="spinner" size={18} />
                            {L.subscribing}
                        </>
                    ) : (
                        <>
                            <Check size={20} />
                            {L.subscribe}
                        </>
                    )}
                </button>
            </div>
        </div>
    );

    // Success Screen
    const renderSuccess = () => (
        <div className="success-screen">
            <div className="success-icon">🎉</div>
            <h2>{L.success}</h2>
            <p>{L.successMsg}</p>

            {subscriptionResult?.initial_plan?.alerts?.length > 0 && (
                <div className="initial-alerts">
                    <h4>⚠️ {lang === 'te' ? 'ప్రస్తుత హెచ్చరికలు' : 'Current Alerts'}</h4>
                    {subscriptionResult.initial_plan.alerts.slice(0, 2).map((alert, i) => (
                        <div key={i} className="alert-item">
                            <span>{alert.icon}</span>
                            <span>{lang === 'te' ? alert.title_te : alert.title_en}</span>
                        </div>
                    ))}
                </div>
            )}

            <div className="success-actions">
                <button
                    className="primary-btn"
                    onClick={() => navigate(`/monitor/${subscriptionResult?.subscription?.subscriptionId}`)}
                >
                    {L.viewPlan}
                    <ChevronRight size={20} />
                </button>
                <button
                    className="secondary-btn"
                    onClick={() => navigate('/my-crops')}
                >
                    {L.goToMyCrops}
                </button>
            </div>
        </div>
    );

    return (
        <div className="subscribe-container">
            {/* Header */}
            <div className="subscribe-header">
                <button className="back-link" onClick={() => navigate(-1)}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
            </div>

            {/* Progress Steps */}
            {!success && (
                <div className="progress-steps">
                    {[1, 2, 3].map((s) => (
                        <div
                            key={s}
                            className={`step ${step >= s ? 'active' : ''} ${step === s ? 'current' : ''}`}
                        >
                            <div className="step-number">{s}</div>
                            <span className="step-label">
                                {s === 1 ? L.step1 : s === 2 ? L.step2 : L.step3}
                            </span>
                        </div>
                    ))}
                </div>
            )}

            {/* Content */}
            {success ? renderSuccess() : (
                step === 1 ? renderStep1() :
                    step === 2 ? renderStep2() :
                        renderStep3()
            )}
        </div>
    );
};

export default CropSubscribe;
