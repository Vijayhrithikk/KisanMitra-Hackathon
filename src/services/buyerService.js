import CryptoJS from 'crypto-js';

const BUYERS_KEY = 'kisanmitra_buyers';

class BuyerService {
    constructor() {
        if (!localStorage.getItem(BUYERS_KEY)) {
            localStorage.setItem(BUYERS_KEY, JSON.stringify([]));
            console.log('👥 Buyer registry initialized');
        }
    }

    // Get all buyers
    _getBuyers() {
        return JSON.parse(localStorage.getItem(BUYERS_KEY) || '[]');
    }

    // Save buyers
    _saveBuyers(buyers) {
        localStorage.setItem(BUYERS_KEY, JSON.stringify(buyers));
    }

    // Generate buyer ID
    _generateBuyerId(type) {
        const prefix = type === 'CONSUMER' ? 'C' : type === 'RESTAURANT' ? 'R' : 'W';
        return `${prefix}-${Date.now().toString(36).toUpperCase()}`;
    }

    // Register new buyer
    registerBuyer(buyerData) {
        const buyers = this._getBuyers();

        // Check if phone already exists
        const existing = buyers.find(b => b.phone === buyerData.phone);
        if (existing) {
            return { success: false, error: 'Phone number already registered', buyer: existing };
        }

        const buyer = {
            buyerId: this._generateBuyerId(buyerData.type),
            type: buyerData.type, // CONSUMER, RESTAURANT, RETAILER, WHOLESALER

            // Profile
            name: buyerData.name,
            phone: buyerData.phone,
            email: buyerData.email || '',

            // Business info (for B2B)
            businessName: buyerData.businessName || '',
            gstNumber: buyerData.gstNumber || '',
            fssaiLicense: buyerData.fssaiLicense || '',

            // Addresses
            addresses: buyerData.addresses || [],

            // Stats
            totalOrders: 0,
            totalSpent: 0,
            rating: 0,

            // Meta
            createdAt: new Date().toISOString(),
            verified: false,
            active: true
        };

        // Generate verification hash
        buyer.verificationHash = CryptoJS.SHA256(
            buyer.buyerId + buyer.phone + buyer.createdAt
        ).toString().substring(0, 16);

        buyers.push(buyer);
        this._saveBuyers(buyers);

        return { success: true, buyer };
    }

    // Get buyer by ID
    getBuyerById(buyerId) {
        const buyers = this._getBuyers();
        return buyers.find(b => b.buyerId === buyerId);
    }

    // Get buyer by phone
    getBuyerByPhone(phone) {
        const buyers = this._getBuyers();
        return buyers.find(b => b.phone === phone);
    }

    // Update buyer profile
    updateBuyer(buyerId, updates) {
        const buyers = this._getBuyers();
        const index = buyers.findIndex(b => b.buyerId === buyerId);
        if (index === -1) return { success: false, error: 'Buyer not found' };

        // Don't allow changing buyerId or type
        const { buyerId: _, type: __, ...allowedUpdates } = updates;
        buyers[index] = { ...buyers[index], ...allowedUpdates };
        this._saveBuyers(buyers);

        return { success: true, buyer: buyers[index] };
    }

    // Add address
    addAddress(buyerId, address) {
        const buyers = this._getBuyers();
        const index = buyers.findIndex(b => b.buyerId === buyerId);
        if (index === -1) return { success: false, error: 'Buyer not found' };

        const newAddress = {
            addressId: `ADDR-${Date.now().toString(36)}`,
            label: address.label || 'Home',
            line1: address.line1,
            line2: address.line2 || '',
            city: address.city,
            district: address.district,
            state: address.state,
            pincode: address.pincode,
            coordinates: address.coordinates || null,
            isDefault: buyers[index].addresses.length === 0
        };

        buyers[index].addresses.push(newAddress);
        this._saveBuyers(buyers);

        return { success: true, address: newAddress };
    }

    // Set default address
    setDefaultAddress(buyerId, addressId) {
        const buyers = this._getBuyers();
        const index = buyers.findIndex(b => b.buyerId === buyerId);
        if (index === -1) return { success: false, error: 'Buyer not found' };

        buyers[index].addresses = buyers[index].addresses.map(addr => ({
            ...addr,
            isDefault: addr.addressId === addressId
        }));
        this._saveBuyers(buyers);

        return { success: true };
    }

    // Get buyer types with labels
    getBuyerTypes() {
        return [
            { id: 'CONSUMER', en: 'Individual Consumer', te: 'వ్యక్తిగత వినియోగదారు', icon: '👤' },
            { id: 'RESTAURANT', en: 'Restaurant / Hotel', te: 'రెస్టారెంట్ / హోటల్', icon: '🍽️' },
            { id: 'RETAILER', en: 'Retail Shop', te: 'రిటైల్ షాప్', icon: '🏪' },
            { id: 'WHOLESALER', en: 'Wholesaler', te: 'హోల్‌సేలర్', icon: '🏭' }
        ];
    }

    // Update order stats
    updateOrderStats(buyerId, orderAmount) {
        const buyers = this._getBuyers();
        const index = buyers.findIndex(b => b.buyerId === buyerId);
        if (index === -1) return;

        buyers[index].totalOrders += 1;
        buyers[index].totalSpent += orderAmount;
        this._saveBuyers(buyers);
    }

    // Get all buyers (admin)
    getAllBuyers() {
        return this._getBuyers();
    }

    // Get buyers by type
    getBuyersByType(type) {
        return this._getBuyers().filter(b => b.type === type);
    }
}

export const buyerService = new BuyerService();
