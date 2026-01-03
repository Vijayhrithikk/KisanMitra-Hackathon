import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { orderService } from '../../services/orderService';
import { transactionBlockchain } from '../../services/transactionBlockchain';
import { marketService } from '../../services/marketService';
import {
    ArrowLeft, Search, Shield, CheckCircle, XCircle, Lock, Building2,
    FileText, Hash, Eye, Download, AlertTriangle, Verified, Clock
} from 'lucide-react';
import './Market.css';

// Simulated bank access codes
const BANK_ACCESS_CODES = {
    'SBI2024': { bankName: 'State Bank of India', code: 'SBIN' },
    'HDFC2024': { bankName: 'HDFC Bank', code: 'HDFC' },
    'ICICI2024': { bankName: 'ICICI Bank', code: 'ICIC' },
    'AXIS2024': { bankName: 'Axis Bank', code: 'AXIS' },
    'KOTAK2024': { bankName: 'Kotak Mahindra Bank', code: 'KKBK' }
};

const BankVerification = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    // Authentication state
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [bankInfo, setBankInfo] = useState(null);
    const [accessCode, setAccessCode] = useState('');
    const [authError, setAuthError] = useState('');

    // Search state
    const [searchType, setSearchType] = useState('order');
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResult, setSearchResult] = useState(null);
    const [searchError, setSearchError] = useState('');

    // Verification state
    const [verificationData, setVerificationData] = useState(null);
    const [blockchainTransactions, setBlockchainTransactions] = useState([]);

    const L = {
        title: lang === 'te' ? '🏦 బ్యాంక్ వెరిఫికేషన్ పోర్టల్' : '🏦 Bank Verification Portal',
        subtitle: lang === 'te' ? 'రైతు లావాదేవీలను ధృవీకరించండి' : 'Verify farmer transactions on blockchain',
        accessCode: lang === 'te' ? 'యాక్సెస్ కోడ్' : 'Bank Access Code',
        verify: lang === 'te' ? 'ధృవీకరించు' : 'Verify',
        search: lang === 'te' ? 'శోధన' : 'Search',
        orderId: lang === 'te' ? 'ఆర్డర్ ID' : 'Order ID',
        farmerId: lang === 'te' ? 'రైతు ID' : 'Farmer ID',
        txHash: lang === 'te' ? 'ట్రాన్సాక్షన్ హాష్' : 'Transaction Hash',
        exportReport: lang === 'te' ? 'రిపోర్ట్ ఎక్స్‌పోర్ట్' : 'Export Report'
    };

    // Bank Authentication
    const handleBankLogin = (e) => {
        e.preventDefault();
        const bank = BANK_ACCESS_CODES[accessCode.toUpperCase()];
        if (bank) {
            setBankInfo(bank);
            setIsAuthenticated(true);
            setAuthError('');
            console.log(`🏦 Bank ${bank.bankName} authenticated`);
        } else {
            setAuthError('Invalid access code. Please contact KisanMitra support.');
        }
    };

    // Search functionality
    const handleSearch = (e) => {
        e.preventDefault();
        setSearchError('');
        setSearchResult(null);
        setVerificationData(null);
        setBlockchainTransactions([]);

        try {
            if (searchType === 'order') {
                const order = orderService.getOrderById(searchQuery);
                if (order) {
                    setSearchResult({ type: 'order', data: order });
                    // Get blockchain transactions for this order
                    const txs = orderService.getOrderBlockchainTransactions(searchQuery);
                    setBlockchainTransactions(txs || []);
                    // Verify integrity
                    verifyOrder(order);
                } else {
                    setSearchError('Order not found');
                }
            } else if (searchType === 'farmer') {
                const orders = orderService.getFarmerOrders(searchQuery);
                const listings = marketService.getFarmerListings(searchQuery);
                if (orders.length > 0 || listings.length > 0) {
                    setSearchResult({
                        type: 'farmer',
                        data: { farmerId: searchQuery, orders, listings }
                    });
                    // Calculate farmer stats
                    calculateFarmerCredibility(orders, listings);
                } else {
                    setSearchError('No records found for this farmer');
                }
            } else if (searchType === 'transaction') {
                // Search by transaction hash - check both blockchain and orders
                let foundTx = null;
                let foundBlock = null;
                let foundOrder = null;

                // First search in blockchain blocks
                const blocks = transactionBlockchain.getBlocks();
                for (const block of blocks) {
                    const tx = block.transactions?.find(t =>
                        t.hash === searchQuery ||
                        t.hash?.includes(searchQuery) ||
                        t.txId?.includes(searchQuery)
                    );
                    if (tx) {
                        foundTx = tx;
                        foundBlock = block;
                        break;
                    }
                }

                // Also search in order payment transactions
                if (!foundTx) {
                    const allOrders = orderService.getAllOrders();
                    for (const order of allOrders) {
                        const paymentTx = order.payment?.transactions?.find(t =>
                            t.blockchainHash === searchQuery ||
                            t.blockchainHash?.includes(searchQuery) ||
                            t.txnId?.includes(searchQuery)
                        );
                        if (paymentTx) {
                            foundTx = {
                                hash: paymentTx.blockchainHash,
                                txId: paymentTx.txnId,
                                amount: paymentTx.amount,
                                type: 'ESCROW_DEPOSIT',
                                timestamp: paymentTx.timestamp,
                                from: order.buyerId,
                                to: 'ESCROW',
                                metadata: { orderId: order.orderId }
                            };
                            foundOrder = order;
                            break;
                        }
                    }
                }

                if (foundTx) {
                    setSearchResult({
                        type: 'transaction',
                        data: {
                            transaction: foundTx,
                            block: foundBlock,
                            order: foundOrder
                        }
                    });
                    // Verify - either Merkle proof or order-based
                    if (foundBlock) {
                        verifyTransaction(foundTx, foundBlock);
                    } else if (foundOrder) {
                        setVerificationData({
                            txHash: foundTx.hash,
                            orderId: foundOrder.orderId,
                            amount: foundTx.amount,
                            type: foundTx.type,
                            timestamp: foundTx.timestamp,
                            orderStatus: foundOrder.status,
                            escrowStatus: foundOrder.payment?.transactions?.[0]?.escrowStatus,
                            verified: true
                        });
                    }
                } else {
                    setSearchError('Transaction hash not found in blockchain or order records');
                }
            }
        } catch (error) {
            setSearchError(error.message);
        }
    };

    const verifyOrder = (order) => {
        const chainValid = orderService.verifyBlockchain();
        const escrowStatus = orderService.getEscrowStatus(order.orderId);

        setVerificationData({
            orderHash: order.orderHash,
            chainIntegrity: chainValid,
            escrowStatus: escrowStatus,
            paymentVerified: order.payment?.status === 'ESCROWED' || order.payment?.status === 'RELEASED',
            createdAt: order.createdAt,
            completedAt: order.status === 'COMPLETED' ? order.updatedAt : null
        });
    };

    const calculateFarmerCredibility = (orders, listings) => {
        const completedOrders = orders.filter(o => o.status === 'COMPLETED');
        const totalRevenue = completedOrders.reduce((sum, o) => sum + (o.payment?.farmerPayout?.amount || 0), 0);
        const avgRating = completedOrders.filter(o => o.buyerRating).reduce((sum, o) => sum + o.buyerRating, 0) /
            (completedOrders.filter(o => o.buyerRating).length || 1);

        setVerificationData({
            totalOrders: orders.length,
            completedOrders: completedOrders.length,
            cancelledOrders: orders.filter(o => o.status === 'CANCELLED').length,
            disputedOrders: orders.filter(o => o.status === 'DISPUTED').length,
            totalRevenue,
            avgRating: avgRating.toFixed(1),
            activeListings: listings.filter(l => l.status === 'LISTED').length,
            credibilityScore: calculateScore(completedOrders.length, orders.length)
        });
    };

    const calculateScore = (completed, total) => {
        if (total === 0) return 50;
        const completionRate = (completed / total) * 100;
        return Math.min(100, Math.round(completionRate * 0.8 + 20));
    };

    const verifyTransaction = (tx, block) => {
        // Verify Merkle proof
        const proof = transactionBlockchain.getMerkleProof(tx.hash, block);
        const isValid = transactionBlockchain.verifyMerkleProof(tx.hash, proof, block.merkleRoot);

        setVerificationData({
            txHash: tx.hash,
            blockIndex: block.blockIndex,
            blockHash: block.hash,
            merkleRoot: block.merkleRoot,
            merkleProofValid: isValid,
            timestamp: tx.timestamp,
            amount: tx.amount,
            type: tx.type
        });
    };

    const exportReport = () => {
        const report = {
            generatedAt: new Date().toISOString(),
            generatedBy: bankInfo?.bankName || 'Unknown',
            searchQuery,
            searchType,
            result: searchResult,
            verification: verificationData,
            transactions: blockchainTransactions
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `verification_report_${searchQuery}_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    // Login Screen
    if (!isAuthenticated) {
        return (
            <div className="market-container bank-portal">
                <header className="market-header-simple">
                    <button className="back-btn" onClick={() => navigate('/market')}>
                        <ArrowLeft size={20} />
                    </button>
                    <h1>{L.title}</h1>
                </header>

                <div className="bank-login-container">
                    <div className="bank-login-card">
                        <div className="bank-icon">
                            <Building2 size={48} />
                        </div>
                        <h2>Financial Institution Access</h2>
                        <p>Enter your bank access code to verify farmer transactions</p>

                        <form onSubmit={handleBankLogin}>
                            <div className="form-group">
                                <label><Lock size={16} /> {L.accessCode}</label>
                                <input
                                    type="password"
                                    value={accessCode}
                                    onChange={(e) => setAccessCode(e.target.value)}
                                    placeholder="Enter bank access code"
                                    required
                                />
                            </div>
                            {authError && (
                                <div className="auth-error">
                                    <AlertTriangle size={16} /> {authError}
                                </div>
                            )}
                            <button type="submit" className="primary-btn full-width">
                                <Shield size={18} /> Authenticate
                            </button>
                        </form>

                        <div className="bank-notice">
                            <p>🔒 This portal is for authorized financial institutions only.</p>
                            <p>Demo codes: SBI2024, HDFC2024, ICICI2024</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="market-container bank-portal">
            <header className="market-header-simple">
                <button className="back-btn" onClick={() => navigate('/market')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
                <div className="bank-badge">
                    <Verified size={16} />
                    {bankInfo?.bankName}
                </div>
            </header>

            {/* Search Section */}
            <div className="bank-search-section">
                <h3><Search size={18} /> Search & Verify</h3>
                <form onSubmit={handleSearch}>
                    <div className="search-type-tabs">
                        <button
                            type="button"
                            className={searchType === 'order' ? 'active' : ''}
                            onClick={() => setSearchType('order')}
                        >
                            {L.orderId}
                        </button>
                        <button
                            type="button"
                            className={searchType === 'farmer' ? 'active' : ''}
                            onClick={() => setSearchType('farmer')}
                        >
                            {L.farmerId}
                        </button>
                        <button
                            type="button"
                            className={searchType === 'transaction' ? 'active' : ''}
                            onClick={() => setSearchType('transaction')}
                        >
                            {L.txHash}
                        </button>
                    </div>
                    <div className="search-input-row">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder={`Enter ${searchType === 'order' ? 'Order ID (e.g., ORD-...)' : searchType === 'farmer' ? 'Farmer ID' : 'Transaction Hash'}`}
                            required
                        />
                        <button type="submit" className="primary-btn">
                            <Search size={18} /> {L.search}
                        </button>
                    </div>
                </form>
                {searchError && (
                    <div className="search-error">
                        <XCircle size={16} /> {searchError}
                    </div>
                )}
            </div>

            {/* Results Section */}
            {searchResult && (
                <div className="bank-results-section">
                    <div className="results-header">
                        <h3>📋 Verification Results</h3>
                        <button className="export-btn" onClick={exportReport}>
                            <Download size={16} /> {L.exportReport}
                        </button>
                    </div>

                    {/* Order Result */}
                    {searchResult.type === 'order' && (
                        <div className="result-card">
                            <div className="result-header">
                                <span className="result-id">{searchResult.data.orderId}</span>
                                <span className={`status-badge ${searchResult.data.status.toLowerCase()}`}>
                                    {searchResult.data.status}
                                </span>
                            </div>
                            <div className="result-details">
                                <div className="detail-row">
                                    <span>Crop:</span>
                                    <strong>{searchResult.data.crop} - {searchResult.data.variety}</strong>
                                </div>
                                <div className="detail-row">
                                    <span>Quantity:</span>
                                    <strong>{searchResult.data.quantity} {searchResult.data.unit}</strong>
                                </div>
                                <div className="detail-row">
                                    <span>Total Value:</span>
                                    <strong>₹{searchResult.data.pricing?.total}</strong>
                                </div>
                                <div className="detail-row">
                                    <span>Farmer ID:</span>
                                    <strong>{searchResult.data.farmerId}</strong>
                                </div>
                                <div className="detail-row">
                                    <span>Buyer ID:</span>
                                    <strong>{searchResult.data.buyerId}</strong>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Farmer Result */}
                    {searchResult.type === 'farmer' && (
                        <div className="result-card">
                            <div className="result-header">
                                <span className="result-id">Farmer: {searchResult.data.farmerId}</span>
                            </div>
                            <div className="farmer-stats-grid">
                                <div className="farmer-stat">
                                    <span className="stat-value">{verificationData?.totalOrders || 0}</span>
                                    <span className="stat-label">Total Orders</span>
                                </div>
                                <div className="farmer-stat completed">
                                    <span className="stat-value">{verificationData?.completedOrders || 0}</span>
                                    <span className="stat-label">Completed</span>
                                </div>
                                <div className="farmer-stat">
                                    <span className="stat-value">₹{verificationData?.totalRevenue?.toLocaleString() || 0}</span>
                                    <span className="stat-label">Total Revenue</span>
                                </div>
                                <div className="farmer-stat">
                                    <span className="stat-value">{verificationData?.credibilityScore || 0}%</span>
                                    <span className="stat-label">Credibility</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Verification Card */}
                    {verificationData && (
                        <div className="verification-card">
                            <h4><Shield size={18} /> Blockchain Verification</h4>

                            {searchResult.type === 'order' && (
                                <div className="verification-grid">
                                    <div className={`verification-item ${verificationData.chainIntegrity ? 'valid' : 'invalid'}`}>
                                        {verificationData.chainIntegrity ? <CheckCircle size={20} /> : <XCircle size={20} />}
                                        <span>Chain Integrity</span>
                                    </div>
                                    <div className={`verification-item ${verificationData.paymentVerified ? 'valid' : 'pending'}`}>
                                        {verificationData.paymentVerified ? <CheckCircle size={20} /> : <Clock size={20} />}
                                        <span>Payment {verificationData.paymentVerified ? 'Verified' : 'Pending'}</span>
                                    </div>
                                </div>
                            )}

                            {searchResult.type === 'transaction' && (
                                <div className="tx-details">
                                    <div className="detail-row">
                                        <span>Block Index:</span>
                                        <strong>#{verificationData.blockIndex}</strong>
                                    </div>
                                    <div className="detail-row">
                                        <span>Transaction Hash:</span>
                                        <code>{verificationData.txHash?.substring(0, 20)}...</code>
                                    </div>
                                    <div className="detail-row">
                                        <span>Merkle Proof:</span>
                                        <span className={verificationData.merkleProofValid ? 'valid-text' : 'invalid-text'}>
                                            {verificationData.merkleProofValid ? '✅ Valid' : '❌ Invalid'}
                                        </span>
                                    </div>
                                    <div className="detail-row">
                                        <span>Amount:</span>
                                        <strong>₹{verificationData.amount}</strong>
                                    </div>
                                    <div className="detail-row">
                                        <span>Type:</span>
                                        <strong>{verificationData.type}</strong>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Blockchain Transactions */}
                    {blockchainTransactions.length > 0 && (
                        <div className="transactions-card">
                            <h4><Hash size={18} /> Blockchain Transactions ({blockchainTransactions.length})</h4>
                            <div className="tx-list">
                                {blockchainTransactions.map((tx, i) => (
                                    <div key={i} className="tx-item">
                                        <div className="tx-type">{tx.type}</div>
                                        <div className="tx-amount">₹{tx.amount}</div>
                                        <div className="tx-hash">{tx.hash?.substring(0, 16)}...</div>
                                        <div className="tx-time">
                                            {new Date(tx.timestamp).toLocaleString()}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default BankVerification;
