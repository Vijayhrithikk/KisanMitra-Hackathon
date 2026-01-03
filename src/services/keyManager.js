/**
 * KeyManager Service for KisanMitra
 * Handles cryptographic key generation, storage, and digital signatures
 * Uses Web Crypto API for secure key operations
 */

const KEY_STORAGE_KEY = 'kisanmitra_farmer_keypair';

class KeyManager {
    constructor() {
        this.keyPair = null;
    }

    /**
     * Initialize the key manager - load existing keys or generate new ones
     */
    async initialize() {
        const storedKeys = localStorage.getItem(KEY_STORAGE_KEY);

        if (storedKeys) {
            try {
                const parsed = JSON.parse(storedKeys);
                this.keyPair = await this._importKeyPair(parsed);
                console.log('🔑 Existing key pair loaded');
            } catch (error) {
                console.warn('Failed to load existing keys, generating new pair:', error);
                await this.generateNewKeyPair();
            }
        } else {
            await this.generateNewKeyPair();
        }

        return this.keyPair;
    }

    /**
     * Generate a new ECDSA key pair for signing
     */
    async generateNewKeyPair() {
        try {
            // Generate ECDSA key pair (P-256 curve, widely supported)
            this.keyPair = await crypto.subtle.generateKey(
                {
                    name: 'ECDSA',
                    namedCurve: 'P-256'
                },
                true, // extractable
                ['sign', 'verify']
            );

            // Store keys
            await this._storeKeyPair();

            console.log('🔑 New key pair generated and stored');
            return this.keyPair;
        } catch (error) {
            console.error('Key generation failed:', error);
            throw error;
        }
    }

    /**
     * Sign data with the private key
     */
    async sign(data) {
        if (!this.keyPair) {
            await this.initialize();
        }

        const encoder = new TextEncoder();
        const dataBytes = encoder.encode(typeof data === 'string' ? data : JSON.stringify(data));

        try {
            const signature = await crypto.subtle.sign(
                {
                    name: 'ECDSA',
                    hash: 'SHA-256'
                },
                this.keyPair.privateKey,
                dataBytes
            );

            // Convert to hex string for storage
            return this._arrayBufferToHex(signature);
        } catch (error) {
            console.error('Signing failed:', error);
            throw error;
        }
    }

    /**
     * Verify a signature against data using stored public key
     */
    async verify(data, signatureHex) {
        if (!this.keyPair) {
            await this.initialize();
        }

        const encoder = new TextEncoder();
        const dataBytes = encoder.encode(typeof data === 'string' ? data : JSON.stringify(data));
        const signatureBytes = this._hexToArrayBuffer(signatureHex);

        try {
            const isValid = await crypto.subtle.verify(
                {
                    name: 'ECDSA',
                    hash: 'SHA-256'
                },
                this.keyPair.publicKey,
                signatureBytes,
                dataBytes
            );

            return isValid;
        } catch (error) {
            console.error('Verification failed:', error);
            return false;
        }
    }

    /**
     * Verify a signature using an external public key
     */
    async verifyWithPublicKey(data, signatureHex, publicKeyJwk) {
        try {
            const publicKey = await crypto.subtle.importKey(
                'jwk',
                publicKeyJwk,
                {
                    name: 'ECDSA',
                    namedCurve: 'P-256'
                },
                false,
                ['verify']
            );

            const encoder = new TextEncoder();
            const dataBytes = encoder.encode(typeof data === 'string' ? data : JSON.stringify(data));
            const signatureBytes = this._hexToArrayBuffer(signatureHex);

            return await crypto.subtle.verify(
                {
                    name: 'ECDSA',
                    hash: 'SHA-256'
                },
                publicKey,
                signatureBytes,
                dataBytes
            );
        } catch (error) {
            console.error('Verification with public key failed:', error);
            return false;
        }
    }

    /**
     * Get the public key in JWK format (for sharing/storing)
     */
    async getPublicKeyJwk() {
        if (!this.keyPair) {
            await this.initialize();
        }

        return await crypto.subtle.exportKey('jwk', this.keyPair.publicKey);
    }

    /**
     * Get a short fingerprint of the public key (for display)
     */
    async getPublicKeyFingerprint() {
        const jwk = await this.getPublicKeyJwk();
        const keyString = jwk.x + jwk.y;

        // Create a short fingerprint
        const encoder = new TextEncoder();
        const hashBuffer = await crypto.subtle.digest('SHA-256', encoder.encode(keyString));
        const hashHex = this._arrayBufferToHex(hashBuffer);

        return hashHex.substring(0, 16).toUpperCase();
    }

    /**
     * Export keys for backup
     */
    async exportKeys() {
        if (!this.keyPair) {
            await this.initialize();
        }

        const publicKeyJwk = await crypto.subtle.exportKey('jwk', this.keyPair.publicKey);
        const privateKeyJwk = await crypto.subtle.exportKey('jwk', this.keyPair.privateKey);

        return {
            publicKey: publicKeyJwk,
            privateKey: privateKeyJwk,
            fingerprint: await this.getPublicKeyFingerprint(),
            exportedAt: new Date().toISOString()
        };
    }

    /**
     * Import keys from backup
     */
    async importKeys(exportedKeys) {
        const publicKey = await crypto.subtle.importKey(
            'jwk',
            exportedKeys.publicKey,
            { name: 'ECDSA', namedCurve: 'P-256' },
            true,
            ['verify']
        );

        const privateKey = await crypto.subtle.importKey(
            'jwk',
            exportedKeys.privateKey,
            { name: 'ECDSA', namedCurve: 'P-256' },
            true,
            ['sign']
        );

        this.keyPair = { publicKey, privateKey };
        await this._storeKeyPair();

        console.log('🔑 Keys imported successfully');
        return this.keyPair;
    }

    // Private: Store key pair to localStorage
    async _storeKeyPair() {
        const publicKeyJwk = await crypto.subtle.exportKey('jwk', this.keyPair.publicKey);
        const privateKeyJwk = await crypto.subtle.exportKey('jwk', this.keyPair.privateKey);

        localStorage.setItem(KEY_STORAGE_KEY, JSON.stringify({
            publicKey: publicKeyJwk,
            privateKey: privateKeyJwk
        }));
    }

    // Private: Import key pair from stored JWK
    async _importKeyPair(stored) {
        const publicKey = await crypto.subtle.importKey(
            'jwk',
            stored.publicKey,
            { name: 'ECDSA', namedCurve: 'P-256' },
            true,
            ['verify']
        );

        const privateKey = await crypto.subtle.importKey(
            'jwk',
            stored.privateKey,
            { name: 'ECDSA', namedCurve: 'P-256' },
            true,
            ['sign']
        );

        return { publicKey, privateKey };
    }

    // Private: Convert ArrayBuffer to hex string
    _arrayBufferToHex(buffer) {
        return Array.from(new Uint8Array(buffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // Private: Convert hex string to ArrayBuffer
    _hexToArrayBuffer(hex) {
        const bytes = new Uint8Array(hex.length / 2);
        for (let i = 0; i < hex.length; i += 2) {
            bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
        }
        return bytes.buffer;
    }
}

// Export singleton
export const keyManager = new KeyManager();
