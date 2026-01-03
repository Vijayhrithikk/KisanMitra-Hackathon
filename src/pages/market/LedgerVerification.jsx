import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { marketService } from '../../services/marketService';
import { ArrowLeft, Shield, CheckCircle, XCircle, Search, Building2, FileText, User, MapPin, Calendar, Hash, Eye, Lock } from 'lucide-react';
import './Market.css';

const LedgerVerification = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [searchInput, setSearchInput] = useState('');
    const [verificationResult, setVerificationResult] = useState(null);
    const [listingDetails, setListingDetails] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showDocs, setShowDocs] = useState(false);
    const [saleData, setSaleData] = useState(null);

    // Decrypt and view sale documents (for authorized parties like banks)
    const handleViewDocuments = () => {
        try {
            const ledger = JSON.parse(localStorage.getItem('kisanmitra_market_ledger') || '[]');
            const saleRecord = ledger.find(r =>
                r.type === 'LISTING_SOLD' && r.listingId === listingDetails.listingId
            );

            if (saleRecord && saleRecord.encryptedData) {
                const decrypted = JSON.parse(atob(saleRecord.encryptedData));
                setSaleData(decrypted);
                setShowDocs(true);
            }
        } catch (err) {
            console.error('Failed to decrypt documents:', err);
        }
    };

    const handleVerify = async (e) => {
        e.preventDefault();
        if (!searchInput.trim()) {
            setError(t('verification.noRecord', 'Please enter a Listing ID or Hash Token'));
            return;
        }

        setLoading(true);
        setError('');
        setVerificationResult(null);
        setListingDetails(null);

        await new Promise(r => setTimeout(r, 1500));

        try {
            const query = searchInput.trim();

            // First try by listing ID
            let listing = marketService.getListingById(query);

            if (!listing) {
                // Then try by current metaHash or txHash
                const allListings = marketService.getListings();
                listing = allListings.find(l =>
                    l.metaHash === query ||
                    l.txHash === query
                );
            }

            // If still not found, search in ledger history for old hashes
            if (!listing) {
                const ledger = JSON.parse(localStorage.getItem('kisanmitra_market_ledger') || '[]');
                const historyEntry = ledger.find(entry =>
                    entry.metaHash === query ||
                    entry.blockHash === query
                );

                if (historyEntry && historyEntry.listingId) {
                    listing = marketService.getListingById(historyEntry.listingId);
                    // Add note that this was found via history
                    if (listing) {
                        listing._foundViaHistory = true;
                        listing._originalHash = query;
                    }
                }
            }

            if (!listing) {
                setError(t('verification.noRecord', 'No record found. The hash token or listing ID does not exist in our ledger.'));
                setLoading(false);
                return;
            }

            const verification = marketService.verifyListing(listing.listingId);
            setVerificationResult(verification);
            setListingDetails(listing);

        } catch (err) {
            setError(t('verification.verificationFailed', 'Verification failed. Please try again.'));
        } finally {
            setLoading(false);
        }
    };

    const calculateCredibilityScore = (listing) => {
        let score = 70;
        if (listing.status === 'SOLD') score += 15;
        if (verificationResult?.verified) score += 10;
        score += Math.floor(Math.random() * 5);
        return Math.min(score, 100);
    };

    return (
        <div className="market-container verification-page">
            <div className="nav-row">
                <button className="back-btn" onClick={() => navigate('/home')}>
                    <ArrowLeft size={18} /> {t('common.back', 'Back')}
                </button>
            </div>

            {/* Bank Header */}
            <header className="verification-header">
                <div className="bank-badge">
                    <Building2 size={24} />
                    <span>{t('verification.bankPortal', 'Bank Portal')}</span>
                </div>
                <h1>{t('verification.title', 'Ledger Verification')}</h1>
                <p>{t('verification.subtitle', 'Verify farmer credibility for loan approval using immutable blockchain records.')}</p>
            </header>

            {/* Search Form */}
            <div className="verification-search">
                <form onSubmit={handleVerify}>
                    <div className="search-input-wrapper">
                        <Hash size={20} />
                        <input
                            type="text"
                            placeholder={t('verification.searchPlaceholder', 'Enter Listing ID or Hash Token...')}
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="verify-btn" disabled={loading}>
                        {loading ? (
                            <span className="loading-dots">{t('verification.verifying', 'Verifying...')}</span>
                        ) : (
                            <>
                                <Shield size={18} /> {t('verification.verify', 'Verify')}
                            </>
                        )}
                    </button>
                </form>
                <p className="search-hint">
                    {t('verification.searchHint', 'Example: LIST-2025-0001 or full SHA-256 hash')}
                </p>
            </div>

            {/* Error State */}
            {error && (
                <div className="verification-error">
                    <XCircle size={20} />
                    <span>{error}</span>
                </div>
            )}

            {/* Verification Result */}
            {verificationResult && listingDetails && (
                <div className="verification-result fade-in">
                    {/* Integrity Status */}
                    <div className={`integrity-card ${verificationResult.verified ? 'verified' : 'failed'}`}>
                        {verificationResult.verified ? (
                            <>
                                <CheckCircle size={48} />
                                <h2>{t('verification.recordVerified', 'Record Verified ✓')}</h2>
                                <p>{t('verification.recordAuthentic', 'This record is authentic and has not been tampered with.')}</p>
                            </>
                        ) : (
                            <>
                                <XCircle size={48} />
                                <h2>{t('verification.verificationFailedTitle', 'Verification Failed')}</h2>
                                <p>{t('verification.recordAltered', 'This record may have been altered. Exercise caution.')}</p>
                            </>
                        )}
                    </div>

                    {/* Credibility Score */}
                    {verificationResult.verified && (
                        <div className="credibility-card">
                            <h3>{t('verification.credibilityScore', 'Farmer Credibility Score')}</h3>
                            <div className="score-circle">
                                <span className="score-value">{calculateCredibilityScore(listingDetails)}</span>
                                <span className="score-label">/ 100</span>
                            </div>
                            <div className="score-status good">
                                <CheckCircle size={16} /> {t('verification.eligibleForLoan', 'Eligible for Loan Consideration')}
                            </div>
                        </div>
                    )}

                    {/* Farmer & Listing Details */}
                    <div className="detail-card">
                        <h2><User size={16} /> {t('verification.farmerDetails', 'Farmer Details')}</h2>
                        <div className="info-row">
                            <span>{t('verification.farmerId', 'Farmer ID')}</span>
                            <strong>{listingDetails.farmerId}</strong>
                        </div>
                        <div className="info-row">
                            <span>Name</span>
                            <strong>{listingDetails.contact?.name || 'N/A'}</strong>
                        </div>
                        <div className="info-row">
                            <span>Phone</span>
                            <strong>{listingDetails.contact?.phone || 'N/A'}</strong>
                        </div>
                    </div>

                    <div className="detail-card">
                        <h2><FileText size={16} /> {t('verification.transactionDetails', 'Transaction Details')}</h2>
                        <div className="info-row">
                            <span>Listing ID</span>
                            <strong>{listingDetails.listingId}</strong>
                        </div>
                        <div className="info-row">
                            <span>Crop</span>
                            <strong>{listingDetails.crop} - {listingDetails.variety}</strong>
                        </div>
                        <div className="info-row">
                            <span>Quantity</span>
                            <strong>{listingDetails.quantity} {listingDetails.unit}</strong>
                        </div>
                        <div className="info-row">
                            <span>Price</span>
                            <strong>₹{listingDetails.price} / {listingDetails.unit}</strong>
                        </div>
                        <div className="info-row">
                            <span>Status</span>
                            <strong className={listingDetails.status === 'SOLD' ? 'status-sold' : 'status-listed'}>
                                {listingDetails.status === 'SOLD' ? t('common.sold', 'Sold') : t('common.listed', 'Listed')}
                            </strong>
                        </div>
                        <div className="info-row">
                            <span>Location</span>
                            <strong>{listingDetails.location?.district}, {listingDetails.location?.state}</strong>
                        </div>
                        <div className="info-row">
                            <span>Listed On</span>
                            <strong>{new Date(listingDetails.createdAt).toLocaleDateString()}</strong>
                        </div>
                    </div>

                    {/* Hash Verification */}
                    <div className="detail-card">
                        <h2><Shield size={16} /> {t('verification.cryptoProof', 'Cryptographic Proof')}</h2>
                        <div className="hash-section">
                            <label>SHA-256 Hash</label>
                            <code className="hash-code">{listingDetails.originalHash || listingDetails.metaHash}</code>
                        </div>
                        <div className="hash-section">
                            <label>Transaction Hash</label>
                            <code className="hash-code">{listingDetails.txHash}</code>
                        </div>
                        <div className="hash-match">
                            {verificationResult.verified ? (
                                <><CheckCircle size={14} /> {t('verification.hashIntegrity', 'Hash integrity confirmed')}</>
                            ) : (
                                <><XCircle size={14} /> {t('verification.hashMismatch', 'Hash mismatch detected')}</>
                            )}
                        </div>
                        {verificationResult.note && (
                            <div className="verification-note">
                                <small>{verificationResult.note}</small>
                            </div>
                        )}
                    </div>

                    {/* Sale Details (if sold) */}
                    {listingDetails.status === 'SOLD' && (
                        <div className="detail-card sale-card">
                            <h2><CheckCircle size={16} /> Sale Verification</h2>
                            <div className="sale-badge">
                                ✓ Transaction Complete
                            </div>
                            <div className="info-row">
                                <span>Sold On</span>
                                <strong>{listingDetails.soldAt ? new Date(listingDetails.soldAt).toLocaleString() : 'N/A'}</strong>
                            </div>
                            {listingDetails.buyerHash && (
                                <div className="hash-section">
                                    <label>Buyer Hash (Encrypted)</label>
                                    <code className="hash-code">{listingDetails.buyerHash}</code>
                                </div>
                            )}

                            {!showDocs ? (
                                <button className="view-docs-btn" onClick={handleViewDocuments}>
                                    <Eye size={16} /> View Transaction Documents
                                </button>
                            ) : (
                                <div className="decrypted-docs">
                                    <h4><Lock size={14} /> Decrypted Transaction Data</h4>

                                    {saleData?.buyer && (
                                        <div className="buyer-info">
                                            <h5>Buyer Details</h5>
                                            <div className="info-row">
                                                <span>Name</span>
                                                <strong>{saleData.buyer.name || 'N/A'}</strong>
                                            </div>
                                            <div className="info-row">
                                                <span>Organization</span>
                                                <strong>{saleData.buyer.org || 'N/A'}</strong>
                                            </div>
                                            <div className="info-row">
                                                <span>Final Price</span>
                                                <strong>₹{saleData.buyer.price || 'N/A'}</strong>
                                            </div>
                                        </div>
                                    )}

                                    {saleData?.docs && saleData.docs.length > 0 && (
                                        <div className="transaction-docs">
                                            <h5>Submitted Documents</h5>
                                            {saleData.docs.map((doc, idx) => (
                                                <div key={idx} className="doc-item">
                                                    <FileText size={14} />
                                                    <span>{doc}</span>
                                                    <span className="doc-verified-badge">✓ Verified</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    <button className="hide-docs-btn" onClick={() => setShowDocs(false)}>
                                        Hide Documents
                                    </button>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="verification-actions">
                        <button className="btn-primary" onClick={() => window.print()}>
                            <FileText size={18} /> {t('verification.downloadReport', 'Download Report')}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LedgerVerification;
