// Kisan Rentals Service - Agricultural Equipment & Services Rental Marketplace

const RENTALS_KEY = 'kisanmitra_rentals_ledger';

// Rental Categories with icons
export const RENTAL_CATEGORIES = {
    TRACTOR: { id: 'TRACTOR', name: 'Tractors', icon: '🚜', color: '#F59E0B' },
    EQUIPMENT: { id: 'EQUIPMENT', name: 'Equipment', icon: '⚙️', color: '#3B82F6' },
    COLD_STORAGE: { id: 'COLD_STORAGE', name: 'Cold Storage', icon: '❄️', color: '#06B6D4' },
    GODOWN: { id: 'GODOWN', name: 'Godowns', icon: '🏭', color: '#8B5CF6' },
    DRONE: { id: 'DRONE', name: 'Drone Services', icon: '🚁', color: '#10B981' },
    TRANSPORT: { id: 'TRANSPORT', name: 'Transport', icon: '🚛', color: '#EF4444' },
    HARVESTER: { id: 'HARVESTER', name: 'Harvesters', icon: '🌾', color: '#84CC16' },
    IRRIGATION: { id: 'IRRIGATION', name: 'Irrigation', icon: '💧', color: '#0EA5E9' }
};

class RentalService {
    constructor() {
        if (!localStorage.getItem(RENTALS_KEY)) {
            localStorage.setItem(RENTALS_KEY, JSON.stringify([]));
            this._seedTestData();
        }
    }

    _seedTestData() {
        const sampleRentals = [
            {
                category: 'TRACTOR',
                title: 'John Deere 5050D - 50HP Tractor',
                description: 'Well-maintained tractor with rotavator. Perfect for ploughing and tilling.',
                dailyRate: 2500,
                monthlyRate: 45000,
                location: { lat: 16.5062, lng: 80.6480, city: 'Vijayawada', district: 'Krishna', state: 'Andhra Pradesh' },
                contact: { name: 'Raju Naidu', phone: '+91 98765 12345' },
                available: true,
                images: []
            },
            {
                category: 'COLD_STORAGE',
                title: '500 MT Cold Storage Facility',
                description: 'Temperature controlled storage for fruits and vegetables. 24/7 power backup.',
                dailyRate: 5000,
                monthlyRate: 80000,
                location: { lat: 17.3850, lng: 78.4867, city: 'Hyderabad', district: 'Rangareddy', state: 'Telangana' },
                contact: { name: 'Krishna Reddy', phone: '+91 87654 23456' },
                available: true,
                images: []
            },
            {
                category: 'DRONE',
                title: 'Agricultural Drone Spraying Service',
                description: 'DJI Agras T30 drone for pesticide/fertilizer spraying. Covers 10 acres/hour.',
                dailyRate: 8000,
                monthlyRate: null,
                location: { lat: 15.8281, lng: 78.0373, city: 'Kurnool', district: 'Kurnool', state: 'Andhra Pradesh' },
                contact: { name: 'Venkat Kumar', phone: '+91 76543 34567' },
                available: true,
                images: []
            },
            {
                category: 'GODOWN',
                title: 'Modern Grain Storage Godown - 1000 MT',
                description: 'Moisture-proof grain storage with pest control. Near highway for easy transport.',
                dailyRate: 3000,
                monthlyRate: 60000,
                location: { lat: 16.3067, lng: 80.4365, city: 'Guntur', district: 'Guntur', state: 'Andhra Pradesh' },
                contact: { name: 'Suresh Babu', phone: '+91 65432 45678' },
                available: true,
                images: []
            },
            {
                category: 'HARVESTER',
                title: 'Combine Harvester - Paddy/Wheat',
                description: 'CLAAS Crop Tiger 30 harvester. Experienced operator included.',
                dailyRate: 15000,
                monthlyRate: null,
                location: { lat: 14.6819, lng: 77.5990, city: 'Anantapur', district: 'Anantapur', state: 'Andhra Pradesh' },
                contact: { name: 'Ramana Murthy', phone: '+91 54321 56789' },
                available: true,
                images: []
            },
            {
                category: 'EQUIPMENT',
                title: 'Rotavator & Cultivator Set',
                description: 'High-quality soil preparation equipment. Can be attached to any 35+ HP tractor.',
                dailyRate: 1200,
                monthlyRate: 25000,
                location: { lat: 17.6868, lng: 83.2185, city: 'Visakhapatnam', district: 'Visakhapatnam', state: 'Andhra Pradesh' },
                contact: { name: 'Apparao', phone: '+91 43210 67890' },
                available: true,
                images: []
            },
            {
                category: 'TRANSPORT',
                title: 'Tata 407 - Crop Transport Vehicle',
                description: '2-ton capacity vehicle for crop transport. Driver included. Interstate permits.',
                dailyRate: 3500,
                monthlyRate: 70000,
                location: { lat: 15.4909, lng: 78.4865, city: 'Nandyal', district: 'Nandyal', state: 'Andhra Pradesh' },
                contact: { name: 'Hussain Basha', phone: '+91 32109 78901' },
                available: true,
                images: []
            },
            {
                category: 'IRRIGATION',
                title: 'Portable Drip Irrigation System',
                description: 'Complete drip irrigation kit for 5 acres. Includes pump and pipes.',
                dailyRate: 800,
                monthlyRate: 15000,
                location: { lat: 16.9891, lng: 82.2475, city: 'Rajahmundry', district: 'East Godavari', state: 'Andhra Pradesh' },
                contact: { name: 'Lakshmi Prasad', phone: '+91 21098 89012' },
                available: false,
                images: []
            }
        ];

        sampleRentals.forEach(rental => this.createRental(rental));
        console.log('🚜 Seed data created: 8 sample rentals added');
    }

    // Calculate distance between two coordinates (Haversine formula)
    _calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    _getLedger() {
        return JSON.parse(localStorage.getItem(RENTALS_KEY));
    }

    _saveLedger(ledger) {
        localStorage.setItem(RENTALS_KEY, JSON.stringify(ledger));
    }

    // Create new rental listing
    createRental(rentalData) {
        const ledger = this._getLedger();
        const rentalId = `RENT-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

        const rental = {
            id: rentalId,
            ...rentalData,
            createdAt: new Date().toISOString(),
            views: 0,
            inquiries: 0
        };

        ledger.push(rental);
        this._saveLedger(ledger);
        return rental;
    }

    // Get all rentals
    getAllRentals() {
        return this._getLedger();
    }

    // Get rental by ID
    getRentalById(rentalId) {
        return this._getLedger().find(r => r.id === rentalId);
    }

    // Search rentals within radius (with simulated delay for animation)
    async searchNearby(userLat, userLng, radiusKm = 200, category = null) {
        // Simulate network delay for Rapido-style animation
        await new Promise(resolve => setTimeout(resolve, 2500));

        const ledger = this._getLedger();

        let results = ledger.map(rental => {
            const distance = this._calculateDistance(
                userLat, userLng,
                rental.location.lat, rental.location.lng
            );
            return { ...rental, distance: Math.round(distance) };
        });

        // Filter by radius
        results = results.filter(r => r.distance <= radiusKm);

        // Filter by category if specified
        if (category && category !== 'ALL') {
            results = results.filter(r => r.category === category);
        }

        // Sort by distance
        results.sort((a, b) => a.distance - b.distance);

        return results;
    }

    // Get rentals by category
    getByCategory(category) {
        return this._getLedger().filter(r => r.category === category);
    }

    // Update rental availability
    updateAvailability(rentalId, available) {
        const ledger = this._getLedger();
        const rental = ledger.find(r => r.id === rentalId);
        if (rental) {
            rental.available = available;
            this._saveLedger(ledger);
        }
        return rental;
    }

    // Increment view count
    incrementViews(rentalId) {
        const ledger = this._getLedger();
        const rental = ledger.find(r => r.id === rentalId);
        if (rental) {
            rental.views = (rental.views || 0) + 1;
            this._saveLedger(ledger);
        }
    }

    // Record inquiry
    recordInquiry(rentalId) {
        const ledger = this._getLedger();
        const rental = ledger.find(r => r.id === rentalId);
        if (rental) {
            rental.inquiries = (rental.inquiries || 0) + 1;
            this._saveLedger(ledger);
        }
    }
}

export const rentalService = new RentalService();
