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

// Mock Global localStorage
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

    verifyListing(listingId) {
        const listing = this.getListingById(listingId);
        if (!listing) return { verified: false, error: 'Listing not found' };

        const originalMetadata = { ...listing };
        delete originalMetadata.txHash;
        delete originalMetadata.metaHash;
        delete originalMetadata.buyerHash;
        delete originalMetadata.soldAt;

        if (originalMetadata.status === 'SOLD') {
            originalMetadata.status = 'LISTED';
        }

        const canonicalJson = this._canonicalize(originalMetadata);
        const computedHash = CryptoJS.SHA256(canonicalJson).toString();
        const isMatch = computedHash === listing.metaHash;

        return { verified: isMatch, computedHash, storedHash: listing.metaHash };
    }

    markAsSold(listingId, buyerDetails) {
        const timestamp = new Date().toISOString();
        const encryptedBuyerData = Buffer.from(JSON.stringify(buyerDetails)).toString('base64');
        const buyerHash = CryptoJS.SHA256(JSON.stringify(buyerDetails)).toString();

        const ledgerRecord = {
            type: 'LISTING_SOLD',
            listingId,
            buyerHash,
            encryptedBuyerData,
            timestamp,
            txHash: '0x' + CryptoJS.SHA256(timestamp + listingId + 'SOLD').toString()
        };

        this._appendToLedger(ledgerRecord);
        return { success: true, txHash: ledgerRecord.txHash };
    }
}

// --- Test Execution ---
const service = new MarketService();

console.log('--- STARTING MARKET SERVICE TEST ---');

// 1. Create Listing
console.log('\n1. Creating Listing...');
const listingData = {
    crop: 'Rice',
    variety: 'Sona Masoori',
    quantity: '100',
    unit: 'Quintal',
    price: '3000',
    location: { state: 'Andhra Pradesh', district: 'Guntur' },
    notes: 'Test Listing'
};
const createResult = service.createListing(listingData);
console.log('Listing Created:', createResult);

// 2. Verify Integrity (Should be TRUE)
console.log('\n2. Verifying Integrity...');
const verifyResult = service.verifyListing(createResult.listingId);
console.log('Verification Result:', verifyResult);

if (verifyResult.verified) {
    console.log('✅ PASS: Listing Integrity Verified');
} else {
    console.error('❌ FAIL: Listing Integrity Failed');
}

// 3. Mark as Sold
console.log('\n3. Marking as Sold...');
const buyerDetails = { name: 'John Doe', org: 'Acme Foods', price: '2950' };
const soldResult = service.markAsSold(createResult.listingId, buyerDetails);
console.log('Sold Result:', soldResult);

// 4. Verify Status Update
console.log('\n4. Verifying Status Update...');
const updatedListing = service.getListingById(createResult.listingId);
console.log('Updated Listing Status:', updatedListing.status);

if (updatedListing.status === 'SOLD') {
    console.log('✅ PASS: Status Updated to SOLD');
} else {
    console.error('❌ FAIL: Status Update Failed');
}

// 5. Verify Integrity AFTER Sold (Should still be TRUE)
console.log('\n5. Verifying Integrity After Sale...');
const verifyAfterSold = service.verifyListing(createResult.listingId);
console.log('Verification After Sold:', verifyAfterSold);

if (verifyAfterSold.verified) {
    console.log('✅ PASS: Integrity Maintained After Sale');
} else {
    console.error('❌ FAIL: Integrity Check Failed After Sale');
}

console.log('\n--- TEST COMPLETE ---');
