/**
 * Auth Context for KisanMitra
 * Provides authentication state throughout the app
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [guestMode, setGuestMode] = useState(false);

    useEffect(() => {
        // Check for existing session on mount
        let currentUser = authService.getCurrentUser();

        // Fallback: Also check currentFarmer for backward compatibility
        if (!currentUser) {
            const currentFarmer = localStorage.getItem('currentFarmer');
            if (currentFarmer) {
                try {
                    currentUser = JSON.parse(currentFarmer);
                    // Also set in correct session key for next time
                    localStorage.setItem('kisanmitra_session', currentFarmer);
                } catch (e) {
                    console.error('Error parsing currentFarmer:', e);
                }
            }
        }

        const isGuest = localStorage.getItem('guestMode') === 'true';
        setUser(currentUser);
        setGuestMode(isGuest);
        setLoading(false);

        console.log('🔐 Auth initialized:', { user: currentUser, isGuest });
    }, []);

    const loginAdmin = async (email, password) => {
        const result = authService.loginAdmin(email, password);
        if (result.success) {
            setUser(result.user);
        }
        return result;
    };

    const sendOTP = async (phone) => {
        return authService.sendOTP(phone);
    };

    const verifyOTP = async (phone, otp) => {
        const result = authService.verifyOTP(phone, otp);
        if (result.success && !result.isNewUser) {
            setUser(result.user);
        }
        return result;
    };

    const registerFarmer = async (farmerData) => {
        const result = authService.registerFarmer(farmerData);
        if (result.success) {
            setUser(result.user);
        }
        return result;
    };

    const updateProfile = async (updates) => {
        if (!user) return { success: false, error: 'Not logged in' };
        const result = authService.updateFarmerProfile(user.id, updates);
        if (result.success) {
            setUser(result.user);
        }
        return result;
    };

    const logout = () => {
        authService.logout();
        setUser(null);
        setGuestMode(false);
        localStorage.removeItem('guestMode');
    };

    const enableGuestMode = () => {
        setGuestMode(true);
        localStorage.setItem('guestMode', 'true');
    };

    const disableGuestMode = () => {
        setGuestMode(false);
        localStorage.removeItem('guestMode');
    };

    const value = {
        user,
        loading,
        isLoggedIn: !!user,
        isAdmin: user?.role === 'admin',
        isFarmer: user?.role === 'farmer',
        guestMode,
        loginAdmin,
        sendOTP,
        verifyOTP,
        registerFarmer,
        updateProfile,
        logout,
        enableGuestMode,
        disableGuestMode
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
