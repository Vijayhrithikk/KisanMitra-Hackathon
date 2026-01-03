import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { orderService } from '../../services/orderService';
import { deliveryService } from '../../services/deliveryService';
import { ArrowLeft, Package, Truck, CheckCircle, Clock, MapPin, Phone } from 'lucide-react';
import './Market.css';
import './OrderTracking.css';

const OrderTracking = () => {
    const { orderId } = useParams();
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [order, setOrder] = useState(null);
    const [tracking, setTracking] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

    const L = {
        title: lang === 'te' ? '📦 ఆర్డర్ ట్రాకింగ్' : '📦 Order Tracking',
        orderPlaced: lang === 'te' ? 'ఆర్డర్ పెట్టారు' : 'Order Placed',
        confirmed: lang === 'te' ? 'కన్ఫర్మ్ అయింది' : 'Confirmed',
        shipped: lang === 'te' ? 'షిప్ అయింది' : 'Shipped',
        outForDelivery: lang === 'te' ? 'డెలివరీకి బయలుదేరింది' : 'Out for Delivery',
        delivered: lang === 'te' ? 'డెలివరీ అయింది' : 'Delivered',
        eta: lang === 'te' ? 'అంచనా రాక' : 'Estimated Arrival',
        contact: lang === 'te' ? 'సంప్రదించండి' : 'Contact'
    };

    const statusSteps = [
        { id: 'PENDING', label: L.orderPlaced, icon: <Package size={20} /> },
        { id: 'CONFIRMED', label: L.confirmed, icon: <CheckCircle size={20} /> },
        { id: 'SHIPPED', label: L.shipped, icon: <Truck size={20} /> },
        { id: 'DELIVERED', label: L.delivered, icon: <MapPin size={20} /> }
    ];

    // Fetch order from DATABASE API
    useEffect(() => {
        const fetchOrder = async () => {
            try {
                setLoading(true);
                console.log('📦 Fetching order from database:', orderId);

                const response = await fetch(`${API_BASE}/orders/${orderId}`);
                if (response.ok) {
                    const orderData = await response.json();
                    console.log('✅ Order loaded:', orderData);

                    // Ensure pricing object exists
                    if (!orderData.pricing) {
                        orderData.pricing = { total: orderData.quantity * 100 };
                    }
                    // Ensure delivery object exists
                    if (!orderData.delivery) {
                        orderData.delivery = { type: 'Standard', partner: 'KisanMitra Logistics' };
                    }

                    setOrder(orderData);

                    if (orderData.delivery?.trackingId) {
                        const trackingData = deliveryService.trackShipment(orderData.delivery.trackingId);
                        setTracking(trackingData);
                    }
                } else {
                    console.error('Order not found:', response.status);
                    setError('Order not found');
                }
            } catch (err) {
                console.error('Error fetching order:', err);
                setError('Failed to load order');
            } finally {
                setLoading(false);
            }
        };

        fetchOrder();
    }, [orderId]);

    const getStepStatus = (stepId) => {
        if (!order) return 'pending';
        const statusOrder = ['PENDING', 'CONFIRMED', 'PAID', 'SHIPPED', 'DELIVERED', 'COMPLETED'];
        const currentIndex = statusOrder.indexOf(order.status);
        const stepIndex = statusOrder.indexOf(stepId);

        if (stepIndex < currentIndex) return 'completed';
        if (stepIndex === currentIndex) return 'current';
        return 'pending';
    };

    if (loading) {
        return (
            <div className="market-container white-theme">
                <div className="loading-state">Loading order...</div>
            </div>
        );
    }

    if (error || !order) {
        return (
            <div className="market-container white-theme">
                <header className="market-header-simple">
                    <button className="back-btn" onClick={() => navigate(-1)}>
                        <ArrowLeft size={20} />
                    </button>
                    <h1>{L.title}</h1>
                </header>
                <div className="error-state" style={{ padding: '40px', textAlign: 'center' }}>
                    <p>❌ {error || 'Order not found'}</p>
                    <p style={{ color: '#666', marginTop: '10px' }}>Order ID: {orderId}</p>
                    <button onClick={() => navigate('/farmer/dashboard')} style={{ marginTop: '20px', padding: '10px 20px', background: '#10b981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                        Go to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="market-container white-theme">
            <header className="market-header-simple">
                <button className="back-btn" onClick={() => navigate(-1)}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
            </header>

            <div className="tracking-content">
                {/* Order Summary */}
                <div className="tracking-summary">
                    <div className="order-id">{order.orderId}</div>
                    <div className="order-product">{order.crop} - {order.quantity} {order.unit}</div>
                    <div className="order-total">₹{order.pricing.total}</div>
                </div>

                {/* Status Timeline */}
                <div className="status-timeline">
                    {statusSteps.map((step, index) => (
                        <div key={step.id} className={`timeline-step ${getStepStatus(step.id)}`}>
                            <div className="step-icon">{step.icon}</div>
                            <div className="step-content">
                                <span className="step-label">{step.label}</span>
                                {getStepStatus(step.id) === 'completed' && (
                                    <span className="step-time">✓</span>
                                )}
                                {getStepStatus(step.id) === 'current' && (
                                    <span className="step-time current">
                                        <Clock size={12} /> Now
                                    </span>
                                )}
                            </div>
                            {index < statusSteps.length - 1 && <div className="step-line" />}
                        </div>
                    ))}
                </div>

                {/* Delivery Info */}
                <div className="tracking-card">
                    <h3>Delivery Details</h3>
                    <div className="delivery-info">
                        <p><strong>Type:</strong> {order.delivery.type}</p>
                        <p><strong>Partner:</strong> {order.delivery.partner}</p>
                        <p><strong>{L.eta}:</strong> {order.delivery.estimatedDate}</p>
                        {order.delivery.trackingId && (
                            <p><strong>Tracking ID:</strong> {order.delivery.trackingId}</p>
                        )}
                    </div>
                </div>

                {/* Address */}
                {order.delivery.address && (
                    <div className="tracking-card">
                        <h3><MapPin size={16} /> Delivery Address</h3>
                        <div className="address-info">
                            <p>{order.delivery.address.line1}</p>
                            <p>{order.delivery.address.city}, {order.delivery.address.district}</p>
                            <p>{order.delivery.address.state} - {order.delivery.address.pincode}</p>
                        </div>
                    </div>
                )}

                {/* Tracking Events */}
                {tracking?.events && (
                    <div className="tracking-card">
                        <h3>Tracking History</h3>
                        <div className="tracking-events">
                            {tracking.events.map((event, i) => (
                                <div key={i} className="tracking-event">
                                    <div className="event-dot" />
                                    <div className="event-content">
                                        <span className="event-status">{event.status}</span>
                                        <span className="event-message">{event.message}</span>
                                        <span className="event-time">
                                            {new Date(event.timestamp).toLocaleString('en-IN')}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Contact */}
                <div className="tracking-card contact">
                    <h3><Phone size={16} /> {L.contact}</h3>
                    <p>{lang === 'te' ? 'సమస్యలకు సంప్రదించండి' : 'Contact for any issues'}</p>
                    <a href="tel:+919876543210" className="contact-btn">📞 Call Support</a>
                </div>
            </div>
        </div>
    );
};

export default OrderTracking;
