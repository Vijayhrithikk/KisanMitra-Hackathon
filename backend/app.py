import sys
import sys
import os
# Add local lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
import requests
import uuid
import tempfile # Added for /train functionality, though not used in the provided snippet, it's good practice for file handling.
from PyPDF2 import PdfReader # For PDF processing without LangChain
import re # For text cleaning/splitting
import hmac
import hashlib

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

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "llama3.2"
CHROMA_PATH = "./chroma_db"

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="kisanmitra_knowledge")

def get_embedding(text):
    response = requests.post(OLLAMA_EMBED_URL, json={
        "model": MODEL_NAME,
        "prompt": text
    })
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        print(f"Error getting embedding: {response.status_code} - {response.text}")
        return None

from flask import Response, stream_with_context

# Hardcoded responses for instant feedback (Zero Latency)
GREETING_RESPONSES = {
    "hi": "Namaskaram! I am KisanMitra. How can I help you with your farming today?",
    "hello": "Namaskaram! I am KisanMitra. How can I help you with your farming today?",
    "namaste": "Namaste! I am KisanMitra. How can I help you?",
    "namaskaram": "Namaskaram! I am KisanMitra. How can I help you?",
    "help": "I can help you with modern farming techniques, crop advice, and weather updates. What do you need?",
    "start": "Let's get started! Ask me anything about agriculture."
}

def query_ollama(prompt):
    # Use 127.0.0.1 to avoid localhost DNS lookup delay
    url = OLLAMA_API_URL.replace("localhost", "127.0.0.1")
    try:
        response = requests.post(url, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True,
            "keep_alive": -1 # Keep model loaded indefinitely
        }, stream=True)
        
        if response.status_code == 200:
            def generate():
                for line in response.iter_lines():
                    if line:
                        import json
                        try:
                            json_response = json.loads(line)
                            if 'response' in json_response:
                                yield json_response['response']
                        except json.JSONDecodeError:
                            continue
            return generate()
        else:
            return None
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return None

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # 1. Check for Greetings (Zero Latency Cache)
    lower_input = user_input.lower()
    if lower_input in GREETING_RESPONSES:
        # Return immediately as a stream (to keep frontend logic consistent)
        def generate_static():
            yield GREETING_RESPONSES[lower_input]
        return Response(stream_with_context(generate_static()), content_type='text/plain')
    
    # 2. Generate Embedding for User Input
    # Use 127.0.0.1 for embedding as well
    embed_url = OLLAMA_EMBED_URL.replace("localhost", "127.0.0.1")
    user_embedding = None
    try:
        emb_response = requests.post(embed_url, json={
            "model": MODEL_NAME,
            "prompt": user_input,
            "keep_alive": -1
        })
        if emb_response.status_code == 200:
            user_embedding = emb_response.json()["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
    
    context_text = ""
    if user_embedding:
        # 3. Query ChromaDB for Context
        results = collection.query(
            query_embeddings=[user_embedding],
            n_results=3,
            include=['documents']
        )
        
        if results['documents'] and results['documents'][0]:
            context_text = "\n".join(results['documents'][0])
    
    # 4. Construct Prompt with Context
    system_prompt = """You are KisanMitra, an expert agricultural assistant for Indian farmers. 
    Answer the user's question based on the following context. 
    If the answer is not in the context, use your general knowledge but mention that it's general advice.
    Keep answers concise and helpful."""
    
    full_prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nUser: {user_input}\nAnswer:"

    # 5. Get Response from Ollama (Streamed)
    generator = query_ollama(full_prompt)
    
    if generator:
        return Response(stream_with_context(generator), content_type='text/plain')
    else:
        return jsonify({"error": "Error communicating with AI"}), 500

@app.route('/train', methods=['POST'])
def train():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    temp_dir = None
    temp_path = None
    try:
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        content = ""
        if file.filename.endswith('.pdf'):
            reader = PdfReader(temp_path)
            for page in reader.pages:
                content += page.extract_text() + "\n"
        else: # Assume text file
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Simple chunking (split by paragraphs or sentences)
        # Using a more robust split than just '\n\n' for better chunking
        chunks = re.split(r'\n\s*\n|\.\s+|\?\s+|!\s+', content)
        chunks = [c.strip() for c in chunks if c.strip()]
        
        # Further split large chunks if they are still too big
        final_chunks = []
        chunk_size_limit = 1000 # Approximate character limit for a chunk
        for chunk in chunks:
            if len(chunk) > chunk_size_limit:
                sub_chunks = [chunk[i:i+chunk_size_limit] for i in range(0, len(chunk), chunk_size_limit)]
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)

        ids = []
        embeddings = []
        documents = []
        
        for i, chunk in enumerate(final_chunks):
            emb = get_embedding(chunk)
            if emb:
                ids.append(f"{file.filename}_{i}_{uuid.uuid4()}")
                embeddings.append(emb)
                documents.append(chunk)
        
        if ids:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents
            )
            return jsonify({"message": f"Successfully trained on {len(ids)} chunks from {file.filename}"})
        else:
            return jsonify({"error": "Failed to generate embeddings or no valid chunks found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)

def warmup_model():
    print("Warming up Ollama model...")
    try:
        # Send a tiny prompt to load the model into memory
        requests.post(OLLAMA_API_URL, json={
            "model": MODEL_NAME,
            "prompt": "hi",
            "stream": False
        })
        print("Model warmed up and ready.")
    except Exception as e:
        print(f"Warmup failed: {e}")


# ==================== MARKETPLACE API ====================
# Import database module
try:
    from database import (
        create_listing, get_all_listings, get_listing_by_id, update_listing, 
        delete_listing, get_farmer_listings,
        create_order, record_payment, get_order_by_id, get_buyer_orders, 
        get_farmer_orders, update_order_status,
        create_user, get_user_by_phone, get_user_by_id,
        get_transactions_by_order, search_by_hash,
        get_marketplace_stats,
        create_farmer, get_farmer_by_phone, update_farmer
    )
    MARKETPLACE_ENABLED = True
    print("✅ Marketplace database connected")
except Exception as e:
    MARKETPLACE_ENABLED = False
    print(f"⚠️ Marketplace database not available: {e}")


# --- Farmers API (WhatsApp Bot) ---
@app.route('/api/farmers', methods=['POST'])
def api_create_farmer():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    farmer = create_farmer(data)
    return jsonify({"success": True, "farmer": farmer}), 201

@app.route('/api/farmers/phone/<phone>', methods=['GET'])
def api_get_farmer_by_phone(phone):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    farmer = get_farmer_by_phone(phone)
    if farmer:
        return jsonify({"success": True, "farmer": farmer})
    return jsonify({"success": False, "farmer": None}), 404


# --- Listings API ---
@app.route('/api/listings', methods=['GET'])
def api_get_listings():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    status = request.args.get('status')
    listings = get_all_listings(status)
    return jsonify(listings)

@app.route('/api/listings/<listing_id>', methods=['GET'])
def api_get_listing(listing_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    listing = get_listing_by_id(listing_id)
    if listing:
        return jsonify(listing)
    return jsonify({"error": "Listing not found"}), 404

@app.route('/api/listings', methods=['POST'])
def api_create_listing():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    listing = create_listing(data)
    return jsonify(listing), 201

@app.route('/api/listings/<listing_id>', methods=['PUT'])
def api_update_listing(listing_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    success = update_listing(listing_id, data)
    if success:
        return jsonify({"message": "Listing updated"})
    return jsonify({"error": "Update failed"}), 400

@app.route('/api/listings/<listing_id>', methods=['DELETE'])
def api_delete_listing(listing_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    success = delete_listing(listing_id)
    if success:
        return jsonify({"message": "Listing deleted"})
    return jsonify({"error": "Delete failed"}), 400

@app.route('/api/listings/farmer/<farmer_id>', methods=['GET'])
def api_get_farmer_listings(farmer_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    listings = get_farmer_listings(farmer_id)
    return jsonify(listings)


# --- Orders API ---
@app.route('/api/orders', methods=['GET'])
def api_get_orders():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    buyer_id = request.args.get('buyerId')
    farmer_id = request.args.get('farmerId')
    if buyer_id:
        orders = get_buyer_orders(buyer_id)
    elif farmer_id:
        orders = get_farmer_orders(farmer_id)
    else:
        return jsonify({"error": "buyerId or farmerId required"}), 400
    return jsonify(orders)

@app.route('/api/orders/<order_id>', methods=['GET'])
def api_get_order(order_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    order = get_order_by_id(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

@app.route('/api/orders', methods=['POST'])
def api_create_order():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    order = create_order(data)
    return jsonify(order), 201

@app.route('/api/orders/<order_id>/pay', methods=['POST'])
def api_record_payment(order_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    blockchain_hash = record_payment(order_id, data)
    return jsonify({
        "message": "Payment recorded",
        "blockchainHash": blockchain_hash
    })

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def api_update_order_status(order_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    status = data.get('status')
    success = update_order_status(order_id, status, data)
    if success:
        return jsonify({"message": "Order status updated"})
    return jsonify({"error": "Update failed"}), 400


# --- Users API ---
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    data = request.json
    # Check if user exists
    existing = get_user_by_phone(data.get('phone'))
    if existing:
        return jsonify(existing)  # Return existing user
    user = create_user(data)
    return jsonify(user), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404


# --- Transactions/Verification API ---
@app.route('/api/transactions/<order_id>', methods=['GET'])
def api_get_transactions(order_id):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    txs = get_transactions_by_order(order_id)
    return jsonify(txs)

@app.route('/api/verify/<tx_hash>', methods=['GET'])
def api_verify_hash(tx_hash):
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    tx = search_by_hash(tx_hash)
    if tx:
        return jsonify({"verified": True, "transaction": tx})
    return jsonify({"verified": False}), 404


# --- Stats API ---
@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    if not MARKETPLACE_ENABLED:
        return jsonify({"error": "Database not connected"}), 503
    stats = get_marketplace_stats()
    return jsonify(stats)


# Guest Order Endpoint
@app.route('/api/orders/guest', methods=['POST'])
def create_guest_order():
    try:
        data = request.json
        from datetime import datetime
        import random
        
        order_id = f"GO-{datetime.now().year}-{random.randint(1000, 9999)}"
        
        order = {
            'orderId': order_id,
            'type': data.get('type', 'guest'),
            'items': data.get('items', []),
            'buyer': data.get('buyer', {}),
            'totalAmount': data.get('totalAmount', 0),
            'status': 'PLACED',
            'createdAt': datetime.utcnow().isoformat() + 'Z'
        }
        
        print(f"Guest order placed: {order_id}")
        print(f"Buyer: {order['buyer'].get('name')} - {order['buyer'].get('phone')}")
        
        return jsonify(order), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== MARKETPLACE API ROUTES ====================

@app.route('/api/listings/phone/<phone>', methods=['GET'])
def get_listings_by_phone(phone):
    """Get all listings for a specific farmer by phone number"""
    try:
        from database import listings_collection, serialize_docs
        print(f"📞 API: Fetching listings for phone: {phone}")
        docs = listings_collection.find({'farmerPhone': phone}).sort('createdAt', -1)
        listings = serialize_docs(list(docs))
        print(f"✅ API: Found {len(listings)} listings for phone {phone}")
        return jsonify(listings)
    except Exception as e:
        print(f"❌ Error fetching listings: {e}")
        return jsonify([])  # Return empty array instead of error

@app.route('/api/orders/farmer/<farmer_id>', methods=['GET'])
def get_farmer_orders_api(farmer_id):
    """Get all orders for a farmer - searches by farmerId, farmerPhone, and listing association"""
    try:
        from database import orders_collection, listings_collection, serialize_docs
        print(f"📦 API: Fetching orders for farmer: {farmer_id}")
        
        # First, get all listings by this farmer (by phone or ID)
        farmer_listings = list(listings_collection.find({
            '$or': [
                {'farmerId': farmer_id},
                {'farmerPhone': farmer_id}
            ]
        }))
        listing_ids = [l.get('listingId') for l in farmer_listings]
        print(f"📋 Found {len(listing_ids)} listings for farmer")
        
        # Query orders by: farmerId, farmerPhone, OR listingId
        query = {
            '$or': [
                {'farmerId': farmer_id},
                {'farmerPhone': farmer_id}
            ]
        }
        
        # Also include orders for this farmer's listings
        if listing_ids:
            query['$or'].append({'listingId': {'$in': listing_ids}})
        
        docs = orders_collection.find(query).sort('createdAt', -1)
        orders = serialize_docs(list(docs))
        
        # Enrich orders with listing info if missing crop/variety
        for order in orders:
            if not order.get('crop') and order.get('listingId'):
                listing = next((l for l in farmer_listings if l.get('listingId') == order.get('listingId')), None)
                if listing:
                    order['crop'] = listing.get('crop')
                    order['variety'] = listing.get('variety')
        
        print(f"✅ API: Found {len(orders)} orders for farmer {farmer_id}")
        return jsonify(orders)
    except Exception as e:
        print(f"❌ Error fetching orders: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])  # Return empty array instead of error

# ==================== USER AUTHENTICATION ====================

@app.route('/api/users/phone/<phone>', methods=['GET'])
def get_user_by_phone(phone):
    """Check if farmer exists in database by phone number"""
    try:
        from database import db
        users_collection = db.users
        
        print(f"📞 Checking if farmer exists for phone: {phone}")
        user = users_collection.find_one({'phone': phone})
        
        if user:
            from database import serialize_docs
            user_data = serialize_docs([user])[0]
            print(f"✅ Found farmer: {user_data.get('name', 'Unknown')}")
            return jsonify({'exists': True, 'user': user_data})
        else:
            print(f"❌ No farmer found for phone: {phone}")
            return jsonify({'exists': False})
    except Exception as e:
        print(f"❌ Error checking farmer: {e}")
        return jsonify({'exists': False, 'error': str(e)})

@app.route('/api/listings', methods=['GET'])
def get_all_listings_route():
    """Get all marketplace listings"""
    try:
        from database import listings_collection, serialize_docs
        status = request.args.get('status')
        query = {'status': status} if status else {}
        docs = listings_collection.find(query).sort('createdAt', -1)
        return jsonify(serialize_docs(list(docs)))
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify([])

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
            'amount': amount,  # Amount in paise (100 paise = 1 INR)
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
        order_id = data.get('order_id')  # Our internal order ID
        order_type = data.get('order_type', 'marketplace')  # marketplace or rental
        
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
        
        # Payment verified - update order status in database
        if order_id and order_type == 'marketplace':
            orders_collection.update_one(
                {'orderId': order_id},
                {'$set': {
                    'payment.status': 'PAID',
                    'payment.razorpay_payment_id': razorpay_payment_id,
                    'payment.razorpay_order_id': razorpay_order_id,
                    'payment.paid_at': datetime.now().isoformat()
                }}
            )
        elif order_id and order_type == 'rental':
            rentals_collection.update_one(
                {'rentalId': order_id},
                {'$set': {
                    'payment.status': 'PAID',
                    'payment.razorpay_payment_id': razorpay_payment_id,
                    'payment.razorpay_order_id': razorpay_order_id,
                    'payment.paid_at': datetime.now().isoformat()
                }}
            )
        
        return jsonify({
            'success': True,
            'verified': True,
            'payment_id': razorpay_payment_id,
            'message': 'Payment verified successfully'
        })
        
    except Exception as e:
        print(f"❌ Payment verification error: {e}")
        return jsonify({'error': str(e), 'verified': False}), 500


@app.route('/api/payments/status/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """Get payment status from Razorpay"""
    if not razorpay_client:
        return jsonify({'error': 'Payment gateway not configured'}), 500
    
    try:
        payment = razorpay_client.payment.fetch(payment_id)
        return jsonify({
            'success': True,
            'payment': {
                'id': payment['id'],
                'amount': payment['amount'],
                'currency': payment['currency'],
                'status': payment['status'],
                'method': payment.get('method'),
                'captured': payment.get('captured', False)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("")
    print("="*60)
    print("🚀 KisanMitra Backend API (Chat + Marketplace)")
    print("="*60)
    print("📍 Port: 5000")
    print("📋 Marketplace Endpoints Added:")
    print("   GET /api/listings/phone/<phone>")
    print("   GET /api/orders/farmer/<farmer_id>")
    print("="*60)
    print("")
    app.run(debug=True, port=5000)
