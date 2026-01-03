import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Monitor, Smartphone } from 'lucide-react';
import './MobileRestricted.css';

const MobileRestricted = () => {
    const navigate = useNavigate();

    return (
        <div className="mobile-restricted">
            <div className="restricted-content">
                <div className="restricted-icon">
                    <Monitor size={48} />
                </div>
                <h2>Desktop Only</h2>
                <p>The Farmer Dashboard is only available on desktop devices for better management experience.</p>
                <div className="restricted-info">
                    <Smartphone size={20} />
                    <span>Please use a desktop or laptop to access this feature.</span>
                </div>
                <button className="btn btn-primary" onClick={() => navigate('/')}>
                    Go to Marketplace
                </button>
            </div>
        </div>
    );
};

export default MobileRestricted;
