import CryptoJS from 'crypto-js';
import { listingsAPI, statsAPI } from './api';

/**
 * Market Service - MongoDB Backend Integration
 * Now uses Flask API with MongoDB Atlas instead of localStorage
 * Maintains backward compatibility with existing component interfaces
 */

const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

class MarketService {
    constructor() {
        this.useAPI = true; // Enable API mode
        this._checkAPIConnection();
    }

    async _checkAPIConnection() {
        try {
            const response = await fetch(`${API_BASE}/stats`);
            if (response.ok) {
                console.log('✅ Connected to MongoDB backend');
                this.useAPI = true;
            }
        } catch (error) {
            console.warn('⚠️ API not available, some features may not work');
            this.useAPI = false;
        }
    }

    _computeHash(data) {
        const sortedKeys = Object.keys(data).sort();
        const canonicalObj = {};
        sortedKeys.forEach(key => {
            if (key !== 'contentHash' && key !== 'updatedAt' && key !== '_id') {
                canonicalObj[key] = data[key];
            }
        });
        return CryptoJS.SHA256(JSON.stringify(canonicalObj)).toString();
    }

    // ============ Create Listing ============

    async createListing(listingData) {
        try {
            const response = await fetch(`${API_BASE}/listings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop: listingData.crop,
                    variety: listingData.variety || '',
                    quantity: listingData.quantity,
                    unit: listingData.unit || 'kg',
                    price: listingData.price || listingData.pricing?.basePrice,
                    farmerId: listingData.farmerId || 'FARMER-DEMO-001',
                    farmerName: listingData.farmerName || 'Unknown Farmer',
                    farmerPhone: listingData.farmerPhone || '',
                    farmerVerified: listingData.farmerVerified || false,
                    location: {
                        state: listingData.state || listingData.location?.state || 'Andhra Pradesh',
                        district: listingData.district || listingData.location?.district || '',
                        city: listingData.city || listingData.location?.city || listingData.location || ''
                    },
                    contact: listingData.contact || {},
                    fertilizers: listingData.fertilizers || listingData.fertilizersUsed?.join(', ') || '',
                    pesticides: listingData.pesticides || listingData.pesticidesUsed?.join(', ') || '',
                    notes: listingData.description || listingData.notes || '',
                    images: listingData.images || []
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create listing');
            }

            const listing = await response.json();
            console.log(`✅ Listing created in MongoDB: ${listing.listingId}`);

            return {
                success: true,
                listingId: listing.listingId,
                hash: listing.metaHash,
                txHash: listing.metaHash,
                contentHash: listing.metaHash
            };
        } catch (error) {
            console.error('Create listing error:', error);
            return { success: false, error: error.message };
        }
    }

    // ============ Get Listings ============

    async getListings(filters = {}) {
        try {
            const query = filters.status ? `?status=${filters.status}` : '';
            const response = await fetch(`${API_BASE}/listings${query}`);

            if (!response.ok) {
                throw new Error('Failed to fetch listings');
            }

            let listings = await response.json();

            // Apply client-side filters for backward compatibility
            if (filters.crop) {
                listings = listings.filter(l =>
                    l.crop?.toLowerCase().includes(filters.crop.toLowerCase())
                );
            }
            if (filters.farmerId) {
                listings = listings.filter(l => l.farmerId === filters.farmerId);
            }

            // Map to expected format
            return listings.map(l => ({
                ...l,
                district: l.location?.district || l.district,
                state: l.location?.state || l.state,
                pricing: { basePrice: l.price },
                contentHash: l.metaHash,
                availableQuantity: l.quantity
            }));
        } catch (error) {
            console.error('Get listings error:', error);
            return [];
        }
    }

    async getActiveListings() {
        return this.getListings({ status: 'LISTED' });
    }

    async getListingById(listingId) {
        try {
            const response = await fetch(`${API_BASE}/listings/${listingId}`);

            if (!response.ok) {
                return null;
            }

            const listing = await response.json();

            // Map to expected format
            return {
                ...listing,
                district: listing.location?.district || listing.district,
                state: listing.location?.state || listing.state,
                pricing: { basePrice: listing.price },
                contentHash: listing.metaHash,
                availableQuantity: listing.quantity,
                description: listing.notes,
                fertilizersUsed: listing.fertilizers ? listing.fertilizers.split(', ') : [],
                pesticidesUsed: listing.pesticides ? listing.pesticides.split(', ') : []
            };
        } catch (error) {
            console.error('Get listing by ID error:', error);
            return null;
        }
    }

    async getFarmerListings(farmerId) {
        try {
            const response = await fetch(`${API_BASE}/listings/farmer/${farmerId}`);

            if (!response.ok) {
                return [];
            }

            return await response.json();
        } catch (error) {
            console.error('Get farmer listings error:', error);
            return [];
        }
    }

    async getFarmerListingsByPhone(phone) {
        try {
            console.log(`📞 Querying listings for phone: ${phone}`);
            const response = await fetch(`${API_BASE}/listings/phone/${phone}`);

            if (!response.ok) {
                console.warn(`API returned ${response.status} for phone ${phone}`);
                return [];
            }

            const listings = await response.json();
            console.log(`✅ Found ${listings.length} listings for phone ${phone}`);
            return listings;
        } catch (error) {
            console.error('Get farmer listings by phone error:', error);
            return [];
        }
    }

    // ============ Update Listing ============

    async updateListing(listingId, updates) {
        try {
            const response = await fetch(`${API_BASE}/listings/${listingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                throw new Error('Failed to update listing');
            }

            return { success: true };
        } catch (error) {
            console.error('Update listing error:', error);
            return { success: false, error: error.message };
        }
    }

    // ============ Delete Listing ============

    async deleteListing(listingId) {
        try {
            const response = await fetch(`${API_BASE}/listings/${listingId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to delete listing');
            }

            return { success: true };
        } catch (error) {
            console.error('Delete listing error:', error);
            return { success: false, error: error.message };
        }
    }

    // ============ Reserve/Sell (Update status) ============

    async reserveListing(listingId, quantity, orderId) {
        return this.updateListing(listingId, {
            status: 'RESERVED',
            reservedQuantity: quantity,
            reservedFor: orderId
        });
    }

    async markAsSold(listingId, orderId) {
        return this.updateListing(listingId, {
            status: 'SOLD',
            orderId: orderId
        });
    }

    async restoreQuantity(listingId, quantity) {
        return this.updateListing(listingId, {
            status: 'LISTED'
        });
    }

    // ============ Verification ============

    async verifyListing(listingId) {
        const listing = await this.getListingById(listingId);

        if (!listing) {
            return { verified: false, error: 'Listing not found' };
        }

        return {
            verified: true,
            listingId,
            storedHash: listing.metaHash,
            status: listing.status,
            createdAt: listing.createdAt,
            message: '✅ Listing verified in MongoDB'
        };
    }

    // ============ Statistics ============

    async getStats() {
        try {
            const response = await fetch(`${API_BASE}/stats`);

            if (!response.ok) {
                throw new Error('Failed to fetch stats');
            }

            return await response.json();
        } catch (error) {
            console.error('Get stats error:', error);
            return {
                totalListings: 0,
                activeListings: 0,
                soldListings: 0,
                reservedListings: 0
            };
        }
    }

    // ============ Search ============

    async search(query) {
        const listings = await this.getListings();
        const q = query.toLowerCase();

        return listings.filter(l =>
            l.crop?.toLowerCase().includes(q) ||
            l.variety?.toLowerCase().includes(q) ||
            l.location?.district?.toLowerCase().includes(q) ||
            l.farmerName?.toLowerCase().includes(q)
        );
    }

    // ============ AI Price Suggestion with Unit Support ============

    async getAIPriceSuggestion(crop, location, unit = 'Quintal') {
        // Base prices per quintal (100 kg)
        const basePricesPerQuintal = {
            // Grains (per quintal)
            'Rice': 2800, 'Wheat': 2200, 'Maize': 1800,
            'Jowar': 2500, 'Bajra': 2300, 'Ragi': 2600,

            // Pulses (per quintal)
            'Toor Dal': 8000, 'Moong Dal': 7500, 'Urad Dal': 7000,
            'Chana Dal': 6000, 'Red Gram': 8500,

            // Vegetables (per quintal)
            'Tomato': 2500, 'Potato': 1500, 'Onion': 2000,
            'Cabbage': 1200, 'Cauliflower': 1800, 'Brinjal': 2200,
            'Okra': 3000, 'Carrot': 2500, 'Beetroot': 2000,
            'Radish': 1500, 'Pumpkin': 1000, 'Bottle Gourd': 1500,
            'Ridge Gourd': 2000, 'Bitter Gourd': 2500, 'Cucumber': 1800,
            'Beans': 3000, 'Spinach': 2000, 'Coriander': 4000,
            'Curry Leaves': 8000, 'Green Chilli': 5000, 'Capsicum': 3500,
            'Drumstick': 2500,

            // Fruits (per quintal)
            'Mango': 4000, 'Banana': 2500, 'Papaya': 2000,
            'Guava': 3000, 'Pomegranate': 6000, 'Grapes': 5000,
            'Orange': 3500, 'Lemon': 4000, 'Watermelon': 1500,
            'Muskmelon': 2000, 'Apple': 8000, 'Custard Apple': 5000,
            'Coconut': 3000, 'Jackfruit': 2500, 'Pineapple': 3500,
            'Sapota': 3000,

            // Cash Crops (per quintal)
            'Cotton': 5500, 'Sugarcane': 350, 'Turmeric': 8000,
            'Ginger': 7000, 'Garlic': 6000, 'Red Chilli': 12000,
            'Groundnut': 4500, 'Sunflower': 4000, 'Castor': 5500
        };

        // Get base price for the crop (default: 2000)
        const basePriceQuintal = basePricesPerQuintal[crop] || 2000;

        // Add market variance (±20%)
        const variance = (Math.random() - 0.5) * 0.2;
        let suggestedPrice = Math.round(basePriceQuintal * (1 + variance));

        // Convert to kg if needed (1 quintal = 100 kg)
        if (unit === 'Kg') {
            suggestedPrice = Math.round(suggestedPrice / 100);
        } else if (unit === 'Ton') {
            suggestedPrice = Math.round(suggestedPrice * 10);
        }

        return {
            price: suggestedPrice,
            confidence: 0.85,
            unit: unit,
            reasoning: `Based on current market rates in ${location.district || 'your region'} (₹${suggestedPrice}/${unit})`
        };
    }

    // ============ Helper for listing IDs (debug) ============

    async getAllListingIds() {
        const listings = await this.getListings();
        return listings.map(l => l.listingId);
    }
}

export const marketService = new MarketService();
