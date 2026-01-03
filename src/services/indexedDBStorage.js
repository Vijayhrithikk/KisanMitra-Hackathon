/**
 * IndexedDB Storage Service for KisanMitra
 * Provides immutable-like storage for the blockchain ledger
 * 
 * Benefits over localStorage:
 * - Larger storage capacity
 * - Async operations (non-blocking)
 * - Transaction support
 * - Can store binary data (for future IPFS integration)
 */

const DB_NAME = 'KisanMitraDB';
const DB_VERSION = 1;
const LEDGER_STORE = 'ledger';
const METADATA_STORE = 'metadata';

class IndexedDBStorage {
    constructor() {
        this.db = null;
        this.isReady = false;
    }

    /**
     * Initialize the database
     */
    async initialize() {
        if (this.isReady) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => {
                console.error('IndexedDB open failed:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                this.isReady = true;
                console.log('📦 IndexedDB initialized');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create ledger store (append-only)
                if (!db.objectStoreNames.contains(LEDGER_STORE)) {
                    const ledgerStore = db.createObjectStore(LEDGER_STORE, {
                        keyPath: 'blockIndex',
                        autoIncrement: false
                    });
                    ledgerStore.createIndex('type', 'type', { unique: false });
                    ledgerStore.createIndex('listingId', 'listingId', { unique: false });
                    ledgerStore.createIndex('timestamp', 'timestamp', { unique: false });
                    ledgerStore.createIndex('blockHash', 'blockHash', { unique: true });
                }

                // Create metadata store (for chain stats, root hashes)
                if (!db.objectStoreNames.contains(METADATA_STORE)) {
                    db.createObjectStore(METADATA_STORE, { keyPath: 'key' });
                }

                console.log('📦 IndexedDB schema created');
            };
        });
    }

    /**
     * Append a block to the ledger (append-only, no delete/update)
     */
    async appendBlock(block) {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([LEDGER_STORE], 'readwrite');
            const store = transaction.objectStore(LEDGER_STORE);

            const request = store.add(block);

            request.onsuccess = () => {
                console.log(`✅ Block ${block.blockIndex} appended to IndexedDB`);
                resolve(block);
            };

            request.onerror = () => {
                console.error('Failed to append block:', request.error);
                reject(request.error);
            };
        });
    }

    /**
     * Get all blocks (read-only)
     */
    async getAllBlocks() {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([LEDGER_STORE], 'readonly');
            const store = transaction.objectStore(LEDGER_STORE);
            const request = store.getAll();

            request.onsuccess = () => {
                resolve(request.result || []);
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    /**
     * Get block by index
     */
    async getBlock(blockIndex) {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([LEDGER_STORE], 'readonly');
            const store = transaction.objectStore(LEDGER_STORE);
            const request = store.get(blockIndex);

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    /**
     * Get last block
     */
    async getLastBlock() {
        const blocks = await this.getAllBlocks();
        return blocks.length > 0 ? blocks[blocks.length - 1] : null;
    }

    /**
     * Get blocks by listing ID
     */
    async getBlocksByListingId(listingId) {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([LEDGER_STORE], 'readonly');
            const store = transaction.objectStore(LEDGER_STORE);
            const index = store.index('listingId');
            const request = index.getAll(listingId);

            request.onsuccess = () => {
                resolve(request.result || []);
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    /**
     * Get block count
     */
    async getBlockCount() {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([LEDGER_STORE], 'readonly');
            const store = transaction.objectStore(LEDGER_STORE);
            const request = store.count();

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    /**
     * Store metadata (like published root hashes)
     */
    async setMetadata(key, value) {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([METADATA_STORE], 'readwrite');
            const store = transaction.objectStore(METADATA_STORE);
            const request = store.put({ key, value, updatedAt: new Date().toISOString() });

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get metadata
     */
    async getMetadata(key) {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([METADATA_STORE], 'readonly');
            const store = transaction.objectStore(METADATA_STORE);
            const request = store.get(key);

            request.onsuccess = () => {
                resolve(request.result?.value || null);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Migrate from localStorage to IndexedDB
     */
    async migrateFromLocalStorage(localStorageKey) {
        const existingData = localStorage.getItem(localStorageKey);
        if (!existingData) {
            console.log('No localStorage data to migrate');
            return 0;
        }

        const blocks = JSON.parse(existingData);
        let migrated = 0;

        for (const block of blocks) {
            try {
                await this.appendBlock(block);
                migrated++;
            } catch (error) {
                // Block might already exist
                console.warn(`Block ${block.blockIndex} already exists, skipping`);
            }
        }

        console.log(`📦 Migrated ${migrated} blocks from localStorage to IndexedDB`);
        return migrated;
    }

    /**
     * Export all data (for backup)
     */
    async exportAll() {
        const blocks = await this.getAllBlocks();
        return {
            version: DB_VERSION,
            exportedAt: new Date().toISOString(),
            blockCount: blocks.length,
            blocks
        };
    }

    /**
     * Clear all data (for testing only - NOT for production)
     */
    async clearAll() {
        await this.initialize();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([LEDGER_STORE, METADATA_STORE], 'readwrite');

            transaction.objectStore(LEDGER_STORE).clear();
            transaction.objectStore(METADATA_STORE).clear();

            transaction.oncomplete = () => {
                console.log('⚠️ All IndexedDB data cleared');
                resolve();
            };

            transaction.onerror = () => reject(transaction.error);
        });
    }
}

// Export singleton
export const indexedDBStorage = new IndexedDBStorage();
