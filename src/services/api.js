/**
 * API Configuration and Wrapper for KisanMitra Marketplace
 * Connects React frontend to Flask backend with MongoDB
 */

// API Base URL - Flask backend
const API_BASE_URL = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

/**
 * Generic fetch wrapper with error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const config = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Request failed' }));
            throw new Error(error.error || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error.message);
        throw error;
    }
}

// ==================== LISTINGS API ====================

export const listingsAPI = {
    getAll: (status = null) => {
        const query = status ? `?status=${status}` : '';
        return apiRequest(`/listings${query}`);
    },

    getById: (listingId) => {
        return apiRequest(`/listings/${listingId}`);
    },

    create: (listingData) => {
        return apiRequest('/listings', {
            method: 'POST',
            body: JSON.stringify(listingData),
        });
    },

    update: (listingId, updateData) => {
        return apiRequest(`/listings/${listingId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData),
        });
    },

    delete: (listingId) => {
        return apiRequest(`/listings/${listingId}`, {
            method: 'DELETE',
        });
    },

    getByFarmer: (farmerId) => {
        return apiRequest(`/listings/farmer/${farmerId}`);
    },
};


// ==================== ORDERS API ====================

export const ordersAPI = {
    getByBuyer: (buyerId) => {
        return apiRequest(`/orders?buyerId=${buyerId}`);
    },

    getByFarmer: (farmerId) => {
        return apiRequest(`/orders?farmerId=${farmerId}`);
    },

    getById: (orderId) => {
        return apiRequest(`/orders/${orderId}`);
    },

    create: (orderData) => {
        return apiRequest('/orders', {
            method: 'POST',
            body: JSON.stringify(orderData),
        });
    },

    recordPayment: (orderId, paymentData) => {
        return apiRequest(`/orders/${orderId}/pay`, {
            method: 'POST',
            body: JSON.stringify(paymentData),
        });
    },

    updateStatus: (orderId, status, additionalData = {}) => {
        return apiRequest(`/orders/${orderId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status, ...additionalData }),
        });
    },
};


// ==================== USERS API ====================

export const usersAPI = {
    register: (userData) => {
        return apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },

    getById: (userId) => {
        return apiRequest(`/users/${userId}`);
    },
};


// ==================== TRANSACTIONS API ====================

export const transactionsAPI = {
    getByOrder: (orderId) => {
        return apiRequest(`/transactions/${orderId}`);
    },

    verifyHash: (txHash) => {
        return apiRequest(`/verify/${txHash}`);
    },
};


// ==================== STATS API ====================

export const statsAPI = {
    getMarketplaceStats: () => {
        return apiRequest('/stats');
    },
};


// Export all APIs
export default {
    listings: listingsAPI,
    orders: ordersAPI,
    users: usersAPI,
    transactions: transactionsAPI,
    stats: statsAPI,
};
