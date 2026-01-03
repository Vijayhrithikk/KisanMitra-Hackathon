import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { buyerService } from '../../services/buyerService';
import { ArrowLeft, User, Store, Building2, Factory, MapPin, Phone, Mail, Check, ArrowRight } from 'lucide-react';
import './Market.css';

const BuyerRegistration = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        type: '',
        name: '',
        phone: '',
        email: '',
        businessName: '',
        gstNumber: '',
        fssaiLicense: '',
        address: {
            label: 'Primary',
            line1: '',
            line2: '',
            city: '',
            district: '',
            state: 'Andhra Pradesh',
            pincode: ''
        }
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(null);

    const L = {
        title: lang === 'te' ? '🛒 కొనుగోలుదారు రిజిస్ట్రేషన్' : '🛒 Buyer Registration',
        selectType: lang === 'te' ? 'మీరు ఎవరు?' : 'Who are you?',
        personalInfo: lang === 'te' ? 'వ్యక్తిగత సమాచారం' : 'Personal Information',
        addressInfo: lang === 'te' ? 'అడ్రస్ సమాచారం' : 'Address Information',
        name: lang === 'te' ? 'పేరు' : 'Full Name',
        phone: lang === 'te' ? 'ఫోన్ నంబర్' : 'Phone Number',
        email: lang === 'te' ? 'ఇమెయిల్' : 'Email (Optional)',
        businessName: lang === 'te' ? 'బిజినెస్ పేరు' : 'Business Name',
        gst: lang === 'te' ? 'GST నంబర్' : 'GST Number (Optional)',
        fssai: lang === 'te' ? 'FSSAI లైసెన్స్' : 'FSSAI License (Optional)',
        address: lang === 'te' ? 'చిరునామా' : 'Address Line 1',
        city: lang === 'te' ? 'నగరం' : 'City',
        district: lang === 'te' ? 'జిల్లా' : 'District',
        pincode: lang === 'te' ? 'పిన్‌కోడ్' : 'Pincode',
        next: lang === 'te' ? 'తదుపరి' : 'Next',
        back: lang === 'te' ? 'వెనుకకు' : 'Back',
        register: lang === 'te' ? 'రిజిస్టర్ చేయండి' : 'Register',
        success: lang === 'te' ? 'విజయవంతంగా నమోదు!' : 'Registration Successful!'
    };

    const buyerTypes = buyerService.getBuyerTypes();

    const handleTypeSelect = (type) => {
        setFormData({ ...formData, type });
        setStep(2);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.startsWith('address.')) {
            const field = name.split('.')[1];
            setFormData({
                ...formData,
                address: { ...formData.address, [field]: value }
            });
        } else {
            setFormData({ ...formData, [name]: value });
        }
    };

    const handleSubmit = () => {
        setError('');

        if (!formData.name.trim() || !formData.phone.trim()) {
            setError(lang === 'te' ? 'పేరు మరియు ఫోన్ అవసరం' : 'Name and phone are required');
            return;
        }

        if (formData.phone.length !== 10) {
            setError(lang === 'te' ? 'సరైన ఫోన్ నంబర్ నమోదు చేయండి' : 'Enter valid 10-digit phone');
            return;
        }

        const result = buyerService.registerBuyer({
            ...formData,
            addresses: formData.address.line1 ? [formData.address] : []
        });

        if (result.success) {
            setSuccess(result.buyer);
            localStorage.setItem('currentBuyer', JSON.stringify(result.buyer));
        } else {
            setError(result.error);
        }
    };

    if (success) {
        return (
            <div className="market-container white-theme">
                <div className="success-screen">
                    <div className="success-icon">✅</div>
                    <h2>{L.success}</h2>
                    <p>Buyer ID: <strong>{success.buyerId}</strong></p>
                    <p>{buyerTypes.find(t => t.id === success.type)?.[lang === 'te' ? 'te' : 'en']}</p>
                    <button className="primary-btn" onClick={() => navigate('/market')}>
                        {lang === 'te' ? 'మార్కెట్‌కు వెళ్ళండి' : 'Go to Market'} <ArrowRight size={18} />
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="market-container white-theme">
            <header className="market-header-simple">
                <button className="back-btn" onClick={() => step > 1 ? setStep(step - 1) : navigate('/market')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
            </header>

            <div className="registration-content">
                {/* Step 1: Select Type */}
                {step === 1 && (
                    <div className="step-container">
                        <h2>{L.selectType}</h2>
                        <div className="type-grid">
                            {buyerTypes.map(type => (
                                <button
                                    key={type.id}
                                    className={`type-card ${formData.type === type.id ? 'selected' : ''}`}
                                    onClick={() => handleTypeSelect(type.id)}
                                >
                                    <span className="type-icon">{type.icon}</span>
                                    <span className="type-name">{lang === 'te' ? type.te : type.en}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 2: Personal/Business Info */}
                {step === 2 && (
                    <div className="step-container">
                        <h2>{L.personalInfo}</h2>

                        <div className="form-group">
                            <label><User size={16} /> {L.name}</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder={lang === 'te' ? 'మీ పేరు' : 'Your full name'}
                            />
                        </div>

                        <div className="form-group">
                            <label><Phone size={16} /> {L.phone}</label>
                            <input
                                type="tel"
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                                placeholder="9876543210"
                                maxLength={10}
                            />
                        </div>

                        <div className="form-group">
                            <label><Mail size={16} /> {L.email}</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="email@example.com"
                            />
                        </div>

                        {(formData.type === 'RESTAURANT' || formData.type === 'RETAILER' || formData.type === 'WHOLESALER') && (
                            <>
                                <div className="form-group">
                                    <label><Store size={16} /> {L.businessName}</label>
                                    <input
                                        type="text"
                                        name="businessName"
                                        value={formData.businessName}
                                        onChange={handleChange}
                                        placeholder={lang === 'te' ? 'బిజినెస్ పేరు' : 'Business name'}
                                    />
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>{L.gst}</label>
                                        <input
                                            type="text"
                                            name="gstNumber"
                                            value={formData.gstNumber}
                                            onChange={handleChange}
                                            placeholder="22AAAAA0000A1Z5"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>{L.fssai}</label>
                                        <input
                                            type="text"
                                            name="fssaiLicense"
                                            value={formData.fssaiLicense}
                                            onChange={handleChange}
                                            placeholder="12345678901234"
                                        />
                                    </div>
                                </div>
                            </>
                        )}

                        {error && <div className="error-msg">{error}</div>}

                        <div className="button-row">
                            <button className="secondary-btn" onClick={() => setStep(1)}>
                                {L.back}
                            </button>
                            <button className="primary-btn" onClick={() => setStep(3)}>
                                {L.next} <ArrowRight size={16} />
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Address */}
                {step === 3 && (
                    <div className="step-container">
                        <h2>{L.addressInfo}</h2>

                        <div className="form-group">
                            <label><MapPin size={16} /> {L.address}</label>
                            <input
                                type="text"
                                name="address.line1"
                                value={formData.address.line1}
                                onChange={handleChange}
                                placeholder={lang === 'te' ? 'వీధి, ప్రాంతం' : 'Street, Area'}
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>{L.city}</label>
                                <input
                                    type="text"
                                    name="address.city"
                                    value={formData.address.city}
                                    onChange={handleChange}
                                    placeholder={lang === 'te' ? 'నగరం' : 'City'}
                                />
                            </div>
                            <div className="form-group">
                                <label>{L.district}</label>
                                <input
                                    type="text"
                                    name="address.district"
                                    value={formData.address.district}
                                    onChange={handleChange}
                                    placeholder={lang === 'te' ? 'జిల్లా' : 'District'}
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>State</label>
                                <select name="address.state" value={formData.address.state} onChange={handleChange}>
                                    <option value="Andhra Pradesh">Andhra Pradesh</option>
                                    <option value="Telangana">Telangana</option>
                                    <option value="Karnataka">Karnataka</option>
                                    <option value="Tamil Nadu">Tamil Nadu</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>{L.pincode}</label>
                                <input
                                    type="text"
                                    name="address.pincode"
                                    value={formData.address.pincode}
                                    onChange={handleChange}
                                    placeholder="518501"
                                    maxLength={6}
                                />
                            </div>
                        </div>

                        {error && <div className="error-msg">{error}</div>}

                        <div className="button-row">
                            <button className="secondary-btn" onClick={() => setStep(2)}>
                                {L.back}
                            </button>
                            <button className="primary-btn" onClick={handleSubmit}>
                                <Check size={16} /> {L.register}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default BuyerRegistration;
