/**
 * Chain Publisher Service for KisanMitra
 * Publishes ledger root hashes to Polygon for public verification
 * 
 * How it works:
 * 1. Compute Merkle root of all ledger entries
 * 2. Publish root hash to Polygon smart contract
 * 3. Anyone can verify local ledger against on-chain root
 */

import CryptoJS from 'crypto-js';

// Polygon Mumbai Testnet Configuration
const POLYGON_CONFIG = {
    chainId: 80001,
    chainName: 'Polygon Mumbai Testnet',
    rpcUrl: 'https://rpc-mumbai.maticvigil.com/',
    explorerUrl: 'https://mumbai.polygonscan.com',
    // Demo contract address (would be deployed separately)
    contractAddress: '0x0000000000000000000000000000000000000000'
};

// Simple ABI for root hash storage contract
const CONTRACT_ABI = [
    {
        "inputs": [{ "name": "root", "type": "bytes32" }],
        "name": "publishRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getLatestRoot",
        "outputs": [{ "name": "", "type": "bytes32" }],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getRootCount",
        "outputs": [{ "name": "", "type": "uint256" }],
        "stateMutability": "view",
        "type": "function"
    }
];

class ChainPublisher {
    constructor() {
        this.isConnected = false;
        this.account = null;
        this.provider = null;
    }

    /**
     * Compute Merkle root of all blocks
     * This creates a single hash that represents the entire ledger
     */
    computeMerkleRoot(blocks) {
        if (!blocks || blocks.length === 0) {
            return '0x' + '0'.repeat(64);
        }

        // Get all block hashes
        let hashes = blocks.map(b => b.blockHash || b.metaHash);

        // Build Merkle tree (bottom-up)
        while (hashes.length > 1) {
            const newLevel = [];
            for (let i = 0; i < hashes.length; i += 2) {
                const left = hashes[i];
                const right = hashes[i + 1] || left; // Duplicate if odd
                const combined = CryptoJS.SHA256(left + right).toString();
                newLevel.push('0x' + combined);
            }
            hashes = newLevel;
        }

        return hashes[0];
    }

    /**
     * Check if MetaMask is available
     */
    isMetaMaskAvailable() {
        return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined';
    }

    /**
     * Connect to MetaMask
     */
    async connect() {
        if (!this.isMetaMaskAvailable()) {
            throw new Error('MetaMask not found. Please install MetaMask extension.');
        }

        try {
            // Request account access
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });

            this.account = accounts[0];
            this.isConnected = true;

            // Check if on correct network
            const chainId = await window.ethereum.request({ method: 'eth_chainId' });
            if (parseInt(chainId, 16) !== POLYGON_CONFIG.chainId) {
                await this.switchToPolygon();
            }

            console.log('🔗 Connected to MetaMask:', this.account);
            return {
                success: true,
                account: this.account,
                network: 'Polygon Mumbai'
            };
        } catch (error) {
            console.error('MetaMask connection failed:', error);
            throw error;
        }
    }

    /**
     * Switch to Polygon Mumbai network
     */
    async switchToPolygon() {
        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: '0x' + POLYGON_CONFIG.chainId.toString(16) }]
            });
        } catch (switchError) {
            // Network not added, add it
            if (switchError.code === 4902) {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: '0x' + POLYGON_CONFIG.chainId.toString(16),
                        chainName: POLYGON_CONFIG.chainName,
                        rpcUrls: [POLYGON_CONFIG.rpcUrl],
                        blockExplorerUrls: [POLYGON_CONFIG.explorerUrl],
                        nativeCurrency: {
                            name: 'MATIC',
                            symbol: 'MATIC',
                            decimals: 18
                        }
                    }]
                });
            } else {
                throw switchError;
            }
        }
    }

    /**
     * Publish root hash to Polygon (simulated for demo)
     * In production, this would interact with a real smart contract
     */
    async publishRoot(blocks) {
        const merkleRoot = this.computeMerkleRoot(blocks);
        const timestamp = new Date().toISOString();

        // For demo: Store locally and simulate on-chain
        const publishRecord = {
            merkleRoot,
            blockCount: blocks.length,
            publishedAt: timestamp,
            publisher: this.account || 'demo-account',
            // Simulated transaction hash
            txHash: '0x' + CryptoJS.SHA256(merkleRoot + timestamp).toString()
        };

        // Store in localStorage as demo (would be on-chain in production)
        const publishHistory = JSON.parse(localStorage.getItem('kisanmitra_publish_history') || '[]');
        publishHistory.push(publishRecord);
        localStorage.setItem('kisanmitra_publish_history', JSON.stringify(publishHistory));

        console.log('📤 Root hash published:', merkleRoot);

        return {
            success: true,
            merkleRoot,
            txHash: publishRecord.txHash,
            explorerUrl: `${POLYGON_CONFIG.explorerUrl}/tx/${publishRecord.txHash}`,
            message: 'Root hash published to ledger (demo mode)'
        };
    }

    /**
     * Verify local ledger against published root
     */
    async verifyAgainstPublished(blocks) {
        const currentRoot = this.computeMerkleRoot(blocks);
        const publishHistory = JSON.parse(localStorage.getItem('kisanmitra_publish_history') || '[]');

        if (publishHistory.length === 0) {
            return {
                verified: false,
                error: 'No published roots found. Publish first to enable verification.'
            };
        }

        const latestPublished = publishHistory[publishHistory.length - 1];

        // Check if current root matches latest published
        const isMatch = currentRoot === latestPublished.merkleRoot;

        return {
            verified: isMatch,
            currentRoot,
            publishedRoot: latestPublished.merkleRoot,
            publishedAt: latestPublished.publishedAt,
            blocksAtPublish: latestPublished.blockCount,
            currentBlockCount: blocks.length,
            message: isMatch
                ? '✅ Ledger matches published state'
                : '⚠️ Ledger has changed since last publish'
        };
    }

    /**
     * Get publish history
     */
    getPublishHistory() {
        return JSON.parse(localStorage.getItem('kisanmitra_publish_history') || '[]');
    }

    /**
     * Generate verification proof for a specific listing
     * This creates a path in the Merkle tree for the listing
     */
    generateMerkleProof(blocks, targetBlockIndex) {
        if (!blocks || blocks.length === 0 || targetBlockIndex >= blocks.length) {
            return null;
        }

        const hashes = blocks.map(b => b.blockHash || b.metaHash);
        const proof = [];
        let index = targetBlockIndex;

        let level = [...hashes];
        while (level.length > 1) {
            const newLevel = [];
            for (let i = 0; i < level.length; i += 2) {
                const left = level[i];
                const right = level[i + 1] || left;

                if (i === index || i + 1 === index) {
                    // This is our path, add sibling to proof
                    proof.push({
                        hash: i === index ? right : left,
                        position: i === index ? 'right' : 'left'
                    });
                    index = Math.floor(i / 2);
                }

                const combined = CryptoJS.SHA256(left + right).toString();
                newLevel.push('0x' + combined);
            }
            level = newLevel;
        }

        return {
            targetHash: hashes[targetBlockIndex],
            proof,
            merkleRoot: level[0]
        };
    }

    /**
     * Get configuration
     */
    getConfig() {
        return {
            ...POLYGON_CONFIG,
            isConnected: this.isConnected,
            account: this.account
        };
    }
}

// Export singleton
export const chainPublisher = new ChainPublisher();
