/**
 * Wallet Service - User Wallet Management
 * Handles wallet creation, balance management, and transactions
 */

import CryptoJS from 'crypto-js';
import { transactionBlockchain } from './transactionBlockchain';

const WALLET_ACCOUNTS_KEY = 'kisanmitra_wallet_accounts';

class WalletService {
    constructor() {
        this._initialize();
    }

    _initialize() {
        if (!localStorage.getItem(WALLET_ACCOUNTS_KEY)) {
            // Create initial wallets with test buyer having ₹100,000
            const initialWallets = {
                'BUYER-TEST-001': {
                    id: 'BUYER-TEST-001',
                    name: 'Test Buyer',
                    phone: '9876543210',
                    type: 'BUYER',
                    balance: 100000, // ₹1,00,000 for testing
                    currency: 'INR',
                    createdAt: Date.now(),
                    transactions: [
                        {
                            id: 'INIT-001',
                            type: 'CREDIT',
                            amount: 100000,
                            description: 'Initial test balance',
                            timestamp: Date.now()
                        }
                    ]
                },
                'FARMER-TEST-001': {
                    id: 'FARMER-TEST-001',
                    name: 'Test Farmer',
                    phone: '9876543211',
                    type: 'FARMER',
                    balance: 0,
                    currency: 'INR',
                    createdAt: Date.now(),
                    upiId: 'farmer@upi',
                    transactions: []
                }
            };
            localStorage.setItem(WALLET_ACCOUNTS_KEY, JSON.stringify(initialWallets));
            console.log('💳 Wallet service initialized with test accounts');
        }
    }

    _getWallets() {
        return JSON.parse(localStorage.getItem(WALLET_ACCOUNTS_KEY) || '{}');
    }

    _saveWallets(wallets) {
        localStorage.setItem(WALLET_ACCOUNTS_KEY, JSON.stringify(wallets));
    }

    _generateWalletId(type) {
        const prefix = type === 'FARMER' ? 'FARMER' : 'BUYER';
        const random = Math.random().toString(36).substring(2, 8).toUpperCase();
        return `${prefix}-${random}`;
    }

    // ============ Wallet Creation ============

    createWallet(userData) {
        const wallets = this._getWallets();
        const walletId = this._generateWalletId(userData.type || 'BUYER');

        const wallet = {
            id: walletId,
            name: userData.name,
            phone: userData.phone,
            email: userData.email || null,
            type: userData.type || 'BUYER',
            balance: 0,
            currency: 'INR',
            upiId: userData.upiId || null,
            createdAt: Date.now(),
            transactions: []
        };

        wallets[walletId] = wallet;
        this._saveWallets(wallets);

        console.log(`💳 Wallet created: ${walletId}`);
        return { success: true, wallet };
    }

    // ============ Get Wallet ============

    getWallet(walletId) {
        const wallets = this._getWallets();
        return wallets[walletId] || null;
    }

    getWalletByPhone(phone) {
        const wallets = this._getWallets();
        return Object.values(wallets).find(w => w.phone === phone) || null;
    }

    getAllWallets() {
        return Object.values(this._getWallets());
    }

    // ============ Balance Operations ============

    getBalance(walletId) {
        const wallet = this.getWallet(walletId);
        return wallet ? wallet.balance : 0;
    }

    /**
     * Load money into wallet (simulates UPI/Bank transfer)
     */
    loadMoney(walletId, amount, paymentMethod = 'UPI') {
        if (amount <= 0) {
            return { success: false, error: 'Amount must be positive' };
        }

        const wallets = this._getWallets();
        const wallet = wallets[walletId];

        if (!wallet) {
            return { success: false, error: 'Wallet not found' };
        }

        // Add balance
        wallet.balance += amount;

        // Record transaction
        const txn = {
            id: `LOAD-${Date.now().toString(36).toUpperCase()}`,
            type: 'CREDIT',
            amount: amount,
            method: paymentMethod,
            description: `Loaded via ${paymentMethod}`,
            timestamp: Date.now(),
            balanceAfter: wallet.balance
        };
        wallet.transactions.push(txn);

        wallets[walletId] = wallet;
        this._saveWallets(wallets);

        console.log(`💰 Loaded ₹${amount} to ${walletId}`);
        return { success: true, transaction: txn, newBalance: wallet.balance };
    }

    /**
     * Deduct money for purchase (goes to blockchain escrow)
     */
    payForOrder(walletId, orderId, amount) {
        const wallets = this._getWallets();
        const wallet = wallets[walletId];

        if (!wallet) {
            return { success: false, error: 'Wallet not found' };
        }

        if (wallet.balance < amount) {
            return { success: false, error: 'Insufficient balance', currentBalance: wallet.balance };
        }

        // Deduct from wallet
        wallet.balance -= amount;

        // Record in wallet
        const walletTxn = {
            id: `PAY-${Date.now().toString(36).toUpperCase()}`,
            type: 'DEBIT',
            amount: amount,
            description: `Payment for order ${orderId}`,
            orderId: orderId,
            timestamp: Date.now(),
            balanceAfter: wallet.balance
        };
        wallet.transactions.push(walletTxn);

        wallets[walletId] = wallet;
        this._saveWallets(wallets);

        // Record on blockchain (escrow deposit)
        let blockchainTx = null;
        try {
            blockchainTx = transactionBlockchain.recordEscrowDeposit(
                orderId,
                walletId,
                amount,
                'WALLET'
            );
        } catch (error) {
            console.error('Blockchain error:', error);
            // Rollback wallet deduction
            wallet.balance += amount;
            wallet.transactions.pop();
            wallets[walletId] = wallet;
            this._saveWallets(wallets);
            return { success: false, error: 'Blockchain transaction failed' };
        }

        console.log(`💸 Paid ₹${amount} from ${walletId} for order ${orderId}`);
        return {
            success: true,
            walletTransaction: walletTxn,
            blockchainTx,
            newBalance: wallet.balance
        };
    }

    /**
     * Credit farmer wallet when escrow is released
     */
    creditFromEscrow(walletId, orderId, amount) {
        const wallets = this._getWallets();
        let wallet = wallets[walletId];

        // Create wallet if farmer doesn't have one
        if (!wallet) {
            wallet = {
                id: walletId,
                name: 'Farmer',
                type: 'FARMER',
                balance: 0,
                currency: 'INR',
                createdAt: Date.now(),
                transactions: []
            };
        }

        wallet.balance += amount;

        const txn = {
            id: `ESCROW-${Date.now().toString(36).toUpperCase()}`,
            type: 'CREDIT',
            amount: amount,
            description: `Payment received for order ${orderId}`,
            orderId: orderId,
            timestamp: Date.now(),
            balanceAfter: wallet.balance
        };
        wallet.transactions.push(txn);

        wallets[walletId] = wallet;
        this._saveWallets(wallets);

        console.log(`💰 Credited ₹${amount} to farmer ${walletId}`);
        return { success: true, transaction: txn, newBalance: wallet.balance };
    }

    /**
     * Refund to buyer wallet when order is cancelled
     */
    refundToWallet(walletId, orderId, amount) {
        const wallets = this._getWallets();
        const wallet = wallets[walletId];

        if (!wallet) {
            return { success: false, error: 'Wallet not found' };
        }

        wallet.balance += amount;

        const txn = {
            id: `REFUND-${Date.now().toString(36).toUpperCase()}`,
            type: 'CREDIT',
            amount: amount,
            description: `Refund for cancelled order ${orderId}`,
            orderId: orderId,
            timestamp: Date.now(),
            balanceAfter: wallet.balance
        };
        wallet.transactions.push(txn);

        wallets[walletId] = wallet;
        this._saveWallets(wallets);

        // Record refund on blockchain
        try {
            transactionBlockchain.refundFromEscrow(orderId, 'ORDER_CANCELLED');
        } catch (error) {
            console.error('Blockchain refund error:', error);
        }

        return { success: true, transaction: txn, newBalance: wallet.balance };
    }

    /**
     * Withdraw to bank account
     */
    withdrawToBank(walletId, amount, bankDetails) {
        const wallets = this._getWallets();
        const wallet = wallets[walletId];

        if (!wallet) {
            return { success: false, error: 'Wallet not found' };
        }

        if (wallet.balance < amount) {
            return { success: false, error: 'Insufficient balance' };
        }

        wallet.balance -= amount;

        const txn = {
            id: `WITHDRAW-${Date.now().toString(36).toUpperCase()}`,
            type: 'DEBIT',
            amount: amount,
            description: `Withdrawal to bank ${bankDetails?.accountLast4 || '****'}`,
            method: 'BANK_TRANSFER',
            timestamp: Date.now(),
            balanceAfter: wallet.balance,
            status: 'PROCESSING' // In real app, would track actual transfer
        };
        wallet.transactions.push(txn);

        wallets[walletId] = wallet;
        this._saveWallets(wallets);

        return {
            success: true,
            transaction: txn,
            newBalance: wallet.balance,
            message: 'Withdrawal initiated. Will be credited to your bank in 24-48 hours.'
        };
    }

    // ============ Transaction History ============

    getTransactionHistory(walletId) {
        const wallet = this.getWallet(walletId);
        if (!wallet) return [];
        return wallet.transactions.sort((a, b) => b.timestamp - a.timestamp);
    }

    // ============ Test Helpers ============

    /**
     * Get test buyer for quick testing
     */
    getTestBuyer() {
        return this.getWallet('BUYER-TEST-001');
    }

    /**
     * Get test farmer for quick testing
     */
    getTestFarmer() {
        return this.getWallet('FARMER-TEST-001');
    }

    /**
     * Reset test accounts
     */
    resetTestAccounts() {
        localStorage.removeItem(WALLET_ACCOUNTS_KEY);
        this._initialize();
        return { success: true, message: 'Test accounts reset' };
    }
}

export const walletService = new WalletService();
