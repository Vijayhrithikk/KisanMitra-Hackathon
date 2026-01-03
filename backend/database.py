"""
Database Module for KisanMitra Marketplace
MongoDB collections: listings, orders, users, transactions
"""

import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import hashlib
import json

load_dotenv()

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kisanmitra')
client = MongoClient(MONGODB_URI)
db = client.kisanmitra

# Collections
listings_collection = db.listings
orders_collection = db.orders
users_collection = db.users
transactions_collection = db.transactions
farmers_collection = db.farmers  # For WhatsApp bot registration
crop_subscriptions_collection = db.crop_subscriptions  # For crop monitoring subscriptions

# Helper to convert ObjectId to string
def serialize_doc(doc):
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    return doc

def serialize_docs(docs):
    return [serialize_doc(doc) for doc in docs]


# ==================== LISTINGS ====================

def create_listing(listing_data):
    """Create a new crop listing"""
    listing = {
        'listingId': f"LIST-{datetime.now().strftime('%Y')}-{str(ObjectId())[-4:].upper()}",
        'crop': listing_data.get('crop'),
        'variety': listing_data.get('variety'),
        'quantity': listing_data.get('quantity'),
        'unit': listing_data.get('unit', 'Quintal'),
        'price': listing_data.get('price'),
        'farmerId': listing_data.get('farmerId'),
        'farmerName': listing_data.get('farmerName'),
        'farmerPhone': listing_data.get('farmerPhone'),
        'farmerVerified': listing_data.get('farmerVerified', False),
        'location': listing_data.get('location', {}),
        'contact': listing_data.get('contact', {}),
        'fertilizers': listing_data.get('fertilizers', ''),
        'pesticides': listing_data.get('pesticides', ''),
        'notes': listing_data.get('notes', ''),
        'images': listing_data.get('images', []),
        'status': 'LISTED',
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow()
    }
    
    # Generate content hash (SHA-256)
    content_str = json.dumps({
        'crop': listing['crop'],
        'variety': listing['variety'],
        'quantity': listing['quantity'],
        'price': listing['price'],
        'farmerId': listing['farmerId'],
        'timestamp': listing['createdAt'].isoformat()
    }, sort_keys=True)
    listing['metaHash'] = hashlib.sha256(content_str.encode()).hexdigest()
    
    result = listings_collection.insert_one(listing)
    listing['_id'] = str(result.inserted_id)
    return listing

def get_all_listings(status=None):
    """Get all listings, optionally filtered by status"""
    query = {}
    if status:
        query['status'] = status
    docs = listings_collection.find(query).sort('createdAt', -1)
    return serialize_docs(list(docs))

def get_listing_by_id(listing_id):
    """Get a single listing by listingId"""
    doc = listings_collection.find_one({'listingId': listing_id})
    return serialize_doc(doc)

def update_listing(listing_id, update_data):
    """Update a listing"""
    update_data['updatedAt'] = datetime.utcnow()
    result = listings_collection.update_one(
        {'listingId': listing_id},
        {'$set': update_data}
    )
    return result.modified_count > 0

def delete_listing(listing_id):
    """Delete a listing"""
    result = listings_collection.delete_one({'listingId': listing_id})
    return result.deleted_count > 0

def get_farmer_listings(farmer_id):
    """Get all listings by a farmer"""
    docs = listings_collection.find({'farmerId': farmer_id}).sort('createdAt', -1)
    return serialize_docs(list(docs))


# ==================== ORDERS ====================

def create_order(order_data):
    """Create a new order"""
    order = {
        'orderId': f"ORD-{str(ObjectId())[-8:].upper()}",
        'listingId': order_data.get('listingId'),
        'farmerId': order_data.get('farmerId'),
        'buyerId': order_data.get('buyerId'),
        'buyerName': order_data.get('buyerName'),
        'buyerPhone': order_data.get('buyerPhone'),
        'crop': order_data.get('crop'),
        'variety': order_data.get('variety'),
        'quantity': order_data.get('quantity'),
        'unit': order_data.get('unit'),
        'pricing': order_data.get('pricing', {}),
        'delivery': order_data.get('delivery', {}),
        'payment': {
            'status': 'PENDING',
            'transactions': []
        },
        'status': 'PENDING',
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow()
    }
    
    result = orders_collection.insert_one(order)
    order['_id'] = str(result.inserted_id)
    return order

def record_payment(order_id, payment_data):
    """Record payment and generate blockchain hash"""
    # Generate SHA-256 hash for blockchain
    tx_data = json.dumps({
        'orderId': order_id,
        'amount': payment_data.get('amount'),
        'method': payment_data.get('method'),
        'timestamp': datetime.utcnow().isoformat()
    }, sort_keys=True)
    blockchain_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    
    transaction = {
        'txnId': f"TXN-{str(ObjectId())[-8:].upper()}",
        'amount': payment_data.get('amount'),
        'method': payment_data.get('method'),
        'status': 'SUCCESS',
        'blockchainHash': blockchain_hash,
        'escrowStatus': 'HELD',
        'timestamp': datetime.utcnow()
    }
    
    result = orders_collection.update_one(
        {'orderId': order_id},
        {
            '$set': {
                'payment.status': 'ESCROWED',
                'status': 'PAID',
                'updatedAt': datetime.utcnow()
            },
            '$push': {'payment.transactions': transaction}
        }
    )
    
    # Also record in transactions collection
    transactions_collection.insert_one({
        'orderId': order_id,
        'type': 'ESCROW_DEPOSIT',
        **transaction
    })
    
    return blockchain_hash

def get_order_by_id(order_id):
    """Get a single order"""
    doc = orders_collection.find_one({'orderId': order_id})
    return serialize_doc(doc)

def get_buyer_orders(buyer_id):
    """Get all orders for a buyer"""
    docs = orders_collection.find({'buyerId': buyer_id}).sort('createdAt', -1)
    return serialize_docs(list(docs))

def get_farmer_orders(farmer_id):
    """Get all orders for a farmer"""
    docs = orders_collection.find({'farmerId': farmer_id}).sort('createdAt', -1)
    return serialize_docs(list(docs))

def update_order_status(order_id, status, additional_data=None):
    """Update order status"""
    update = {
        'status': status,
        'updatedAt': datetime.utcnow()
    }
    if additional_data:
        update.update(additional_data)
    
    result = orders_collection.update_one(
        {'orderId': order_id},
        {'$set': update}
    )
    return result.modified_count > 0


def update_order_payment(order_id, payment_data):
    """Update order payment status (for Razorpay)"""
    update = {
        'payment': payment_data,
        'updatedAt': datetime.utcnow()
    }
    result = orders_collection.update_one(
        {'orderId': order_id},
        {'$set': update}
    )
    return result.modified_count > 0


# ==================== USERS ====================

def create_user(user_data):
    """Create a new user (farmer or buyer)"""
    user = {
        'userId': f"USER-{str(ObjectId())[-8:].upper()}",
        'phone': user_data.get('phone'),
        'name': user_data.get('name'),
        'type': user_data.get('type', 'FARMER'),  # FARMER or BUYER
        'village': user_data.get('village'),
        'district': user_data.get('district'),
        'state': user_data.get('state'),
        'verified': False,
        'createdAt': datetime.utcnow()
    }
    
    result = users_collection.insert_one(user)
    user['_id'] = str(result.inserted_id)
    return user

def get_user_by_phone(phone):
    """Get user by phone number"""
    doc = users_collection.find_one({'phone': phone})
    return serialize_doc(doc)

def get_user_by_id(user_id):
    """Get user by userId"""
    doc = users_collection.find_one({'userId': user_id})
    return serialize_doc(doc)


# ==================== TRANSACTIONS (Blockchain) ====================

def get_transactions_by_order(order_id):
    """Get all blockchain transactions for an order"""
    docs = transactions_collection.find({'orderId': order_id}).sort('timestamp', -1)
    return serialize_docs(list(docs))

def search_by_hash(tx_hash):
    """Search for a transaction by blockchain hash"""
    doc = transactions_collection.find_one({'blockchainHash': tx_hash})
    return serialize_doc(doc)


# ==================== STATS ====================

def get_marketplace_stats():
    """Get marketplace statistics"""
    total_listings = listings_collection.count_documents({})
    active_listings = listings_collection.count_documents({'status': 'LISTED'})
    total_orders = orders_collection.count_documents({})
    completed_orders = orders_collection.count_documents({'status': 'COMPLETED'})
    total_users = users_collection.count_documents({})
    
    return {
        'totalListings': total_listings,
        'activeListings': active_listings,
        'totalOrders': total_orders,
        'completedOrders': completed_orders,
        'totalUsers': total_users
    }


# ==================== FARMERS (WhatsApp) ====================

def create_farmer(farmer_data):
    """Register a farmer from WhatsApp bot"""
    farmer = {
        'name': farmer_data.get('name'),
        'phone': farmer_data.get('phone'),
        'village': farmer_data.get('village'),
        'district': farmer_data.get('district'),
        'created_at': datetime.utcnow(),
        'source': 'whatsapp'
    }
    result = farmers_collection.insert_one(farmer)
    farmer['_id'] = str(result.inserted_id)
    return farmer

def get_farmer_by_phone(phone):
    """Get farmer by phone number"""
    # Clean phone number (remove whatsapp: prefix and + sign)
    clean_phone = phone.replace("whatsapp:", "").replace("+", "").strip()
    
    # Try multiple formats
    farmer = farmers_collection.find_one({'phone': clean_phone})
    if not farmer:
        farmer = farmers_collection.find_one({'phone': f"+{clean_phone}"})
    if not farmer:
        # Try last 10 digits
        if len(clean_phone) > 10:
            farmer = farmers_collection.find_one({'phone': {'$regex': clean_phone[-10:]}})
    
    return serialize_doc(farmer)

def update_farmer(phone, update_data):
    """Update farmer info"""
    clean_phone = phone.replace("whatsapp:", "").replace("+", "").strip()
    result = farmers_collection.update_one(
        {'phone': {'$regex': clean_phone[-10:]}},
        {'$set': update_data}
    )
    return result.modified_count > 0


# ==================== CROP SUBSCRIPTIONS ====================

def create_crop_subscription(subscription_data):
    """Create a new crop subscription for monitoring"""
    subscription = {
        'subscriptionId': f"SUB-{str(ObjectId())[-8:].upper()}",
        'farmerId': subscription_data.get('farmerId'),
        'farmerPhone': subscription_data.get('farmerPhone'),
        'crop': subscription_data.get('crop'),
        'sowingDate': subscription_data.get('sowingDate'),
        'areaAcres': subscription_data.get('areaAcres', 1.0),
        'previousCrop': subscription_data.get('previousCrop'),
        'location': {
            'name': subscription_data.get('locationName'),
            'lat': subscription_data.get('lat'),
            'lon': subscription_data.get('lon'),
            'district': subscription_data.get('district')
        },
        'soilType': subscription_data.get('soilType'),
        'irrigationType': subscription_data.get('irrigationType', 'canal'),
        'status': 'ACTIVE',  # ACTIVE, PAUSED, HARVESTED
        'alerts_enabled': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = crop_subscriptions_collection.insert_one(subscription)
    subscription['_id'] = str(result.inserted_id)
    return subscription


def get_farmer_subscriptions(farmer_id):
    """Get all subscriptions for a farmer"""
    docs = crop_subscriptions_collection.find({
        'farmerId': farmer_id,
        'status': {'$in': ['ACTIVE', 'PAUSED']}
    }).sort('created_at', -1)
    return serialize_docs(list(docs))


def get_subscription_by_id(subscription_id):
    """Get single subscription by ID"""
    doc = crop_subscriptions_collection.find_one({'subscriptionId': subscription_id})
    return serialize_doc(doc)


def update_subscription_status(subscription_id, status, additional_data=None):
    """Update subscription status"""
    update = {
        'status': status,
        'updated_at': datetime.utcnow()
    }
    if additional_data:
        update.update(additional_data)
    
    result = crop_subscriptions_collection.update_one(
        {'subscriptionId': subscription_id},
        {'$set': update}
    )
    return result.modified_count > 0


def delete_subscription(subscription_id):
    """Delete a subscription"""
    result = crop_subscriptions_collection.delete_one({'subscriptionId': subscription_id})
    return result.deleted_count > 0

