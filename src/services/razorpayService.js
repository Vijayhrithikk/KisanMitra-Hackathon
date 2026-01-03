/**
 * Razorpay Payment Service for KisanMitra
 * Handles payment integration for Marketplace and Rentals
 */

const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

// Razorpay script URL
const RAZORPAY_SCRIPT_URL = 'https://checkout.razorpay.com/v1/checkout.js';

/**
 * Load Razorpay SDK script dynamically
 */
export const loadRazorpayScript = () => {
    return new Promise((resolve, reject) => {
        // Check if already loaded
        if (window.Razorpay) {
            resolve(true);
            return;
        }

        const script = document.createElement('script');
        script.src = RAZORPAY_SCRIPT_URL;
        script.onload = () => resolve(true);
        script.onerror = () => reject(new Error('Failed to load Razorpay SDK'));
        document.body.appendChild(script);
    });
};

/**
 * Create a Razorpay order via backend
 * @param {number} amount - Amount in INR (will be converted to paise)
 * @param {string} receipt - Receipt/Order ID for reference
 * @param {object} notes - Additional notes
 */
export const createRazorpayOrder = async (amount, receipt, notes = {}) => {
    try {
        const response = await fetch(`${API_BASE}/payments/create-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: Math.round(amount * 100), // Convert to paise
                currency: 'INR',
                receipt,
                notes
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to create order');
        }

        return data;
    } catch (error) {
        console.error('Create order error:', error);
        throw error;
    }
};

/**
 * Verify payment signature via backend
 */
export const verifyPayment = async (paymentData) => {
    try {
        const response = await fetch(`${API_BASE}/payments/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(paymentData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Payment verification failed');
        }

        return data;
    } catch (error) {
        console.error('Verify payment error:', error);
        throw error;
    }
};

/**
 * Open Razorpay checkout modal
 * @param {object} options - Razorpay options
 * @param {function} onSuccess - Success callback
 * @param {function} onFailure - Failure callback
 */
export const openRazorpayCheckout = async (options, onSuccess, onFailure) => {
    try {
        // Ensure Razorpay is loaded
        await loadRazorpayScript();

        const razorpay = new window.Razorpay({
            key: options.key_id,
            amount: options.amount,
            currency: options.currency || 'INR',
            name: 'KisanMitra',
            description: options.description || 'Payment for order',
            order_id: options.order_id,
            prefill: {
                name: options.prefill?.name || '',
                email: options.prefill?.email || '',
                contact: options.prefill?.contact || ''
            },
            notes: options.notes || {},
            theme: {
                color: '#16a34a' // KisanMitra green
            },
            handler: async function (response) {
                try {
                    // Verify payment on backend
                    const verifyData = {
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_signature: response.razorpay_signature,
                        order_id: options.internal_order_id,
                        order_type: options.order_type || 'marketplace'
                    };

                    const result = await verifyPayment(verifyData);

                    if (result.verified) {
                        onSuccess({
                            ...response,
                            verified: true,
                            internal_order_id: options.internal_order_id
                        });
                    } else {
                        onFailure(new Error('Payment verification failed'));
                    }
                } catch (error) {
                    onFailure(error);
                }
            },
            modal: {
                ondismiss: function () {
                    onFailure(new Error('Payment cancelled by user'));
                }
            }
        });

        razorpay.open();
    } catch (error) {
        onFailure(error);
    }
};

/**
 * Complete payment flow - creates order and opens checkout
 * @param {number} amount - Amount in INR
 * @param {string} orderId - Internal order ID
 * @param {string} orderType - 'marketplace' or 'rental'
 * @param {object} customerInfo - Customer details
 * @returns {Promise} - Resolves with payment result
 */
export const initiatePayment = async (amount, orderId, orderType = 'marketplace', customerInfo = {}) => {
    return new Promise(async (resolve, reject) => {
        try {
            // Create Razorpay order
            const orderData = await createRazorpayOrder(amount, orderId, {
                order_id: orderId,
                order_type: orderType
            });

            // Open checkout
            openRazorpayCheckout(
                {
                    key_id: orderData.key_id,
                    amount: orderData.amount,
                    currency: orderData.currency,
                    order_id: orderData.order_id,
                    internal_order_id: orderId,
                    order_type: orderType,
                    description: orderType === 'rental'
                        ? `Equipment Rental - ${orderId}`
                        : `Order Payment - ${orderId}`,
                    prefill: {
                        name: customerInfo.name || '',
                        contact: customerInfo.phone || ''
                    }
                },
                (successData) => resolve(successData),
                (error) => reject(error)
            );
        } catch (error) {
            reject(error);
        }
    });
};

export default {
    loadRazorpayScript,
    createRazorpayOrder,
    verifyPayment,
    openRazorpayCheckout,
    initiatePayment
};
