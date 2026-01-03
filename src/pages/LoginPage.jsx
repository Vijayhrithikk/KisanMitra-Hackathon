import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { Phone, Mail, Lock, ArrowRight, User, ShieldCheck, Globe, ShoppingCart } from 'lucide-react';
import './Login.css';

const LoginPage = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { loginAdmin, sendOTP, verifyOTP } = useAuth();

    const [activeTab, setActiveTab] = useState('farmer');
    const [step, setStep] = useState('phone');

    // Language toggle
    const toggleLanguage = () => {
        const newLang = i18n.language === 'te' ? 'en' : 'te';
        i18n.changeLanguage(newLang);
    };

    // Farmer state
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');

    // Admin state
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSendOTP = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (phone.length < 10) {
            setError('Please enter a valid phone number');
            setLoading(false);
            return;
        }

        const result = await sendOTP(phone);
        setLoading(false);

        if (result.success) {
            setStep('otp');
        } else {
            setError(result.error);
        }
    };

    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await verifyOTP(phone, otp);
        setLoading(false);

        if (result.success) {
            if (result.isNewUser) {
                navigate('/farmer/register', { state: { phone } });
            } else {
                navigate('/home');
            }
        } else {
            setError(result.error);
        }
    };

    const handleAdminLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await loginAdmin(email, password);
        setLoading(false);

        if (result.success) {
            navigate('/admin');
        } else {
            setError(result.error);
        }
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <div className="login-header">
                    <button className="lang-toggle" onClick={toggleLanguage}>
                        <Globe size={16} />
                        {i18n.language === 'te' ? 'EN' : 'తెలుగు'}
                    </button>
                    <div className="logo">🌾</div>
                    <h1>KisanMitra</h1>
                    <p>{t('login.subtitle', 'Your farming companion')}</p>
                </div>

                <div className="login-tabs">
                    <button
                        className={activeTab === 'farmer' ? 'active' : ''}
                        onClick={() => { setActiveTab('farmer'); setError(''); setStep('phone'); }}
                    >
                        <User size={18} />
                        {t('login.farmer', 'Farmer')}
                    </button>
                    <button
                        className={activeTab === 'admin' ? 'active' : ''}
                        onClick={() => { setActiveTab('admin'); setError(''); }}
                    >
                        <ShieldCheck size={18} />
                        {t('login.admin', 'Admin')}
                    </button>
                </div>

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                {activeTab === 'farmer' ? (
                    <div className="login-form farmer-form">
                        {step === 'phone' ? (
                            <form onSubmit={handleSendOTP}>
                                <div className="form-group">
                                    <label>
                                        <Phone size={16} />
                                        {t('login.phoneNumber', 'Phone Number')}
                                    </label>
                                    <div className="phone-input">
                                        <span className="country-code">+91</span>
                                        <input
                                            type="tel"
                                            value={phone}
                                            onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                                            placeholder="9876543210"
                                            maxLength={10}
                                            required
                                        />
                                    </div>
                                </div>
                                <button type="submit" className="submit-btn" disabled={loading}>
                                    {loading ? 'Sending...' : t('login.sendOTP', 'Send OTP')}
                                    <ArrowRight size={18} />
                                </button>
                            </form>
                        ) : (
                            <form onSubmit={handleVerifyOTP}>
                                <div className="form-group">
                                    <label>
                                        <Lock size={16} />
                                        {t('login.enterOTP', 'Enter OTP')}
                                    </label>
                                    <input
                                        type="text"
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                        placeholder="123456"
                                        maxLength={6}
                                        className="otp-input"
                                        required
                                    />
                                    <small className="otp-hint">
                                        {t('login.otpHint', 'Demo OTP: 123456')}
                                    </small>
                                </div>
                                <button type="submit" className="submit-btn" disabled={loading}>
                                    {loading ? 'Verifying...' : t('login.verify', 'Verify & Login')}
                                    <ArrowRight size={18} />
                                </button>
                                <button
                                    type="button"
                                    className="back-link"
                                    onClick={() => setStep('phone')}
                                >
                                    ← {t('login.changeNumber', 'Change Number')}
                                </button>
                            </form>
                        )}

                        {/* Guest Options */}
                        {step === 'phone' && (
                            <div className="guest-section">
                                <div className="divider"><span>OR</span></div>

                                {/* Guest Farmer - Explore App */}
                                <div className="guest-card" style={{ borderLeft: '4px solid #2E7D32' }}>
                                    <div className="guest-icon">
                                        <User size={28} color="#2E7D32" />
                                    </div>
                                    <h3>Explore as Guest Farmer</h3>
                                    <p>Get crop recommendations, weather, techniques & more without login</p>
                                    <button
                                        className="guest-btn"
                                        style={{ background: '#2E7D32' }}
                                        onClick={() => {
                                            localStorage.setItem('guestFarmer', 'true');
                                            navigate('/home');
                                        }}
                                    >
                                        Continue as Guest Farmer <ArrowRight size={18} />
                                    </button>
                                </div>

                                {/* Guest Buyer - Shop Option */}
                                <div className="guest-card" style={{ marginTop: '1rem', borderLeft: '4px solid #10b981' }}>
                                    <div className="guest-icon">
                                        <ShoppingCart size={28} color="#10b981" />
                                    </div>
                                    <h3>Want to Buy Crops?</h3>
                                    <p>Browse fresh crops and order directly from farmers</p>
                                    <button
                                        className="guest-btn"
                                        style={{ background: '#10b981' }}
                                        onClick={() => {
                                            localStorage.setItem('guestMode', 'true');
                                            navigate('/market');
                                        }}
                                    >
                                        Continue as Guest Buyer <ArrowRight size={18} />
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="login-form admin-form">
                        <form onSubmit={handleAdminLogin}>
                            <div className="form-group">
                                <label>
                                    <Mail size={16} />
                                    {t('login.email', 'Email')}
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="admin@kisanmitra.com"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>
                                    <Lock size={16} />
                                    {t('login.password', 'Password')}
                                </label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                            <button type="submit" className="submit-btn" disabled={loading}>
                                {loading ? 'Logging in...' : t('login.login', 'Login')}
                                <ArrowRight size={18} />
                            </button>

                        </form>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoginPage;
