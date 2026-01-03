import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Trash2, Plus, Minus, ShoppingBag } from 'lucide-react';
import './Cart.css';

const Cart = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const { items = [], updateQuantity, removeFromCart, cartTotal = 0, cartCount = 0 } = useCart();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const L = {
        title: lang === 'te' ? 'కార్ట్' : 'Cart',
        empty: lang === 'te' ? 'మీ కార్ట్ ఖాళీగా ఉంది' : 'Your cart is empty',
        emptySubtitle: lang === 'te' ? 'మార్కెట్‌లో పంటలు వెతకండి' : 'Browse crops in the marketplace',
        browse: lang === 'te' ? 'మార్కెట్ చూడండి' : 'Browse Market',
        subtotal: lang === 'te' ? 'సబ్‌టోటల్' : 'Subtotal',
        delivery: lang === 'te' ? 'డెలివరీ' : 'Delivery',
        total: lang === 'te' ? 'మొత్తం' : 'Total',
        checkout: lang === 'te' ? 'ఆర్డర్ చేయండి' : 'Proceed to Order',
        perQuintal: lang === 'te' ? 'క్వింటాల్' : 'Quintal'
    };

    if (items.length === 0) {
        return (
            <div className="cart-page">
                <header className="page-header">
                    <button className="back-btn" onClick={() => navigate('/')}>
                        <ArrowLeft size={20} />
                    </button>
                    <h1>{L.title}</h1>
                    <div style={{ width: 36 }} />
                </header>

                <div className="cart-empty">
                    <span className="empty-icon">🛒</span>
                    <h2>{L.empty}</h2>
                    <p>{L.emptySubtitle}</p>
                    <button className="browse-btn" onClick={() => navigate('/market')}>
                        <ShoppingBag size={18} />
                        {L.browse}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="cart-page">
            {/* Header */}
            <header className="page-header">
                <button className="back-btn" onClick={() => navigate('/')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title} ({items.length})</h1>
                <div style={{ width: 36 }} />
            </header>

            {/* Cart Items */}
            <div className="cart-items">
                {items.map(item => (
                    <div key={item.listingId} className="cart-item">
                        <img
                            src={item.imageUrl || `https://picsum.photos/seed/${item.crop}/100/100`}
                            alt={item.crop}
                            className="cart-item-image"
                            onError={(e) => e.target.src = 'https://picsum.photos/seed/farm/100/100'}
                        />
                        <div className="cart-item-details">
                            <h3>{item.crop}</h3>
                            <p className="cart-item-price">
                                ₹{item.price}/{L.perQuintal}
                            </p>
                            <div className="cart-item-quantity">
                                <button
                                    className="qty-btn"
                                    onClick={() => updateQuantity && updateQuantity(item.listingId, item.quantity - 1)}
                                >
                                    <Minus size={16} />
                                </button>
                                <span className="qty-value">{item.quantity}</span>
                                <button
                                    className="qty-btn"
                                    onClick={() => updateQuantity && updateQuantity(item.listingId, item.quantity + 1)}
                                >
                                    <Plus size={16} />
                                </button>
                            </div>
                        </div>
                        <button
                            className="cart-item-remove"
                            onClick={() => removeFromCart && removeFromCart(item.listingId)}
                        >
                            <Trash2 size={14} />
                        </button>
                    </div>
                ))}
            </div>

            {/* Cart Summary */}
            <div className="cart-summary">
                <div className="summary-row">
                    <span>{L.subtotal}</span>
                    <span>₹{cartTotal.toLocaleString()}</span>
                </div>
                <div className="summary-row">
                    <span>{L.delivery}</span>
                    <span style={{ color: '#4CAF50' }}>Free</span>
                </div>
                <div className="summary-row total">
                    <span>{L.total}</span>
                    <span>₹{cartTotal.toLocaleString()}</span>
                </div>
                <button
                    className="checkout-btn"
                    onClick={() => navigate('/checkout/guest', { state: { fromCart: true, cartItems: items } })}
                >
                    {L.checkout}
                </button>
            </div>
        </div>
    );
};

export default Cart;
