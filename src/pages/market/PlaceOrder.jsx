import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { marketService } from '../../services/marketService';
import { orderService } from '../../services/orderService';
import { walletService } from '../../services/walletService';
import { ArrowLeft, Minus, Plus, MapPin, Truck, CreditCard, Check, AlertCircle } from 'lucide-react';
import './Market.css';

const PlaceOrder = () => {
    const { listingId } = useParams();
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [listing, setListing] = useState(null);
    const [buyer, setBuyer] = useState(null);
    const [walletBalance, setWalletBalance] = useState(0);
    const [quantity, setQuantity] = useState(0);
    const [deliveryType, setDeliveryType] = useState('pickup');
    const [paymentMethod, setPaymentMethod] = useState('WALLET');
    const [pricing, setPricing] = useState(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    const L = {
        title: lang === 'te' ? '🛒 ఆర్డర్ పెట్టండి' : '🛒 Place Order',
        quantity: lang === 'te' ? 'పరిమాణం' : 'Quantity',
        delivery: lang === 'te' ? 'డెలివరీ' : 'Delivery',
        payment: lang === 'te' ? 'చెల్లింపు' : 'Payment',
        priceBreakdown: lang === 'te' ? 'ధర వివరాలు' : 'Price Breakdown',
        subtotal: lang === 'te' ? 'ఉప మొత్తం' : 'Subtotal',
        deliveryCharge: lang === 'te' ? 'డెలివరీ ఛార్జ్' : 'Delivery Charge',
        platformFee: lang === 'te' ? 'ప్లాట్‌ఫాం ఫీ' : 'Platform Fee (1%)',
        total: lang === 'te' ? 'మొత్తం' : 'Total',
        farmerGets: lang === 'te' ? 'రైతుకు వెళ్ళేది' : 'Farmer Gets',
        placeOrder: lang === 'te' ? 'ఆర్డర్ ఇవ్వండి' : 'Place Order',
        minOrder: lang === 'te' ? 'కనీస ఆర్డర్' : 'Min. Order',
        pickup: lang === 'te' ? 'స్వయంగా తీసుకెళ్ళండి' : 'Self Pickup',
        local: lang === 'te' ? 'లోకల్ డెలివరీ' : 'Local Delivery',
        state: lang === 'te' ? 'స్టేట్ డెలివరీ' : 'State Delivery',
        registerFirst: lang === 'te' ? 'ముందుగా రిజిస్టర్ చేయండి' : 'Please register first'
    };

    const deliveryOptions = [
        { id: 'pickup', label: L.pickup, icon: '🏪', charge: 0 },
        { id: 'local', label: L.local, icon: '🛵', charge: 200 },
        { id: 'state', label: L.state, icon: '🚛', charge: 500 }
    ];

    const paymentOptions = [
        { id: 'WALLET', label: `Kisan Wallet (₹${walletBalance.toLocaleString()})`, icon: '💳' },
        { id: 'UPI', label: 'UPI', icon: '📱' },
        { id: 'BANK_TRANSFER', label: 'Bank Transfer', icon: '🏦' },
        { id: 'COD', label: 'Cash on Delivery', icon: '💵' }
    ];

    useEffect(() => {
        const fetchData = async () => {
            // Get listing from MongoDB
            const listingData = await marketService.getListingById(listingId);
            if (listingData) {
                setListing(listingData);
                const minQty = listingData.pricing?.minOrderQty || 10;
                setQuantity(minQty);
            }

            // Get current buyer and wallet balance
            const storedBuyer = localStorage.getItem('currentBuyer');
            if (storedBuyer) {
                const buyerData = JSON.parse(storedBuyer);
                setBuyer(buyerData);

                // Get wallet balance - create wallet if needed for farmer-buyers
                let balance = walletService.getBalance(buyerData.buyerId);

                // If no wallet exists and this is a farmer-buyer, create one
                if (balance === 0 && buyerData.type === 'FARMER_BUYER') {
                    const existingWallet = walletService.getWallet(buyerData.buyerId);
                    if (!existingWallet) {
                        // Use test buyer wallet for farmer-buyers
                        const testBuyer = walletService.getTestBuyer();
                        if (testBuyer) {
                            balance = testBuyer.balance;
                            buyerData.buyerId = testBuyer.id;
                            setBuyer(buyerData);
                        }
                    }
                }

                setWalletBalance(balance);
            }
        };

        fetchData();
    }, [listingId]);

    useEffect(() => {
        if (listing && quantity > 0) {
            const calc = orderService.calculatePricing(listing, quantity, deliveryType);
            setPricing(calc);
        }
    }, [listing, quantity, deliveryType]);

    const handleQuantityChange = (delta) => {
        const minQty = listing?.pricing?.minOrderQty || 10;
        const maxQty = listing?.quantity || 1000;
        const newQty = Math.max(minQty, Math.min(maxQty, quantity + delta));
        setQuantity(newQty);
    };

    const handlePlaceOrder = async () => {
        if (!buyer) {
            // Redirect to guest checkout instead of buyer login
            navigate('/checkout/guest', { state: { listingId, quantity, deliveryType } });
            return;
        }

        setLoading(true);
        setError('');

        try {
            // Check wallet balance for WALLET payment
            if (paymentMethod === 'WALLET') {
                if (walletBalance < pricing.total) {
                    setError(`Insufficient wallet balance. You have ₹${walletBalance.toLocaleString()} but need ₹${pricing.total.toLocaleString()}. Please add money to your wallet.`);
                    setLoading(false);
                    return;
                }
            }

            // Create order via DATABASE API (not localStorage)
            const orderData = {
                listingId: listing.listingId,
                farmerId: listing.farmerId,
                farmerPhone: listing.farmerPhone,
                buyerId: buyer.buyerId,
                buyerName: buyer.name,
                buyerPhone: buyer.phone,
                crop: listing.crop,
                variety: listing.variety,
                quantity,
                unit: listing.unit,
                pricing: {
                    unitPrice: pricing.unitPrice,
                    subtotal: pricing.subtotal,
                    deliveryCharge: pricing.deliveryCharge,
                    platformFee: pricing.platformFee,
                    total: pricing.total
                },
                delivery: {
                    type: deliveryType,
                    address: buyer.addresses?.[0] || null
                },
                payment: {
                    method: paymentMethod,
                    status: 'PENDING'
                },
                status: 'PENDING'
            };

            console.log('📦 Creating order via API:', orderData);

            const response = await fetch(`${import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api'}/orders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });

            const result = await response.json();
            console.log('📦 Order API response:', result);

            if (response.ok && result.orderId) {
                // Process payment for WALLET method
                if (paymentMethod === 'WALLET') {
                    const payResult = walletService.payForOrder(
                        buyer.buyerId,
                        result.orderId,
                        pricing.total
                    );

                    if (!payResult.success) {
                        setError(payResult.error);
                        setLoading(false);
                        return;
                    }

                    // Update wallet balance display
                    setWalletBalance(payResult.newBalance);
                }

                setSuccess({ orderId: result.orderId, pricing });
            } else {
                setError(result.error || 'Order creation failed');
            }
        } catch (err) {
            console.error('Order error:', err);
            setError('Order creation failed: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!listing) {
        return (
            <div className="market-container white-theme">
                <div className="loading-state">Loading...</div>
            </div>
        );
    }

    if (success) {
        return (
            <div className="market-container white-theme">
                <div className="success-screen">
                    <div className="success-icon">✅</div>
                    <h2>{lang === 'te' ? 'ఆర్డర్ విజయవంతం!' : 'Order Placed!'}</h2>
                    <p>Order ID: <strong>{success.orderId}</strong></p>
                    <div className="order-summary-mini">
                        <p>{listing.crop} - {quantity} {listing.unit}</p>
                        <p className="total">₹{success.pricing.total}</p>
                    </div>
                    <button className="primary-btn" onClick={() => navigate('/market')}>
                        {lang === 'te' ? 'మార్కెట్‌కు వెళ్ళండి' : 'Back to Market'}
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

            <div className="order-content">
                {/* Product Info */}
                <div className="product-card">
                    <div className="product-crop">{listing.crop}</div>
                    <div className="product-variety">{listing.variety}</div>
                    <div className="product-price">₹{listing.pricing?.basePrice || listing.price}/{listing.unit}</div>
                    <div className="product-available">
                        {lang === 'te' ? 'అందుబాటులో' : 'Available'}: {listing.quantity} {listing.unit}
                    </div>
                </div>

                {/* Quantity Selector */}
                <div className="order-section">
                    <h3>{L.quantity}</h3>
                    <div className="quantity-selector">
                        <button onClick={() => handleQuantityChange(-10)} disabled={quantity <= (listing.pricing?.minOrderQty || 10)}>
                            <Minus size={20} />
                        </button>
                        <div className="quantity-display">
                            <span className="quantity-value">{quantity}</span>
                            <span className="quantity-unit">{listing.unit}</span>
                        </div>
                        <button onClick={() => handleQuantityChange(10)} disabled={quantity >= listing.quantity}>
                            <Plus size={20} />
                        </button>
                    </div>
                    <div className="min-order-note">
                        {L.minOrder}: {listing.pricing?.minOrderQty || 10} {listing.unit}
                    </div>
                </div>

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
                {pricing && (
                    <div className="order-section pricing-section">
                        <h3>{L.priceBreakdown}</h3>
                        <div className="price-rows">
                            <div className="price-row">
                                <span>{quantity} {listing.unit} × ₹{pricing.unitPrice}</span>
                                <span>₹{pricing.subtotal}</span>
                            </div>
                            {pricing.discountApplied && (
                                <div className="price-row discount">
                                    <span>Bulk Discount Applied</span>
                                    <span className="green">-₹{(pricing.originalPrice - pricing.unitPrice) * quantity}</span>
                                </div>
                            )}
                            <div className="price-row">
                                <span>{L.deliveryCharge}</span>
                                <span>{pricing.deliveryCharge === 0 ? 'Free' : `₹${pricing.deliveryCharge}`}</span>
                            </div>
                            <div className="price-row">
                                <span>{L.platformFee}</span>
                                <span>₹{pricing.platformFee}</span>
                            </div>
                            <div className="price-row total">
                                <span>{L.total}</span>
                                <span>₹{pricing.total}</span>
                            </div>
                            <div className="price-row farmer">
                                <span>{L.farmerGets}</span>
                                <span className="green">₹{pricing.farmerGets}</span>
                            </div>
                        </div>
                    </div>
                )}

                {!buyer && (
                    <div className="warning-banner">
                        <AlertCircle size={18} />
                        <span>{L.registerFirst}</span>
                        <button onClick={() => navigate('/market/register')}>
                            {lang === 'te' ? 'రిజిస్టర్' : 'Register'}
                        </button>
                    </div>
                )}

                {error && <div className="error-msg">{error}</div>}

                <button
                    className="primary-btn large"
                    onClick={handlePlaceOrder}
                    disabled={loading || !buyer}
                >
                    {loading ? 'Processing...' : (
                        <>
                            <Check size={20} />
                            {L.placeOrder} - ₹{pricing?.total || 0}
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default PlaceOrder;
