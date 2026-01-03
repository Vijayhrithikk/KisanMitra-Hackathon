import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { orderService } from '../../services/orderService';
import { buyerService } from '../../services/buyerService';
import { walletService } from '../../services/walletService';
import {
    ArrowLeft, Package, Truck, CheckCircle, AlertTriangle, Eye,
    Wallet, Shield, ChevronDown, Star, Hash, Clock, MapPin,
    ShoppingBag, TrendingUp, CreditCard
} from 'lucide-react';
import './Market.css';

const BuyerDashboard = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [orders, setOrders] = useState([]);
    const [wallet, setWallet] = useState(null);
    const [buyer, setBuyer] = useState(null);
    const [activeTab, setActiveTab] = useState('orders');
    const [expandedOrder, setExpandedOrder] = useState(null);

    const L = {
        title: lang === 'te' ? '🛒 నా ఆర్డర్లు' : '🛒 My Orders',
        orders: lang === 'te' ? 'ఆర్డర్లు' : 'Orders',
        wallet: lang === 'te' ? 'వాలెట్' : 'Wallet',
        noOrders: lang === 'te' ? 'ఇంకా ఆర్డర్లు చేయలేదు' : 'No orders placed yet',
        shopNow: lang === 'te' ? 'షాపింగ్ చేయండి' : 'Start Shopping',
        confirmDelivery: lang === 'te' ? 'డెలివరీ కన్ఫర్మ్' : 'Confirm Delivery',
        raiseDispute: lang === 'te' ? 'సమస్య నమోదు' : 'Report Issue',
        trackOrder: lang === 'te' ? 'ట్రాక్' : 'Track',
        viewBlockchain: lang === 'te' ? 'బ్లాక్‌చెయిన్' : 'Blockchain'
    };

    useEffect(() => {
        loadData();
    }, []);

    const loadData = () => {
        // Try to get buyer from localStorage, but also load guest orders
        const storedBuyer = localStorage.getItem('currentBuyer');

        if (storedBuyer) {
            const buyerData = JSON.parse(storedBuyer);
            setBuyer(buyerData);
            const buyerOrders = orderService.getBuyerOrders(buyerData.buyerId);
            setOrders(buyerOrders);
            const buyerWallet = walletService.getWallet(buyerData.buyerId);
            setWallet(buyerWallet);
        } else {
            // Guest mode - show all recent orders or orders by session
            const guestId = localStorage.getItem('guestBuyerId') || `GUEST-${Date.now().toString(36)}`;
            localStorage.setItem('guestBuyerId', guestId);

            // Get guest orders
            const guestOrders = orderService.getBuyerOrders(guestId);
            setOrders(guestOrders);
            setBuyer({ name: 'Guest', buyerId: guestId, isGuest: true });
        }
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;

        return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    };

    const getStatusInfo = (status) => {
        const statusMap = {
            PENDING: { icon: Clock, color: '#f59e0b', bg: '#fef3c7', label: 'Pending' },
            CONFIRMED: { icon: CheckCircle, color: '#3b82f6', bg: '#dbeafe', label: 'Confirmed' },
            PAID: { icon: CreditCard, color: '#10b981', bg: '#d1fae5', label: 'Paid' },
            PROCESSING: { icon: Package, color: '#6366f1', bg: '#e0e7ff', label: 'Processing' },
            SHIPPED: { icon: Truck, color: '#8b5cf6', bg: '#ede9fe', label: 'Shipped' },
            IN_TRANSIT: { icon: Truck, color: '#ec4899', bg: '#fce7f3', label: 'In Transit' },
            DELIVERED: { icon: CheckCircle, color: '#22c55e', bg: '#dcfce7', label: 'Delivered' },
            COMPLETED: { icon: CheckCircle, color: '#16a34a', bg: '#dcfce7', label: 'Completed' },
            CANCELLED: { icon: AlertTriangle, color: '#ef4444', bg: '#fee2e2', label: 'Cancelled' },
            DISPUTED: { icon: AlertTriangle, color: '#f59e0b', bg: '#fef3c7', label: 'Disputed' }
        };
        return statusMap[status] || { icon: Clock, color: '#6b7280', bg: '#f3f4f6', label: status };
    };

    const handleConfirmDelivery = (orderId) => {
        const rating = prompt('Rate your experience (1-5 stars):', '5');
        const feedback = prompt('Any feedback? (optional):');

        if (rating) {
            const result = orderService.buyerConfirmDelivery(orderId, parseInt(rating), feedback || '');
            if (result.success) {
                loadData();
                alert('✅ Delivery confirmed! Thank you.');
            } else {
                alert(result.error);
            }
        }
    };

    const handleRaiseDispute = (orderId) => {
        const reason = prompt('Describe the issue:');
        if (reason) {
            const result = orderService.raiseDispute(orderId, 'BUYER', reason);
            if (result.success) {
                loadData();
                alert(`⚠️ Issue reported: ${result.disputeId}`);
            } else {
                alert(result.error);
            }
        }
    };

    // Calculate stats
    const stats = {
        total: orders.length,
        active: orders.filter(o => !['COMPLETED', 'CANCELLED'].includes(o.status)).length,
        completed: orders.filter(o => o.status === 'COMPLETED').length,
        spent: orders.filter(o => o.status !== 'CANCELLED').reduce((sum, o) => sum + (o.pricing?.total || 0), 0)
    };

    return (
        <div className="buyer-dashboard-container">
            {/* Header */}
            <header className="buyer-dashboard-header">
                <button className="back-btn-modern" onClick={() => navigate('/market')}>
                    <ArrowLeft size={20} />
                </button>
                <div className="header-content">
                    <h1>{L.title}</h1>
                    <p>{buyer?.isGuest ? 'Shopping as Guest' : buyer?.name}</p>
                </div>
            </header>

            {/* Stats Row */}
            <div className="buyer-stats-row">
                <div className="buyer-stat-chip">
                    <ShoppingBag size={18} />
                    <span className="chip-value">{stats.total}</span>
                    <span className="chip-label">Orders</span>
                </div>
                <div className="buyer-stat-chip active">
                    <Truck size={18} />
                    <span className="chip-value">{stats.active}</span>
                    <span className="chip-label">Active</span>
                </div>
                <div className="buyer-stat-chip success">
                    <CheckCircle size={18} />
                    <span className="chip-value">{stats.completed}</span>
                    <span className="chip-label">Done</span>
                </div>
                <div className="buyer-stat-chip">
                    <TrendingUp size={18} />
                    <span className="chip-value">₹{stats.spent.toLocaleString()}</span>
                    <span className="chip-label">Spent</span>
                </div>
            </div>

            {/* Orders List */}
            <div className="buyer-orders-section">
                <h3>📦 {lang === 'te' ? 'మీ ఆర్డర్లు' : 'Your Orders'}</h3>

                {orders.length === 0 ? (
                    <div className="empty-orders-card">
                        <div className="empty-icon">
                            <ShoppingBag size={48} />
                        </div>
                        <h4>{L.noOrders}</h4>
                        <p>{lang === 'te' ? 'నేరుగా రైతుల నుండి తాజా ఉత్పత్తులు కొనండి' : 'Buy fresh produce directly from farmers'}</p>
                        <button className="shop-now-btn" onClick={() => navigate('/market')}>
                            {L.shopNow}
                        </button>
                    </div>
                ) : (
                    <div className="buyer-orders-list">
                        {orders.map(order => {
                            const statusInfo = getStatusInfo(order.status);
                            const StatusIcon = statusInfo.icon;
                            const isExpanded = expandedOrder === order.orderId;

                            return (
                                <div key={order.orderId} className={`buyer-order-card ${isExpanded ? 'expanded' : ''}`}>
                                    {/* Order Header */}
                                    <div
                                        className="order-card-header"
                                        onClick={() => setExpandedOrder(isExpanded ? null : order.orderId)}
                                    >
                                        <div className="order-product">
                                            <div className="product-emoji">🌾</div>
                                            <div className="product-info">
                                                <span className="product-name">{order.crop}</span>
                                                <span className="product-qty">{order.quantity} {order.unit} • {formatDate(order.createdAt)}</span>
                                            </div>
                                        </div>
                                        <div className="order-right-side">
                                            <span className="order-amount">₹{order.pricing?.total?.toLocaleString()}</span>
                                            <div className="status-pill" style={{ background: statusInfo.bg, color: statusInfo.color }}>
                                                <StatusIcon size={14} />
                                                {statusInfo.label}
                                            </div>
                                            <ChevronDown
                                                size={18}
                                                className={`expand-chevron ${isExpanded ? 'rotated' : ''}`}
                                            />
                                        </div>
                                    </div>

                                    {/* Expanded Content */}
                                    {isExpanded && (
                                        <div className="order-expanded-content">
                                            {/* Order Details */}
                                            <div className="order-details-grid">
                                                <div className="detail-item">
                                                    <span className="detail-label">Order ID</span>
                                                    <code className="detail-value">{order.orderId}</code>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">Farmer</span>
                                                    <span className="detail-value">{order.farmerId}</span>
                                                </div>
                                                {order.delivery?.trackingId && (
                                                    <div className="detail-item">
                                                        <span className="detail-label">Tracking</span>
                                                        <code className="detail-value">{order.delivery.trackingId}</code>
                                                    </div>
                                                )}
                                                {order.delivery?.estimatedDate && (
                                                    <div className="detail-item">
                                                        <span className="detail-label">Expected</span>
                                                        <span className="detail-value">{order.delivery.estimatedDate}</span>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Blockchain Verification */}
                                            {order.payment?.transactions?.length > 0 && (
                                                <div className="blockchain-proof-card">
                                                    <div className="proof-header">
                                                        <Shield size={16} />
                                                        <span>Blockchain Verified</span>
                                                    </div>
                                                    <div className="proof-details">
                                                        <div className="proof-item">
                                                            <Hash size={14} />
                                                            <code>{order.payment.transactions[0].blockchainHash?.substring(0, 24) || 'Pending'}...</code>
                                                        </div>
                                                        <div className="proof-status">
                                                            <CheckCircle size={14} />
                                                            Escrow: {order.payment.transactions[0].escrowStatus}
                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Action Buttons */}
                                            <div className="order-action-buttons">
                                                <button
                                                    className="action-btn-modern track"
                                                    onClick={() => navigate(`/market/track/${order.orderId}`)}
                                                >
                                                    <MapPin size={16} />
                                                    {L.trackOrder}
                                                </button>

                                                {['SHIPPED', 'IN_TRANSIT', 'DELIVERED'].includes(order.status) && !order.buyerConfirmed && (
                                                    <button
                                                        className="action-btn-modern confirm"
                                                        onClick={() => handleConfirmDelivery(order.orderId)}
                                                    >
                                                        <CheckCircle size={16} />
                                                        {L.confirmDelivery}
                                                    </button>
                                                )}

                                                {['PAID', 'PROCESSING', 'SHIPPED', 'IN_TRANSIT', 'DELIVERED'].includes(order.status) &&
                                                    order.status !== 'DISPUTED' && !order.buyerConfirmed && (
                                                        <button
                                                            className="action-btn-modern dispute"
                                                            onClick={() => handleRaiseDispute(order.orderId)}
                                                        >
                                                            <AlertTriangle size={16} />
                                                            {L.raiseDispute}
                                                        </button>
                                                    )}

                                                {order.buyerConfirmed && (
                                                    <div className="rating-stars">
                                                        {[...Array(5)].map((_, i) => (
                                                            <Star
                                                                key={i}
                                                                size={16}
                                                                fill={i < (order.buyerRating || 5) ? '#f59e0b' : 'none'}
                                                                color="#f59e0b"
                                                            />
                                                        ))}
                                                        <span>Your rating</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Wallet Section (only if logged in) */}
            {wallet && (
                <div className="buyer-wallet-section">
                    <div className="wallet-card-modern">
                        <div className="wallet-info">
                            <Wallet size={24} />
                            <div>
                                <span className="wallet-label">Wallet Balance</span>
                                <span className="wallet-amount">₹{wallet.balance?.toLocaleString() || 0}</span>
                            </div>
                        </div>
                        <button className="wallet-action-btn" onClick={() => navigate('/wallet')}>
                            Manage
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BuyerDashboard;
