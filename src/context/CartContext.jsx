import React, { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext();

export const useCart = () => {
    const context = useContext(CartContext);
    if (!context) {
        throw new Error('useCart must be used within CartProvider');
    }
    return context;
};

export const CartProvider = ({ children }) => {
    const [items, setItems] = useState(() => {
        const saved = localStorage.getItem('kisanmitra_cart');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('kisanmitra_cart', JSON.stringify(items));
    }, [items]);

    const addToCart = (product, quantity = 1) => {
        setItems(prev => {
            const existing = prev.find(item => item.id === product.id || item.listingId === product.listingId);
            if (existing) {
                return prev.map(item =>
                    (item.id === product.id || item.listingId === product.listingId)
                        ? { ...item, quantity: item.quantity + quantity }
                        : item
                );
            }
            return [...prev, { ...product, quantity }];
        });
    };

    const removeFromCart = (productId) => {
        setItems(prev => prev.filter(item => item.id !== productId && item.listingId !== productId));
    };

    const updateQuantity = (productId, quantity) => {
        if (quantity <= 0) {
            removeFromCart(productId);
            return;
        }
        setItems(prev => prev.map(item =>
            (item.id === productId || item.listingId === productId)
                ? { ...item, quantity }
                : item
        ));
    };

    const clearCart = () => setItems([]);

    const cartCount = items.reduce((sum, item) => sum + item.quantity, 0);
    const cartTotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    return (
        <CartContext.Provider value={{
            items,
            cart: items, // Alias for GuestCheckout compatibility
            addToCart,
            removeFromCart,
            updateQuantity,
            clearCart,
            cartCount,
            cartTotal
        }}>
            {children}
        </CartContext.Provider>
    );
};

export default CartContext;
