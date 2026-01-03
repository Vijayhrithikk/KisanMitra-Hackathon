/**
 * API Configuration for KisanMitra
 * Centralized API URL management for both development and production
 */

// ML Engine API (FastAPI - Crop recommendations, SMS, etc.)
export const ML_API_URL = import.meta.env.VITE_ML_API_URL || 'http://localhost:8001';

// Marketplace API (Flask - Listings, Orders, Users)
export const MARKET_API_URL = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

// Convenience exports
export const API_ENDPOINTS = {
    // ML Engine endpoints
    recommend: `${ML_API_URL}/recommend`,
    classifySoil: `${ML_API_URL}/classify-soil`,
    whatifScenario: `${ML_API_URL}/whatif-scenario`,
    subscribeCrop: `${ML_API_URL}/subscribe-crop`,
    getCropStage: `${ML_API_URL}/crop-stage`,
    getCropFaqs: `${ML_API_URL}/crop-faqs`,
    smsWebhook: `${ML_API_URL}/sms-webhook`,

    // Marketplace endpoints
    listings: `${MARKET_API_URL}/listings`,
    orders: `${MARKET_API_URL}/orders`,
    users: `${MARKET_API_URL}/users`,
    stats: `${MARKET_API_URL}/stats`,
};

export default { ML_API_URL, MARKET_API_URL, API_ENDPOINTS };
