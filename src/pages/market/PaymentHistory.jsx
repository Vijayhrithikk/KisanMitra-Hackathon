import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { paymentService } from '../../services/paymentService';
import { ArrowLeft, Wallet, TrendingUp, Clock, CheckCircle, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import './Market.css';

const PaymentHistory = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const { user } = useAuth();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [summary, setSummary] = useState(null);
    const [payouts, setPayouts] = useState([]);
    const [activeTab, setActiveTab] = useState('summary');

    const L = {
        title: lang === 'te' ? '💰 చెల్లింపులు' : '💰 Payments',
        summary: lang === 'te' ? 'సారాంశం' : 'Summary',
        history: lang === 'te' ? 'చరిత్ర' : 'History',
        totalEarnings: lang === 'te' ? 'మొత్తం సంపాదన' : 'Total Earnings',
        pendingPayouts: lang === 'te' ? 'పెండింగ్ పేఔట్స్' : 'Pending Payouts',
        completedPayouts: lang === 'te' ? 'పూర్తయినవి' : 'Completed Payouts',
        lastPayout: lang === 'te' ? 'చివరి పేఔట్' : 'Last Payout',
        noPayouts: lang === 'te' ? 'పేఔట్స్ లేవు' : 'No payouts yet',
        processing: lang === 'te' ? 'ప్రాసెసింగ్' : 'Processing',
        completed: lang === 'te' ? 'పూర్తయింది' : 'Completed'
    };

    useEffect(() => {
        if (user?.farmerId) {
            const summaryData = paymentService.getPaymentSummary(user.farmerId);
            setSummary(summaryData);

            const payoutHistory = paymentService.getFarmerPayoutHistory(user.farmerId);
            setPayouts(payoutHistory);
        }
    }, [user]);

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    };

    return (
        <div className="market-container white-theme">
            <header className="market-header-simple">
                <button className="back-btn" onClick={() => navigate('/market')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
            </header>

            {/* Tabs */}
            <div className="payment-tabs">
                <button
                    className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
                    onClick={() => setActiveTab('summary')}
                >
                    <TrendingUp size={18} />
                    {L.summary}
                </button>
                <button
                    className={`tab ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    <Clock size={18} />
                    {L.history}
                </button>
            </div>

            <div className="payment-content">
                {/* Summary Tab */}
                {activeTab === 'summary' && (
                    <div className="summary-view">
                        {/* Total Earnings Card */}
                        <div className="earnings-card">
                            <div className="earnings-icon">
                                <Wallet size={32} />
                            </div>
                            <div className="earnings-info">
                                <span className="earnings-label">{L.totalEarnings}</span>
                                <span className="earnings-amount">₹{summary?.totalEarnings || 0}</span>
                            </div>
                        </div>

                        {/* Stats Grid */}
                        <div className="stats-grid">
                            <div className="stat-card pending">
                                <Clock size={24} />
                                <span className="stat-value">₹{summary?.pendingPayouts || 0}</span>
                                <span className="stat-label">{L.pendingPayouts}</span>
                            </div>
                            <div className="stat-card completed">
                                <CheckCircle size={24} />
                                <span className="stat-value">{summary?.completedPayouts || 0}</span>
                                <span className="stat-label">{L.completedPayouts}</span>
                            </div>
                        </div>

                        {/* Last Payout */}
                        {summary?.lastPayout && (
                            <div className="last-payout-card">
                                <h4>{L.lastPayout}</h4>
                                <div className="payout-info">
                                    <span className="payout-amount">₹{summary.lastPayout.amount}</span>
                                    <span className="payout-date">{formatDate(summary.lastPayout.completedAt)}</span>
                                </div>
                                <div className="payout-upi">
                                    To: {summary.lastPayout.upiId}
                                </div>
                            </div>
                        )}

                        {/* UPI Setup */}
                        <div className="upi-setup-card">
                            <h4>{lang === 'te' ? 'UPI ID సెట్ చేయండి' : 'Set Up UPI for Payouts'}</h4>
                            <p>{lang === 'te' ? 'మీ UPI ID జోడించి వేగంగా పేఔట్ పొందండి' : 'Add your UPI ID for instant payouts'}</p>
                            <input type="text" placeholder="yourname@upi" className="upi-input" />
                            <button className="save-upi-btn">
                                {lang === 'te' ? 'సేవ్ చేయండి' : 'Save UPI ID'}
                            </button>
                        </div>
                    </div>
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                    <div className="history-view">
                        {payouts.length === 0 ? (
                            <div className="empty-payouts">
                                <Wallet size={48} />
                                <p>{L.noPayouts}</p>
                            </div>
                        ) : (
                            <div className="payouts-list">
                                {payouts.map(payout => (
                                    <div key={payout.payoutId} className="payout-item">
                                        <div className="payout-icon">
                                            <ArrowDownLeft size={20} />
                                        </div>
                                        <div className="payout-details">
                                            <span className="payout-id">{payout.payoutId}</span>
                                            <span className="payout-order">Order: {payout.orderId}</span>
                                            <span className="payout-date">{formatDate(payout.createdAt)}</span>
                                        </div>
                                        <div className="payout-right">
                                            <span className="payout-amount">₹{payout.amount}</span>
                                            <span className={`payout-status ${payout.status.toLowerCase()}`}>
                                                {payout.status === 'PROCESSING' ? L.processing : L.completed}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default PaymentHistory;
