import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MessageCircle, X, Send } from 'lucide-react';
import intentParser from '../../services/intentParser';
import formAutomator from '../../services/formAutomator';
import './AIAssistant.css';

const AIAssistant = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'ai',
            text: 'నమస్కారం! 🙏 నేను కిసాన్ మిత్ర AI. మీ వ్యవసాయ సహాయకుడు.\n\nనేను మీకు ఏమి సహాయం చేయగలను?',
            timestamp: new Date()
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Handle sending message
    const handleSend = async () => {
        if (!inputText.trim()) return;

        // Add user message
        const userMessage = {
            id: Date.now(),
            type: 'user',
            text: inputText,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);
        const currentInput = inputText;
        setInputText('');
        setIsTyping(true);

        // Process intent using enhanced parser
        setTimeout(() => {
            const result = intentParser.parseIntent(currentInput, location.pathname);

            // Add AI response
            const aiResponse = {
                id: Date.now() + 1,
                type: 'ai',
                text: result.response,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiResponse]);
            setIsTyping(false);

            // Execute actions if any
            if (result.action === 'NAVIGATE' && result.route) {
                // Navigate after a short delay to let user see the message
                setTimeout(() => {
                    navigate(result.route);
                }, 800);
            }

            // Start conversation flow if specified
            if (result.startFlow) {
                intentParser.startFlow(result.startFlow);
            }

            // Handle marketplace listing creation
            if (result.action === 'CREATE_LISTING' && result.listingData) {
                // Process and store listing data
                const processedData = formAutomator.processListingData(result.listingData);
                formAutomator.setPendingListing(processedData);

                // Navigate to create listing page
                setTimeout(() => {
                    navigate('/market/create');
                }, 1000);
            }
        }, 500);
    };

    // Simple intent processing (will be enhanced)
    const processIntent = (text, currentPath) => {
        const lowerText = text.toLowerCase();
        let response = '';

        // Navigation intents
        if (lowerText.includes('మార్కెట్') || lowerText.includes('market')) {
            navigate('/marketplace');
            response = '✅ మిమ్మల్ని మార్కెట్‌కి తీసుకెళ్తున్నాను...';
        } else if (lowerText.includes('వాతావరణం') || lowerText.includes('weather')) {
            navigate('/weather');
            response = '🌤️ వాతావరణ సమాచారం చూపిస్తున్నాను...';
        } else if (lowerText.includes('పంట') && (lowerText.includes('సూచన') || lowerText.includes('recommend'))) {
            navigate('/recommend');
            response = '🌾 పంట సూచనల పేజీకి వెళ్తున్నాను...';
        }
        // Listing produce intent
        else if (lowerText.includes('అమ్మ') || lowerText.includes('జాబితా') || lowerText.includes('sell') || lowerText.includes('list')) {
            navigate('/marketplace');
            response = '📦 అద్భుతం! మీ పంటను జాబితా చేద్దాం. మొదట మీ పంట పేరు చెప్పండి.';
        }
        // Greeting
        else if (lowerText.includes('హలో') || lowerText.includes('hello') || lowerText.includes('hi') || lowerText.includes('నమస్కారం')) {
            response = 'నమస్కారం! 🙏\n\nనేను ఈ విషయాలలో సహాయం చేయగలను:\n\n🛒 మార్కెట్‌లో పంట అమ్మడం\n🌾 పంట సూచనలు\n🌤️ వాతావరణ సమాచారం\n\nమీకు ఏమి కావాలి?';
        }
        // Help
        else if (lowerText.includes('help') || lowerText.includes('సహాయం')) {
            response = '📱 నేను మీకు ఇలా సహాయం చేయగలను:\n\n• "మార్కెట్ చూపించు" - మార్కెట్‌కి వెళ్ళడానికి\n• "పంట అమ్మాలి" - మీ పంట జాబితా చేయడానికి\n• "వాతావరణం చూడు" - వాతావరణ సమాచారం కోసం\n• "పంట సూచనలు" - మీ ప్రాంతానికి సరైన పంటలు\n\nఏదైనా అడగండి!';
        }
        // Default
        else {
            response = 'క్షమించండి, అర్థం కాలేదు. 😊\n\n"సహాయం" అని టైప్ చేసి నేను ఏమి చేయగలనో చూడండి.';
        }

        return {
            id: Date.now() + 1,
            type: 'ai',
            text: response,
            timestamp: new Date()
        };
    };

    // Format timestamp
    const formatTime = (date) => {
        return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    };

    // Quick action handlers
    const handleQuickAction = (action) => {
        setInputText(action);
        // Auto-send after a tiny delay
        setTimeout(() => {
            handleSend();
        }, 100);
    };

    return (
        <>
            {/* Floating Chat Bubble */}
            {!isOpen && (
                <button
                    className="ai-assistant-bubble"
                    onClick={() => setIsOpen(true)}
                    aria-label="Open AI Assistant"
                >
                    <MessageCircle size={28} color="white" />
                    <span className="pulse-ring"></span>
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="ai-assistant-window">
                    {/* Header */}
                    <div className="ai-assistant-header">
                        <div className="header-info">
                            <div className="ai-avatar">🤖</div>
                            <div>
                                <h3>కిసాన్ మిత్ర AI</h3>
                                <p className="status">ఆన్‌లైన్</p>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="close-chat-btn">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Messages Container */}
                    <div className="messages-container">
                        {messages.map((message) => (
                            <div key={message.id} className={`message ${message.type}`}>
                                <div className="message-bubble">
                                    <div className="message-text">{message.text}</div>
                                    <div className="message-time">{formatTime(message.timestamp)}</div>
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="message ai">
                                <div className="message-bubble typing">
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="input-container">
                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="ఇక్కడ టైప్ చేయండి..."
                            className="message-input"
                            lang="te"
                        />
                        <button
                            onClick={handleSend}
                            className="send-btn"
                            disabled={!inputText.trim()}
                        >
                            <Send size={20} />
                        </button>
                    </div>

                    {/* Quick Actions */}
                    <div className="quick-actions">
                        <button onClick={() => handleQuickAction('మార్కెట్ చూపించు')}>
                            🛒 మార్కెట్
                        </button>
                        <button onClick={() => handleQuickAction('పంట సూచనలు')}>
                            🌾 సూచనలు
                        </button>
                        <button onClick={() => handleQuickAction('సహాయం')}>
                            ℹ️ సహాయం
                        </button>
                    </div>
                </div>
            )}
        </>
    );
};

export default AIAssistant;
