import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { orderService } from '../../services/orderService';
import FarmerHeader from '../../components/ui/FarmerHeader';
import { ArrowLeft, Package, Clock, CheckCircle, Truck, XCircle, ChevronRight } from 'lucide-react';
import './Market.css';

const FarmerOrders = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const { user } = useAuth();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [orders, setOrders] = useState([]);
    const [filter, setFilter] = useState('ALL');
    const [selectedOrder, setSelectedOrder] = useState(null);

    const L = {
        title: lang === 'te' ? '📦 నా ఆర్డర్లు' : '📦 My Orders',
        all: lang === 'te' ? 'అన్నీ' : 'All',
        pending: lang === 'te' ? 'పెండింగ్' : 'Pending',
        confirmed: lang === 'te' ? 'కన్ఫర్మ్' : 'Confirmed',
        shipped: lang === 'te' ? 'షిప్' : 'Shipped',
        completed: lang === 'te' ? 'పూర్తి' : 'Completed',
        noOrders: lang === 'te' ? 'ఆర్డర్లు లేవు' : 'No orders yet',
        accept: lang === 'te' ? 'అంగీకరించు' : 'Accept',
        reject: lang === 'te' ? 'తిరస్కరించు' : 'Reject',
        ship: lang === 'te' ? 'షిప్ చేయు' : 'Mark Shipped',
        delivered: lang === 'te' ? 'డెలివరీ అయింది' : 'Mark Delivered',
        buyer: lang === 'te' ? 'కొనుగోలుదారు' : 'Buyer',
        payout: lang === 'te' ? 'మీకు వచ్చేది' : 'Your Payout'
    };

    const statusIcons = {
        PENDING: <Clock size={16} className="status-icon pending" />,
        CONFIRMED: <CheckCircle size={16} className="status-icon confirmed" />,
        PAID: <CheckCircle size={16} className="status-icon paid" />,
        SHIPPED: <Truck size={16} className="status-icon shipped" />,
        DELIVERED: <Package size={16} className="status-icon delivered" />,
        COMPLETED: <CheckCircle size={16} className="status-icon completed" />,
        CANCELLED: <XCircle size={16} className="status-icon cancelled" />
    };

    const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';
    const [loading, setLoading] = useState(true);

    // Fetch orders from DATABASE
    useEffect(() => {
        const loadOrders = async () => {
            try {
                // Get farmer phone or ID
                const farmerPhone = user?.phone || user?.phoneNumber;
                const farmerId = user?.farmerId || user?.id;

                console.log('📦 Fetching orders from database for:', farmerId || farmerPhone);

                if (!farmerPhone && !farmerId) {
                    console.warn('No farmer identifier found');
                    setLoading(false);
                    return;
                }

                // Fetch from database API
                const response = await fetch(`${API_BASE}/orders/farmer/${farmerId || farmerPhone}`);
                if (response.ok) {
                    const farmerOrders = await response.json();
                    console.log(`✅ Found ${farmerOrders.length} orders from database`);
                    setOrders(farmerOrders);
                } else {
                    console.warn('Orders API returned:', response.status);
                    setOrders([]);
                }
            } catch (error) {
                console.error('Error fetching orders from database:', error);
                setOrders([]);
            } finally {
                setLoading(false);
            }
        };

        loadOrders();
    }, [user]);

    const filteredOrders = orders.filter(o => {
        if (filter === 'ALL') return true;
        return o.status === filter;
    });

    const handleStatusUpdate = (orderId, newStatus) => {
        orderService.updateOrderStatus(orderId, newStatus);
        setOrders(orderService.getFarmerOrders(user.farmerId));
        setSelectedOrder(null);
    };

    const handleDeliveryUpdate = (orderId, status) => {
        orderService.updateDeliveryStatus(orderId, status);
        if (status === 'DELIVERED') {
            orderService.updateOrderStatus(orderId, 'COMPLETED');
        }
        setOrders(orderService.getFarmerOrders(user.farmerId));
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    };

    // Show loading state
    if (loading) {
        return (
            <div className="market-container white-theme">
                <FarmerHeader />
                <div className="loading-state" style={{ marginTop: '100px', textAlign: 'center', padding: '40px' }}>
                    <Clock size={32} className="animate-spin" />
                    <p>{lang === 'te' ? 'ఆర్డర్లు లోడ్ అవుతున్నాయి...' : 'Loading orders...'}</p>
                </div>
            </div>
        );
    }

    // Require login
    if (!user) {
        return (
            <div className="market-container white-theme">
                <FarmerHeader />
                <div className="empty-state" style={{ marginTop: '100px', textAlign: 'center', padding: '40px' }}>
                    <Package size={48} />
                    <p>{lang === 'te' ? 'దయచేసి లాగిన్ అవ్వండి' : 'Please login first'}</p>
                    <button className="primary-btn" onClick={() => navigate('/login')}>Login</button>
                </div>
            </div>
        );
    }

    return (
        <div className="market-container white-theme">
            {/* Persistent Navigation */}
            <FarmerHeader />

            <header className="market-header-simple" style={{ marginTop: '70px' }}>
                <h1>{L.title}</h1>
            </header>

            {/* Filter Tabs */}
            <div className="order-filters" style={{ display: 'flex', gap: '8px', padding: '0 16px 16px', overflowX: 'auto' }}>
                {['ALL', 'PENDING', 'CONFIRMED', 'SHIPPED', 'COMPLETED'].map(f => (
                    <button
                        key={f}
                        className={`filter-tab ${filter === f ? 'active' : ''}`}
                        onClick={() => setFilter(f)}
                        style={{
                            padding: '8px 16px',
                            border: 'none',
                            borderRadius: '20px',
                            background: filter === f ? '#10b981' : '#f3f4f6',
                            color: filter === f ? 'white' : '#374151',
                            cursor: 'pointer',
                            fontWeight: '500',
                            whiteSpace: 'nowrap'
                        }}
                    >
                        {L[f.toLowerCase()] || f}
                    </button>
                ))}
            </div>

            {/* Orders List */}
            <div className="orders-list" style={{ padding: '0 16px' }}>
                {filteredOrders.length === 0 ? (
                    <div className="empty-orders" style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
                        <Package size={48} />
                        <p>{L.noOrders}</p>
                    </div>
                ) : (
                    filteredOrders.map(order => (
                        <div
                            key={order.orderId}
                            className={`order-card ${selectedOrder?.orderId === order.orderId ? 'expanded' : ''}`}
                            onClick={() => setSelectedOrder(selectedOrder?.orderId === order.orderId ? null : order)}
                        >
                            <div className="order-header">
                                <div className="order-info">
                                    <span className="order-id">{order.orderId}</span>
                                    <span className="order-date">{formatDate(order.createdAt)}</span>
                                </div>
                                <div className={`order-status ${(order.status || 'pending').toLowerCase()}`}>
                                    {statusIcons[order.status] || statusIcons.PENDING}
                                    <span>{order.status || 'PENDING'}</span>
                                </div>
                            </div>

                            <div className="order-product">
                                <span className="crop-name">{order.crop}</span>
                                <span className="quantity">{order.quantity} {order.unit}</span>
                            </div>

                            <div className="order-pricing">
                                <span className="total">₹{order.pricing?.total || 0}</span>
                                <span className="payout">{L.payout}: ₹{order.payment?.farmerPayout?.amount || order.pricing?.total || 0}</span>
                            </div>

                            {/* Expanded View */}
                            {selectedOrder?.orderId === order.orderId && (
                                <div className="order-details">
                                    <div className="detail-section">
                                        <h4>{L.buyer}</h4>
                                        <p>ID: {order.buyerId || 'Guest'}</p>
                                        {order.delivery?.address && (
                                            <p>{order.delivery.address.city}, {order.delivery.address.district}</p>
                                        )}
                                    </div>

                                    <div className="detail-section">
                                        <h4>Delivery</h4>
                                        <p>Type: {order.delivery.type}</p>
                                        <p>Status: {order.delivery.status}</p>
                                        <p>ETA: {order.delivery.estimatedDate}</p>
                                    </div>

                                    <div className="detail-section">
                                        <h4>Payment</h4>
                                        <p>Status: {order.payment.status}</p>
                                        <p>Method: {order.payment.method}</p>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="order-actions">
                                        {order.status === 'PENDING' && (
                                            <>
                                                <button
                                                    className="action-btn accept"
                                                    onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.orderId, 'CONFIRMED'); }}
                                                >
                                                    ✓ {L.accept}
                                                </button>
                                                <button
                                                    className="action-btn reject"
                                                    onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.orderId, 'CANCELLED'); }}
                                                >
                                                    ✕ {L.reject}
                                                </button>
                                            </>
                                        )}
                                        {order.status === 'CONFIRMED' && (
                                            <button
                                                className="action-btn ship"
                                                onClick={(e) => { e.stopPropagation(); handleDeliveryUpdate(order.orderId, 'PICKED_UP'); handleStatusUpdate(order.orderId, 'SHIPPED'); }}
                                            >
                                                🚚 {L.ship}
                                            </button>
                                        )}
                                        {order.status === 'SHIPPED' && (
                                            <button
                                                className="action-btn deliver"
                                                onClick={(e) => { e.stopPropagation(); handleDeliveryUpdate(order.orderId, 'DELIVERED'); }}
                                            >
                                                ✓ {L.delivered}
                                            </button>
                                        )}
                                    </div>
                                </div>
                            )}

                            <ChevronRight size={20} className={`chevron ${selectedOrder?.orderId === order.orderId ? 'rotated' : ''}`} />
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default FarmerOrders;
