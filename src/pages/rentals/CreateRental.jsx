import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rentalService, RENTAL_CATEGORIES } from '../../services/rentalService';
import { ArrowLeft, MapPin, CheckCircle, Loader2 } from 'lucide-react';
import './Rentals.css';

const CreateRental = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(null);

    const [formData, setFormData] = useState({
        category: '',
        title: '',
        description: '',
        dailyRate: '',
        monthlyRate: '',
        city: '',
        district: '',
        state: 'Andhra Pradesh',
        contactName: '',
        contactPhone: '',
        available: true
    });

    const handleCategorySelect = (categoryId) => {
        setFormData({ ...formData, category: categoryId });
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);

        // Get user's location
        let location = { lat: 17.3850, lng: 78.4867, city: formData.city, district: formData.district, state: formData.state };

        try {
            if (navigator.geolocation) {
                const position = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
                });
                location.lat = position.coords.latitude;
                location.lng = position.coords.longitude;
            }
        } catch (e) {
            console.log('Using default location');
        }

        // Simulate processing delay
        await new Promise(r => setTimeout(r, 1500));

        const rental = rentalService.createRental({
            category: formData.category,
            title: formData.title,
            description: formData.description,
            dailyRate: parseInt(formData.dailyRate) || 0,
            monthlyRate: formData.monthlyRate ? parseInt(formData.monthlyRate) : null,
            location,
            contact: { name: formData.contactName, phone: formData.contactPhone },
            available: true,
            images: []
        });

        setSuccess(rental);
        setSubmitting(false);

        // Redirect after delay
        setTimeout(() => navigate('/rentals'), 2500);
    };

    if (success) {
        return (
            <div className="rentals-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div className="success-card" style={{ textAlign: 'center', padding: 'var(--space-xl)' }}>
                    <CheckCircle size={64} color="#16A34A" />
                    <h2 style={{ margin: 'var(--space-md) 0' }}>Rental Listed!</h2>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Your equipment is now visible to farmers within 200km radius.
                    </p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                        Rental ID: {success.id}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="create-rental-container">
            {/* Header */}
            <header className="market-header" style={{ background: 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)' }}>
                <button className="back-btn" onClick={() => navigate('/rentals')} style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none' }}>
                    <ArrowLeft size={18} />
                </button>
                <div style={{ flex: 1 }}>
                    <h1 style={{ color: 'white', fontSize: '1.125rem', margin: 0 }}>List Your Equipment</h1>
                    <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.75rem', margin: 0 }}>Help other farmers, earn extra income</p>
                </div>
            </header>

            {/* Step Indicator */}
            <div style={{ display: 'flex', gap: 'var(--space-xs)', padding: 'var(--space-md)', background: 'var(--color-surface)' }}>
                <div style={{ flex: 1, height: 4, borderRadius: 2, background: step >= 1 ? 'var(--color-primary)' : 'var(--color-divider)' }}></div>
                <div style={{ flex: 1, height: 4, borderRadius: 2, background: step >= 2 ? 'var(--color-primary)' : 'var(--color-divider)' }}></div>
                <div style={{ flex: 1, height: 4, borderRadius: 2, background: step >= 3 ? 'var(--color-primary)' : 'var(--color-divider)' }}></div>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Step 1: Category Selection */}
                {step === 1 && (
                    <div style={{ padding: 'var(--space-md)' }}>
                        <h2 style={{ fontSize: '1rem', marginBottom: 'var(--space-md)' }}>What do you want to rent out?</h2>
                        <div className="category-grid">
                            {Object.values(RENTAL_CATEGORIES).map(cat => (
                                <div
                                    key={cat.id}
                                    className={`category-option ${formData.category === cat.id ? 'selected' : ''}`}
                                    onClick={() => handleCategorySelect(cat.id)}
                                >
                                    <span className="icon">{cat.icon}</span>
                                    <span className="label">{cat.name}</span>
                                </div>
                            ))}
                        </div>
                        <button
                            type="button"
                            className="submit-btn"
                            style={{ marginTop: 'var(--space-lg)' }}
                            disabled={!formData.category}
                            onClick={() => setStep(2)}
                        >
                            Continue
                        </button>
                    </div>
                )}

                {/* Step 2: Details */}
                {step === 2 && (
                    <div style={{ padding: 'var(--space-md)' }}>
                        <div className="form-card">
                            <h3 className="form-card-title">Equipment Details</h3>

                            <div className="form-group">
                                <label>Title</label>
                                <input
                                    type="text"
                                    name="title"
                                    placeholder="e.g., John Deere 50HP Tractor with Rotavator"
                                    value={formData.title}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    name="description"
                                    placeholder="Describe condition, features, and what's included..."
                                    value={formData.description}
                                    onChange={handleChange}
                                    rows={3}
                                    style={{ resize: 'none' }}
                                    required
                                />
                            </div>

                            <h3 className="form-card-title" style={{ marginTop: 'var(--space-lg)' }}>Rental Rates</h3>

                            <div className="rate-inputs">
                                <div className="rate-group">
                                    <label>Daily Rate (₹) *</label>
                                    <input
                                        type="number"
                                        name="dailyRate"
                                        placeholder="2500"
                                        value={formData.dailyRate}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="rate-group">
                                    <label>Monthly Rate (₹)</label>
                                    <input
                                        type="number"
                                        name="monthlyRate"
                                        placeholder="Optional"
                                        value={formData.monthlyRate}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 'var(--space-lg)' }}>
                            <button type="button" className="back-btn" onClick={() => setStep(1)}>Back</button>
                            <button
                                type="button"
                                className="submit-btn"
                                style={{ flex: 1 }}
                                disabled={!formData.title || !formData.dailyRate}
                                onClick={() => setStep(3)}
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Location & Contact */}
                {step === 3 && (
                    <div style={{ padding: 'var(--space-md)' }}>
                        <div className="form-card">
                            <h3 className="form-card-title">
                                <MapPin size={16} /> Location
                            </h3>

                            <div className="form-group">
                                <label>City / Village</label>
                                <input
                                    type="text"
                                    name="city"
                                    placeholder="e.g., Tenali"
                                    value={formData.city}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>District</label>
                                    <input
                                        type="text"
                                        name="district"
                                        placeholder="e.g., Guntur"
                                        value={formData.district}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>State</label>
                                    <input
                                        type="text"
                                        name="state"
                                        value={formData.state}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="form-card">
                            <h3 className="form-card-title">Contact Details</h3>

                            <div className="form-group">
                                <label>Your Name</label>
                                <input
                                    type="text"
                                    name="contactName"
                                    placeholder="Full name"
                                    value={formData.contactName}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Phone Number</label>
                                <input
                                    type="tel"
                                    name="contactPhone"
                                    placeholder="+91 98765 43210"
                                    value={formData.contactPhone}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 'var(--space-lg)' }}>
                            <button type="button" className="back-btn" onClick={() => setStep(2)}>Back</button>
                            <button
                                type="submit"
                                className="submit-btn"
                                style={{ flex: 1 }}
                                disabled={submitting || !formData.city || !formData.contactName}
                            >
                                {submitting ? (
                                    <><Loader2 size={18} className="spin" /> Publishing...</>
                                ) : (
                                    'Publish Rental'
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </form>
        </div>
    );
};

export default CreateRental;
