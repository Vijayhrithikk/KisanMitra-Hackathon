"""
Flask API for KisanMitra Marketplace
Handles listings, orders, and users
Run on port 5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import database as db
import os
import uuid
import hmac
import hashlib
from datetime import datetime

# Razorpay SDK
try:
    import razorpay
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_RtY3DP4HEeNptd')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'f3rBpxA4k0eU5RRqsy2pnk88')
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    print("✅ Razorpay client initialized")
except ImportError:
    razorpay_client = None
    RAZORPAY_KEY_ID = None
    print("⚠️ Razorpay SDK not installed")

app = Flask(__name__)
CORS(app)

# ==================== LISTINGS ENDPOINTS ====================

@app.route('/api/listings', methods=['GET'])
def get_listings():
    """Get all listings, optionally filtered by status"""
    status = request.args.get('status')
    listings = db.get_all_listings(status=status)
    return jsonify(listings)

@app.route('/api/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Get a single listing by ID"""
    listing = db.get_listing_by_id(listing_id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@app.route('/api/listings', methods=['POST'])
def create_listing():
    """Create a new listing"""
    data = request.json
    listing = db.create_listing(data)
    return jsonify(listing), 201

@app.route('/api/listings/<listing_id>', methods=['PUT'])
def update_listing(listing_id):
    """Update a listing"""
    data = request.json
    success = db.update_listing(listing_id, data)
    if success:
        return jsonify({'message': 'Listing updated'})
    return jsonify({'error': 'Failed to update'}), 400

@app.route('/api/listings/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Delete a listing"""
    success = db.delete_listing(listing_id)
    if success:
        return jsonify({'message': 'Listing deleted'})
    return jsonify({'error': 'Failed to delete'}), 400

@app.route('/api/listings/farmer/<farmer_id>', methods=['GET'])
def get_farmer_listings(farmer_id):
    """Get all listings for a specific farmer by farmerId"""
    listings = db.get_farmer_listings(farmer_id)
    return jsonify(listings)

@app.route('/api/listings/phone/<phone>', methods=['GET'])
def get_farmer_listings_by_phone(phone):
    """Get all listings for a specific farmer by phone number - NEW ENDPOINT"""
    print(f"📞 API: Fetching listings for phone: {phone}")
    
    # Query MongoDB for listings with this farmerPhone
    from database import listings_collection, serialize_docs
    docs = listings_collection.find({'farmerPhone': phone}).sort('createdAt', -1)
    listings = serialize_docs(list(docs))
    
    print(f"✅ API: Found {len(listings)} listings for phone {phone}")
    return jsonify(listings)

# ==================== ORDERS ENDPOINTS ====================

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    data = request.json
    order = db.create_order(data)
    return jsonify(order), 201

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order by ID"""
    order = db.get_order_by_id(order_id)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/orders/buyer/<buyer_id>', methods=['GET'])
def get_buyer_orders(buyer_id):
    """Get all orders for a buyer"""
    orders = db.get_buyer_orders(buyer_id)
    return jsonify(orders)

@app.route('/api/orders/farmer/<farmer_id>', methods=['GET'])
def get_farmer_orders(farmer_id):
    """Get all orders for a farmer"""
    orders = db.get_farmer_orders(farmer_id)
    return jsonify(orders)

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    data = request.json
    status = data.get('status')
    additional = data.get('additional_data')
    success = db.update_order_status(order_id, status, additional)
    if success:
        return jsonify({'message': 'Status updated'})
    return jsonify({'error': 'Failed to update'}), 400

@app.route('/api/orders/<order_id>/payment', methods=['POST'])
def record_payment(order_id):
    """Record payment for an order"""
    data = request.json
    blockchain_hash = db.record_payment(order_id, data)
    return jsonify({'blockchainHash': blockchain_hash})

# ==================== GUEST ORDERS ====================

@app.route('/api/orders/guest', methods=['POST'])
def create_guest_order():
    """Create order for guest (non-registered buyer)"""
    try:
        data = request.json
        print(f"📦 Creating guest order: {data.get('buyer', {}).get('name', 'Unknown')}")
        
        # Generate a guest order
        order_data = {
            'buyerId': f"GUEST-{data['buyer']['phone'][-4:]}",
            'buyerName': data['buyer']['name'],
            'buyerPhone': data['buyer']['phone'],
            **{k: v for k, v in data.items() if k != 'buyer'}
        }
        order = db.create_order(order_data)
        print(f"✅ Order created: {order.get('orderId', 'Unknown')}")
        return jsonify(order), 201
    except Exception as e:
        print(f"❌ Guest order error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """Cancel an unpaid order (used when payment fails)"""
    try:
        data = request.json
        reason = data.get('reason', 'Payment cancelled')
        
        # Update order status to CANCELLED
        success = db.update_order_status(order_id, 'CANCELLED', {
            'cancellation_reason': reason,
            'cancelled_at': datetime.now().isoformat()
        })
        
        if success:
            print(f"❌ Order {order_id} cancelled: {reason}")
            return jsonify({'message': 'Order cancelled', 'orderId': order_id})
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        print(f"❌ Cancel order error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== USERS ENDPOINTS ====================

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    user = db.create_user(data)
    return jsonify(user), 201

@app.route('/api/users/phone/<phone>', methods=['GET'])
def get_user_by_phone(phone):
    """Get user by phone number"""
    user = db.get_user_by_phone(phone)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/buyers/check-phone/<phone>', methods=['GET'])
def check_phone_exists(phone):
    """Check if phone number is already registered"""
    user = db.get_user_by_phone(phone)
    if user:
        return jsonify({'exists': True, 'buyerType': user.get('type')})
    return jsonify({'exists': False})

# ==================== STATS ENDPOINTS ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get marketplace statistics"""
    stats = db.get_marketplace_stats()
    return jsonify(stats)

# ==================== TRANSACTIONS ENDPOINTS ====================

@app.route('/api/transactions/order/<order_id>', methods=['GET'])
def get_order_transactions(order_id):
    """Get all transactions for an order"""
    transactions = db.get_transactions_by_order(order_id)
    return jsonify(transactions)

@app.route('/api/transactions/search/<tx_hash>', methods=['GET'])
def search_transaction(tx_hash):
    """Search transaction by blockchain hash"""
    transaction = db.search_by_hash(tx_hash)
    if transaction:
        return jsonify(transaction)
    return jsonify({'error': 'Transaction not found'}), 404

# ==================== RAZORPAY PAYMENT ENDPOINTS ====================

@app.route('/api/payments/create-order', methods=['POST'])
def create_razorpay_order():
    """Create a Razorpay order for payment"""
    if not razorpay_client:
        return jsonify({'error': 'Payment gateway not configured'}), 500
    
    try:
        data = request.json
        amount = int(data.get('amount', 0))  # Amount in paise
        currency = data.get('currency', 'INR')
        receipt = data.get('receipt', f'order_{uuid.uuid4().hex[:8]}')
        notes = data.get('notes', {})
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Create Razorpay order
        order_data = {
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'notes': notes
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key_id': RAZORPAY_KEY_ID
        })
        
    except Exception as e:
        print(f"❌ Razorpay order creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/payments/verify', methods=['POST'])
def verify_razorpay_payment():
    """Verify Razorpay payment signature"""
    if not razorpay_client:
        return jsonify({'error': 'Payment gateway not configured'}), 500
    
    try:
        data = request.json
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        order_id = data.get('order_id')
        order_type = data.get('order_type', 'marketplace')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({'error': 'Missing payment details'}), 400
        
        # Verify signature
        msg = razorpay_order_id + "|" + razorpay_payment_id
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            return jsonify({'error': 'Invalid signature', 'verified': False}), 400
        
        # Payment verified - update order payment status AND order status
        if order_id:
            db.update_order_payment(order_id, {
                'status': 'PAID',
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'paid_at': datetime.now().isoformat()
            })
            # Also update order status from PAYMENT_PENDING to PLACED
            db.update_order_status(order_id, 'PLACED')
        
        return jsonify({
            'success': True,
            'verified': True,
            'payment_id': razorpay_payment_id,
            'message': 'Payment verified successfully'
        })
        
    except Exception as e:
        print(f"❌ Payment verification error: {e}")
        return jsonify({'error': str(e), 'verified': False}), 500

# ==================== RUN ====================

if __name__ == '__main__':
    print("🚀 KisanMitra Marketplace API starting on http://localhost:5000")
    print("📋 Endpoints:")
    print("   GET  /api/listings")
    print("   GET  /api/listings/phone/<phone>  ← NEW ENDPOINT")
    print("   POST /api/orders/guest")
    app.run(debug=True, port=5000)
