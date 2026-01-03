import CryptoJS from 'crypto-js';
import { transactionBlockchain } from './transactionBlockchain';

const ORDERS_KEY = 'kisanmitra_orders';

class OrderService {
    constructor() {
        if (!localStorage.getItem(ORDERS_KEY)) {
            localStorage.setItem(ORDERS_KEY, JSON.stringify([]));
            console.log('📦 Orders registry initialized');
        }
    }

    _getOrders() {
        return JSON.parse(localStorage.getItem(ORDERS_KEY) || '[]');
    }

    _saveOrders(orders) {
        localStorage.setItem(ORDERS_KEY, JSON.stringify(orders));
    }

    _generateOrderId() {
        return `ORD-${Date.now().toString(36).toUpperCase()}`;
    }

    // Create new order
    createOrder(orderData) {
        const orders = this._getOrders();

        const order = {
            orderId: this._generateOrderId(),
            listingId: orderData.listingId,
            farmerId: orderData.farmerId,
            buyerId: orderData.buyerId,

            // Product details
            crop: orderData.crop,
            variety: orderData.variety,
            quantity: orderData.quantity,
            unit: orderData.unit,

            // Pricing breakdown
            pricing: {
                unitPrice: orderData.unitPrice,
                subtotal: orderData.quantity * orderData.unitPrice,
                deliveryCharge: orderData.deliveryCharge || 0,
                platformFee: Math.round(orderData.quantity * orderData.unitPrice * 0.01), // 1%
                gst: 0, // Agricultural exemption
                total: 0
            },

            // Delivery info
            delivery: {
                type: orderData.deliveryType || 'pickup', // pickup, local, state
                address: orderData.deliveryAddress || null,
                distance: orderData.distance || 0,
                partner: orderData.deliveryPartner || 'Self',
                trackingId: null,
                estimatedDate: this._calculateDeliveryDate(orderData.deliveryType),
                actualDate: null,
                status: 'PENDING'
            },

            // Order status
            status: 'PENDING', // PENDING, CONFIRMED, PAID, SHIPPED, DELIVERED, COMPLETED, CANCELLED

            // Payment tracking
            payment: {
                status: 'PENDING', // PENDING, PARTIAL, PAID, RELEASED
                method: orderData.paymentMethod || 'UPI',
                transactions: [],
                farmerPayout: {
                    status: 'PENDING',
                    amount: 0,
                    upiId: null,
                    releaseDate: null
                }
            },

            // Communication
            messages: [],

            // Meta
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        // Calculate total
        order.pricing.total = order.pricing.subtotal + order.pricing.deliveryCharge + order.pricing.platformFee;

        // Calculate farmer payout
        order.payment.farmerPayout.amount = order.pricing.subtotal - order.pricing.platformFee;

        // Generate order hash
        order.orderHash = CryptoJS.SHA256(
            order.orderId + order.listingId + order.buyerId + order.createdAt
        ).toString().substring(0, 16);

        orders.push(order);
        this._saveOrders(orders);

        return { success: true, order };
    }

    _calculateDeliveryDate(type) {
        const days = type === 'pickup' ? 1 : type === 'local' ? 3 : 7;
        const date = new Date();
        date.setDate(date.getDate() + days);
        return date.toISOString().split('T')[0];
    }

    // Get order by ID
    getOrderById(orderId) {
        return this._getOrders().find(o => o.orderId === orderId);
    }

    // Get orders by farmer
    getFarmerOrders(farmerId) {
        return this._getOrders()
            .filter(o => o.farmerId === farmerId)
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    // Get orders by buyer
    getBuyerOrders(buyerId) {
        return this._getOrders()
            .filter(o => o.buyerId === buyerId)
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    // Update order status
    updateOrderStatus(orderId, status, note = '') {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        orders[index].status = status;
        orders[index].updatedAt = new Date().toISOString();

        if (note) {
            orders[index].messages.push({
                type: 'STATUS_UPDATE',
                message: note,
                timestamp: new Date().toISOString()
            });
        }

        this._saveOrders(orders);
        return { success: true, order: orders[index] };
    }

    // Update delivery status
    updateDeliveryStatus(orderId, deliveryStatus, trackingId = null) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        orders[index].delivery.status = deliveryStatus;
        if (trackingId) orders[index].delivery.trackingId = trackingId;
        if (deliveryStatus === 'DELIVERED') {
            orders[index].delivery.actualDate = new Date().toISOString().split('T')[0];
        }
        orders[index].updatedAt = new Date().toISOString();

        this._saveOrders(orders);
        return { success: true, order: orders[index] };
    }

    // Record payment - funds go to blockchain escrow
    recordPayment(orderId, transactionData) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        const order = orders[index];

        // Record escrow deposit on transaction blockchain
        let blockchainTx = null;
        try {
            blockchainTx = transactionBlockchain.recordEscrowDeposit(
                orderId,
                order.buyerId,
                transactionData.amount,
                transactionData.method || 'UPI'
            );
        } catch (error) {
            console.error('Blockchain escrow error:', error);
        }

        const txn = {
            txnId: blockchainTx?.txId || `TXN-${Date.now().toString(36).toUpperCase()}`,
            amount: transactionData.amount,
            method: transactionData.method,
            status: 'SUCCESS',
            blockchainHash: blockchainTx?.hash || null,
            escrowStatus: 'HELD', // Funds held in escrow until delivery
            timestamp: new Date().toISOString()
        };

        orders[index].payment.transactions.push(txn);

        // Calculate total paid
        const totalPaid = orders[index].payment.transactions
            .filter(t => t.status === 'SUCCESS')
            .reduce((sum, t) => sum + t.amount, 0);

        if (totalPaid >= orders[index].pricing.total) {
            orders[index].payment.status = 'ESCROWED'; // Changed from PAID to ESCROWED
            orders[index].status = 'PAID';
        } else if (totalPaid > 0) {
            orders[index].payment.status = 'PARTIAL';
        }

        orders[index].updatedAt = new Date().toISOString();
        this._saveOrders(orders);

        return { success: true, order: orders[index], transaction: txn, blockchainTx };
    }

    // Release farmer payout from blockchain escrow upon successful delivery
    releaseFarmerPayout(orderId, upiId, deliveryProof = {}) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        const order = orders[index];

        // Release from blockchain escrow
        let blockchainTx = null;
        try {
            blockchainTx = transactionBlockchain.releaseEscrowToFarmer(
                orderId,
                order.farmerId,
                { hash: deliveryProof.hash || CryptoJS.SHA256(orderId + Date.now()).toString() }
            );
        } catch (error) {
            console.error('Blockchain release error:', error);
            return { success: false, error: error.message };
        }

        orders[index].payment.farmerPayout = {
            status: 'COMPLETED',
            amount: blockchainTx?.amount || orders[index].payment.farmerPayout.amount,
            platformFee: blockchainTx?.platformFee || Math.round(order.pricing.subtotal * 0.01),
            upiId: upiId,
            blockchainTxId: blockchainTx?.txId,
            blockchainHash: blockchainTx?.hash,
            releaseDate: new Date().toISOString()
        };
        orders[index].payment.status = 'RELEASED';
        orders[index].status = 'COMPLETED';
        orders[index].updatedAt = new Date().toISOString();

        this._saveOrders(orders);
        return { success: true, order: orders[index], blockchainTx };
    }

    // Refund buyer from escrow (for cancelled orders)
    refundBuyer(orderId, reason = 'ORDER_CANCELLED') {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        // Refund from blockchain escrow
        let blockchainTx = null;
        try {
            blockchainTx = transactionBlockchain.refundFromEscrow(orderId, reason);
        } catch (error) {
            console.error('Blockchain refund error:', error);
            return { success: false, error: error.message };
        }

        orders[index].payment.status = 'REFUNDED';
        orders[index].payment.refund = {
            amount: blockchainTx?.amount,
            reason: reason,
            blockchainTxId: blockchainTx?.txId,
            blockchainHash: blockchainTx?.hash,
            refundDate: new Date().toISOString()
        };
        orders[index].status = 'CANCELLED';
        orders[index].updatedAt = new Date().toISOString();

        this._saveOrders(orders);
        return { success: true, order: orders[index], blockchainTx };
    }

    // Get escrow status for an order
    getEscrowStatus(orderId) {
        return transactionBlockchain.getEscrowStatus(orderId);
    }

    // Get all blockchain transactions for an order
    getOrderBlockchainTransactions(orderId) {
        return transactionBlockchain.getOrderTransactions(orderId);
    }

    // Get transaction blockchain stats
    getBlockchainStats() {
        return transactionBlockchain.getStats();
    }

    // Verify blockchain integrity
    verifyBlockchain() {
        return transactionBlockchain.verifyChain();
    }

    // Calculate pricing for order
    calculatePricing(listing, quantity, deliveryType) {
        const basePrice = listing.pricing?.basePrice || listing.price;
        let unitPrice = basePrice;

        // Apply bulk discount
        if (listing.pricing?.bulkDiscount) {
            const applicableDiscount = listing.pricing.bulkDiscount
                .filter(d => quantity >= d.qty)
                .sort((a, b) => b.qty - a.qty)[0];

            if (applicableDiscount) {
                unitPrice = basePrice * (1 - applicableDiscount.discount / 100);
            }
        }

        const subtotal = Math.round(quantity * unitPrice);
        const deliveryCharge = this._estimateDelivery(deliveryType);
        const platformFee = Math.round(subtotal * 0.01);
        const total = subtotal + deliveryCharge + platformFee;

        return {
            unitPrice: Math.round(unitPrice),
            originalPrice: basePrice,
            discountApplied: basePrice !== unitPrice,
            subtotal,
            deliveryCharge,
            platformFee,
            gst: 0,
            total,
            farmerGets: subtotal - platformFee
        };
    }

    _estimateDelivery(type) {
        const rates = { pickup: 0, local: 200, state: 500, national: 1000 };
        return rates[type] || 0;
    }

    // Get order statistics
    getOrderStats() {
        const orders = this._getOrders();
        return {
            total: orders.length,
            pending: orders.filter(o => o.status === 'PENDING').length,
            confirmed: orders.filter(o => o.status === 'CONFIRMED').length,
            processing: orders.filter(o => o.status === 'PROCESSING').length,
            shipped: orders.filter(o => o.status === 'SHIPPED').length,
            inTransit: orders.filter(o => o.status === 'IN_TRANSIT').length,
            delivered: orders.filter(o => o.status === 'DELIVERED').length,
            completed: orders.filter(o => o.status === 'COMPLETED').length,
            cancelled: orders.filter(o => o.status === 'CANCELLED').length,
            disputed: orders.filter(o => o.status === 'DISPUTED').length,
            totalValue: orders.reduce((sum, o) => sum + o.pricing.total, 0)
        };
    }

    // ===== NEW ORDER LIFECYCLE METHODS =====

    // Farmer confirms order
    confirmOrder(orderId) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (orders[index].status !== 'PENDING') {
            return { success: false, error: `Cannot confirm order in ${orders[index].status} status` };
        }

        orders[index].status = 'CONFIRMED';
        orders[index].confirmedAt = new Date().toISOString();
        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'STATUS_UPDATE',
            message: 'Order confirmed by farmer',
            timestamp: new Date().toISOString()
        });

        this._saveOrders(orders);
        console.log(`✅ Order ${orderId} confirmed by farmer`);
        return { success: true, order: orders[index] };
    }

    // Farmer rejects order
    rejectOrder(orderId, reason = 'Unable to fulfill') {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (!['PENDING', 'CONFIRMED'].includes(orders[index].status)) {
            return { success: false, error: `Cannot reject order in ${orders[index].status} status` };
        }

        orders[index].status = 'CANCELLED';
        orders[index].cancelledAt = new Date().toISOString();
        orders[index].cancellationReason = reason;
        orders[index].cancelledBy = 'FARMER';
        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'CANCELLED',
            message: `Order rejected by farmer: ${reason}`,
            timestamp: new Date().toISOString()
        });

        this._saveOrders(orders);
        console.log(`❌ Order ${orderId} rejected by farmer`);
        return { success: true, order: orders[index] };
    }

    // Farmer marks order as processing (preparing for shipment)
    markAsProcessing(orderId) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (!['CONFIRMED', 'PAID'].includes(orders[index].status)) {
            return { success: false, error: `Cannot process order in ${orders[index].status} status` };
        }

        orders[index].status = 'PROCESSING';
        orders[index].processingAt = new Date().toISOString();
        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'STATUS_UPDATE',
            message: 'Order being prepared for shipment',
            timestamp: new Date().toISOString()
        });

        this._saveOrders(orders);
        console.log(`📦 Order ${orderId} now processing`);
        return { success: true, order: orders[index] };
    }

    // Farmer ships order (creates shipment)
    shipOrder(orderId, shipmentDetails = {}) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (!['PAID', 'PROCESSING'].includes(orders[index].status)) {
            return { success: false, error: `Cannot ship order in ${orders[index].status} status` };
        }

        const trackingId = shipmentDetails.trackingId ||
            `TRK-${shipmentDetails.partner || 'SELF'}-${Date.now().toString(36).toUpperCase()}`;

        orders[index].status = 'SHIPPED';
        orders[index].shippedAt = new Date().toISOString();
        orders[index].delivery.status = 'SHIPPED';
        orders[index].delivery.trackingId = trackingId;
        orders[index].delivery.partner = shipmentDetails.partner || 'Self';
        orders[index].delivery.vehicleNumber = shipmentDetails.vehicleNumber || null;
        orders[index].delivery.driverPhone = shipmentDetails.driverPhone || null;
        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'SHIPPED',
            message: `Order shipped via ${shipmentDetails.partner || 'Self'}. Tracking: ${trackingId}`,
            timestamp: new Date().toISOString()
        });

        // Add shipment events
        orders[index].delivery.events = [
            { status: 'PICKED_UP', location: shipmentDetails.origin || 'Farmer Location', timestamp: new Date().toISOString() }
        ];

        this._saveOrders(orders);
        console.log(`🚛 Order ${orderId} shipped. Tracking: ${trackingId}`);
        return { success: true, order: orders[index], trackingId };
    }

    // Update shipment location (simulates GPS tracking)
    updateShipmentLocation(orderId, location, status = 'IN_TRANSIT') {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (status === 'IN_TRANSIT' && orders[index].status === 'SHIPPED') {
            orders[index].status = 'IN_TRANSIT';
        }

        orders[index].delivery.currentLocation = location;
        orders[index].delivery.lastUpdate = new Date().toISOString();
        orders[index].delivery.status = status;
        orders[index].delivery.events = orders[index].delivery.events || [];
        orders[index].delivery.events.push({
            status,
            location,
            timestamp: new Date().toISOString()
        });
        orders[index].updatedAt = new Date().toISOString();

        this._saveOrders(orders);
        return { success: true, order: orders[index] };
    }

    // Buyer confirms delivery
    buyerConfirmDelivery(orderId, rating = 5, feedback = '') {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (!['SHIPPED', 'IN_TRANSIT', 'DELIVERED'].includes(orders[index].status)) {
            return { success: false, error: `Cannot confirm delivery for order in ${orders[index].status} status` };
        }

        orders[index].status = 'DELIVERED';
        orders[index].delivery.status = 'DELIVERED';
        orders[index].delivery.actualDate = new Date().toISOString().split('T')[0];
        orders[index].deliveredAt = new Date().toISOString();
        orders[index].buyerConfirmed = true;
        orders[index].buyerRating = rating;
        orders[index].buyerFeedback = feedback;
        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'DELIVERED',
            message: `Delivery confirmed by buyer. Rating: ${rating}/5`,
            timestamp: new Date().toISOString()
        });

        this._saveOrders(orders);
        console.log(`✅ Order ${orderId} delivery confirmed by buyer`);
        return { success: true, order: orders[index] };
    }

    // Raise a dispute (locks escrow)
    raiseDispute(orderId, raisedBy, reason, evidence = []) {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        const validStatuses = ['PAID', 'PROCESSING', 'SHIPPED', 'IN_TRANSIT', 'DELIVERED'];
        if (!validStatuses.includes(orders[index].status)) {
            return { success: false, error: `Cannot raise dispute for order in ${orders[index].status} status` };
        }

        const disputeId = `DISP-${Date.now().toString(36).toUpperCase()}`;

        orders[index].previousStatus = orders[index].status;
        orders[index].status = 'DISPUTED';
        orders[index].dispute = {
            disputeId,
            raisedBy, // 'BUYER' or 'FARMER'
            reason,
            evidence,
            status: 'OPEN',
            raisedAt: new Date().toISOString(),
            resolution: null
        };
        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'DISPUTE_RAISED',
            message: `Dispute raised by ${raisedBy}: ${reason}`,
            timestamp: new Date().toISOString()
        });

        this._saveOrders(orders);
        console.log(`⚠️ Dispute ${disputeId} raised for order ${orderId}`);
        return { success: true, order: orders[index], disputeId };
    }

    // Resolve dispute (admin action)
    resolveDispute(orderId, resolution, refundAmount = 0, notes = '') {
        const orders = this._getOrders();
        const index = orders.findIndex(o => o.orderId === orderId);
        if (index === -1) return { success: false, error: 'Order not found' };

        if (orders[index].status !== 'DISPUTED') {
            return { success: false, error: 'Order is not in disputed status' };
        }

        orders[index].dispute.status = 'RESOLVED';
        orders[index].dispute.resolution = resolution; // 'REFUND_BUYER', 'RELEASE_TO_FARMER', 'PARTIAL_REFUND'
        orders[index].dispute.refundAmount = refundAmount;
        orders[index].dispute.notes = notes;
        orders[index].dispute.resolvedAt = new Date().toISOString();

        // Handle resolution
        if (resolution === 'REFUND_BUYER') {
            orders[index].status = 'CANCELLED';
            orders[index].payment.status = 'REFUNDED';
        } else if (resolution === 'RELEASE_TO_FARMER') {
            orders[index].status = 'COMPLETED';
            orders[index].payment.status = 'RELEASED';
        } else if (resolution === 'PARTIAL_REFUND') {
            orders[index].status = 'COMPLETED';
            orders[index].payment.status = 'PARTIAL_RELEASED';
        }

        orders[index].updatedAt = new Date().toISOString();
        orders[index].messages.push({
            type: 'DISPUTE_RESOLVED',
            message: `Dispute resolved: ${resolution}. ${notes}`,
            timestamp: new Date().toISOString()
        });

        this._saveOrders(orders);
        console.log(`✅ Dispute for order ${orderId} resolved: ${resolution}`);
        return { success: true, order: orders[index] };
    }

    // Get all orders (for admin/bank)
    getAllOrders() {
        return this._getOrders().sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    // Get orders by status
    getOrdersByStatus(status) {
        return this._getOrders().filter(o => o.status === status);
    }

    // Get disputed orders
    getDisputedOrders() {
        return this._getOrders().filter(o => o.status === 'DISPUTED');
    }
}

export const orderService = new OrderService();

