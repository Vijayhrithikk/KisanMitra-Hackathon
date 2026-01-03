// Enhanced Intent Parser for AI Assistant
import { intentKeywords, routes, teluguResponses } from './teluguResponses';

class IntentParser {
    constructor() {
        this.conversationState = {
            currentFlow: null,
            data: {},
            step: 0
        };
    }

    // Main intent recognition
    parseIntent(message, currentPath) {
        const lowerMessage = message.toLowerCase().trim();

        // Check for greetings first
        if (this.matchesIntent(lowerMessage, intentKeywords.greetings)) {
            return {
                intent: 'GREETING',
                response: teluguResponses.greetings.hello,
                action: null
            };
        }

        // Check for help
        if (this.matchesIntent(lowerMessage, intentKeywords.help)) {
            return {
                intent: 'HELP',
                response: teluguResponses.help.mainMenu,
                action: null
            };
        }

        // Check for sell/list produce
        if (this.matchesIntent(lowerMessage, intentKeywords.sell)) {
            return {
                intent: 'LIST_PRODUCE',
                response: teluguResponses.marketplace.startListing,
                action: 'NAVIGATE',
                route: routes.marketplace,
                startFlow: 'LIST_PRODUCE'
            };
        }

        // Check for marketplace navigation
        if (this.matchesIntent(lowerMessage, intentKeywords.marketplace)) {
            return {
                intent: 'NAVIGATE_MARKETPLACE',
                response: teluguResponses.navigation.goingToMarket,
                action: 'NAVIGATE',
                route: routes.marketplace
            };
        }

        // Check for crop recommendations
        if (this.matchesIntent(lowerMessage, intentKeywords.recommendations)) {
            return {
                intent: 'NAVIGATE_RECOMMENDATIONS',
                response: teluguResponses.navigation.goingToRecommend,
                action: 'NAVIGATE',
                route: routes.recommendations
            };
        }

        // Check for weather
        if (this.matchesIntent(lowerMessage, intentKeywords.weather)) {
            return {
                intent: 'NAVIGATE_WEATHER',
                response: teluguResponses.navigation.goingToWeather,
                action: 'NAVIGATE',
                route: '/weather' // Assuming you have a weather route
            };
        }

        // Check for rentals
        if (this.matchesIntent(lowerMessage, intentKeywords.rentals)) {
            return {
                intent: 'NAVIGATE_RENTALS',
                response: teluguResponses.navigation.goingToRentals,
                action: 'NAVIGATE',
                route: routes.rentals
            };
        }

        // Check for wallet
        if (this.matchesIntent(lowerMessage, intentKeywords.wallet)) {
            return {
                intent: 'NAVIGATE_WALLET',
                response: teluguResponses.navigation.goingToWallet,
                action: 'NAVIGATE',
                route: routes.wallet
            };
        }

        // Check for home
        if (this.matchesIntent(lowerMessage, intentKeywords.home)) {
            return {
                intent: 'NAVIGATE_HOME',
                response: teluguResponses.navigation.goingToHome,
                action: 'NAVIGATE',
                route: routes.home
            };
        }

        // If in a conversation flow, handle it
        if (this.conversationState.currentFlow) {
            return this.handleFlowStep(lowerMessage);
        }

        // Default: didn't understand
        return {
            intent: 'UNKNOWN',
            response: teluguResponses.errors.notUnderstood,
            action: null
        };
    }

    // Helper to match keywords
    matchesIntent(message, keywords) {
        return keywords.some(keyword =>
            message.includes(keyword.toLowerCase())
        );
    }

    // Handle multi-step conversation flows
    handleFlowStep(message) {
        const { currentFlow, data, step } = this.conversationState;

        if (currentFlow === 'LIST_PRODUCE') {
            switch (step) {
                case 0: // Got crop name
                    this.conversationState.data.crop = message;
                    this.conversationState.step = 1;
                    return {
                        intent: 'FLOW_CONTINUE',
                        response: teluguResponses.marketplace.askQuantity,
                        action: null
                    };

                case 1: // Got quantity
                    const quantity = parseInt(message);
                    if (isNaN(quantity)) {
                        return {
                            intent: 'FLOW_ERROR',
                            response: "దయచేసి సంఖ్యలో పరిమాణం ఇవ్వండి.\n\n(ఉదా: 100, 50, 200)",
                            action: null
                        };
                    }
                    this.conversationState.data.quantity = quantity;
                    this.conversationState.step = 2;
                    return {
                        intent: 'FLOW_CONTINUE',
                        response: teluguResponses.marketplace.askPrice,
                        action: null
                    };

                case 2: // Got price
                    const price = parseInt(message);
                    if (isNaN(price)) {
                        return {
                            intent: 'FLOW_ERROR',
                            response: "దయచేసి సంఖ్యలో ధర ఇవ్వండి.\n\n(ఉదా: 40, 50, 60)",
                            action: null
                        };
                    }
                    this.conversationState.data.price = price;
                    this.conversationState.step = 3;

                    const confirmMsg = teluguResponses.marketplace.confirmListing
                        .replace('{crop}', data.crop)
                        .replace('{quantity}', data.quantity)
                        .replace('{price}', price);

                    return {
                        intent: 'FLOW_CONFIRM',
                        response: confirmMsg,
                        action: null
                    };

                case 3: // Confirmation
                    if (this.matchesIntent(message, ['అవును', 'yes', 'సరే', 'okay', 'ok'])) {
                        const successMsg = teluguResponses.marketplace.listingSuccess
                            .replace('{crop}', data.crop);

                        // Reset flow
                        this.resetFlow();

                        return {
                            intent: 'FLOW_COMPLETE',
                            response: successMsg,
                            action: 'CREATE_LISTING',
                            listingData: data
                        };
                    } else {
                        this.resetFlow();
                        return {
                            intent: 'FLOW_CANCEL',
                            response: "సరే, రద్దు చేశాను. మళ్ళీ ప్రయత్నించాలంటే \"పంట అమ్మాలి\" అని చెప్పండి.",
                            action: null
                        };
                    }
            }
        }

        return {
            intent: 'UNKNOWN',
            response: teluguResponses.errors.notUnderstood,
            action: null
        };
    }

    // Start a new conversation flow
    startFlow(flowName) {
        this.conversationState = {
            currentFlow: flowName,
            data: {},
            step: 0
        };
    }

    // Reset conversation flow
    resetFlow() {
        this.conversationState = {
            currentFlow: null,
            data: {},
            step: 0
        };
    }

    // Get current flow state
    getFlowState() {
        return this.conversationState;
    }
}

export default new IntentParser();
