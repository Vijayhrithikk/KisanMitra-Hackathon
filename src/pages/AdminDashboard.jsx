/**
 * Admin Dashboard for KisanMitra
 * Complete monitoring and control panel
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { marketService } from '../services/marketService';
import { authService } from '../services/authService';
import { orderService } from '../services/orderService';
import {
    ShieldCheck, Users, Package, LogOut, CheckCircle, Clock,
    AlertTriangle, Trash2, Eye, RefreshCw, ShoppingBag,
    Tractor, Leaf, X, Check, Loader2
} from 'lucide-react';
import './AdminDashboard.css';

const API_BASE = import.meta.env.VITE_ML_API_URL || 'http://localhost:8001';

const AdminDashboard = () => {
    const navigate = useNavigate();
    const { user, logout, isAdmin } = useAuth();

    const [activeTab, setActiveTab] = useState('overview');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Data states
    const [farmers, setFarmers] = useState([]);
    const [listings, setListings] = useState([]);
    const [orders, setOrders] = useState([]);
    const [rentals, setRentals] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);

    // Delete confirmation state
    const [deleteConfirm, setDeleteConfirm] = useState(null);

    useEffect(() => {
        if (!isAdmin) {
            navigate('/login');
            return;
        }
        loadAllData();
    }, [isAdmin, navigate]);

    const loadAllData = async () => {
        setLoading(true);
        setError(null);

        try {
            // Load farmers
            const farmersResult = authService.getAllFarmers();
            if (farmersResult.success) {
                setFarmers(farmersResult.farmers || []);
            }

            // Load listings
            const listingsData = await marketService.getListings();
            setListings(listingsData || []);

            // Load orders
            try {
                const ordersData = await orderService.getAllOrders();
                setOrders(ordersData || []);
            } catch (e) {
                console.log('Orders not available');
            }

            // Load rentals
            try {
                const rentalsRes = await fetch(`${API_BASE}/rentals`);
                if (rentalsRes.ok) {
                    const rentalsData = await rentalsRes.json();
                    setRentals(rentalsData.rentals || []);
                }
            } catch (e) {
                console.log('Rentals not available');
            }

            // Load subscriptions
            try {
                const subsRes = await fetch(`${API_BASE}/all-subscriptions`);
                if (subsRes.ok) {
                    const subsData = await subsRes.json();
                    setSubscriptions(subsData.subscriptions || []);
                }
            } catch (e) {
                console.log('Subscriptions not available');
            }

        } catch (err) {
            console.error('Error loading admin data:', err);
            setError('Failed to load some dashboard data');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyFarmer = (farmerId) => {
        const result = authService.verifyFarmer(farmerId);
        if (result.success) {
            setFarmers(prev => prev.map(f =>
                f.id === farmerId ? { ...f, verified: true } : f
            ));
        }
    };

    const handleDeleteFarmer = (farmerId) => {
        if (deleteConfirm === `farmer-${farmerId}`) {
            authService.deleteFarmer?.(farmerId);
            setFarmers(prev => prev.filter(f => f.id !== farmerId));
            setDeleteConfirm(null);
        } else {
            setDeleteConfirm(`farmer-${farmerId}`);
            setTimeout(() => setDeleteConfirm(null), 3000);
        }
    };

    const handleDeleteListing = async (listingId) => {
        if (deleteConfirm === `listing-${listingId}`) {
            try {
                await marketService.deleteListing?.(listingId);
                setListings(prev => prev.filter(l => l.listingId !== listingId));
            } catch (e) {
                console.error('Delete failed:', e);
            }
            setDeleteConfirm(null);
        } else {
            setDeleteConfirm(`listing-${listingId}`);
            setTimeout(() => setDeleteConfirm(null), 3000);
        }
    };

    const handleDeleteOrder = async (orderId) => {
        if (deleteConfirm === `order-${orderId}`) {
            try {
                await orderService.deleteOrder?.(orderId);
                setOrders(prev => prev.filter(o => o.orderId !== orderId));
            } catch (e) {
                console.error('Delete failed:', e);
            }
            setDeleteConfirm(null);
        } else {
            setDeleteConfirm(`order-${orderId}`);
            setTimeout(() => setDeleteConfirm(null), 3000);
        }
    };

    const handleDeleteRental = async (rentalId) => {
        if (deleteConfirm === `rental-${rentalId}`) {
            try {
                await fetch(`${API_BASE}/rental/${rentalId}`, { method: 'DELETE' });
                setRentals(prev => prev.filter(r => r.id !== rentalId));
            } catch (e) {
                console.error('Delete failed:', e);
            }
            setDeleteConfirm(null);
        } else {
            setDeleteConfirm(`rental-${rentalId}`);
            setTimeout(() => setDeleteConfirm(null), 3000);
        }
    };

    const handleDeleteSubscription = async (subId) => {
        if (deleteConfirm === `sub-${subId}`) {
            try {
                await fetch(`${API_BASE}/subscription/${subId}`, { method: 'DELETE' });
                setSubscriptions(prev => prev.filter(s => s.subscriptionId !== subId));
            } catch (e) {
                console.error('Delete failed:', e);
            }
            setDeleteConfirm(null);
        } else {
            setDeleteConfirm(`sub-${subId}`);
            setTimeout(() => setDeleteConfirm(null), 3000);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!isAdmin) return null;

    // Stats calculations
    const stats = {
        totalFarmers: farmers.length,
        verifiedFarmers: farmers.filter(f => f.verified).length,
        pendingVerification: farmers.filter(f => f.verificationDoc && !f.verified).length,
        totalListings: listings.length,
        activeListings: listings.filter(l => l.status === 'ACTIVE').length,
        totalOrders: orders.length,
        pendingOrders: orders.filter(o => o.status === 'pending' || o.status === 'confirmed').length,
        disputedOrders: orders.filter(o => o.status === 'disputed').length,
        totalRentals: rentals.length,
        totalSubs: subscriptions.length
    };

    return (
        <div className="admin-page">
            <header className="admin-header">
                <h1>
                    <ShieldCheck size={22} />
                    Admin Panel
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <button onClick={loadAllData} style={{ background: 'rgba(255,255,255,0.2)', border: 'none', padding: '0.5rem', borderRadius: '8px', color: 'white', cursor: 'pointer' }}>
                        <RefreshCw size={16} />
                    </button>
                    <button onClick={handleLogout} className="logout-btn">
                        <LogOut size={16} /> Logout
                    </button>
                </div>
            </header>

            <div className="admin-content">
                {/* Loading State */}
                {loading && (
                    <div className="loading-state">
                        <Loader2 size={32} className="spinner" />
                        <div>Loading dashboard...</div>
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.2)', borderRadius: '8px', marginBottom: '1rem', color: '#fca5a5' }}>
                        <AlertTriangle size={16} style={{ marginRight: '0.5rem' }} />
                        {error}
                    </div>
                )}

                {!loading && (
                    <>
                        {/* Tab Navigation */}
                        <div className="admin-tabs">
                            <button className={activeTab === 'overview' ? 'active' : ''} onClick={() => setActiveTab('overview')}>
                                📊 Overview
                            </button>
                            <button className={activeTab === 'farmers' ? 'active' : ''} onClick={() => setActiveTab('farmers')}>
                                <Users size={16} /> Farmers <span className="badge">{stats.totalFarmers}</span>
                            </button>
                            <button className={activeTab === 'listings' ? 'active' : ''} onClick={() => setActiveTab('listings')}>
                                <Package size={16} /> Listings <span className="badge">{stats.totalListings}</span>
                            </button>
                            <button className={activeTab === 'orders' ? 'active' : ''} onClick={() => setActiveTab('orders')}>
                                <ShoppingBag size={16} /> Orders <span className="badge">{stats.totalOrders}</span>
                            </button>
                            <button className={activeTab === 'rentals' ? 'active' : ''} onClick={() => setActiveTab('rentals')}>
                                <Tractor size={16} /> Rentals <span className="badge">{stats.totalRentals}</span>
                            </button>
                            <button className={activeTab === 'subs' ? 'active' : ''} onClick={() => setActiveTab('subs')}>
                                <Leaf size={16} /> Crops <span className="badge">{stats.totalSubs}</span>
                            </button>
                        </div>

                        {/* Overview Tab */}
                        {activeTab === 'overview' && (
                            <>
                                <div className="admin-stats">
                                    <div className="stat-card">
                                        <h4>Total Farmers</h4>
                                        <div className="value">{stats.totalFarmers}</div>
                                    </div>
                                    <div className="stat-card">
                                        <h4>Verified</h4>
                                        <div className="value valid">{stats.verifiedFarmers}</div>
                                    </div>
                                    <div className="stat-card">
                                        <h4>Pending Verify</h4>
                                        <div className="value warning">{stats.pendingVerification}</div>
                                    </div>
                                    <div className="stat-card">
                                        <h4>Active Listings</h4>
                                        <div className="value">{stats.activeListings}</div>
                                    </div>
                                    <div className="stat-card">
                                        <h4>Pending Orders</h4>
                                        <div className="value warning">{stats.pendingOrders}</div>
                                    </div>
                                    <div className="stat-card">
                                        <h4>Disputed</h4>
                                        <div className="value" style={{ color: stats.disputedOrders > 0 ? '#ef4444' : '#22c55e' }}>
                                            {stats.disputedOrders}
                                        </div>
                                    </div>
                                </div>

                                {/* Quick Action Cards */}
                                <div className="admin-section">
                                    <div className="admin-section-header">
                                        <h3>⚡ Quick Actions</h3>
                                    </div>
                                    <div style={{ padding: '1rem', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
                                        <button onClick={() => setActiveTab('farmers')} style={{ padding: '1rem', background: 'rgba(34, 197, 94, 0.2)', border: 'none', borderRadius: '8px', color: '#22c55e', cursor: 'pointer', textAlign: 'left' }}>
                                            <Users size={20} />
                                            <div style={{ marginTop: '0.5rem', fontWeight: '600' }}>Verify Farmers</div>
                                            <small style={{ opacity: 0.8 }}>{stats.pendingVerification} pending</small>
                                        </button>
                                        <button onClick={() => setActiveTab('orders')} style={{ padding: '1rem', background: 'rgba(245, 158, 11, 0.2)', border: 'none', borderRadius: '8px', color: '#f59e0b', cursor: 'pointer', textAlign: 'left' }}>
                                            <ShoppingBag size={20} />
                                            <div style={{ marginTop: '0.5rem', fontWeight: '600' }}>Manage Orders</div>
                                            <small style={{ opacity: 0.8 }}>{stats.pendingOrders} active</small>
                                        </button>
                                        <button onClick={() => setActiveTab('listings')} style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.2)', border: 'none', borderRadius: '8px', color: '#3b82f6', cursor: 'pointer', textAlign: 'left' }}>
                                            <Package size={20} />
                                            <div style={{ marginTop: '0.5rem', fontWeight: '600' }}>View Listings</div>
                                            <small style={{ opacity: 0.8 }}>{stats.totalListings} total</small>
                                        </button>
                                        <button onClick={() => setActiveTab('subs')} style={{ padding: '1rem', background: 'rgba(139, 92, 246, 0.2)', border: 'none', borderRadius: '8px', color: '#8b5cf6', cursor: 'pointer', textAlign: 'left' }}>
                                            <Leaf size={20} />
                                            <div style={{ marginTop: '0.5rem', fontWeight: '600' }}>Crop Monitoring</div>
                                            <small style={{ opacity: 0.8 }}>{stats.totalSubs} active</small>
                                        </button>
                                    </div>
                                </div>
                            </>
                        )}

                        {/* Farmers Tab */}
                        {activeTab === 'farmers' && (
                            <div className="admin-section">
                                <div className="admin-section-header">
                                    <h3><Users size={18} /> All Farmers ({farmers.length})</h3>
                                </div>
                                {farmers.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="icon">👨‍🌾</div>
                                        <div>No farmers registered yet</div>
                                    </div>
                                ) : (
                                    <div className="table-wrapper">
                                        <table className="admin-table">
                                            <thead>
                                                <tr>
                                                    <th>ID</th>
                                                    <th>Name</th>
                                                    <th>Phone</th>
                                                    <th>Location</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {farmers.map(farmer => (
                                                    <tr key={farmer.id}>
                                                        <td><code>{farmer.id?.slice(-6)}</code></td>
                                                        <td>{farmer.name || '-'}</td>
                                                        <td>{farmer.phone}</td>
                                                        <td>{farmer.village ? `${farmer.village}` : '-'}</td>
                                                        <td>
                                                            {farmer.verified ? (
                                                                <span className="status-badge active">
                                                                    <CheckCircle size={12} /> Verified
                                                                </span>
                                                            ) : farmer.verificationDoc ? (
                                                                <span className="status-badge pending">
                                                                    <Clock size={12} /> Pending
                                                                </span>
                                                            ) : (
                                                                <span className="status-badge">Unverified</span>
                                                            )}
                                                        </td>
                                                        <td style={{ display: 'flex', gap: '0.5rem' }}>
                                                            <button
                                                                className="action-btn verify"
                                                                onClick={() => handleVerifyFarmer(farmer.id)}
                                                                disabled={farmer.verified}
                                                            >
                                                                <Check size={12} /> {farmer.verified ? 'Done' : 'Verify'}
                                                            </button>
                                                            <button
                                                                className={`action-btn delete ${deleteConfirm === `farmer-${farmer.id}` ? 'confirming' : ''}`}
                                                                onClick={() => handleDeleteFarmer(farmer.id)}
                                                            >
                                                                <Trash2 size={12} /> {deleteConfirm === `farmer-${farmer.id}` ? 'Sure?' : 'Del'}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Listings Tab */}
                        {activeTab === 'listings' && (
                            <div className="admin-section">
                                <div className="admin-section-header">
                                    <h3><Package size={18} /> All Listings ({listings.length})</h3>
                                </div>
                                {listings.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="icon">📦</div>
                                        <div>No listings yet</div>
                                    </div>
                                ) : (
                                    <div className="table-wrapper">
                                        <table className="admin-table">
                                            <thead>
                                                <tr>
                                                    <th>ID</th>
                                                    <th>Crop</th>
                                                    <th>Farmer</th>
                                                    <th>Price</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {listings.map(listing => (
                                                    <tr key={listing.listingId}>
                                                        <td><code>{listing.listingId?.slice(-6)}</code></td>
                                                        <td>{listing.crop}</td>
                                                        <td>{listing.farmerName || listing.farmerId?.slice(-6)}</td>
                                                        <td>₹{listing.price}/{listing.unit}</td>
                                                        <td>
                                                            <span className={`status-badge ${listing.status?.toLowerCase()}`}>
                                                                {listing.status}
                                                            </span>
                                                        </td>
                                                        <td style={{ display: 'flex', gap: '0.5rem' }}>
                                                            <button className="action-btn edit" onClick={() => navigate(`/market/${listing.listingId}`)}>
                                                                <Eye size={12} /> View
                                                            </button>
                                                            <button
                                                                className={`action-btn delete ${deleteConfirm === `listing-${listing.listingId}` ? 'confirming' : ''}`}
                                                                onClick={() => handleDeleteListing(listing.listingId)}
                                                            >
                                                                <Trash2 size={12} /> {deleteConfirm === `listing-${listing.listingId}` ? 'Sure?' : 'Del'}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Orders Tab */}
                        {activeTab === 'orders' && (
                            <div className="admin-section">
                                <div className="admin-section-header">
                                    <h3><ShoppingBag size={18} /> All Orders ({orders.length})</h3>
                                </div>
                                {orders.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="icon">🛒</div>
                                        <div>No orders yet</div>
                                    </div>
                                ) : (
                                    <div className="table-wrapper">
                                        <table className="admin-table">
                                            <thead>
                                                <tr>
                                                    <th>Order ID</th>
                                                    <th>Crop</th>
                                                    <th>Buyer</th>
                                                    <th>Amount</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {orders.map(order => (
                                                    <tr key={order.orderId}>
                                                        <td><code>{order.orderId?.slice(-8)}</code></td>
                                                        <td>{order.crop}</td>
                                                        <td>{order.buyerName || order.buyerPhone}</td>
                                                        <td>₹{order.totalAmount?.toLocaleString()}</td>
                                                        <td>
                                                            <span className={`status-badge ${order.status}`}>
                                                                {order.status}
                                                            </span>
                                                        </td>
                                                        <td style={{ display: 'flex', gap: '0.5rem' }}>
                                                            <button
                                                                className={`action-btn delete ${deleteConfirm === `order-${order.orderId}` ? 'confirming' : ''}`}
                                                                onClick={() => handleDeleteOrder(order.orderId)}
                                                            >
                                                                <Trash2 size={12} /> {deleteConfirm === `order-${order.orderId}` ? 'Sure?' : 'Del'}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Rentals Tab */}
                        {activeTab === 'rentals' && (
                            <div className="admin-section">
                                <div className="admin-section-header">
                                    <h3><Tractor size={18} /> All Rentals ({rentals.length})</h3>
                                </div>
                                {rentals.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="icon">🚜</div>
                                        <div>No rentals yet</div>
                                    </div>
                                ) : (
                                    <div className="table-wrapper">
                                        <table className="admin-table">
                                            <thead>
                                                <tr>
                                                    <th>Title</th>
                                                    <th>Category</th>
                                                    <th>Owner</th>
                                                    <th>Rate</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {rentals.map(rental => (
                                                    <tr key={rental.id}>
                                                        <td>{rental.title?.slice(0, 20)}...</td>
                                                        <td>{rental.category}</td>
                                                        <td>{rental.ownerName}</td>
                                                        <td>₹{rental.dailyRate}/day</td>
                                                        <td>
                                                            <span className={`status-badge ${rental.available ? 'available' : 'booked'}`}>
                                                                {rental.available ? 'Available' : 'Booked'}
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <button
                                                                className={`action-btn delete ${deleteConfirm === `rental-${rental.id}` ? 'confirming' : ''}`}
                                                                onClick={() => handleDeleteRental(rental.id)}
                                                            >
                                                                <Trash2 size={12} /> {deleteConfirm === `rental-${rental.id}` ? 'Sure?' : 'Del'}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Subscriptions Tab */}
                        {activeTab === 'subs' && (
                            <div className="admin-section">
                                <div className="admin-section-header">
                                    <h3><Leaf size={18} /> Crop Subscriptions ({subscriptions.length})</h3>
                                </div>
                                {subscriptions.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="icon">🌾</div>
                                        <div>No crop subscriptions yet</div>
                                    </div>
                                ) : (
                                    <div className="table-wrapper">
                                        <table className="admin-table">
                                            <thead>
                                                <tr>
                                                    <th>ID</th>
                                                    <th>Crop</th>
                                                    <th>Farmer</th>
                                                    <th>Location</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {subscriptions.map(sub => (
                                                    <tr key={sub.subscriptionId}>
                                                        <td><code>{sub.subscriptionId?.slice(-8)}</code></td>
                                                        <td>{sub.crop}</td>
                                                        <td>{sub.farmerPhone}</td>
                                                        <td>{sub.locationName || sub.location?.name}</td>
                                                        <td>
                                                            <span className={`status-badge ${sub.status?.toLowerCase()}`}>
                                                                {sub.status}
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <button
                                                                className={`action-btn delete ${deleteConfirm === `sub-${sub.subscriptionId}` ? 'confirming' : ''}`}
                                                                onClick={() => handleDeleteSubscription(sub.subscriptionId)}
                                                            >
                                                                <Trash2 size={12} /> {deleteConfirm === `sub-${sub.subscriptionId}` ? 'Sure?' : 'Del'}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
