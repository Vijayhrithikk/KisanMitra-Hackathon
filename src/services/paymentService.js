// Payment Tracking Service
const PAYMENTS_KEY = 'kisanmitra_payments';

class PaymentService {
    constructor() {
        if (!localStorage.getItem(PAYMENTS_KEY)) {
            localStorage.setItem(PAYMENTS_KEY, JSON.stringify([]));
        }
    }

    _getPayments() {
        return JSON.parse(localStorage.getItem(PAYMENTS_KEY) || '[]');
    }

    _savePayments(payments) {
        localStorage.setItem(PAYMENTS_KEY, JSON.stringify(payments));
    }

    // Payment methods
    getPaymentMethods() {
        return [
            { id: 'UPI', en: 'UPI Payment', te: 'UPI చెల్లింపు', icon: '📱' },
            { id: 'BANK', en: 'Bank Transfer', te: 'బ్యాంక్ ట్రాన్స్‌ఫర్', icon: '🏦' },
            { id: 'COD', en: 'Cash on Delivery', te: 'డెలివరీ తర్వాత క్యాష్', icon: '💵' },
            { id: 'WALLET', en: 'KisanMitra Wallet', te: 'కిసాన్ మిత్ర వాలెట్', icon: '👛' }
        ];
    }

    // Initiate payment (mock UPI flow)
    initiatePayment(orderId, amount, method = 'UPI', buyerId) {
        const payments = this._getPayments();

        const payment = {
            paymentId: `PAY-${Date.now().toString(36).toUpperCase()}`,
            orderId,
            buyerId,
            amount,
            method,
            status: 'INITIATED',
            createdAt: new Date().toISOString(),
            upiLink: method === 'UPI' ? this._generateUPILink(amount, orderId) : null,
            transactions: []
        };

        payments.push(payment);
        this._savePayments(payments);

        return { success: true, payment };
    }

    _generateUPILink(amount, orderId) {
        // Mock UPI link - in real app, use Razorpay/PayU
        return `upi://pay?pa=kisanmitra@upi&pn=KisanMitra&am=${amount}&tn=Order-${orderId}`;
    }

    // Record payment success (mock callback)
    recordPaymentSuccess(paymentId, transactionDetails) {
        const payments = this._getPayments();
        const index = payments.findIndex(p => p.paymentId === paymentId);

        if (index === -1) return { success: false, error: 'Payment not found' };

        const txn = {
            txnId: transactionDetails.txnId || `TXN-${Date.now().toString(36)}`,
            amount: transactionDetails.amount || payments[index].amount,
            method: transactionDetails.method || payments[index].method,
            status: 'SUCCESS',
            timestamp: new Date().toISOString(),
            utrNumber: transactionDetails.utrNumber || null
        };

        payments[index].status = 'COMPLETED';
        payments[index].completedAt = new Date().toISOString();
        payments[index].transactions.push(txn);
        this._savePayments(payments);

        return { success: true, payment: payments[index], transaction: txn };
    }

    // Get payment by order
    getPaymentByOrder(orderId) {
        return this._getPayments().find(p => p.orderId === orderId);
    }

    // Get farmer's pending payouts
    getFarmerPayouts(farmerId) {
        // In real app, aggregate from orders
        return {
            pending: 0,
            processing: 0,
            completed: 0,
            totalEarned: 0
        };
    }

    // Release farmer payout (mock)
    releasePayout(orderId, farmerId, amount, upiId) {
        const payouts = JSON.parse(localStorage.getItem('kisanmitra_payouts') || '[]');

        const payout = {
            payoutId: `POUT-${Date.now().toString(36).toUpperCase()}`,
            orderId,
            farmerId,
            amount,
            upiId,
            status: 'PROCESSING',
            createdAt: new Date().toISOString(),
            estimatedArrival: new Date(Date.now() + 172800000).toISOString() // +2 days
        };

        payouts.push(payout);
        localStorage.setItem('kisanmitra_payouts', JSON.stringify(payouts));

        // Simulate payout completion after delay
        setTimeout(() => {
            const updatedPayouts = JSON.parse(localStorage.getItem('kisanmitra_payouts') || '[]');
            const idx = updatedPayouts.findIndex(p => p.payoutId === payout.payoutId);
            if (idx !== -1) {
                updatedPayouts[idx].status = 'COMPLETED';
                updatedPayouts[idx].completedAt = new Date().toISOString();
                localStorage.setItem('kisanmitra_payouts', JSON.stringify(updatedPayouts));
            }
        }, 5000);

        return { success: true, payout };
    }

    // Get farmer payout history
    getFarmerPayoutHistory(farmerId) {
        const payouts = JSON.parse(localStorage.getItem('kisanmitra_payouts') || '[]');
        return payouts.filter(p => p.farmerId === farmerId);
    }

    // Get payment summary for dashboard
    getPaymentSummary(farmerId) {
        const payouts = this.getFarmerPayoutHistory(farmerId);

        return {
            totalEarnings: payouts.filter(p => p.status === 'COMPLETED').reduce((sum, p) => sum + p.amount, 0),
            pendingPayouts: payouts.filter(p => p.status === 'PROCESSING').reduce((sum, p) => sum + p.amount, 0),
            completedPayouts: payouts.filter(p => p.status === 'COMPLETED').length,
            lastPayout: payouts.filter(p => p.status === 'COMPLETED').slice(-1)[0] || null
        };
    }

    // Simulate payment for testing
    simulatePayment(orderId, amount) {
        const result = this.initiatePayment(orderId, amount, 'UPI', 'TEST');
        if (result.success) {
            return this.recordPaymentSuccess(result.payment.paymentId, {
                amount,
                utrNumber: `UTR${Date.now()}`
            });
        }
        return result;
    }
}

export const paymentService = new PaymentService();
