// Form Automator Service
// Programmatically fills and submits forms based on AI Assistant conversation data

class FormAutomator {
    constructor() {
        this.pendingListingData = null;
    }

    // Store listing data from conversation
    setPendingListing(data) {
        this.pendingListingData = {
            crop: data.crop || '',
            quantity: parseInt(data.quantity) || 0,
            price: parseInt(data.price) || 0,
            variety: data.variety || 'Standard',
            unit: 'Kg',
            timestamp: Date.now()
        };

        // Store in sessionStorage for persistence across navigation
        sessionStorage.setItem('aiPendingListing', JSON.stringify(this.pendingListingData));

        return this.pendingListingData;
    }

    // Get pending listing data
    getPendingListing() {
        if (this.pendingListingData) {
            return this.pendingListingData;
        }

        // Try to retrieve from sessionStorage
        const stored = sessionStorage.getItem('aiPendingListing');
        if (stored) {
            this.pendingListingData = JSON.parse(stored);
            return this.pendingListingData;
        }

        return null;
    }

    // Clear pending listing
    clearPendingListing() {
        this.pendingListingData = null;
        sessionStorage.removeItem('aiPendingListing');
    }

    // Auto-fill marketplace form
    async autoFillMarketplaceForm() {
        const data = this.getPendingListing();
        if (!data) {
            console.warn('No pending listing data to fill');
            return false;
        }

        // Wait a bit for the form to render
        await new Promise(resolve => setTimeout(resolve, 500));

        try {
            // Fill crop
            const cropSelect = document.querySelector('select[name="crop"]');
            if (cropSelect && data.crop) {
                cropSelect.value = data.crop;
                cropSelect.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Fill quantity
            const quantityInput = document.querySelector('input[name="quantity"]');
            if (quantityInput && data.quantity) {
                quantityInput.value = data.quantity.toString();
                quantityInput.dispatchEvent(new Event('input', { bubbles: true }));
                quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Fill unit
            const unitSelect = document.querySelector('select[name="unit"]');
            if (unitSelect && data.unit) {
                unitSelect.value = data.unit;
                unitSelect.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Fill price
            const priceInput = document.querySelector('input[name="price"]');
            if (priceInput && data.price) {
                priceInput.value = data.price.toString();
                priceInput.dispatchEvent(new Event('input', { bubbles: true }));
                priceInput.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // Fill variety if available
            if (data.variety) {
                const varietyInput = document.querySelector('input[name="variety"]');
                if (varietyInput) {
                    varietyInput.value = data.variety;
                    varietyInput.dispatchEvent(new Event('input', { bubbles: true }));
                    varietyInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }

            console.log('Form auto-filled successfully:', data);
            return true;
        } catch (error) {
            console.error('Error auto-filling form:', error);
            return false;
        }
    }

    // Programmatically submit form
    async submitForm() {
        try {
            const submitButton = document.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                submitButton.click();
                this.clearPendingListing();
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error submitting form:', error);
            return false;
        }
    }

    // Helper: Map Telugu crop names to English
    mapCropName(teluguName) {
        const cropMapping = {
            'టమాటా': 'Tomato',
            'ఆలూగడ్డ': 'Potato',
            'ఉల్లిపాయ': 'Onion',
            'వరి': 'Rice',
            'గోధుమ': 'Wheat',
            'మిర్చి': 'Green Chilli',
            'క్యాబేజీ': 'Cabbage',
            'కాలీఫ్లవర్': 'Cauliflower',
            'వంకాయ': 'Brinjal',
            'బెండకాయ': 'Okra',
            'క్యారెట్': 'Carrot',
            'పత్తి': 'Cotton',
            'చెరకు': 'Sugarcane',
            'పసుపు': 'Turmeric',
            'అరటి': 'Banana',
            'మామిడి': 'Mango',
            // Add more mappings as needed
        };

        return cropMapping[teluguName] || teluguName;
    }

    // Process listing data with Telugu translation
    processListingData(rawData) {
        return {
            crop: this.mapCropName(rawData.crop),
            quantity: rawData.quantity,
            price: rawData.price,
            variety: rawData.variety || 'Standard',
            unit: rawData.unit || 'Kg'
        };
    }
}

export default new FormAutomator();
