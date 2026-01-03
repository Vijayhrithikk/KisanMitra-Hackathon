// Delivery Logistics Service - Enhanced Supply Chain Management

const SHIPMENTS_KEY = 'kisanmitra_shipments';

class DeliveryService {
    constructor() {
        if (!localStorage.getItem(SHIPMENTS_KEY)) {
            localStorage.setItem(SHIPMENTS_KEY, JSON.stringify([]));
        }
    }

    // Simulated Delivery Partners
    getPartners() {
        return [
            { id: 'SELF', name: 'Self Delivery', en: 'Self/Farmer Delivery', te: 'స్వయం డెలివరీ', icon: '🚜', type: 'local' },
            { id: 'KISAN_EXPRESS', name: 'Kisan Express', en: 'Kisan Express (Rural)', te: 'కిసాన్ ఎక్స్‌ప్రెస్', icon: '🛵', type: 'rural' },
            { id: 'AGRISHIP', name: 'AgriShip', en: 'AgriShip (Wholesale)', te: 'అగ్రిషిప్', icon: '🚛', type: 'wholesale' },
            { id: 'INDIA_POST', name: 'India Post', en: 'India Post (Universal)', te: 'ఇండియా పోస్ట్', icon: '📦', type: 'universal' }
        ];
    }

    // Delivery types
    getDeliveryTypes() {
        return [
            { id: 'pickup', en: 'Self Pickup', te: 'స్వయంగా తీసుకెళ్ళండి', icon: '🏪', baseCharge: 0, days: 0 },
            { id: 'local', en: 'Local (Same District)', te: 'లోకల్ (అదే జిల్లా)', icon: '🛵', baseCharge: 100, days: 1 },
            { id: 'state', en: 'State Delivery', te: 'స్టేట్ డెలివరీ', icon: '🚛', baseCharge: 300, days: 3 },
            { id: 'national', en: 'Pan India', te: 'పాన్ ఇండియా', icon: '✈️', baseCharge: 800, days: 7 }
        ];
    }

    // Estimate delivery cost
    estimateCost(fromPincode, toPincode, weight, deliveryType = 'local') {
        const type = this.getDeliveryTypes().find(t => t.id === deliveryType);
        const baseCharge = type?.baseCharge || 0;

        // Weight-based pricing (₹ per kg after first 10kg)
        const extraWeight = Math.max(0, weight - 10);
        const weightCharge = extraWeight * 5;

        // Distance factor (mock - in real app use distance API)
        const distanceFactor = this._getDistanceFactor(fromPincode, toPincode);

        const total = Math.round((baseCharge + weightCharge) * distanceFactor);

        return {
            baseCharge,
            weightCharge,
            distanceFactor,
            total,
            estimatedDays: type?.days || 3
        };
    }

    _getDistanceFactor(from, to) {
        if (!from || !to) return 1;
        const fromPrefix = from.toString().substring(0, 2);
        const toPrefix = to.toString().substring(0, 2);

        if (fromPrefix === toPrefix) return 1;
        if (Math.abs(parseInt(fromPrefix) - parseInt(toPrefix)) <= 5) return 1.5;
        return 2;
    }

    // ===== ENHANCED SHIPMENT MANAGEMENT =====

    _getShipments() {
        return JSON.parse(localStorage.getItem(SHIPMENTS_KEY) || '[]');
    }

    _saveShipments(shipments) {
        localStorage.setItem(SHIPMENTS_KEY, JSON.stringify(shipments));
    }

    // Create a comprehensive shipment
    createShipment(orderId, fromAddress, toAddress, partner = 'KISAN_EXPRESS', weight = 10) {
        const shipments = this._getShipments();
        const trackingId = `TRK-${partner}-${Date.now().toString(36).toUpperCase()}`;

        const deliveryType = this._determineDeliveryType(fromAddress, toAddress);
        const estimate = this.estimateCost(fromAddress.pincode, toAddress.pincode, weight, deliveryType);

        const shipment = {
            trackingId,
            orderId,
            partner,
            partnerName: this.getPartners().find(p => p.id === partner)?.name || partner,
            status: 'CREATED',
            fromAddress,
            toAddress,
            weight,
            deliveryType,
            estimatedCost: estimate.total,
            estimatedDelivery: this._calculateETA(estimate.estimatedDays),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            events: [
                {
                    status: 'CREATED',
                    location: fromAddress.city || 'Origin',
                    message: 'Shipment created, awaiting pickup',
                    timestamp: new Date().toISOString()
                }
            ],
            route: this._generateRoute(fromAddress, toAddress)
        };

        shipments.push(shipment);
        this._saveShipments(shipments);

        console.log(`📦 Shipment ${trackingId} created for order ${orderId}`);
        return { success: true, shipment };
    }

    // Update shipment status with location
    updateShipmentStatus(trackingId, status, location, notes = '') {
        const shipments = this._getShipments();
        const index = shipments.findIndex(s => s.trackingId === trackingId);
        if (index === -1) return { success: false, error: 'Shipment not found' };

        shipments[index].status = status;
        shipments[index].currentLocation = location;
        shipments[index].updatedAt = new Date().toISOString();
        shipments[index].events.push({
            status,
            location,
            message: notes || this._getStatusMessage(status),
            timestamp: new Date().toISOString()
        });

        // Update ETA if in transit
        if (status === 'IN_TRANSIT') {
            const remaining = this._estimateRemainingDays(shipments[index].route, location);
            shipments[index].estimatedDelivery = this._calculateETA(remaining);
        }

        this._saveShipments(shipments);
        return { success: true, shipment: shipments[index] };
    }

    // Get shipment by tracking ID
    getShipment(trackingId) {
        return this._getShipments().find(s => s.trackingId === trackingId);
    }

    // Get shipments by order ID
    getShipmentsByOrder(orderId) {
        return this._getShipments().filter(s => s.orderId === orderId);
    }

    // Get full timeline/events for a shipment
    getShipmentTimeline(trackingId) {
        const shipment = this.getShipment(trackingId);
        if (!shipment) return null;

        return {
            trackingId,
            currentStatus: shipment.status,
            currentLocation: shipment.currentLocation || shipment.fromAddress.city,
            estimatedDelivery: shipment.estimatedDelivery,
            events: shipment.events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)),
            route: shipment.route
        };
    }

    // Track shipment (enhanced)
    trackShipment(trackingId) {
        const shipment = this.getShipment(trackingId);
        if (!shipment) {
            // Fallback for legacy orders
            return this._simulateTracking(trackingId);
        }
        return this.getShipmentTimeline(trackingId);
    }

    // ===== HELPER METHODS =====

    _determineDeliveryType(from, to) {
        if (!from?.pincode || !to?.pincode) return 'local';
        const fromPrefix = from.pincode.toString().substring(0, 2);
        const toPrefix = to.pincode.toString().substring(0, 2);

        if (fromPrefix === toPrefix) return 'local';
        if (from.state === to.state) return 'state';
        return 'national';
    }

    _calculateETA(days) {
        const date = new Date();
        date.setDate(date.getDate() + days);
        return date.toISOString().split('T')[0];
    }

    _generateRoute(from, to) {
        // Simulate route waypoints
        return [
            { name: from.city || 'Origin', type: 'PICKUP' },
            { name: `${from.district || 'District'} Hub`, type: 'HUB' },
            { name: to.state !== from.state ? `${to.state} Hub` : null, type: 'TRANSIT' },
            { name: `${to.district || 'District'} Hub`, type: 'HUB' },
            { name: to.city || 'Destination', type: 'DELIVERY' }
        ].filter(r => r.name);
    }

    _estimateRemainingDays(route, currentLocation) {
        if (!route || !currentLocation) return 2;
        const currentIndex = route.findIndex(r => r.name.includes(currentLocation));
        const remaining = route.length - currentIndex - 1;
        return Math.max(1, remaining);
    }

    _getStatusMessage(status) {
        const messages = {
            'CREATED': 'Shipment created, awaiting pickup',
            'PICKED_UP': 'Package picked up from farmer',
            'IN_TRANSIT': 'Package in transit to destination',
            'AT_HUB': 'Package arrived at distribution hub',
            'OUT_FOR_DELIVERY': 'Package out for delivery',
            'DELIVERED': 'Package delivered successfully',
            'FAILED': 'Delivery attempt failed'
        };
        return messages[status] || status;
    }

    _simulateTracking(trackingId) {
        // Fallback for orders without proper shipment records
        return {
            trackingId,
            currentStatus: 'IN_TRANSIT',
            events: [
                { status: 'CREATED', timestamp: new Date(Date.now() - 86400000).toISOString(), message: 'Shipment created' },
                { status: 'PICKED_UP', timestamp: new Date(Date.now() - 43200000).toISOString(), message: 'Picked up from farmer' },
                { status: 'IN_TRANSIT', timestamp: new Date().toISOString(), message: 'In transit to destination' }
            ],
            estimatedDelivery: new Date(Date.now() + 172800000).toISOString().split('T')[0]
        };
    }

    // Get all active shipments
    getActiveShipments() {
        return this._getShipments().filter(s =>
            !['DELIVERED', 'CANCELLED', 'FAILED'].includes(s.status)
        );
    }

    // Get farmer's shipments
    getFarmerShipments(farmerId) {
        // Note: This requires orderId->farmerId mapping from orderService
        return this._getShipments();
    }
}

export const deliveryService = new DeliveryService();

