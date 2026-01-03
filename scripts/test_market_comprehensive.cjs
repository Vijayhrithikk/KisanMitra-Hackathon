const CryptoJS = require('crypto-js');

// Mock LocalStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: (key) => store[key] || null,
        setItem: (key, value) => store[key] = value.toString(),
        clear: () => store = {}
    };
})();
global.localStorage = localStorageMock;

// --- MarketService Code (Copied for Standalone Test) ---
const LEDGER_KEY = 'kisanmitra_market_ledger';

class MarketService {
    constructor() {
        if (!localStorage.getItem(LEDGER_KEY)) {
            localStorage.setItem(LEDGER_KEY, JSON.stringify([]));
        }
    }

    _canonicalize(data) {
        const sortedKeys = Object.keys(data).sort();
        const canonicalObj = {};
        sortedKeys.forEach(key => {
            canonicalObj[key] = data[key];
        });
        return JSON.stringify(canonicalObj);
    }

    _getLedger() {
        return JSON.parse(localStorage.getItem(LEDGER_KEY));
    }

    _appendToLedger(record) {
        const ledger = this._getLedger();
        ledger.push(record);
        localStorage.setItem(LEDGER_KEY, JSON.stringify(ledger));
        return record;
    }

    createListing(listingData) {
        const timestamp = new Date().toISOString();
        const listingId = `LIST-${new Date().getFullYear()}-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`;

        const metadata = {
            listingId,
            farmerId: 'FARMER-DEMO-001',
            ...listingData,
            createdAt: timestamp,
            status: 'LISTED'
        };

        const canonicalJson = this._canonicalize(metadata);
        const hash = CryptoJS.SHA256(canonicalJson).toString();
        const ipfsCid = `ipfs://bafy${hash.substring(0, 16)}...`;

        const ledgerRecord = {
            type: 'LISTING_CREATED',
            listingId,
            ipfsCid,
            metaHash: hash,
            data: metadata,
            timestamp,
            txHash: '0x' + CryptoJS.SHA256(timestamp + listingId).toString()
        };

        this._appendToLedger(ledgerRecord);
        return { success: true, listingId, hash, ipfsCid, txHash: ledgerRecord.txHash };
    }

    getListings() {
        const ledger = this._getLedger();
        const listings = {};

        ledger.forEach(record => {
            if (record.type === 'LISTING_CREATED') {
                listings[record.listingId] = { ...record.data, txHash: record.txHash, metaHash: record.metaHash };
            } else if (record.type === 'LISTING_UPDATED') {
                if (listings[record.listingId]) {
                    listings[record.listingId] = {
                        ...listings[record.listingId],
                        ...record.data,
                        txHash: record.txHash,
                        metaHash: record.metaHash
                    };
                }
            } else if (record.type === 'LISTING_SOLD') {
                if (listings[record.listingId]) {
                    listings[record.listingId].status = 'SOLD';
                    listings[record.listingId].buyerHash = record.buyerHash;
                    listings[record.listingId].soldAt = record.timestamp;
                }
            }
        });
        return Object.values(listings).reverse();
    }

    getListingById(listingId) {
        const listings = this.getListings();
        return listings.find(l => l.listingId === listingId);
    }

    updateListing(listingId, newData, farmerId) {
        const listing = this.getListingById(listingId);
        if (!listing) throw new Error('Listing not found');
        if (listing.farmerId !== farmerId) throw new Error('Unauthorized: Only the owner can edit');
        if (listing.status !== 'LISTED') throw new Error('Cannot edit: Listing is already sold');

        const timestamp = new Date().toISOString();
        const updatedMetadata = { ...listing, ...newData, updatedAt: timestamp };

        delete updatedMetadata.txHash;
        delete updatedMetadata.metaHash;
        delete updatedMetadata.buyerHash;
        delete updatedMetadata.soldAt;

        const canonicalJson = this._canonicalize(updatedMetadata);
        const hash = CryptoJS.SHA256(canonicalJson).toString();
        const ipfsCid = `ipfs://bafy${hash.substring(0, 16)}...`;

        const ledgerRecord = {
            type: 'LISTING_UPDATED',
            listingId,
            ipfsCid,
            metaHash: hash,
            data: updatedMetadata,
            timestamp,
            txHash: '0x' + CryptoJS.SHA256(timestamp + listingId + 'UPDATE').toString()
        };

        this._appendToLedger(ledgerRecord);
        return { success: true, txHash: ledgerRecord.txHash };
    }

    markAsSold(listingId, buyerDetails, transactionDocs, farmerId) {
        const listing = this.getListingById(listingId);
        if (!listing) throw new Error('Listing not found');
        if (listing.farmerId !== farmerId) throw new Error('Unauthorized: Only the owner can mark as sold');

        if (!transactionDocs || transactionDocs.length === 0) {
            throw new Error('Transaction documents are required to mark as sold');
        }

        const timestamp = new Date().toISOString();
        const sensitiveData = { buyer: buyerDetails, docs: transactionDocs };
        const encryptedData = Buffer.from(JSON.stringify(sensitiveData)).toString('base64');
        const buyerHash = CryptoJS.SHA256(JSON.stringify(sensitiveData)).toString();

        const ledgerRecord = {
            type: 'LISTING_SOLD',
            listingId,
            buyerHash,
            encryptedData,
            timestamp,
            txHash: '0x' + CryptoJS.SHA256(timestamp + listingId + 'SOLD').toString()
        };

        this._appendToLedger(ledgerRecord);
        return { success: true, txHash: ledgerRecord.txHash };
    }
}

// --- TEST SUITE ---
const service = new MarketService();
const OWNER_ID = 'FARMER-DEMO-001';
const HACKER_ID = 'HACKER-007';

console.log('--- STARTING RIGOROUS MARKET TEST ---');

// 1. Create Listing
console.log('\n1. Creating Listing...');
const listingData = { crop: 'Rice', variety: 'Sona Masoori', quantity: '100', price: '3000' };
const createResult = service.createListing(listingData);
console.log(`✅ Listing Created: ${createResult.listingId}`);

// 2. Test Unauthorized Edit (Hacker)
console.log('\n2. Testing Unauthorized Edit...');
try {
    service.updateListing(createResult.listingId, { price: '100' }, HACKER_ID);
    console.error('❌ FAIL: Hacker was able to edit listing!');
} catch (e) {
    console.log(`✅ PASS: Hacker blocked: ${e.message}`);
}

// 3. Test Authorized Edit (Owner)
console.log('\n3. Testing Authorized Edit (Price Change)...');
try {
    service.updateListing(createResult.listingId, { price: '3500' }, OWNER_ID);
    const updated = service.getListingById(createResult.listingId);
    if (updated.price === '3500') console.log('✅ PASS: Owner updated price successfully');
    else console.error('❌ FAIL: Price did not update');
} catch (e) {
    console.error(`❌ FAIL: Owner edit failed: ${e.message}`);
}

// 4. Test Mark Sold WITHOUT Docs
console.log('\n4. Testing Mark Sold WITHOUT Docs...');
try {
    service.markAsSold(createResult.listingId, { name: 'Buyer' }, null, OWNER_ID);
    console.error('❌ FAIL: Sold without docs!');
} catch (e) {
    console.log(`✅ PASS: Blocked missing docs: ${e.message}`);
}

// 5. Test Mark Sold WITH Docs (Owner)
console.log('\n5. Testing Mark Sold WITH Docs...');
try {
    const docs = ['invoice.pdf'];
    service.markAsSold(createResult.listingId, { name: 'Buyer' }, docs, OWNER_ID);
    const soldListing = service.getListingById(createResult.listingId);
    if (soldListing.status === 'SOLD') console.log('✅ PASS: Listing marked as SOLD');
    else console.error('❌ FAIL: Status not updated');
} catch (e) {
    console.error(`❌ FAIL: Mark Sold failed: ${e.message}`);
}

// 6. Test Edit AFTER Sold (Should Fail)
console.log('\n6. Testing Edit AFTER Sold...');
try {
    service.updateListing(createResult.listingId, { price: '4000' }, OWNER_ID);
    console.error('❌ FAIL: Edited sold listing!');
} catch (e) {
    console.log(`✅ PASS: Blocked edit on sold listing: ${e.message}`);
}

console.log('\n--- TEST COMPLETE ---');
