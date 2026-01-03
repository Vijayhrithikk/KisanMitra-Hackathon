/**
 * Auth Service for KisanMitra
 * Handles Admin (email/password) and Farmer (phone/OTP) authentication
 */

const USERS_KEY = 'kisanmitra_users';
const SESSION_KEY = 'kisanmitra_session';
const DEFAULT_OTP = '123456';

// Default admin user
const DEFAULT_ADMIN = {
    id: 'ADMIN-001',
    role: 'admin',
    email: 'admin@kisanmitra.com',
    password: 'admin123', // In production, this would be hashed
    name: 'Admin User',
    createdAt: new Date().toISOString()
};

class AuthService {
    constructor() {
        this._initializeUsers();
    }

    _initializeUsers() {
        const users = localStorage.getItem(USERS_KEY);
        if (!users) {
            localStorage.setItem(USERS_KEY, JSON.stringify({
                admins: [DEFAULT_ADMIN],
                farmers: []
            }));
        }
    }

    _getUsers() {
        return JSON.parse(localStorage.getItem(USERS_KEY) || '{"admins":[],"farmers":[]}');
    }

    _saveUsers(users) {
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }

    _setSession(user) {
        const session = {
            ...user,
            loginAt: new Date().toISOString()
        };
        delete session.password; // Don't store password in session
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        // Also store in sessionStorage as fallback
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
        // Store phone mapping for backward compatibility
        if (user.phone) {
            localStorage.setItem('farmer_phone', user.phone);
        }
    }

    // ========== Admin Auth ==========

    loginAdmin(email, password) {
        const users = this._getUsers();
        const admin = users.admins.find(a => a.email === email && a.password === password);

        if (admin) {
            this._setSession(admin);
            return { success: true, user: { ...admin, password: undefined } };
        }
        return { success: false, error: 'Invalid email or password' };
    }

    // ========== Farmer Auth ==========

    sendOTP(phone) {
        // In production, this would send actual SMS
        // For demo, OTP is always 123456
        console.log(`📱 OTP sent to ${phone}: ${DEFAULT_OTP}`);

        // Store pending OTP verification
        sessionStorage.setItem('pending_otp_phone', phone);

        return { success: true, message: `OTP sent to ${phone}` };
    }

    async verifyOTP(phone, otp) {
        const pendingPhone = sessionStorage.getItem('pending_otp_phone');

        if (pendingPhone !== phone) {
            return { success: false, error: 'Phone number mismatch. Please request OTP again.' };
        }

        if (otp !== DEFAULT_OTP) {
            return { success: false, error: 'Invalid OTP. Use 123456 for demo.' };
        }

        sessionStorage.removeItem('pending_otp_phone');

        // Check if farmer exists in localStorage first
        const users = this._getUsers();
        let farmer = users.farmers.find(f => f.phone === phone);

        if (farmer) {
            // Existing farmer in localStorage - log in
            this._setSession(farmer);
            return { success: true, isNewUser: false, user: farmer };
        }

        // Also check the DATABASE API for existing farmers
        try {
            console.log('🔍 Checking database for farmer with phone:', phone);
            const response = await fetch(`${import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api'}/users/phone/${phone}`);
            if (response.ok) {
                const data = await response.json();
                if (data.exists && data.user) {
                    console.log('✅ Found farmer in database:', data.user.name);
                    // Create local session from database user
                    const dbUser = {
                        id: data.user.userId || data.user._id,
                        farmerId: data.user.userId || data.user._id,
                        role: 'farmer',
                        phone: data.user.phone,
                        name: data.user.name,
                        village: data.user.village,
                        district: data.user.district,
                        state: data.user.state,
                        verified: data.user.verified || false
                    };
                    // Store in localStorage for future
                    users.farmers.push(dbUser);
                    this._saveUsers(users);
                    this._setSession(dbUser);
                    return { success: true, isNewUser: false, user: dbUser };
                }
            }
        } catch (error) {
            console.warn('Database check failed, continuing with localStorage only:', error);
        }

        // New farmer - needs registration
        return { success: true, isNewUser: true, phone };
    }

    registerFarmer(farmerData) {
        const users = this._getUsers();

        // Check if phone already exists
        if (users.farmers.find(f => f.phone === farmerData.phone)) {
            return { success: false, error: 'Phone number already registered' };
        }

        const newFarmer = {
            id: `FARMER-${Date.now().toString(36).toUpperCase()}`,
            role: 'farmer',
            phone: farmerData.phone,
            name: farmerData.name,
            village: farmerData.village || '',
            district: farmerData.district || '',
            state: farmerData.state || '',
            verified: false,
            verificationDoc: farmerData.verificationDoc || null,
            createdAt: new Date().toISOString()
        };

        users.farmers.push(newFarmer);
        this._saveUsers(users);
        this._setSession(newFarmer);

        return { success: true, user: newFarmer };
    }

    updateFarmerProfile(farmerId, updates) {
        const users = this._getUsers();
        const farmerIndex = users.farmers.findIndex(f => f.id === farmerId);

        if (farmerIndex === -1) {
            return { success: false, error: 'Farmer not found' };
        }

        // Update allowed fields only
        const allowedFields = ['name', 'village', 'district', 'state', 'verificationDoc'];
        allowedFields.forEach(field => {
            if (updates[field] !== undefined) {
                users.farmers[farmerIndex][field] = updates[field];
            }
        });

        this._saveUsers(users);

        // Update session if this is current user
        const session = this.getCurrentUser();
        if (session && session.id === farmerId) {
            this._setSession(users.farmers[farmerIndex]);
        }

        return { success: true, user: users.farmers[farmerIndex] };
    }

    // ========== Session Management ==========

    getCurrentUser() {
        // Try localStorage first
        let session = localStorage.getItem(SESSION_KEY);
        if (!session) {
            // Fallback to sessionStorage
            session = sessionStorage.getItem(SESSION_KEY);
        }
        if (!session) {
            // Last resort: check old currentFarmer key
            const oldSession = localStorage.getItem('currentFarmer');
            if (oldSession) {
                try {
                    const parsed = JSON.parse(oldSession);
                    // Migrate to new key
                    this._setSession(parsed);
                    return parsed;
                } catch (e) {
                    console.error('Error parsing legacy session:', e);
                }
            }
        }
        return session ? JSON.parse(session) : null;
    }

    isLoggedIn() {
        return this.getCurrentUser() !== null;
    }

    isAdmin() {
        const user = this.getCurrentUser();
        return user && user.role === 'admin';
    }

    isFarmer() {
        const user = this.getCurrentUser();
        return user && user.role === 'farmer';
    }

    logout() {
        localStorage.removeItem(SESSION_KEY);
        sessionStorage.removeItem(SESSION_KEY);
        localStorage.removeItem('farmer_phone');
        localStorage.removeItem('currentFarmer'); // Clear legacy key
        return { success: true };
    }

    // ========== Admin Functions ==========

    getAllFarmers() {
        if (!this.isAdmin()) {
            return { success: false, error: 'Unauthorized' };
        }
        const users = this._getUsers();
        return { success: true, farmers: users.farmers };
    }

    verifyFarmer(farmerId) {
        if (!this.isAdmin()) {
            return { success: false, error: 'Unauthorized' };
        }

        const users = this._getUsers();
        const farmerIndex = users.farmers.findIndex(f => f.id === farmerId);

        if (farmerIndex === -1) {
            return { success: false, error: 'Farmer not found' };
        }

        users.farmers[farmerIndex].verified = true;
        users.farmers[farmerIndex].verifiedAt = new Date().toISOString();
        this._saveUsers(users);

        return { success: true, farmer: users.farmers[farmerIndex] };
    }

    // ========== Utility ==========

    getFarmerById(farmerId) {
        const users = this._getUsers();
        return users.farmers.find(f => f.id === farmerId) || null;
    }

    getFarmerByPhone(phone) {
        const users = this._getUsers();
        return users.farmers.find(f => f.phone === phone) || null;
    }

    // Get farmer by either phone or ID
    getFarmerByPhoneOrId(phoneOrId) {
        const users = this._getUsers();
        return users.farmers.find(f => f.phone === phoneOrId || f.id === phoneOrId) || null;
    }
}

export const authService = new AuthService();
