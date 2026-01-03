import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import { marketService } from '../../services/marketService';
import { authService } from '../../services/authService';
import { ShieldCheck, CheckCircle, XCircle, Lock, User, Calendar, FileText, Package, BadgeCheck, ShoppingCart } from 'lucide-react';
import './Market.css';

const ListingDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user, isLoggedIn } = useAuth();
    const { addToCart } = useCart();
    const [listing, setListing] = useState(null);
    const [addToCartQty, setAddToCartQty] = useState(10);
    const [verification, setVerification] = useState(null);
    const [farmerInfo, setFarmerInfo] = useState(null);
    const [farmerListings, setFarmerListings] = useState([]);

    // Edit & Sold State
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({});
    const [showBuyerForm, setShowBuyerForm] = useState(false);
    const [buyerData, setBuyerData] = useState({ name: '', org: '', price: '' });
    const [transactionDoc, setTransactionDoc] = useState(null);

    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchListing = async () => {
            try {
                const data = await marketService.getListingById(id);
                if (data) {
                    setListing(data);
                    setEditData(data);

                    // Fetch farmer info
                    if (data.farmerId) {
                        const farmer = authService.getFarmerById(data.farmerId);
                        setFarmerInfo(farmer);

                        // Get all listings by this farmer
                        const allListings = await marketService.getListings();
                        const farmerListings = allListings.filter(l => l.farmerId === data.farmerId);
                        setFarmerListings(farmerListings);
                    }
                } else {
                    setError('Listing not found. It may have been removed or the ID is incorrect.');
                }
            } catch (err) {
                setError('Error loading listing: ' + err.message);
            }
        };

        fetchListing();
    }, [id]);

    // Handle save edited listing
    const handleSaveEdit = async () => {
        try {
            const updates = {
                variety: editData.variety,
                quantity: parseInt(editData.quantity),
                price: parseFloat(editData.price)
            };

            const result = await marketService.updateListing(listing.listingId, updates);

            if (result.success) {
                // Update local state with new values
                setListing({ ...listing, ...updates });
                setIsEditing(false);
                alert('Listing updated successfully!');
            } else {
                alert('Failed to update listing: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Save error:', error);
            alert('Error saving changes: ' + error.message);
        }
    };

    // Handle delete listing
    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this listing? This cannot be undone.')) {
            return;
        }

        try {
            const result = await marketService.deleteListing(listing.listingId);

            if (result.success) {
                alert('Listing deleted successfully!');
                navigate('/market');
            } else {
                alert('Failed to delete listing: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert('Error deleting listing: ' + error.message);
        }
    };

    if (error) {
        const availableIds = marketService.getAllListingIds();
        return (
            <div className="market-container">
                <div className="error-state" style={{ textAlign: 'center', padding: '4rem' }}>
                    <h2>⚠️ Listing Not Found</h2>
                    <p>{error}</p>
                    <p>Requested ID: <strong>{id}</strong></p>

                    <div className="debug-ids" style={{ marginTop: '2rem', textAlign: 'left', background: '#f1f5f9', padding: '1rem', borderRadius: '8px' }}>
                        <h4>Debug: Available Listings in LocalStorage</h4>
                        {availableIds.length > 0 ? (
                            <ul style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                {availableIds.map(aid => (
                                    <li key={aid}>
                                        <a href={`/market/${aid}`}>{aid}</a>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p>No listings found in local storage.</p>
                        )}
                    </div>

                    <button className="back-btn" onClick={() => navigate('/market')} style={{ marginTop: '2rem' }}>← Back to Market</button>
                </div>
            </div>
        );
    }

    if (!listing) return <div className="market-container" style={{ padding: '4rem', textAlign: 'center' }}>Loading Listing...</div>;

    // Check if current user is owner - check multiple possible ID fields
    const isOwner = isLoggedIn && (
        user?.id === listing.farmerId ||
        user?.farmerId === listing.farmerId ||
        user?.phone === listing.farmerPhone ||
        user?.userId === listing.farmerId
    );

    // Debug logging
    console.log('isOwner check:', {
        isLoggedIn,
        userId: user?.id,
        userFarmerId: user?.farmerId,
        userPhone: user?.phone,
        listingFarmerId: listing.farmerId,
        listingFarmerPhone: listing.farmerPhone,
        listingStatus: listing.status,
        isEditing,
        isOwner,
        shouldShowDelete: isOwner && listing.status === 'LISTED' && !isEditing
    });

    const handleVerify = () => {
        const result = marketService.verifyListing(id);
        setVerification(result);
    };



    const handleMarkSold = (e) => {
        e.preventDefault();
        try {
            // In a real app, we would upload the file to IPFS here and get a hash/URL
            // For this demo, we just pass the file object name or a dummy string
            const docs = transactionDoc ? [transactionDoc.name] : [];

            const result = marketService.markAsSold(id, buyerData, docs, user?.id);
            if (result.success) {
                // Refresh listing to get the updated status and buyerHash
                const updated = marketService.getListingById(id);
                setListing(updated);
                setShowBuyerForm(false);
            }
        } catch (err) {
            alert(err.message);
        }
    };



    return (
        <div className="market-container">
            <div className="nav-row">
                <button className="back-btn" onClick={() => navigate('/market')}>← Back to Market</button>
            </div>

            <div className="detail-grid">
                {/* Main Content */}
                <div className="detail-main">
                    <div className="detail-header">
                        <div>
                            {isEditing ? (
                                <input
                                    className="edit-input-title"
                                    value={editData.crop}
                                    onChange={e => setEditData({ ...editData, crop: e.target.value })}
                                />
                            ) : (
                                <h1>{listing.crop} - {listing.variety}</h1>
                            )}
                            <p className="location">{listing.location.district}, {listing.location.state}</p>
                        </div>
                        <div className={`status-badge large ${listing.status.toLowerCase()}`}>
                            {listing.status}
                        </div>
                    </div>

                    {/* Image Gallery */}
                    {listing.images && listing.images.length > 0 && (
                        <div className="listing-image-gallery" style={{ marginBottom: '1.5rem' }}>
                            <div className="main-image" style={{ borderRadius: '16px', overflow: 'hidden', marginBottom: '0.5rem' }}>
                                <img
                                    src={listing.images[0].data}
                                    alt={listing.crop}
                                    style={{ width: '100%', height: '250px', objectFit: 'cover' }}
                                />
                            </div>
                            {listing.images.length > 1 && (
                                <div className="thumbnail-row" style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto' }}>
                                    {listing.images.slice(1).map((img, idx) => (
                                        <img
                                            key={idx}
                                            src={img.data}
                                            alt={`${listing.crop} ${idx + 2}`}
                                            style={{ width: '80px', height: '60px', objectFit: 'cover', borderRadius: '8px', cursor: 'pointer' }}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    <div className="detail-card">
                        <div className="card-header-row">
                            <h3>Listing Details</h3>
                            {isOwner && (
                                <div className="owner-actions" style={{ display: 'flex', gap: '0.5rem' }}>
                                    {listing.status === 'LISTED' && !isEditing && (
                                        <button className="edit-btn" onClick={() => setIsEditing(true)}>Edit</button>
                                    )}
                                    <button
                                        className="delete-btn"
                                        onClick={handleDelete}
                                        style={{
                                            background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                                            color: 'white',
                                            border: 'none',
                                            padding: '0.5rem 1rem',
                                            borderRadius: '8px',
                                            cursor: 'pointer',
                                            fontSize: '0.9rem',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.25rem'
                                        }}
                                    >
                                        <XCircle size={16} /> Delete
                                    </button>
                                </div>
                            )}
                        </div>

                        {isEditing ? (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Variety</label>
                                    <input value={editData.variety} onChange={e => setEditData({ ...editData, variety: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label>Quantity</label>
                                    <input value={editData.quantity} onChange={e => setEditData({ ...editData, quantity: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label>Price</label>
                                    <input value={editData.price} onChange={e => setEditData({ ...editData, price: e.target.value })} />
                                </div>
                                <div className="edit-actions">
                                    <button className="save-btn" onClick={handleSaveEdit}>Save Changes</button>
                                    <button className="cancel-btn" onClick={() => setIsEditing(false)}>Cancel</button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="info-row">
                                    <span>Quantity:</span> <strong>{listing.quantity} {listing.unit}</strong>
                                </div>
                                <div className="info-row">
                                    <span>Asking Price:</span> <strong>₹{listing.price} / {listing.unit}</strong>
                                </div>
                                <div className="info-row">
                                    <span>Created At:</span> <strong>{new Date(listing.createdAt).toLocaleString()}</strong>
                                </div>
                                <div className="info-row">
                                    <span>Farming Method:</span>
                                    <strong>{listing.farmingMethod || (listing.isOrganic ? 'Organic' : 'Conventional')}</strong>
                                </div>
                                {listing.isOrganic && (
                                    <div className="info-row">
                                        <span>Certification:</span>
                                        <span className="organic-badge">
                                            🌱 {listing.organicCertified ? `Certified by ${listing.certificationBody || 'Agency'}` : 'Organic (Self-Declared)'}
                                        </span>
                                    </div>
                                )}
                                {listing.fertilizersUsed && (
                                    <div className="info-row">
                                        <span>Fertilizers:</span> <p>{listing.fertilizersUsed}</p>
                                    </div>
                                )}
                                <div className="info-row">
                                    <span>Notes:</span> <p>{listing.notes || 'None'}</p>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Farmer Trust Section */}
                    <div className="detail-card farmer-trust-section">
                        <h3><User size={20} /> Farmer Trust Profile</h3>

                        <div className="farmer-trust-content">
                            <div className="farmer-avatar-large">
                                👨‍🌾
                            </div>

                            <div className="farmer-trust-info">
                                <div className="farmer-name-row">
                                    <strong>{farmerInfo?.name || listing.contact?.name || 'Farmer'}</strong>
                                    {farmerInfo?.verified && (
                                        <span className="verified-tag">
                                            <BadgeCheck size={14} /> Verified
                                        </span>
                                    )}
                                </div>

                                <div className="trust-stats">
                                    <div className="trust-stat">
                                        <Package size={16} />
                                        <span><strong>{farmerListings.length}</strong> Listings</span>
                                    </div>
                                    <div className="trust-stat">
                                        <Calendar size={16} />
                                        <span>Since {farmerInfo?.createdAt ? new Date(farmerInfo.createdAt).toLocaleDateString() : 'N/A'}</span>
                                    </div>
                                    {farmerInfo?.village && (
                                        <div className="trust-stat">
                                            <span>📍 {farmerInfo.village}, {farmerInfo.district}</span>
                                        </div>
                                    )}
                                </div>

                                {farmerInfo?.verificationDoc && (
                                    <div className="verification-doc">
                                        <FileText size={14} />
                                        <span>ID Document Submitted ✓</span>
                                    </div>
                                )}

                                {!farmerInfo?.verified && (
                                    <div className="unverified-notice">
                                        ⚠️ Farmer not yet verified by admin
                                    </div>
                                )}
                            </div>
                        </div>

                        {farmerListings.length > 1 && (
                            <div className="past-listings">
                                <h4>Other Listings by this Farmer</h4>
                                <div className="past-listings-grid">
                                    {farmerListings
                                        .filter(l => l.listingId !== listing.listingId)
                                        .slice(0, 3)
                                        .map(l => (
                                            <div
                                                key={l.listingId}
                                                className="past-listing-item"
                                                onClick={() => navigate(`/market/${l.listingId}`)}
                                            >
                                                <span>{l.crop}</span>
                                                <span className={`status-badge ${l.status.toLowerCase()}`}>{l.status}</span>
                                            </div>
                                        ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Verification Section */}
                    <div className="detail-card verification-section">
                        <h3><ShieldCheck size={20} /> Blockchain Verification</h3>
                        <p>Verify the integrity of this listing by re-computing its SHA-256 hash.</p>

                        <div className="hash-box">
                            <label>🔒 Original Hash (Immutable):</label>
                            <code>{listing.originalHash || listing.metaHash}</code>
                            <small style={{ color: '#6b7280', display: 'block', marginTop: '0.25rem' }}>
                                Created: {new Date(listing.createdAt).toLocaleString()}
                            </small>
                        </div>

                        {listing.updateHistory && listing.updateHistory.length > 0 && (
                            <div className="update-history">
                                <label>📝 Update History ({listing.updateHistory.length} modification{listing.updateHistory.length > 1 ? 's' : ''}):</label>
                                {listing.updateHistory.map((update, idx) => (
                                    <div key={idx} className="update-entry">
                                        <div className="update-header">
                                            <span className="update-number">#{idx + 1}</span>
                                            <small>{new Date(update.timestamp).toLocaleString()}</small>
                                        </div>
                                        <div className="changes-list">
                                            {update.changes && Object.keys(update.changes).length > 0 ? (
                                                Object.entries(update.changes).map(([field, change]) => (
                                                    <div key={field} className="change-item">
                                                        <span className="field-label">
                                                            {field === 'price' ? '💰 Price' :
                                                                field === 'quantity' ? '📦 Quantity' :
                                                                    field === 'variety' ? '🌾 Variety' :
                                                                        field === 'notes' ? '📝 Notes' : field}:
                                                        </span>
                                                        <span className="old-value">{field === 'price' ? `₹${change.from}` : change.from}</span>
                                                        <span className="arrow">→</span>
                                                        <span className="new-value">{field === 'price' ? `₹${change.to}` : change.to}</span>
                                                    </div>
                                                ))
                                            ) : (
                                                <span className="no-details">Metadata updated</span>
                                            )}
                                        </div>
                                        {update.hash && (
                                            <div className="update-footer">
                                                <small className="update-hash">Hash: {update.hash.substring(0, 16)}...</small>
                                                {update.authorizedBy && (
                                                    <span className="authorized-badge">
                                                        ✓ Authorized by Owner
                                                    </span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}

                        {listing.currentHash && listing.currentHash !== listing.originalHash && (
                            <div className="hash-box current">
                                <label>🔄 Current Hash (After Updates):</label>
                                <code>{listing.currentHash}</code>
                                <small style={{ color: '#6b7280', display: 'block', marginTop: '0.25rem' }}>
                                    Last updated: {listing.lastUpdated ? new Date(listing.lastUpdated).toLocaleString() : 'N/A'}
                                </small>
                            </div>
                        )}

                        {!verification ? (
                            <button className="verify-btn" onClick={handleVerify}>
                                Verify Integrity
                            </button>
                        ) : (
                            <div className={`verification-result ${verification.verified ? 'valid' : 'invalid'}`}>
                                {verification.verified ? (
                                    <>
                                        <CheckCircle size={24} />
                                        <div>
                                            <h4>Verified Immutable</h4>
                                            <p>Computed hash matches the ledger record.</p>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <XCircle size={24} />
                                        <div>
                                            <h4>Verification Failed</h4>
                                            <p>Data has been tampered with.</p>
                                        </div>
                                    </>
                                )}
                            </div>
                        )}

                        {verification && (
                            <div className="debug-info">
                                <small>Computed: {verification.computedHash}</small>
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar */}
                <div className="detail-sidebar">
                    {listing.status === 'LISTED' ? (
                        <div className="action-card">
                            <h3>Manage Listing</h3>
                            <p>Are you the farmer? Mark this listing as sold when you find a buyer.</p>

                            {isOwner ? (
                                !showBuyerForm ? (
                                    <button className="sold-btn" onClick={() => setShowBuyerForm(true)}>
                                        Mark as Sold
                                    </button>
                                ) : (
                                    <form onSubmit={handleMarkSold} className="buyer-form">
                                        <h4>Buyer Details (Encrypted)</h4>
                                        <input
                                            type="text"
                                            placeholder="Buyer Name"
                                            value={buyerData.name}
                                            onChange={e => setBuyerData({ ...buyerData, name: e.target.value })}
                                            required
                                        />
                                        <input
                                            type="text"
                                            placeholder="Organization / VPA"
                                            value={buyerData.org}
                                            onChange={e => setBuyerData({ ...buyerData, org: e.target.value })}
                                            required
                                        />
                                        <input
                                            type="number"
                                            placeholder="Final Sale Price"
                                            value={buyerData.price}
                                            onChange={e => setBuyerData({ ...buyerData, price: e.target.value })}
                                            required
                                        />

                                        <div className="file-upload-small">
                                            <label>Transaction Document *</label>
                                            <input
                                                type="file"
                                                accept=".pdf,.jpg,.png"
                                                onChange={e => setTransactionDoc(e.target.files[0])}
                                                required
                                            />
                                            <small>Upload Invoice/Receipt</small>
                                        </div>

                                        <div className="privacy-note">
                                            <Lock size={12} /> Info & Docs are encrypted.
                                        </div>
                                        <button type="submit" className="confirm-btn">Confirm Sale</button>
                                        <button type="button" className="cancel-btn" onClick={() => setShowBuyerForm(false)}>Cancel</button>
                                    </form>
                                )
                            ) : (
                                <div className="not-owner-msg">
                                    <Lock size={16} /> Only the owner can manage this listing.
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="action-card sold-info">
                            <h3><CheckCircle size={20} /> Sold</h3>
                            <p>This listing has been sold.</p>
                            <div className="buyer-hash">
                                <label>Buyer Record Hash:</label>
                                <code>{listing.buyerHash}</code>
                            </div>
                            <small><Lock size={12} /> Buyer details are encrypted on-chain.</small>
                        </div>
                    )}

                    <div className="ledger-info">
                        <h4>Ledger Metadata</h4>
                        <div className="meta-item">
                            <FileText size={14} /> <span>IPFS CID: {listing.ipfsCid?.substring(0, 12)}...</span>
                        </div>
                        <div className="meta-item">
                            <Calendar size={14} /> <span>Tx: {listing.txHash?.substring(0, 12)}...</span>
                        </div>
                    </div>

                    {/* Add to Cart Section */}
                    {listing.status === 'LISTED' && !isOwner && (
                        <div className="add-to-cart-section" style={{ marginBottom: '16px', padding: '16px', background: '#F0FDF4', borderRadius: '12px' }}>
                            <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#065f46' }}>Add to Cart</h4>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                                <button
                                    style={{ width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'white', border: '1px solid #10b981', borderRadius: '8px', cursor: 'pointer' }}
                                    onClick={() => setAddToCartQty(Math.max(10, addToCartQty - 10))}
                                >
                                    -
                                </button>
                                <span style={{ flex: 1, textAlign: 'center', fontWeight: '600' }}>{addToCartQty} {listing.unit}</span>
                                <button
                                    style={{ width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'white', border: '1px solid #10b981', borderRadius: '8px', cursor: 'pointer' }}
                                    onClick={() => setAddToCartQty(Math.min(listing.quantity, addToCartQty + 10))}
                                >
                                    +
                                </button>
                            </div>
                            <button
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    background: 'linear-gradient(135deg, #10b981, #059669)',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '10px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px'
                                }}
                                onClick={() => {
                                    addToCart({
                                        listingId: listing.listingId,
                                        crop: listing.crop,
                                        variety: listing.variety,
                                        price: listing.pricing?.basePrice || listing.price,
                                        unit: listing.unit,
                                        farmerId: listing.farmerId
                                    }, addToCartQty);
                                    alert(`Added ${addToCartQty} ${listing.unit} of ${listing.crop} to cart!`);
                                }}
                            >
                                <ShoppingCart size={18} /> Add to Cart
                            </button>
                        </div>
                    )}

                    {/* Buy Now Button for Buyers */}
                    {listing.status === 'LISTED' && (
                        <div className="buy-button-section">
                            <button
                                className="buy-now-btn"
                                onClick={() => {
                                    // Check if buyer is logged in OR if farmer is logged in
                                    const currentBuyer = localStorage.getItem('currentBuyer');
                                    const farmerSession = localStorage.getItem('farmer');

                                    if (currentBuyer) {
                                        // Buyer already logged in
                                        navigate(`/market/order/${listing.listingId}`);
                                    } else if (farmerSession || isLoggedIn) {
                                        // Farmer is logged in - create a buyer session from farmer data
                                        const farmer = JSON.parse(farmerSession || '{}');
                                        const buyerData = {
                                            buyerId: farmer.id || user?.id || `FARMER-${Date.now()}`,
                                            name: farmer.name || user?.name || 'Farmer',
                                            phone: farmer.phone || user?.phone || '',
                                            type: 'FARMER_BUYER'
                                        };
                                        localStorage.setItem('currentBuyer', JSON.stringify(buyerData));
                                        navigate(`/market/order/${listing.listingId}`);
                                    } else {
                                        // Not logged in - set guest mode and proceed to order
                                        localStorage.setItem('guestMode', 'true');
                                        localStorage.setItem('returnToListing', listing.listingId);
                                        navigate(`/market/order/${listing.listingId}`);
                                    }
                                }}
                            >
                                🛒 Buy Now - ₹{listing.pricing?.basePrice || listing.price}/{listing.unit}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div >
    );
};

export default ListingDetail;
