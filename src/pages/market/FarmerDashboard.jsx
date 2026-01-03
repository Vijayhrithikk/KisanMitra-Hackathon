import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { orderService } from '../../services/orderService';
import { marketService } from '../../services/marketService';
import { walletService } from '../../services/walletService';
import { deliveryService } from '../../services/deliveryService';
import FarmerHeader from '../../components/ui/FarmerHeader';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';
import {
    ArrowLeft, Package, Truck, CheckCircle, XCircle, Clock,
    DollarSign, BarChart3, Edit2, Trash2, Eye, MapPin, Phone,
    TrendingUp, AlertCircle, RefreshCw
} from 'lucide-react';
import './Market.css';

const FarmerDashboard = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const { user } = useAuth();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [activeTab, setActiveTab] = useState('overview');
    const [orders, setOrders] = useState([]);
    const [listings, setListings] = useState([]);
    const [wallet, setWallet] = useState(null);
    const [stats, setStats] = useState({});
    const [shipments, setShipments] = useState([]);
    const [loading, setLoading] = useState(true);

    // Localization
    const L = {
        title: lang === 'te' ? '👨‍🌾 రైతు డాష్‌బోర్డ్' : '👨‍🌾 Farmer Dashboard',
        overview: lang === 'te' ? 'అవలోకనం' : 'Overview',
        orders: lang === 'te' ? 'ఆర్డర్లు' : 'Orders',
        listings: lang === 'te' ? 'లిస్టింగ్‌లు' : 'Listings',
        shipments: lang === 'te' ? 'షిప్‌మెంట్స్' : 'Shipments',
        payouts: lang === 'te' ? 'పేఔట్స్' : 'Payouts',
        totalRevenue: lang === 'te' ? 'మొత్తం ఆదాయం' : 'Total Revenue',
        pendingOrders: lang === 'te' ? 'పెండింగ్ ఆర్డర్లు' : 'Pending Orders',
        activeListings: lang === 'te' ? 'యాక్టివ్ లిస్టింగ్‌లు' : 'Active Listings',
        inTransit: lang === 'te' ? 'రవాణాలో' : 'In Transit',
        confirm: lang === 'te' ? 'కన్ఫర్మ్' : 'Confirm',
        reject: lang === 'te' ? 'రిజెక్ట్' : 'Reject',
        ship: lang === 'te' ? 'షిప్' : 'Ship',
        noOrders: lang === 'te' ? 'ఆర్డర్లు లేవు' : 'No orders yet'
    };

    useEffect(() => {
        loadDashboardData();
    }, [user]);

    const loadDashboardData = async () => {
        try {
            // CHANGED: Use phone number for authentication instead of farmerId
            const farmerPhone = user?.phone || user?.phoneNumber ||
                (localStorage.getItem('currentFarmer') &&
                    JSON.parse(localStorage.getItem('currentFarmer'))?.phone);

            const farmerId = user?.farmerId ||
                (localStorage.getItem('currentFarmer') &&
                    JSON.parse(localStorage.getItem('currentFarmer'))?.farmerId);

            console.log('🔑 Farmer Auth:', { farmerPhone, farmerId, user });

            if (!farmerPhone && !farmerId) {
                console.warn('No farmer phone or ID found');
                setLoading(false);
                return;
            }

            // Load orders from API - FIXED: Call backend API instead of local storage
            console.log('📦 Fetching orders for farmer:', farmerId || farmerPhone);
            let farmerOrders = [];
            try {
                const ordersResponse = await fetch(`${API_BASE}/orders/farmer/${farmerId || farmerPhone}`);
                if (ordersResponse.ok) {
                    farmerOrders = await ordersResponse.json();
                    console.log(`✅ Found ${farmerOrders.length} orders from API`);
                } else {
                    console.warn('Orders API returned error:', ordersResponse.status);
                }
            } catch (error) {
                console.error('Error fetching orders:', error);
            }
            setOrders(farmerOrders);

            // Load listings - CHANGED: Query by phone number since listings store farmerPhone
            let farmerListings = [];
            if (farmerPhone) {
                console.log('📋 Fetching listings for phone:', farmerPhone);
                farmerListings = await marketService.getFarmerListingsByPhone(farmerPhone);
            } else if (farmerId) {
                farmerListings = await marketService.getFarmerListings(farmerId);
            }

            // DEBUG: Log what we got from the API
            console.log('Raw farmerListings response:', farmerListings);
            console.log('Type:', typeof farmerListings);
            console.log('Is array:', Array.isArray(farmerListings));

            // Ensure it's always an array
            if (!Array.isArray(farmerListings)) {
                console.warn('getFarmerListings did not return an array, converting...');
                farmerListings = [];
            }

            setListings(farmerListings);

            // Load wallet
            const farmerWallet = walletService.getWallet(farmerId);
            setWallet(farmerWallet);

            // Load active shipments
            const activeShipments = deliveryService.getActiveShipments();
            setShipments(activeShipments.filter(s =>
                farmerOrders.some(o => o.orderId === s.orderId)
            ));

            // Calculate stats - Now safe since farmerListings is guaranteed to be array
            const completedOrders = farmerOrders.filter(o => o.status === 'COMPLETED');
            setStats({
                totalRevenue: completedOrders.reduce((sum, o) => sum + o.payment?.farmerPayout?.amount || 0, 0),
                pendingOrders: farmerOrders.filter(o => ['PENDING', 'CONFIRMED', 'PAID'].includes(o.status)).length,
                activeListings: farmerListings.filter(l => l.status === 'LISTED').length,
                inTransit: farmerOrders.filter(o => ['SHIPPED', 'IN_TRANSIT'].includes(o.status)).length,
                totalOrders: farmerOrders.length,
                completedOrders: completedOrders.length
            });

            setLoading(false);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            setLoading(false);
        }
    };

    // Order Actions
    const handleConfirmOrder = (orderId) => {
        const result = orderService.confirmOrder(orderId);
        if (result.success) {
            loadDashboardData();
        } else {
            alert(result.error);
        }
    };

    const handleRejectOrder = (orderId) => {
        const reason = prompt('Reason for rejection:');
        if (reason) {
            const result = orderService.rejectOrder(orderId, reason);
            if (result.success) {
                loadDashboardData();
            } else {
                alert(result.error);
            }
        }
    };

    const handleShipOrder = (orderId) => {
        const partner = prompt('Delivery partner (SELF/KISAN_EXPRESS/AGRISHIP/INDIA_POST):', 'KISAN_EXPRESS');
        const vehicleNumber = prompt('Vehicle number (optional):');

        const result = orderService.shipOrder(orderId, {
            partner: partner || 'SELF',
            vehicleNumber,
            origin: user?.village || 'Farm Location'
        });

        if (result.success) {
            loadDashboardData();
            alert(`Order shipped! Tracking ID: ${result.trackingId}`);
        } else {
            alert(result.error);
        }
    };

    const handleMarkProcessing = (orderId) => {
        const result = orderService.markAsProcessing(orderId);
        if (result.success) {
            loadDashboardData();
        } else {
            alert(result.error);
        }
    };

    const getStatusBadge = (status) => {
        const colors = {
            PENDING: { bg: '#fef3c7', color: '#92400e' },
            CONFIRMED: { bg: '#dbeafe', color: '#1e40af' },
            PAID: { bg: '#d1fae5', color: '#065f46' },
            PROCESSING: { bg: '#e0e7ff', color: '#3730a3' },
            SHIPPED: { bg: '#fce7f3', color: '#9d174d' },
            IN_TRANSIT: { bg: '#fae8ff', color: '#86198f' },
            DELIVERED: { bg: '#dcfce7', color: '#166534' },
            COMPLETED: { bg: '#dcfce7', color: '#166534' },
            CANCELLED: { bg: '#fee2e2', color: '#991b1b' },
            DISPUTED: { bg: '#fef3c7', color: '#92400e' }
        };
        const style = colors[status] || { bg: '#f3f4f6', color: '#374151' };
        return (
            <span className="status-badge" style={{ background: style.bg, color: style.color }}>
                {status}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="market-container">
                <div className="loading-state">
                    <RefreshCw className="animate-spin" size={32} />
                    <p>Loading dashboard...</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="market-container">
                <div className="empty-state">
                    <AlertCircle size={48} />
                    <p>{lang === 'te' ? 'దయచేసి లాగిన్ అవ్వండి' : 'Please login first'}</p>
                    <button className="primary-btn" onClick={() => navigate('/login')}>
                        {lang === 'te' ? 'లాగిన్' : 'Login'}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="market-container">
            {/* Persistent Navigation Header */}
            <FarmerHeader />

            {/* Page Header */}
            <header className="market-header-simple" style={{ marginTop: '70px' }}>
                <h1>{L.title}</h1>
            </header>

            {/* Stats Cards */}
            <div className="dashboard-stats">
                <div className="stat-card revenue">
                    <DollarSign size={24} />
                    <div className="stat-info">
                        <span className="stat-value">₹{stats.totalRevenue?.toLocaleString() || 0}</span>
                        <span className="stat-label">{L.totalRevenue}</span>
                    </div>
                </div>
                <div className="stat-card orders">
                    <Package size={24} />
                    <div className="stat-info">
                        <span className="stat-value">{stats.pendingOrders || 0}</span>
                        <span className="stat-label">{L.pendingOrders}</span>
                    </div>
                </div>
                <div className="stat-card listings">
                    <BarChart3 size={24} />
                    <div className="stat-info">
                        <span className="stat-value">{stats.activeListings || 0}</span>
                        <span className="stat-label">{L.activeListings}</span>
                    </div>
                </div>
                <div className="stat-card transit">
                    <Truck size={24} />
                    <div className="stat-info">
                        <span className="stat-value">{stats.inTransit || 0}</span>
                        <span className="stat-label">{L.inTransit}</span>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="dashboard-tabs">
                {['overview', 'orders', 'listings', 'shipments', 'payouts'].map(tab => (
                    <button
                        key={tab}
                        className={`tab ${activeTab === tab ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab)}
                    >
                        {L[tab]}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="dashboard-content">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="overview-section">
                        <h3>📊 {lang === 'te' ? 'త్వరిత చూపు' : 'Quick Overview'}</h3>
                        <div className="overview-grid">
                            <div className="overview-card">
                                <h4>{lang === 'te' ? 'ఇటీవలి ఆర్డర్లు' : 'Recent Orders'}</h4>
                                {orders.slice(0, 3).map(order => (
                                    <div key={order.orderId} className="overview-item">
                                        <span>{order.crop} - {order.quantity} {order.unit}</span>
                                        {getStatusBadge(order.status)}
                                    </div>
                                ))}
                                {orders.length === 0 && <p className="empty-text">{L.noOrders}</p>}
                            </div>
                            <div className="overview-card">
                                <h4>{lang === 'te' ? 'యాక్టివ్ షిప్‌మెంట్స్' : 'Active Shipments'}</h4>
                                {shipments.slice(0, 3).map(ship => (
                                    <div key={ship.trackingId} className="overview-item">
                                        <span>{ship.trackingId}</span>
                                        {getStatusBadge(ship.status)}
                                    </div>
                                ))}
                                {shipments.length === 0 && <p className="empty-text">No active shipments</p>}
                            </div>
                        </div>
                    </div>
                )}

                {/* Orders Tab */}
                {activeTab === 'orders' && (
                    <div className="orders-section">
                        {orders.length === 0 ? (
                            <div className="empty-state">
                                <Package size={48} />
                                <p>{L.noOrders}</p>
                            </div>
                        ) : (
                            <div className="orders-list">
                                {orders.map(order => (
                                    <div key={order.orderId} className="order-card-farmer">
                                        <div className="order-header">
                                            <span className="order-id">{order.orderId}</span>
                                            {getStatusBadge(order.status)}
                                        </div>
                                        <div className="order-details">
                                            <p><strong>{order.crop}</strong> - {order.variety}</p>
                                            <p>{order.quantity} {order.unit} × ₹{order.pricing?.unitPrice}</p>
                                            <p className="order-total">Total: ₹{order.pricing?.total}</p>
                                        </div>
                                        <div className="order-buyer">
                                            <MapPin size={14} />
                                            <span>{order.delivery?.address?.city || 'Pickup'}</span>
                                        </div>
                                        <div className="order-actions">
                                            {order.status === 'PENDING' && (
                                                <>
                                                    <button className="action-btn confirm" onClick={() => handleConfirmOrder(order.orderId)}>
                                                        <CheckCircle size={16} /> {L.confirm}
                                                    </button>
                                                    <button className="action-btn reject" onClick={() => handleRejectOrder(order.orderId)}>
                                                        <XCircle size={16} /> {L.reject}
                                                    </button>
                                                </>
                                            )}
                                            {['CONFIRMED', 'PAID'].includes(order.status) && (
                                                <>
                                                    <button className="action-btn process" onClick={() => handleMarkProcessing(order.orderId)}>
                                                        <Package size={16} /> Process
                                                    </button>
                                                    <button className="action-btn ship" onClick={() => handleShipOrder(order.orderId)}>
                                                        <Truck size={16} /> {L.ship}
                                                    </button>
                                                </>
                                            )}
                                            {order.status === 'PROCESSING' && (
                                                <button className="action-btn ship" onClick={() => handleShipOrder(order.orderId)}>
                                                    <Truck size={16} /> {L.ship}
                                                </button>
                                            )}
                                            <button className="action-btn view" onClick={() => navigate(`/market/track/${order.orderId}`)}>
                                                <Eye size={16} /> View
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Listings Tab */}
                {activeTab === 'listings' && (
                    <div className="listings-section">
                        <div className="section-header">
                            <h3>{lang === 'te' ? 'నా లిస్టింగ్‌లు' : 'My Listings'}</h3>
                            <button className="primary-btn" onClick={() => navigate('/market/create')}>
                                + {lang === 'te' ? 'కొత్త లిస్టింగ్' : 'New Listing'}
                            </button>
                        </div>
                        <div className="listings-grid">
                            {listings.map(listing => (
                                <div key={listing.listingId} className="listing-card-compact">
                                    {/* Listing Image */}
                                    <div className="listing-image" style={{ height: '80px', marginBottom: '8px', borderRadius: '8px', overflow: 'hidden', background: '#E8F5E9' }}>
                                        {(listing.images?.[0]?.data || listing.imageUrl) ? (
                                            <img
                                                src={listing.images[0].data || listing.imageUrl}
                                                alt={listing.crop}
                                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                            />
                                        ) : (
                                            <div style={{ width: '100%', height: '100%', backgroundColor: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', color: '#9ca3af' }}>
                                                No Image
                                            </div>
                                        )}
                                    </div>
                                    <div className="listing-header">
                                        <span className="listing-crop">{listing.crop}</span>
                                        {getStatusBadge(listing.status)}
                                    </div>
                                    <p style={{ fontSize: '12px', color: '#6B7280', margin: '4px 0' }}>{listing.quantity} {listing.unit} @ ₹{listing.price}/{listing.unit}</p>
                                    <div className="listing-actions">
                                        <button onClick={() => navigate(`/market/${listing.listingId}`)}>
                                            <Eye size={14} />
                                        </button>
                                        <button onClick={() => navigate(`/market/create?edit=${listing.listingId}`)}>
                                            <Edit2 size={14} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                            {listings.length === 0 && (
                                <div className="empty-state">
                                    <p>{lang === 'te' ? 'లిస్టింగ్‌లు లేవు' : 'No listings yet'}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Shipments Tab */}
                {activeTab === 'shipments' && (
                    <div className="shipments-section">
                        <h3>🚛 {lang === 'te' ? 'యాక్టివ్ షిప్‌మెంట్స్' : 'Active Shipments'}</h3>
                        {shipments.length === 0 ? (
                            <div className="empty-state">
                                <Truck size={48} />
                                <p>{lang === 'te' ? 'షిప్‌మెంట్స్ లేవు' : 'No active shipments'}</p>
                            </div>
                        ) : (
                            <div className="shipments-list">
                                {shipments.map(ship => (
                                    <div key={ship.trackingId} className="shipment-card">
                                        <div className="shipment-header">
                                            <span className="tracking-id">{ship.trackingId}</span>
                                            {getStatusBadge(ship.status)}
                                        </div>
                                        <div className="shipment-route">
                                            <span>{ship.fromAddress?.city}</span>
                                            <span className="route-arrow">→</span>
                                            <span>{ship.toAddress?.city}</span>
                                        </div>
                                        <div className="shipment-info">
                                            <p>Partner: {ship.partnerName}</p>
                                            <p>ETA: {ship.estimatedDelivery}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Payouts Tab */}
                {activeTab === 'payouts' && (
                    <div className="payouts-section">
                        <h3>💰 {lang === 'te' ? 'పేఔట్ హిస్టరీ' : 'Payout History'}</h3>
                        <div className="wallet-summary">
                            <div className="wallet-balance">
                                <span className="balance-label">{lang === 'te' ? 'వాలెట్ బ్యాలెన్స్' : 'Wallet Balance'}</span>
                                <span className="balance-amount">₹{wallet?.balance?.toLocaleString() || 0}</span>
                            </div>
                        </div>
                        <div className="payouts-list">
                            {orders.filter(o => o.payment?.farmerPayout?.status === 'COMPLETED').map(order => (
                                <div key={order.orderId} className="payout-item">
                                    <div className="payout-info">
                                        <span className="payout-order">{order.orderId}</span>
                                        <span className="payout-date">
                                            {new Date(order.payment.farmerPayout.releaseDate).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <span className="payout-amount">+₹{order.payment.farmerPayout.amount}</span>
                                </div>
                            ))}
                            {orders.filter(o => o.payment?.farmerPayout?.status === 'COMPLETED').length === 0 && (
                                <div className="empty-state">
                                    <p>{lang === 'te' ? 'పేఔట్స్ లేవు' : 'No payouts yet'}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FarmerDashboard;
