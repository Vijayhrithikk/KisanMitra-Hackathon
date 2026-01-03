import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { rentalService, RENTAL_CATEGORIES } from '../../services/rentalService';
import { ArrowLeft, MapPin, Phone, Clock, Eye, MessageCircle, Share2, Check } from 'lucide-react';
import './Rentals.css';

const RentalDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [rental, setRental] = useState(null);
    const [showPhone, setShowPhone] = useState(false);

    useEffect(() => {
        const data = rentalService.getRentalById(id);
        if (data) {
            setRental(data);
            rentalService.incrementViews(id);
        }
    }, [id]);

    const getCategoryInfo = (categoryId) => {
        return RENTAL_CATEGORIES[categoryId] || { icon: '📦', name: categoryId, color: '#666' };
    };

    const handleContact = () => {
        rentalService.recordInquiry(id);
        setShowPhone(true);
    };

    const handleCall = () => {
        window.location.href = `tel:${rental.contact.phone}`;
    };

    if (!rental) {
        return (
            <div className="rental-detail-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
                <p>Rental not found</p>
            </div>
        );
    }

    const category = getCategoryInfo(rental.category);

    return (
        <div className="rental-detail-container">
            {/* Fixed Back Button */}
            <div style={{ position: 'fixed', top: 'var(--space-md)', left: 'var(--space-md)', zIndex: 100 }}>
                <button
                    onClick={() => navigate('/rentals')}
                    style={{
                        width: 40,
                        height: 40,
                        borderRadius: 'var(--radius-full)',
                        background: 'rgba(255,255,255,0.9)',
                        backdropFilter: 'blur(8px)',
                        border: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: 'var(--shadow-md)'
                    }}
                >
                    <ArrowLeft size={20} />
                </button>
            </div>

            {/* Hero Section */}
            <div className="rental-hero">
                <div className="category-big">{category.icon}</div>
                <h1>{rental.title}</h1>
                <div className="location-text">
                    <MapPin size={14} />
                    <span>{rental.location.city}, {rental.location.district}</span>
                    {rental.distance && <span> • {rental.distance} km away</span>}
                </div>
            </div>

            {/* Content */}
            <div className="detail-content">
                {/* Pricing Card */}
                <div className="pricing-card">
                    <div className="prices">
                        <div className="price-item">
                            <div className="amount">₹{rental.dailyRate?.toLocaleString()}</div>
                            <div className="per">per day</div>
                        </div>
                        {rental.monthlyRate && (
                            <div className="price-item">
                                <div className="amount">₹{rental.monthlyRate?.toLocaleString()}</div>
                                <div className="per">per month</div>
                            </div>
                        )}
                    </div>

                    {!showPhone ? (
                        <button className="contact-btn" onClick={handleContact}>
                            <Phone size={18} /> Contact Owner
                        </button>
                    ) : (
                        <button className="contact-btn" onClick={handleCall} style={{ background: '#16A34A' }}>
                            <Phone size={18} /> {rental.contact.phone}
                        </button>
                    )}
                </div>

                {/* Availability */}
                <div className="detail-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                        <div style={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            background: rental.available ? '#16A34A' : '#DC2626'
                        }}></div>
                        <span style={{ fontWeight: 600 }}>
                            {rental.available ? 'Available for Rent' : 'Currently Booked'}
                        </span>
                    </div>
                </div>

                {/* Description */}
                <div className="detail-card">
                    <h2>Description</h2>
                    <p style={{ fontSize: '0.9375rem', lineHeight: 1.6, color: 'var(--color-text-secondary)', margin: 0 }}>
                        {rental.description}
                    </p>
                </div>

                {/* Owner Card */}
                <div className="owner-card">
                    <div className="owner-avatar">👨‍🌾</div>
                    <div className="owner-info">
                        <h4>{rental.contact.name}</h4>
                        <p>Equipment Owner • {rental.location.district}</p>
                    </div>
                </div>

                {/* Stats */}
                <div style={{ display: 'flex', gap: 'var(--space-md)', marginTop: 'var(--space-md)', padding: 'var(--space-md)', background: 'var(--color-surface)', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-xs)', color: 'var(--color-text-muted)' }}>
                            <Eye size={14} />
                            <span style={{ fontSize: '0.75rem' }}>Views</span>
                        </div>
                        <div style={{ fontWeight: 700, fontSize: '1.125rem' }}>{rental.views || 0}</div>
                    </div>
                    <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-xs)', color: 'var(--color-text-muted)' }}>
                            <MessageCircle size={14} />
                            <span style={{ fontSize: '0.75rem' }}>Inquiries</span>
                        </div>
                        <div style={{ fontWeight: 700, fontSize: '1.125rem' }}>{rental.inquiries || 0}</div>
                    </div>
                    <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-xs)', color: 'var(--color-text-muted)' }}>
                            <Clock size={14} />
                            <span style={{ fontSize: '0.75rem' }}>Listed</span>
                        </div>
                        <div style={{ fontWeight: 700, fontSize: '0.875rem' }}>
                            {new Date(rental.createdAt).toLocaleDateString()}
                        </div>
                    </div>
                </div>

                {/* Category Badge */}
                <div style={{
                    marginTop: 'var(--space-lg)',
                    padding: 'var(--space-md)',
                    background: category.color + '15',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${category.color}30`
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                        <span style={{ fontSize: '1.5rem' }}>{category.icon}</span>
                        <div>
                            <div style={{ fontWeight: 600, color: category.color }}>{category.name}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                                Category
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RentalDetail;
