import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useCart } from '../../context/CartContext';
import { ArrowLeft, ShoppingBag, MapPin, Phone, User, Loader2, CheckCircle, Truck, Store, Building2, Factory, CreditCard } from 'lucide-react';
import { initiatePayment } from '../../services/razorpayService';
import './GuestCheckout.css';

const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

const GuestCheckout = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { cart, clearCart } = useCart();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [step, setStep] = useState(1); // 1: Buyer Type, 2: Delivery, 3: Details
    const [formData, setFormData] = useState({
        buyerType: '',
        name: '',
        phone: '',
        businessName: '',
        address: '',
        city: '',
        district: '',
        state: 'Andhra Pradesh',
        pincode: '',
        notes: ''
    });
    const [deliveryType, setDeliveryType] = useState('pickup');
    const [paymentMethod, setPaymentMethod] = useState('COD');
    const [loading, setLoading] = useState(false);
    const [orderPlaced, setOrderPlaced] = useState(false);
    const [orderId, setOrderId] = useState('');

    // Buyer types
    const buyerTypes = [
        { id: 'CONSUMER', icon: '👤', en: 'Consumer', te: 'వినియోగదారుడు' },
        { id: 'RESTAURANT', icon: '🍽️', en: 'Restaurant/Hotel', te: 'రెస్టారెంట్/హోటల్' },
        { id: 'RETAILER', icon: '🏪', en: 'Retailer/Shop', te: 'రిటైలర్/షాప్' },
        { id: 'WHOLESALER', icon: '🏭', en: 'Wholesaler', te: 'హోల్‌సేలర్' }
    ];

    // Delivery options
    const deliveryOptions = [
        { id: 'pickup', label: lang === 'te' ? 'స్వయంగా తీసుకెళ్ళండి' : 'Self Pickup', icon: '🏪', charge: 0 },
        { id: 'local', label: lang === 'te' ? 'లోకల్ డెలివరీ' : 'Local Delivery', icon: '🛵', charge: 200 },
        { id: 'state', label: lang === 'te' ? 'స్టేట్ డెలివరీ' : 'State Delivery', icon: '🚛', charge: 500 }
    ];

    // Payment options
    const paymentOptions = [
        { id: 'PAY_ONLINE', label: 'Pay Online', icon: '💳', description: 'Cards, UPI, NetBanking' },
        { id: 'COD', label: 'Cash on Delivery', icon: '💵', description: 'Pay when you receive' }
    ];

    const L = {
        title: lang === 'te' ? 'చెక్అవుట్' : 'Checkout',
        selectType: lang === 'te' ? 'మీరు ఎవరు?' : 'What type of buyer are you?',
        delivery: lang === 'te' ? 'డెలివరీ' : 'Delivery Options',
        payment: lang === 'te' ? 'చెల్లింపు' : 'Payment Method',
        details: lang === 'te' ? 'డెలివరీ వివరాలు' : 'Delivery Details',
        yourOrder: lang === 'te' ? 'మీ ఆర్డర్' : 'Your Order',
        subtotal: lang === 'te' ? 'ఉప మొత్తం' : 'Subtotal',
        deliveryCharge: lang === 'te' ? 'డెలివరీ ఛార్జ్' : 'Delivery Charge',
        platformFee: lang === 'te' ? 'ప్లాట్‌ఫాం ఫీ (1%)' : 'Platform Fee (1%)',
        total: lang === 'te' ? 'మొత్తం' : 'Total',
        farmerGets: lang === 'te' ? 'రైతుకు వెళ్ళేది' : 'Farmer Gets',
        placeOrder: lang === 'te' ? 'ఆర్డర్ ఇవ్వండి' : 'Place Order',
        next: lang === 'te' ? 'తదుపరి' : 'Next',
        back: lang === 'te' ? 'వెనుకకు' : 'Back'
    };

    // Calculate pricing
    const calculateSubtotal = () => cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const getDeliveryCharge = () => deliveryOptions.find(d => d.id === deliveryType)?.charge || 0;
    const calculatePlatformFee = () => Math.round(calculateSubtotal() * 0.01);
    const calculateTotal = () => calculateSubtotal() + getDeliveryCharge() + calculatePlatformFee();
    const calculateFarmerGets = () => calculateSubtotal() - calculatePlatformFee();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleTypeSelect = (type) => {
        setFormData({ ...formData, buyerType: type });
        setStep(2);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // For online payment, create order with PAYMENT_PENDING status
            // For COD, create order with PLACED status
            const orderData = {
                type: 'guest',
                buyerType: formData.buyerType,
                items: cart.map(item => ({
                    listingId: item.listingId,
                    crop: item.crop,
                    variety: item.variety,
                    quantity: item.quantity,
                    price: item.price,
                    farmerId: item.farmerId
                })),
                buyer: {
                    type: formData.buyerType,
                    name: formData.name,
                    phone: formData.phone,
                    businessName: formData.businessName || null
                },
                delivery: {
                    type: deliveryType,
                    charge: getDeliveryCharge(),
                    address: {
                        line1: formData.address,
                        city: formData.city,
                        district: formData.district,
                        state: formData.state,
                        pincode: formData.pincode
                    }
                },
                pricing: {
                    subtotal: calculateSubtotal(),
                    deliveryCharge: getDeliveryCharge(),
                    platformFee: calculatePlatformFee(),
                    total: calculateTotal(),
                    farmerGets: calculateFarmerGets()
                },
                payment: {
                    method: paymentMethod,
                    status: paymentMethod === 'PAY_ONLINE' ? 'PENDING' : 'COD'
                },
                notes: formData.notes,
                // Use PAYMENT_PENDING for online payments, PLACED for COD
                status: paymentMethod === 'PAY_ONLINE' ? 'PAYMENT_PENDING' : 'PLACED'
            };

            const response = await fetch(`${API_BASE}/orders/guest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();

            if (response.ok) {
                // If online payment selected, initiate Razorpay
                if (paymentMethod === 'PAY_ONLINE') {
                    try {
                        const paymentResult = await initiatePayment(
                            calculateTotal(),
                            result.orderId,
                            'marketplace',
                            { name: formData.name, phone: formData.phone }
                        );

                        // Payment successful and verified - now mark order as PLACED
                        console.log('✅ Payment successful:', paymentResult);
                        setOrderId(result.orderId);
                        setOrderPlaced(true);
                        clearCart();
                    } catch (paymentError) {
                        console.error('Payment cancelled or failed:', paymentError);

                        // Cancel the pending order since payment failed
                        try {
                            await fetch(`${API_BASE}/orders/${result.orderId}/cancel`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ reason: paymentError.message || 'Payment cancelled by user' })
                            });
                        } catch (cancelError) {
                            console.error('Failed to cancel order:', cancelError);
                        }

                        // Show error and DO NOT mark as order placed
                        alert(lang === 'te'
                            ? 'చెల్లింపు రద్దు చేయబడింది. దయచేసి మళ్ళీ ప్రయత్నించండి.'
                            : 'Payment was cancelled. Please try again.');
                        // Do NOT set orderPlaced to true or clear cart
                    }
                } else {
                    // COD - just show success
                    setOrderId(result.orderId);
                    setOrderPlaced(true);
                    clearCart();
                }
            } else {
                alert('Order placement failed. Please try again.');
            }
        } catch (error) {
            console.error('Order error:', error);
            alert('Failed to place order. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (orderPlaced) {
        return (
            <div className="checkout-page">
                <div className="order-success">
                    <CheckCircle size={64} color="#16a34a" />
                    <h2>{lang === 'te' ? 'ఆర్డర్ విజయవంతం!' : 'Order Placed Successfully!'}</h2>
                    <p className="order-id">{lang === 'te' ? 'ఆర్డర్ ID' : 'Order ID'}: <strong>{orderId}</strong></p>
                    <div className="order-summary-success">
                        <p>💰 Total: <strong>₹{calculateTotal()}</strong></p>
                        <p>🚚 Delivery: <strong>{deliveryOptions.find(d => d.id === deliveryType)?.label}</strong></p>
                    </div>
                    <p>{lang === 'te' ? 'రైతు త్వరలో మిమ్మల్ని సంప్రదిస్తారు' : 'Farmer will contact you shortly'}</p>
                    <button className="primary-btn" onClick={() => navigate('/market')}>
                        {lang === 'te' ? 'షాపింగ్ కొనసాగించండి' : 'Continue Shopping'}
                    </button>
                    <button className="secondary-btn" onClick={() => navigate(`/market/track/${orderId}`)}>
                        {lang === 'te' ? 'ఆర్డర్ ట్రాక్ చేయండి' : 'Track Order'}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="checkout-page">
            <header className="checkout-header">
                <button className="back-btn" onClick={() => step > 1 ? setStep(step - 1) : navigate('/cart')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
                <div className="step-indicator">{step}/3</div>
            </header>

            <div className="checkout-content">
                {/* Step 1: Buyer Type Selection */}
                {step === 1 && (
                    <div className="step-container">
                        <h2>{L.selectType}</h2>
                        <div className="type-grid">
                            {buyerTypes.map(type => (
                                <button
                                    key={type.id}
                                    className={`type-card ${formData.buyerType === type.id ? 'selected' : ''}`}
                                    onClick={() => handleTypeSelect(type.id)}
                                >
                                    <span className="type-icon">{type.icon}</span>
                                    <span className="type-name">{lang === 'te' ? type.te : type.en}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 2: Delivery & Payment */}
                {step === 2 && (
                    <div className="step-container">
                        {/* Delivery Options */}
                        <div className="order-section">
                            <h3><Truck size={18} /> {L.delivery}</h3>
                            <div className="option-grid">
                                {deliveryOptions.map(opt => (
                                    <button
                                        key={opt.id}
                                        className={`option-card ${deliveryType === opt.id ? 'selected' : ''}`}
                                        onClick={() => setDeliveryType(opt.id)}
                                    >
                                        <span className="option-icon">{opt.icon}</span>
                                        <span className="option-label">{opt.label}</span>
                                        <span className="option-price">
                                            {opt.charge === 0 ? 'Free' : `₹${opt.charge}`}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Payment Options */}
                        <div className="order-section">
                            <h3><CreditCard size={18} /> {L.payment}</h3>
                            <div className="option-grid compact">
                                {paymentOptions.map(opt => (
                                    <button
                                        key={opt.id}
                                        className={`option-card ${paymentMethod === opt.id ? 'selected' : ''}`}
                                        onClick={() => setPaymentMethod(opt.id)}
                                    >
                                        <span className="option-icon">{opt.icon}</span>
                                        <span className="option-label">{opt.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Price Breakdown */}
                        <div className="order-section pricing-section">
                            <h3>💰 {lang === 'te' ? 'ధర వివరాలు' : 'Price Breakdown'}</h3>
                            <div className="price-rows">
                                <div className="price-row">
                                    <span>{L.subtotal}</span>
                                    <span>₹{calculateSubtotal().toLocaleString()}</span>
                                </div>
                                <div className="price-row">
                                    <span>{L.deliveryCharge}</span>
                                    <span>{getDeliveryCharge() === 0 ? 'Free' : `₹${getDeliveryCharge()}`}</span>
                                </div>
                                <div className="price-row">
                                    <span>{L.platformFee}</span>
                                    <span>₹{calculatePlatformFee()}</span>
                                </div>
                                <div className="price-row total">
                                    <span>{L.total}</span>
                                    <span>₹{calculateTotal().toLocaleString()}</span>
                                </div>
                                <div className="price-row farmer">
                                    <span>{L.farmerGets}</span>
                                    <span className="green">₹{calculateFarmerGets().toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        <button className="primary-btn" onClick={() => setStep(3)}>
                            {L.next} →
                        </button>
                    </div>
                )}

                {/* Step 3: Delivery Details Form */}
                {step === 3 && (
                    <form onSubmit={handleSubmit} className="checkout-form">
                        <h3><User size={20} /> {L.details}</h3>

                        <div className="form-group">
                            <label>{lang === 'te' ? 'పేరు' : 'Full Name'} *</label>
                            <input type="text" name="name" value={formData.name} onChange={handleChange} required />
                        </div>

                        <div className="form-group">
                            <label><Phone size={16} /> {lang === 'te' ? 'ఫోన్ నంబర్' : 'Phone Number'} *</label>
                            <input type="tel" name="phone" value={formData.phone} onChange={handleChange} pattern="[0-9]{10}" required />
                        </div>

                        {(formData.buyerType === 'RESTAURANT' || formData.buyerType === 'RETAILER' || formData.buyerType === 'WHOLESALER') && (
                            <div className="form-group">
                                <label><Store size={16} /> {lang === 'te' ? 'బిజినెస్ పేరు' : 'Business Name'}</label>
                                <input type="text" name="businessName" value={formData.businessName} onChange={handleChange} />
                            </div>
                        )}

                        {deliveryType !== 'pickup' && (
                            <>
                                <div className="form-group">
                                    <label><MapPin size={16} /> {lang === 'te' ? 'చిరునామా' : 'Delivery Address'} *</label>
                                    <textarea name="address" value={formData.address} onChange={handleChange} rows="2" required />
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>{lang === 'te' ? 'నగరం/గ్రామం' : 'City/Village'} *</label>
                                        <input type="text" name="city" value={formData.city} onChange={handleChange} required />
                                    </div>
                                    <div className="form-group">
                                        <label>{lang === 'te' ? 'జిల్లా' : 'District'} *</label>
                                        <input type="text" name="district" value={formData.district} onChange={handleChange} required />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>{lang === 'te' ? 'రాష్ట్రం' : 'State'} *</label>
                                        <select name="state" value={formData.state} onChange={handleChange}>
                                            <option>Andhra Pradesh</option>
                                            <option>Telangana</option>
                                            <option>Karnataka</option>
                                            <option>Tamil Nadu</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>{lang === 'te' ? 'పిన్‌కోడ్' : 'Pin Code'} *</label>
                                        <input type="text" name="pincode" value={formData.pincode} onChange={handleChange} pattern="[0-9]{6}" required />
                                    </div>
                                </div>
                            </>
                        )}

                        <div className="form-group">
                            <label>{lang === 'te' ? 'నోట్స్ (ఐచ్ఛికం)' : 'Order Notes (Optional)'}</label>
                            <textarea name="notes" value={formData.notes} onChange={handleChange} rows="2"
                                placeholder={lang === 'te' ? 'ఏదైనా ప్రత్యేక సూచనలు...' : 'Any special instructions...'} />
                        </div>

                        {/* Order Summary */}
                        <div className="order-summary-final">
                            <h4>{L.yourOrder}</h4>
                            {cart.map((item, idx) => (
                                <div key={idx} className="summary-item">
                                    <span>{item.crop} × {item.quantity}</span>
                                    <span>₹{(item.price * item.quantity).toLocaleString()}</span>
                                </div>
                            ))}
                            <div className="summary-total">
                                <strong>{L.total}</strong>
                                <strong>₹{calculateTotal().toLocaleString()}</strong>
                            </div>
                        </div>

                        <button type="submit" className="place-order-btn" disabled={loading}>
                            {loading ? (
                                <><Loader2 className="spin" /> {lang === 'te' ? 'ఆర్డర్ చేస్తోంది...' : 'Placing Order...'}</>
                            ) : (
                                <>{L.placeOrder} - ₹{calculateTotal().toLocaleString()}</>
                            )}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default GuestCheckout;

