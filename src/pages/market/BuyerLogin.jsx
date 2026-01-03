import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { walletService } from '../../services/walletService';
import './BuyerLogin.css';

const BuyerLogin = () => {
    const navigate = useNavigate();
    const [phone, setPhone] = useState('');
    const [showRegister, setShowRegister] = useState(false);
    const [name, setName] = useState('');
    const [existingBuyers, setExistingBuyers] = useState([]);

    useEffect(() => {
        // Get all buyers for quick login
        const wallets = walletService.getAllWallets().filter(w => w.type === 'BUYER');
        setExistingBuyers(wallets);
    }, []);

    const handleLogin = (buyerId = null) => {
        let buyer;

        if (buyerId) {
            // Quick login with existing buyer
            buyer = walletService.getWallet(buyerId);
        } else {
            // Login with phone number
            buyer = walletService.getWalletByPhone(phone);
            if (!buyer) {
                alert('No account found with this phone number. Please register.');
                setShowRegister(true);
                return;
            }
        }

        if (buyer) {
            // Store current buyer in localStorage
            localStorage.setItem('currentBuyer', JSON.stringify({
                buyerId: buyer.id,
                name: buyer.name,
                phone: buyer.phone,
                type: 'BUYER'
            }));

            // Check if user was trying to buy something
            const returnToListing = localStorage.getItem('returnToListing');
            if (returnToListing) {
                localStorage.removeItem('returnToListing');
                navigate(`/market/order/${returnToListing}`);
            } else {
                navigate('/market');
            }
        }
    };

    const handleRegister = () => {
        if (!name.trim() || !phone.trim()) {
            alert('Please enter name and phone number');
            return;
        }

        const result = walletService.createWallet({
            name: name.trim(),
            phone: phone.trim(),
            type: 'BUYER'
        });

        if (result.success) {
            // Give new buyers ₹5000 welcome bonus
            walletService.loadMoney(result.wallet.id, 5000, 'WELCOME_BONUS');

            localStorage.setItem('currentBuyer', JSON.stringify({
                buyerId: result.wallet.id,
                name: result.wallet.name,
                phone: result.wallet.phone,
                type: 'BUYER'
            }));

            alert(`Welcome! You've received ₹5,000 welcome bonus!`);

            // Check if user was trying to buy something
            const returnToListing = localStorage.getItem('returnToListing');
            if (returnToListing) {
                localStorage.removeItem('returnToListing');
                navigate(`/market/order/${returnToListing}`);
            } else {
                navigate('/market');
            }
        }
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    };

    return (
        <div className="buyer-login-page">
            <div className="login-header">
                <h1>🛒 Buyer Login</h1>
                <p>Login to buy farm fresh produce</p>
            </div>

            {/* Quick Login with Test Accounts */}
            <div className="quick-login-section">
                <h3>Quick Login (Test Accounts)</h3>
                <div className="buyer-cards">
                    {existingBuyers.map(buyer => (
                        <div
                            key={buyer.id}
                            className="buyer-card"
                            onClick={() => handleLogin(buyer.id)}
                        >
                            <div className="buyer-avatar">👤</div>
                            <div className="buyer-info">
                                <div className="buyer-name">{buyer.name}</div>
                                <div className="buyer-balance">{formatCurrency(buyer.balance)}</div>
                            </div>
                            <div className="login-arrow">→</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="divider">
                <span>or login with phone</span>
            </div>

            {/* Phone Login */}
            {!showRegister ? (
                <div className="phone-login">
                    <input
                        type="tel"
                        placeholder="Enter Phone Number"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        maxLength={10}
                    />
                    <button className="login-btn" onClick={() => handleLogin()}>
                        Login
                    </button>
                    <button className="register-link" onClick={() => setShowRegister(true)}>
                        New user? Register here
                    </button>
                </div>
            ) : (
                <div className="register-form">
                    <h3>Create Account</h3>
                    <input
                        type="text"
                        placeholder="Your Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                    <input
                        type="tel"
                        placeholder="Phone Number"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        maxLength={10}
                    />
                    <div className="bonus-info">
                        🎁 New users get ₹5,000 welcome bonus!
                    </div>
                    <button className="register-btn" onClick={handleRegister}>
                        Register & Get ₹5,000
                    </button>
                    <button className="back-link" onClick={() => setShowRegister(false)}>
                        ← Back to Login
                    </button>
                </div>
            )}

            <button className="back-btn" onClick={() => navigate('/login')}>
                ← Back to Main
            </button>
        </div>
    );
};

export default BuyerLogin;
