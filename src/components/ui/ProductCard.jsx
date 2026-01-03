import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { ShoppingCart, Plus } from 'lucide-react';
import './ProductCard.css';

const ProductCard = ({ product = {} }) => {
    const navigate = useNavigate();
    const cart = useCart() || {};
    const addToCart = cart.addToCart || (() => { });

    const {
        listingId,
        crop,
        variety,
        price,
        quantity,
        unit = 'Quintal',
        farmerName,
        location,
        imageUrl,
        status
    } = product;

    const handleAddToCart = (e) => {
        e.stopPropagation();
        addToCart({
            ...product,
            id: listingId
        }, 1);
    };

    const handleClick = () => {
        navigate(`/market/listing/${listingId}`);
    };

    const defaultImage = `https://picsum.photos/seed/${encodeURIComponent(crop || 'farm')}/400/300`;

    // Handle location - could be string or object
    const getLocationString = (loc) => {
        if (!loc) return 'India';
        if (typeof loc === 'string') return loc;
        if (typeof loc === 'object') {
            return loc.district || loc.city || loc.state || 'India';
        }
        return 'India';
    };

    return (
        <div className="product-card" onClick={handleClick}>
            {/* Image */}
            <div className="product-image-wrapper">
                <img
                    src={imageUrl || defaultImage}
                    alt={crop || 'Product'}
                    className="product-image"
                    onError={(e) => e.target.src = defaultImage}
                />
                {status === 'LISTED' && (
                    <span className="product-badge fresh">Fresh</span>
                )}
            </div>

            {/* Content */}
            <div className="product-content">
                <div className="product-category">{variety || 'Organic'}</div>
                <h3 className="product-name">{crop || 'Product'}</h3>

                <div className="product-meta">
                    <span className="product-location">📍 {getLocationString(location)}</span>
                    <span className="product-farmer">by {farmerName || 'Farmer'}</span>
                </div>

                <div className="product-footer">
                    <div className="product-price">
                        <span className="price-amount">₹{price || 0}</span>
                        <span className="price-unit">/{unit}</span>
                    </div>
                    <button
                        className="add-to-cart-btn"
                        onClick={handleAddToCart}
                    >
                        <Plus size={18} />
                    </button>
                </div>

                <div className="product-stock">
                    {quantity} {unit} available
                </div>
            </div>
        </div>
    );
};

export default ProductCard;
