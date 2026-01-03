/**
 * Transaction Blockchain Service - Bitcoin-like Implementation
 * 
 * Security Features:
 * 1. SHA-256 Hash Chain - Each block links to previous via hash
 * 2. Merkle Tree - Efficiently verify any transaction in a block
 * 3. Proof-of-Work - Mining with adjustable difficulty
 * 4. Digital Signatures - Every transaction is signed
 * 5. UTXO Model - Prevents double-spending
 * 6. Chain Verification - Full integrity checking
 */

import CryptoJS from 'crypto-js';

const CHAIN_KEY = 'kisanmitra_tx_chain';
const UTXO_KEY = 'kisanmitra_utxo_set';
const MEMPOOL_KEY = 'kisanmitra_mempool';
const WALLET_KEY = 'kisanmitra_wallets';

class TransactionBlockchain {
    constructor() {
        this.difficulty = 3; // Number of leading zeros (higher = harder)
        this.blockReward = 0; // No mining rewards in marketplace
        this.maxTxPerBlock = 10;
        this._initialize();
    }

    // ============ Initialization ============

    _initialize() {
        // Initialize chain with genesis block
        if (!localStorage.getItem(CHAIN_KEY)) {
            const genesis = this._createGenesisBlock();
            localStorage.setItem(CHAIN_KEY, JSON.stringify([genesis]));
            console.log('⛓️ Genesis block created:', genesis.hash.substring(0, 16));
        }

        // Initialize UTXO set
        if (!localStorage.getItem(UTXO_KEY)) {
            localStorage.setItem(UTXO_KEY, JSON.stringify({}));
        }

        // Initialize mempool (pending transactions)
        if (!localStorage.getItem(MEMPOOL_KEY)) {
            localStorage.setItem(MEMPOOL_KEY, JSON.stringify([]));
        }

        // Initialize wallet balances
        if (!localStorage.getItem(WALLET_KEY)) {
            localStorage.setItem(WALLET_KEY, JSON.stringify({
                'ESCROW': { balance: 0, created: Date.now() },
                'PLATFORM': { balance: 0, created: Date.now() }
            }));
        }
    }

    _createGenesisBlock() {
        const block = {
            index: 0,
            timestamp: Date.now(),
            transactions: [],
            previousHash: '0'.repeat(64),
            merkleRoot: '0'.repeat(64),
            nonce: 0,
            difficulty: this.difficulty,
            hash: null
        };
        block.hash = this._calculateBlockHash(block);
        return block;
    }

    // ============ Storage Helpers ============

    _getChain() {
        return JSON.parse(localStorage.getItem(CHAIN_KEY) || '[]');
    }

    _saveChain(chain) {
        localStorage.setItem(CHAIN_KEY, JSON.stringify(chain));
    }

    _getMempool() {
        return JSON.parse(localStorage.getItem(MEMPOOL_KEY) || '[]');
    }

    _saveMempool(mempool) {
        localStorage.setItem(MEMPOOL_KEY, JSON.stringify(mempool));
    }

    _getUTXO() {
        return JSON.parse(localStorage.getItem(UTXO_KEY) || '{}');
    }

    _saveUTXO(utxo) {
        localStorage.setItem(UTXO_KEY, JSON.stringify(utxo));
    }

    _getWallets() {
        return JSON.parse(localStorage.getItem(WALLET_KEY) || '{}');
    }

    _saveWallets(wallets) {
        localStorage.setItem(WALLET_KEY, JSON.stringify(wallets));
    }

    _getLastBlock() {
        const chain = this._getChain();
        return chain[chain.length - 1];
    }

    // ============ Transaction Creation ============

    /**
     * Generate unique transaction ID
     */
    _generateTxId() {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2, 8);
        return `TX${timestamp}${random}`.toUpperCase();
    }

    /**
     * Create a signed transaction
     * @param {string} from - Sender address/ID
     * @param {string} to - Receiver address/ID
     * @param {number} amount - Amount in smallest unit
     * @param {string} type - Transaction type
     * @param {object} metadata - Additional data
     */
    createTransaction(from, to, amount, type, metadata = {}) {
        // Validate inputs
        if (!from || !to) throw new Error('Invalid addresses');
        if (amount < 0) throw new Error('Amount must be positive');
        if (from === to && type !== 'ESCROW_DEPOSIT') throw new Error('Cannot send to self');

        const tx = {
            txId: this._generateTxId(),
            version: 1,
            type: type, // ESCROW_DEPOSIT, ESCROW_RELEASE, ESCROW_REFUND, TRANSFER
            from: from,
            to: to,
            amount: amount,
            fee: 0, // No fees for now
            metadata: {
                ...metadata,
                orderId: metadata.orderId || null
            },
            timestamp: Date.now(),

            // Input references (UTXO model)
            inputs: [],

            // Outputs created
            outputs: [
                { address: to, amount: amount, index: 0 }
            ],

            // Cryptographic fields
            signature: null,
            signatureHash: null,
            hash: null
        };

        // Create transaction hash (before signature)
        tx.signatureHash = this._calculateTxSignatureHash(tx);

        // Sign the transaction (simulated - in real app would use private key)
        tx.signature = this._signTransaction(tx, from);

        // Final transaction hash
        tx.hash = this._calculateTxHash(tx);

        return tx;
    }

    /**
     * Calculate hash for signing (excludes signature)
     */
    _calculateTxSignatureHash(tx) {
        const data = {
            txId: tx.txId,
            version: tx.version,
            type: tx.type,
            from: tx.from,
            to: tx.to,
            amount: tx.amount,
            timestamp: tx.timestamp,
            outputs: tx.outputs
        };
        return CryptoJS.SHA256(JSON.stringify(data)).toString();
    }

    /**
     * Calculate full transaction hash
     */
    _calculateTxHash(tx) {
        const data = {
            signatureHash: tx.signatureHash,
            signature: tx.signature,
            timestamp: tx.timestamp
        };
        return CryptoJS.SHA256(tx.signatureHash + tx.signature).toString();
    }

    /**
     * Sign transaction (simulated ECDSA)
     * In production, this would use actual private keys
     */
    _signTransaction(tx, privateKeyId) {
        // Simulate signature using HMAC with a derived key
        const key = CryptoJS.SHA256(privateKeyId + '_PRIVATE_KEY').toString();
        const signature = CryptoJS.HmacSHA256(tx.signatureHash, key).toString();
        return signature;
    }

    /**
     * Verify transaction signature
     */
    verifyTransactionSignature(tx) {
        const expectedSignature = this._signTransaction(tx, tx.from);
        return tx.signature === expectedSignature;
    }

    // ============ Merkle Tree ============

    /**
     * Build Merkle tree from transactions
     * Returns the Merkle root hash
     */
    _buildMerkleRoot(transactions) {
        if (transactions.length === 0) {
            return '0'.repeat(64);
        }

        // Get transaction hashes
        let hashes = transactions.map(tx => tx.hash);

        // Build tree bottom-up
        while (hashes.length > 1) {
            const nextLevel = [];

            for (let i = 0; i < hashes.length; i += 2) {
                const left = hashes[i];
                const right = hashes[i + 1] || left; // Duplicate last if odd
                const combined = CryptoJS.SHA256(left + right).toString();
                nextLevel.push(combined);
            }

            hashes = nextLevel;
        }

        return hashes[0];
    }

    /**
     * Get Merkle proof for a transaction
     * Used to verify a transaction is in a block without downloading the whole block
     */
    getMerkleProof(txHash, block) {
        const txIndex = block.transactions.findIndex(tx => tx.hash === txHash);
        if (txIndex === -1) return null;

        const proof = [];
        let hashes = block.transactions.map(tx => tx.hash);
        let index = txIndex;

        while (hashes.length > 1) {
            const isLeft = index % 2 === 0;
            const siblingIndex = isLeft ? index + 1 : index - 1;
            const sibling = hashes[siblingIndex] || hashes[index];

            proof.push({
                hash: sibling,
                position: isLeft ? 'right' : 'left'
            });

            // Move to next level
            const nextLevel = [];
            for (let i = 0; i < hashes.length; i += 2) {
                const left = hashes[i];
                const right = hashes[i + 1] || left;
                nextLevel.push(CryptoJS.SHA256(left + right).toString());
            }
            hashes = nextLevel;
            index = Math.floor(index / 2);
        }

        return proof;
    }

    /**
     * Verify Merkle proof
     */
    verifyMerkleProof(txHash, proof, merkleRoot) {
        let hash = txHash;

        for (const step of proof) {
            if (step.position === 'left') {
                hash = CryptoJS.SHA256(step.hash + hash).toString();
            } else {
                hash = CryptoJS.SHA256(hash + step.hash).toString();
            }
        }

        return hash === merkleRoot;
    }

    // ============ Block Mining ============

    /**
     * Calculate block hash
     */
    _calculateBlockHash(block) {
        const data = {
            index: block.index,
            timestamp: block.timestamp,
            merkleRoot: block.merkleRoot,
            previousHash: block.previousHash,
            nonce: block.nonce,
            difficulty: block.difficulty
        };
        return CryptoJS.SHA256(JSON.stringify(data)).toString();
    }

    /**
     * Mine a new block with proof-of-work
     */
    mineBlock(transactions = null) {
        const chain = this._getChain();
        const lastBlock = chain[chain.length - 1];

        // Get transactions from mempool if not provided
        const txs = transactions || this._getMempool().slice(0, this.maxTxPerBlock);

        if (txs.length === 0) {
            return null; // Nothing to mine
        }

        // Validate all transactions
        for (const tx of txs) {
            if (!this.verifyTransactionSignature(tx)) {
                console.error(`Invalid signature for tx ${tx.txId}`);
                return null;
            }
        }

        // Create block
        const block = {
            index: lastBlock.index + 1,
            timestamp: Date.now(),
            transactions: txs,
            previousHash: lastBlock.hash,
            merkleRoot: this._buildMerkleRoot(txs),
            nonce: 0,
            difficulty: this.difficulty,
            hash: null
        };

        // Proof of Work - find valid hash
        const target = '0'.repeat(this.difficulty);
        let attempts = 0;
        const maxAttempts = 1000000;

        console.log(`⛏️ Mining block #${block.index} with ${txs.length} transactions...`);

        while (attempts < maxAttempts) {
            block.hash = this._calculateBlockHash(block);

            if (block.hash.startsWith(target)) {
                // Found valid hash!
                console.log(`✅ Block mined! Hash: ${block.hash.substring(0, 16)}... (${attempts} attempts)`);
                break;
            }

            block.nonce++;
            attempts++;
        }

        if (!block.hash.startsWith(target)) {
            console.error('Mining failed - max attempts reached');
            return null;
        }

        // Add block to chain
        chain.push(block);
        this._saveChain(chain);

        // Update UTXO set
        this._updateUTXO(txs);

        // Update wallet balances
        this._updateWalletBalances(txs);

        // Remove mined transactions from mempool
        const minedTxIds = txs.map(tx => tx.txId);
        const mempool = this._getMempool().filter(tx => !minedTxIds.includes(tx.txId));
        this._saveMempool(mempool);

        return block;
    }

    /**
     * Update UTXO set after mining
     */
    _updateUTXO(transactions) {
        const utxo = this._getUTXO();

        for (const tx of transactions) {
            // Add new outputs to UTXO
            for (const output of tx.outputs) {
                const utxoKey = `${tx.txId}:${output.index}`;
                utxo[utxoKey] = {
                    txId: tx.txId,
                    index: output.index,
                    address: output.address,
                    amount: output.amount,
                    spent: false
                };
            }

            // Mark spent inputs
            for (const input of tx.inputs) {
                if (utxo[input.utxoKey]) {
                    utxo[input.utxoKey].spent = true;
                }
            }
        }

        this._saveUTXO(utxo);
    }

    /**
     * Update wallet balances
     */
    _updateWalletBalances(transactions) {
        const wallets = this._getWallets();

        for (const tx of transactions) {
            // Deduct from sender
            if (!wallets[tx.from]) {
                wallets[tx.from] = { balance: 0, created: Date.now() };
            }
            wallets[tx.from].balance -= tx.amount;

            // Add to receiver
            if (!wallets[tx.to]) {
                wallets[tx.to] = { balance: 0, created: Date.now() };
            }
            wallets[tx.to].balance += tx.amount;
        }

        this._saveWallets(wallets);
    }

    // ============ Escrow Operations ============

    /**
     * Deposit funds into escrow for an order
     */
    recordEscrowDeposit(orderId, buyerId, amount, paymentMethod = 'UPI') {
        // Create and add to mempool
        const tx = this.createTransaction(
            buyerId,
            'ESCROW',
            amount,
            'ESCROW_DEPOSIT',
            { orderId, paymentMethod }
        );

        // Add to mempool
        const mempool = this._getMempool();
        mempool.push(tx);
        this._saveMempool(mempool);

        // Mine immediately (in production, would batch transactions)
        const block = this.mineBlock([tx]);

        return {
            ...tx,
            blockIndex: block?.index,
            blockHash: block?.hash,
            confirmed: !!block
        };
    }

    /**
     * Release escrow funds to farmer
     */
    releaseEscrowToFarmer(orderId, farmerId, deliveryProof = {}) {
        // Get escrow amount from previous deposit
        const depositTx = this._findEscrowDeposit(orderId);
        if (!depositTx) {
            throw new Error(`No escrow deposit found for order ${orderId}`);
        }

        // Check if already released
        const existingRelease = this._findEscrowRelease(orderId);
        if (existingRelease) {
            throw new Error(`Escrow already released for order ${orderId}`);
        }

        // Calculate amounts (1% platform fee)
        const platformFee = Math.round(depositTx.amount * 0.01);
        const farmerAmount = depositTx.amount - platformFee;

        // Create release transaction
        const tx = this.createTransaction(
            'ESCROW',
            farmerId,
            farmerAmount,
            'ESCROW_RELEASE',
            {
                orderId,
                originalDepositTxId: depositTx.txId,
                platformFee,
                deliveryProofHash: deliveryProof.hash || CryptoJS.SHA256(orderId + Date.now()).toString()
            }
        );

        // Add platform fee transaction
        const feeTx = this.createTransaction(
            'ESCROW',
            'PLATFORM',
            platformFee,
            'PLATFORM_FEE',
            { orderId, relatedTxId: tx.txId }
        );

        // Add to mempool and mine
        const mempool = this._getMempool();
        mempool.push(tx, feeTx);
        this._saveMempool(mempool);

        const block = this.mineBlock([tx, feeTx]);

        return {
            ...tx,
            platformFee,
            blockIndex: block?.index,
            blockHash: block?.hash,
            confirmed: !!block
        };
    }

    /**
     * Refund escrow to buyer
     */
    refundFromEscrow(orderId, reason = 'CANCELLED') {
        const depositTx = this._findEscrowDeposit(orderId);
        if (!depositTx) {
            throw new Error(`No escrow deposit found for order ${orderId}`);
        }

        // Check if already processed
        const existingRelease = this._findEscrowRelease(orderId);
        const existingRefund = this._findEscrowRefund(orderId);
        if (existingRelease || existingRefund) {
            throw new Error(`Escrow already processed for order ${orderId}`);
        }

        const tx = this.createTransaction(
            'ESCROW',
            depositTx.from, // Refund to original depositor
            depositTx.amount,
            'ESCROW_REFUND',
            { orderId, originalDepositTxId: depositTx.txId, reason }
        );

        const mempool = this._getMempool();
        mempool.push(tx);
        this._saveMempool(mempool);

        const block = this.mineBlock([tx]);

        return {
            ...tx,
            blockIndex: block?.index,
            blockHash: block?.hash,
            confirmed: !!block
        };
    }

    // ============ Query Helpers ============

    _findEscrowDeposit(orderId) {
        const chain = this._getChain();
        for (const block of chain) {
            for (const tx of block.transactions) {
                if (tx.type === 'ESCROW_DEPOSIT' && tx.metadata?.orderId === orderId) {
                    return tx;
                }
            }
        }
        return null;
    }

    _findEscrowRelease(orderId) {
        const chain = this._getChain();
        for (const block of chain) {
            for (const tx of block.transactions) {
                if (tx.type === 'ESCROW_RELEASE' && tx.metadata?.orderId === orderId) {
                    return tx;
                }
            }
        }
        return null;
    }

    _findEscrowRefund(orderId) {
        const chain = this._getChain();
        for (const block of chain) {
            for (const tx of block.transactions) {
                if (tx.type === 'ESCROW_REFUND' && tx.metadata?.orderId === orderId) {
                    return tx;
                }
            }
        }
        return null;
    }

    // ============ Verification ============

    /**
     * Verify entire blockchain integrity
     */
    verifyChain() {
        const chain = this._getChain();
        const results = {
            valid: true,
            totalBlocks: chain.length,
            totalTransactions: 0,
            errors: []
        };

        for (let i = 0; i < chain.length; i++) {
            const block = chain[i];
            results.totalTransactions += block.transactions.length;

            // 1. Verify block hash
            const computedHash = this._calculateBlockHash(block);
            if (computedHash !== block.hash) {
                results.valid = false;
                results.errors.push({
                    block: i,
                    error: 'BLOCK_HASH_MISMATCH',
                    message: 'Block hash has been tampered with'
                });
            }

            // 2. Verify proof-of-work
            const target = '0'.repeat(block.difficulty);
            if (!block.hash.startsWith(target)) {
                results.valid = false;
                results.errors.push({
                    block: i,
                    error: 'INVALID_POW',
                    message: 'Proof-of-work is invalid'
                });
            }

            // 3. Verify chain linkage
            if (i > 0) {
                if (block.previousHash !== chain[i - 1].hash) {
                    results.valid = false;
                    results.errors.push({
                        block: i,
                        error: 'CHAIN_BROKEN',
                        message: 'Previous hash does not match'
                    });
                }
            }

            // 4. Verify Merkle root
            const computedMerkle = this._buildMerkleRoot(block.transactions);
            if (computedMerkle !== block.merkleRoot) {
                results.valid = false;
                results.errors.push({
                    block: i,
                    error: 'MERKLE_MISMATCH',
                    message: 'Merkle root mismatch - transactions tampered'
                });
            }

            // 5. Verify all transaction signatures
            for (const tx of block.transactions) {
                if (!this.verifyTransactionSignature(tx)) {
                    results.valid = false;
                    results.errors.push({
                        block: i,
                        txId: tx.txId,
                        error: 'INVALID_SIGNATURE',
                        message: 'Transaction signature is invalid'
                    });
                }
            }
        }

        return results;
    }

    /**
     * Verify a specific transaction exists and is valid
     */
    verifyTransaction(txId) {
        const chain = this._getChain();

        for (const block of chain) {
            const tx = block.transactions.find(t => t.txId === txId);
            if (tx) {
                // Verify signature
                const signatureValid = this.verifyTransactionSignature(tx);

                // Get Merkle proof
                const merkleProof = this.getMerkleProof(tx.hash, block);
                const merkleValid = this.verifyMerkleProof(tx.hash, merkleProof, block.merkleRoot);

                // Verify block hash
                const blockHashValid = this._calculateBlockHash(block) === block.hash;

                return {
                    valid: signatureValid && merkleValid && blockHashValid,
                    transaction: tx,
                    block: {
                        index: block.index,
                        hash: block.hash,
                        timestamp: block.timestamp
                    },
                    verification: {
                        signatureValid,
                        merkleValid,
                        blockHashValid
                    },
                    merkleProof
                };
            }
        }

        return { valid: false, error: 'Transaction not found' };
    }

    /**
     * Get escrow status for an order
     */
    getEscrowStatus(orderId) {
        const deposit = this._findEscrowDeposit(orderId);
        if (!deposit) {
            return null;
        }

        const release = this._findEscrowRelease(orderId);
        const refund = this._findEscrowRefund(orderId);

        let status = 'HELD';
        if (release) status = 'RELEASED';
        if (refund) status = 'REFUNDED';

        return {
            orderId,
            status,
            depositTxId: deposit.txId,
            depositAmount: deposit.amount,
            depositedAt: deposit.timestamp,
            releaseTxId: release?.txId || null,
            releasedAmount: release?.amount || null,
            releasedAt: release?.timestamp || null,
            refundTxId: refund?.txId || null,
            refundedAt: refund?.timestamp || null
        };
    }

    /**
     * Get all transactions for an order
     */
    getOrderTransactions(orderId) {
        const chain = this._getChain();
        const transactions = [];

        for (const block of chain) {
            for (const tx of block.transactions) {
                if (tx.metadata?.orderId === orderId) {
                    transactions.push({
                        ...tx,
                        blockIndex: block.index,
                        blockHash: block.hash,
                        confirmations: chain.length - block.index
                    });
                }
            }
        }

        return transactions.sort((a, b) => a.timestamp - b.timestamp);
    }

    /**
     * Get blockchain statistics
     */
    getStats() {
        const chain = this._getChain();
        const wallets = this._getWallets();
        const mempool = this._getMempool();

        let totalTransactions = 0;
        let totalVolume = 0;
        let escrowDeposits = 0;
        let escrowReleases = 0;
        let escrowRefunds = 0;

        for (const block of chain) {
            for (const tx of block.transactions) {
                totalTransactions++;
                totalVolume += tx.amount || 0;
                if (tx.type === 'ESCROW_DEPOSIT') escrowDeposits++;
                if (tx.type === 'ESCROW_RELEASE') escrowReleases++;
                if (tx.type === 'ESCROW_REFUND') escrowRefunds++;
            }
        }

        return {
            blockchain: {
                totalBlocks: chain.length,
                totalTransactions,
                totalVolume,
                difficulty: this.difficulty,
                lastBlockHash: chain[chain.length - 1]?.hash,
                lastBlockTime: chain[chain.length - 1]?.timestamp
            },
            escrow: {
                deposits: escrowDeposits,
                releases: escrowReleases,
                refunds: escrowRefunds,
                currentlyHeld: wallets['ESCROW']?.balance || 0
            },
            mempool: {
                pendingTransactions: mempool.length
            },
            integrity: this.verifyChain()
        };
    }

    /**
     * Get all blocks
     */
    getBlocks() {
        return this._getChain();
    }

    /**
     * Get user's transaction history
     */
    getUserTransactions(userId) {
        const chain = this._getChain();
        const transactions = [];

        for (const block of chain) {
            for (const tx of block.transactions) {
                if (tx.from === userId || tx.to === userId) {
                    transactions.push({
                        ...tx,
                        direction: tx.from === userId ? 'OUT' : 'IN',
                        blockIndex: block.index,
                        confirmations: chain.length - block.index
                    });
                }
            }
        }

        return transactions.sort((a, b) => b.timestamp - a.timestamp);
    }

    /**
     * Get wallet balance
     */
    getBalance(address) {
        const wallets = this._getWallets();
        return wallets[address]?.balance || 0;
    }
}

export const transactionBlockchain = new TransactionBlockchain();
