import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MessageCircle, X, Send, Bot, User, ArrowRight, Loader2 } from 'lucide-react';
import './Chatbot.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const Chatbot = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const L = {
        title: lang === 'te' ? 'కిసాన్‌మిత్ర AI' : 'KisanMitra AI',
        placeholder: lang === 'te' ? 'మీ ప్రశ్న అడగండి...' : 'Ask your question...',
        greeting: lang === 'te'
            ? 'నమస్తే! నేను కిసాన్‌మిత్ర AI. పంటలు, వాతావరణం, మార్కెట్ గురించి అడగండి!'
            : 'Namaste! I\'m KisanMitra AI. Ask me about crops, weather, or market!',
        suggestions: lang === 'te'
            ? ['ఏ పంట వేయాలి?', 'ఈ రోజు వాతావరణం', 'వరి ధర ఎంత?', 'సబ్సిడీలు చెప్పు']
            : ['Which crop to grow?', 'Today\'s weather', 'Rice price?', 'Tell me about subsidies']
    };

    // Add greeting on first open
    useEffect(() => {
        if (isOpen && messages.length === 0) {
            setMessages([{
                role: 'assistant',
                content: L.greeting,
                timestamp: new Date()
            }]);
        }
    }, [isOpen]);

    // Scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input when opened
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    const sendMessage = async (text) => {
        if (!text.trim()) return;

        const userMessage = {
            role: 'user',
            content: text.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            // Build conversation history for context
            const history = messages.slice(-6).map(m => ({
                role: m.role,
                content: m.content
            }));

            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text.trim(),
                    conversation_history: history
                })
            });

            const data = await response.json();

            const botMessage = {
                role: 'assistant',
                content: data.response || 'I\'m having trouble. Please try again.',
                actions: data.actions || [],
                intent: data.intent,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: lang === 'te'
                    ? 'క్షమించండి, కనెక్షన్ సమస్య. మళ్ళీ ప్రయత్నించండి.'
                    : 'Sorry, connection issue. Please try again.',
                timestamp: new Date()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        sendMessage(input);
    };

    const handleSuggestionClick = (suggestion) => {
        sendMessage(suggestion);
    };

    const handleActionClick = (action) => {
        if (action.type === 'navigate') {
            setIsOpen(false);
            navigate(action.path);
        }
    };

    return (
        <>
            {/* Floating Chat Button */}
            {!isOpen && (
                <button className="chat-fab" onClick={() => setIsOpen(true)}>
                    <MessageCircle size={24} />
                    <span className="chat-fab-label">AI</span>
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="chat-window">
                    {/* Header */}
                    <div className="chat-header">
                        <div className="chat-header-info">
                            <Bot size={20} />
                            <span>{L.title}</span>
                        </div>
                        <button className="chat-close" onClick={() => setIsOpen(false)}>
                            <X size={20} />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="chat-messages">
                        {messages.map((msg, i) => (
                            <div key={i} className={`chat-message ${msg.role}`}>
                                <div className="message-avatar">
                                    {msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
                                </div>
                                <div className="message-content">
                                    <p>{msg.content}</p>

                                    {/* Action buttons */}
                                    {msg.actions?.length > 0 && (
                                        <div className="message-actions">
                                            {msg.actions.map((action, j) => (
                                                <button
                                                    key={j}
                                                    className="action-btn"
                                                    onClick={() => handleActionClick(action)}
                                                >
                                                    {action.label}
                                                    <ArrowRight size={14} />
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {loading && (
                            <div className="chat-message assistant">
                                <div className="message-avatar"><Bot size={16} /></div>
                                <div className="message-content typing">
                                    <Loader2 size={16} className="spin" />
                                    <span>{lang === 'te' ? 'ఆలోచిస్తున్నాను...' : 'Thinking...'}</span>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Suggestions */}
                    {messages.length <= 1 && (
                        <div className="chat-suggestions">
                            {L.suggestions.map((s, i) => (
                                <button key={i} onClick={() => handleSuggestionClick(s)}>
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input */}
                    <form className="chat-input" onSubmit={handleSubmit}>
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={L.placeholder}
                            disabled={loading}
                        />
                        <button type="submit" disabled={loading || !input.trim()}>
                            <Send size={20} />
                        </button>
                    </form>
                </div>
            )}
        </>
    );
};

export default Chatbot;
