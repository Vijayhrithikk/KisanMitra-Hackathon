import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Sprout, ArrowRight, Loader2, ShoppingCart } from 'lucide-react';
import { motion } from 'framer-motion';
import { MARKET_API_URL } from '../config/api';
import LanguageSelector from '../components/LanguageSelector';
import './Login.css';

const Login = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');
    const [step, setStep] = useState('phone');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSendOtp = (e) => {
        e.preventDefault();
        if (phone.length === 10 && /^\d+$/.test(phone)) {
            setLoading(true);
            setTimeout(() => {
                setLoading(false);
                setStep('otp');
                setError('');
            }, 1000);
        } else {
            setError(t('login.invalidPhone'));
        }
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        if (otp.length === 6) {
            setLoading(true);

            try {
                // Check BOTH farmers and users collections
                // First, check farmers collection
                let farmerExists = false;
                let userData = null;

                // Try farmers endpoint first
                try {
                    const farmersResponse = await fetch(`${MARKET_API_URL}/farmers/phone/${phone}`);
                    const farmersData = await farmersResponse.json();
                    if (farmersData && farmersData.success && farmersData.farmer) {
                        farmerExists = true;
                        userData = farmersData.farmer;
                    }
                } catch (e) {
                    console.log('Farmers check failed, trying users...');
                }

                // If not in farmers, try users collection
                if (!farmerExists) {
                    try {
                        const usersResponse = await fetch(`${MARKET_API_URL}/users/phone/${phone}`);
                        const usersData = await usersResponse.json();
                        if (usersData && !usersData.error && (usersData.user || usersData.exists || usersData.userId || usersData.phone || usersData._id)) {
                            farmerExists = true;
                            userData = usersData.user || usersData;
                        }
                    } catch (e) {
                        console.log('Users check failed');
                    }
                }

                if (farmerExists && userData) {
                    // Farmer exists in database - log them in
                    const user = userData;
                    const farmerSession = {
                        id: user._id || user.id || user.userId || user.farmerId || `FARMER-${phone.slice(-4)}`,
                        role: 'farmer',
                        phone: phone,
                        phoneNumber: phone,
                        farmerId: user.farmerId || user.userId || user._id || `FARMER-${phone.slice(-4)}`,
                        name: user.name || user.farmerName || `Farmer ${phone.slice(-4)}`,
                        verified: user.verified ?? true,
                        loginAt: new Date().toISOString()
                    };

                    // Store session
                    localStorage.setItem('kisanmitra_session', JSON.stringify(farmerSession));
                    localStorage.setItem('userPhone', phone);
                    localStorage.setItem('farmerPhone', phone);
                    localStorage.setItem('currentFarmer', JSON.stringify(farmerSession));
                    localStorage.setItem('isAuthenticated', 'true');

                    setLoading(false);
                    navigate('/home');
                } else {
                    // Farmer doesn't exist - need to register
                    setLoading(false);
                    const { i18n } = useTranslation;
                    setError(t('login.notRegistered') || 'You are not registered. Please register first.');
                    // Redirect to registration page
                    setTimeout(() => {
                        navigate('/farmer/register', { state: { phone } });
                    }, 2000);
                }
            } catch (error) {
                console.error('Error checking farmer:', error);
                setLoading(false);
                setError(t('login.error'));
            }
        } else {
            setError(t('login.invalidOtp'));
        }
    };

    const handleGuestContinue = () => {
        localStorage.setItem('guestMode', 'true');
        navigate('/market');
    };

    return (
        <div className="login-container">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="login-card"
            >
                <div className="login-header-row">
                    <LanguageSelector />
                </div>

                <div className="brand-header">
                    <motion.div
                        whileHover={{ rotate: 10, scale: 1.1 }}
                        className="logo-wrapper"
                    >
                        <Sprout size={40} color="#fff" />
                    </motion.div>
                    <h1>KisanMitra AI</h1>
                    <p>{t('login.subtitle')}</p>
                </div>

                {step === 'phone' ? (
                    <motion.form
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        onSubmit={handleSendOtp}
                        className="login-form"
                    >
                        <div className="input-group">
                            <span className="country-code">+91</span>
                            <input
                                type="tel"
                                placeholder={t('login.phonePlaceholder')}
                                value={phone}
                                onChange={(e) => {
                                    setPhone(e.target.value.replace(/\D/g, '').slice(0, 10));
                                    setError('');
                                }}
                                autoFocus
                            />
                        </div>
                        {error && <p className="error-message">{error}</p>}

                        <motion.button
                            whileTap={{ scale: 0.95 }}
                            type="submit"
                            className="primary-btn"
                            disabled={phone.length !== 10 || loading}
                        >
                            {loading ? (
                                <Loader2 className="spin" />
                            ) : (
                                <>
                                    {t('login.getOtp')} <ArrowRight size={18} />
                                </>
                            )}
                        </motion.button>
                    </motion.form>
                ) : (
                    <motion.form
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        onSubmit={handleVerifyOtp}
                        className="login-form"
                    >
                        <div className="input-group">
                            <input
                                type="text"
                                placeholder="Enter 6-digit OTP"
                                value={otp}
                                onChange={(e) => {
                                    setOtp(e.target.value.replace(/\D/g, '').slice(0, 6));
                                    setError('');
                                }}
                                className="otp-input"
                                autoFocus
                            />
                        </div>
                        {error && <p className="error-message">{error}</p>}

                        <motion.button
                            whileTap={{ scale: 0.95 }}
                            type="submit"
                            className="primary-btn"
                            disabled={otp.length !== 6 || loading}
                        >
                            {loading ? <Loader2 className="spin" /> : t('login.verify')}
                        </motion.button>

                        <button
                            type="button"
                            className="text-btn"
                            onClick={() => {
                                setStep('phone');
                                setOtp('');
                                setError('');
                            }}
                        >
                            {t('login.changePhone')}
                        </button>
                    </motion.form>
                )}

                {step === 'phone' && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="guest-buyer-section"
                    >
                        <div className="divider">
                            <span>{t('login.or') || 'OR'}</span>
                        </div>

                        <div className="guest-card">
                            <div className="guest-icon">
                                <ShoppingCart size={32} color="#10b981" />
                            </div>
                            <h3>{t('login.buyerTitle') || 'Want to Buy Crops?'}</h3>
                            <p>{t('login.buyerSubtitle') || 'Browse fresh crops and order directly from farmers'}</p>
                            <motion.button
                                whileTap={{ scale: 0.95 }}
                                className="guest-btn"
                                onClick={handleGuestContinue}
                            >
                                {t('login.continueAsGuest') || 'Continue as Guest'} <ArrowRight size={18} />
                            </motion.button>
                        </div>
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
};

export default Login;
