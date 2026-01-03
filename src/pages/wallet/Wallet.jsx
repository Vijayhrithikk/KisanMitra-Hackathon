import React, { useState, useEffect } from 'react';
import { walletService } from '../../services/walletService';
import { transactionBlockchain } from '../../services/transactionBlockchain';
import './Wallet.css';

const Wallet = () => {
    const [wallet, setWallet] = useState(null);
    const [showLoadMoney, setShowLoadMoney] = useState(false);
    const [loadAmount, setLoadAmount] = useState('');
    const [transactions, setTransactions] = useState([]);
    const [blockchainStats, setBlockchainStats] = useState(null);
    const [activeTab, setActiveTab] = useState('wallet'); // wallet, transactions, blockchain

    useEffect(() => {
        loadWalletData();
    }, []);

    const loadWalletData = () => {
        // Get test buyer wallet
        const buyerWallet = walletService.getTestBuyer();
        setWallet(buyerWallet);

        if (buyerWallet) {
            setTransactions(walletService.getTransactionHistory(buyerWallet.id));
        }

        // Get blockchain stats
        const stats = transactionBlockchain.getStats();
        setBlockchainStats(stats);
    };

    const handleLoadMoney = () => {
        const amount = parseInt(loadAmount);
        if (isNaN(amount) || amount <= 0) {
            alert('Please enter a valid amount');
            return;
        }

        const result = walletService.loadMoney(wallet.id, amount, 'UPI');
        if (result.success) {
            setLoadAmount('');
            setShowLoadMoney(false);
            loadWalletData();
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    };

    const formatDate = (timestamp) => {
        return new Date(timestamp).toLocaleString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (!wallet) {
        return (
            <div className="wallet-page">
                <div className="wallet-loading">Loading wallet...</div>
            </div>
        );
    }

    return (
        <div className="wallet-page">
            {/* Wallet Header */}
            <div className="wallet-header">
                <h1>💳 Kisan Wallet</h1>
                <p className="wallet-user">{wallet.name}</p>
            </div>

            {/* Balance Card */}
            <div className="balance-card">
                <div className="balance-label">Available Balance</div>
                <div className="balance-amount">{formatCurrency(wallet.balance)}</div>
                <div className="wallet-id">ID: {wallet.id}</div>

                <div className="wallet-actions">
                    <button
                        className="btn-load"
                        onClick={() => setShowLoadMoney(true)}
                    >
                        ➕ Add Money
                    </button>
                    <button className="btn-withdraw">
                        🏦 Withdraw
                    </button>
                </div>
            </div>

            {/* Load Money Modal */}
            {showLoadMoney && (
                <div className="modal-overlay" onClick={() => setShowLoadMoney(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <h3>Add Money to Wallet</h3>
                        <div className="quick-amounts">
                            {[500, 1000, 2000, 5000, 10000].map(amt => (
                                <button
                                    key={amt}
                                    className="quick-amount-btn"
                                    onClick={() => setLoadAmount(amt.toString())}
                                >
                                    ₹{amt.toLocaleString()}
                                </button>
                            ))}
                        </div>
                        <input
                            type="number"
                            placeholder="Enter amount"
                            value={loadAmount}
                            onChange={(e) => setLoadAmount(e.target.value)}
                            className="amount-input"
                        />
                        <div className="modal-actions">
                            <button className="btn-cancel" onClick={() => setShowLoadMoney(false)}>
                                Cancel
                            </button>
                            <button className="btn-confirm" onClick={handleLoadMoney}>
                                Add ₹{loadAmount || '0'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="wallet-tabs">
                <button
                    className={activeTab === 'wallet' ? 'active' : ''}
                    onClick={() => setActiveTab('wallet')}
                >
                    📜 History
                </button>
                <button
                    className={activeTab === 'blockchain' ? 'active' : ''}
                    onClick={() => { setActiveTab('blockchain'); loadWalletData(); }}
                >
                    ⛓️ Blockchain
                </button>
            </div>

            {/* Transaction History */}
            {activeTab === 'wallet' && (
                <div className="transactions-list">
                    <h3>Transaction History</h3>
                    {transactions.length === 0 ? (
                        <p className="no-transactions">No transactions yet</p>
                    ) : (
                        transactions.map((txn, idx) => (
                            <div key={idx} className={`transaction-item ${txn.type.toLowerCase()}`}>
                                <div className="txn-icon">
                                    {txn.type === 'CREDIT' ? '📥' : '📤'}
                                </div>
                                <div className="txn-details">
                                    <div className="txn-description">{txn.description}</div>
                                    <div className="txn-date">{formatDate(txn.timestamp)}</div>
                                </div>
                                <div className={`txn-amount ${txn.type.toLowerCase()}`}>
                                    {txn.type === 'CREDIT' ? '+' : '-'}{formatCurrency(txn.amount)}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Blockchain Stats */}
            {activeTab === 'blockchain' && blockchainStats && (
                <div className="blockchain-section">
                    <h3>⛓️ Transaction Blockchain</h3>

                    <div className="blockchain-stats">
                        <div className="stat-card">
                            <div className="stat-value">{blockchainStats.blockchain.totalBlocks}</div>
                            <div className="stat-label">Blocks</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{blockchainStats.blockchain.totalTransactions}</div>
                            <div className="stat-label">Transactions</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{formatCurrency(blockchainStats.blockchain.totalVolume)}</div>
                            <div className="stat-label">Volume</div>
                        </div>
                    </div>

                    <div className="chain-validity">
                        <div className={`validity-badge ${blockchainStats.integrity.valid ? 'valid' : 'invalid'}`}>
                            {blockchainStats.integrity.valid ? '✅ Chain Valid' : '❌ Chain Invalid'}
                        </div>
                        <div className="validity-details">
                            Difficulty: {blockchainStats.blockchain.difficulty} |
                            Last Block: {blockchainStats.blockchain.lastBlockHash?.substring(0, 12)}...
                        </div>
                    </div>

                    <div className="escrow-stats">
                        <h4>Escrow Status</h4>
                        <div className="escrow-grid">
                            <div className="escrow-item">
                                <span className="escrow-count">{blockchainStats.escrow.deposits}</span>
                                <span className="escrow-label">Deposits</span>
                            </div>
                            <div className="escrow-item">
                                <span className="escrow-count">{blockchainStats.escrow.releases}</span>
                                <span className="escrow-label">Released</span>
                            </div>
                            <div className="escrow-item">
                                <span className="escrow-count">{blockchainStats.escrow.refunds}</span>
                                <span className="escrow-label">Refunded</span>
                            </div>
                            <div className="escrow-item">
                                <span className="escrow-count">{formatCurrency(blockchainStats.escrow.currentlyHeld)}</span>
                                <span className="escrow-label">In Escrow</span>
                            </div>
                        </div>
                    </div>

                    <div className="pending-txns">
                        <span>⏳ Pending in Mempool: {blockchainStats.mempool.pendingTransactions}</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Wallet;
