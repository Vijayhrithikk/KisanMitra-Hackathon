/**
 * Farmer Registration Page
 * Collects farmer details after phone/OTP verification
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { User, MapPin, FileText, Upload, ArrowRight } from 'lucide-react';
import './Login.css';

const FarmerRegister = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const { registerFarmer } = useAuth();

    const phone = location.state?.phone || '';

    const [formData, setFormData] = useState({
        name: '',
        village: '',
        district: '',
        state: 'Andhra Pradesh'
    });
    const [verificationDoc, setVerificationDoc] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (field) => (e) => {
        setFormData(prev => ({ ...prev, [field]: e.target.value }));
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Convert to base64 for storage (demo purposes)
            const reader = new FileReader();
            reader.onloadend = () => {
                setVerificationDoc({
                    name: file.name,
                    type: file.type,
                    data: reader.result
                });
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        if (!formData.name.trim()) {
            setError('Name is required');
            setLoading(false);
            return;
        }

        const result = await registerFarmer({
            phone,
            ...formData,
            verificationDoc
        });

        setLoading(false);

        if (result.success) {
            navigate('/home');
        } else {
            setError(result.error);
        }
    };

    if (!phone) {
        navigate('/login');
        return null;
    }

    return (
        <div className="register-page">
            <div className="register-container">
                <div className="register-header">
                    <h1>🌾 {t('register.title', 'Complete Your Profile')}</h1>
                    <p>{t('register.subtitle', 'Tell us about yourself')}</p>
                </div>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="register-form">
                    <div className="form-group">
                        <label>
                            <User size={16} />
                            {t('register.name', 'Full Name')} *
                        </label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={handleChange('name')}
                            placeholder="Enter your name"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>
                            <MapPin size={16} />
                            {t('register.village', 'Village/Town')}
                        </label>
                        <input
                            type="text"
                            value={formData.village}
                            onChange={handleChange('village')}
                            placeholder="Your village or town"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>{t('register.district', 'District')}</label>
                            <input
                                type="text"
                                value={formData.district}
                                onChange={handleChange('district')}
                                placeholder="District"
                            />
                        </div>
                        <div className="form-group">
                            <label>{t('register.state', 'State')}</label>
                            <select value={formData.state} onChange={handleChange('state')}>
                                <option value="Andhra Pradesh">Andhra Pradesh</option>
                                <option value="Telangana">Telangana</option>
                                <option value="Karnataka">Karnataka</option>
                                <option value="Tamil Nadu">Tamil Nadu</option>
                                <option value="Maharashtra">Maharashtra</option>
                                <option value="Gujarat">Gujarat</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>
                            <FileText size={16} />
                            {t('register.verification', 'Verification Document')}
                            <span className="optional-badge">Optional</span>
                        </label>
                        <div
                            className={`file-upload ${verificationDoc ? 'has-file' : ''}`}
                            onClick={() => document.getElementById('doc-upload').click()}
                        >
                            <input
                                id="doc-upload"
                                type="file"
                                accept="image/*,.pdf"
                                onChange={handleFileChange}
                            />
                            <div className="file-upload-content">
                                <Upload size={32} />
                                {verificationDoc ? (
                                    <p>✓ {verificationDoc.name}</p>
                                ) : (
                                    <>
                                        <p>{t('register.uploadDoc', 'Upload Aadhar, Voter ID, or Land Doc')}</p>
                                        <small>{t('register.optional', 'Optional - helps verify your profile')}</small>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    <button type="submit" className="submit-btn" disabled={loading}>
                        {loading ? 'Creating Profile...' : t('register.submit', 'Complete Registration')}
                        <ArrowRight size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default FarmerRegister;
