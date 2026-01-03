import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

// Pages
import LoginPage from './pages/LoginPage';
import Home from './pages/Home';
import TechniquesList from './pages/TechniquesList';
import TechniqueDetail from './pages/TechniqueDetail';
import CropRecommendation from './pages/CropRecommendation';
import CropAdvisory from './pages/CropAdvisory';
import MyCrops from './pages/MyCrops';
import CropSubscribe from './pages/CropSubscribe';
import CropMonitor from './pages/CropMonitor';
import Marketplace from './pages/market/Marketplace';
import CreateListing from './pages/market/CreateListing';
import ListingDetail from './pages/market/ListingDetail';
import GuestCheckout from './pages/market/GuestCheckout';
import LedgerVerification from './pages/market/LedgerVerification';
import BuyerRegistration from './pages/market/BuyerRegistration';
import PlaceOrder from './pages/market/PlaceOrder';
import FarmerOrders from './pages/market/FarmerOrders';
import BuyerDashboard from './pages/market/BuyerDashboard';
import OrderTracking from './pages/market/OrderTracking';
import PaymentHistory from './pages/market/PaymentHistory';
import Rentals from './pages/rentals/Rentals';
import CreateRental from './pages/rentals/CreateRental';
import RentalDetail from './pages/rentals/RentalDetail';
import Wallet from './pages/wallet/Wallet';
import AdminDashboard from './pages/AdminDashboard';
import FarmerProfile from './pages/FarmerProfile';
import FarmerRegister from './pages/FarmerRegister';
import FarmerDashboard from './pages/market/FarmerDashboard';
import BankVerification from './pages/market/BankVerification';
import Cart from './pages/Cart';
import AIAssistant from './components/AIAssistant/AIAssistant';
import SmartIrrigation from './pages/SmartIrrigation';

// Styles
import './styles/design-system.css';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <div className="app">
            <Routes>
              {/* Auth Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/profile" element={<FarmerProfile />} />
              <Route path="/farmer/register" element={<FarmerRegister />} />

              {/* Main Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/home" element={<Home />} />
              <Route path="/recommend" element={<CropRecommendation />} />
              <Route path="/advisory" element={<CropAdvisory />} />

              {/* Crop Monitoring Routes */}
              <Route path="/my-crops" element={<MyCrops />} />
              <Route path="/subscribe-crop" element={<CropSubscribe />} />
              <Route path="/monitor/:subscriptionId" element={<CropMonitor />} />

              {/* Smart Irrigation - Standalone Hardware Feature */}
              <Route path="/irrigation" element={<SmartIrrigation />} />

              {/* Market Routes */}
              <Route path="/market" element={<Marketplace />} />
              <Route path="/market/create" element={<CreateListing />} />
              <Route path="/market/register" element={<BuyerRegistration />} />
              <Route path="/market/orders" element={<FarmerOrders />} />
              <Route path="/market/dashboard" element={<BuyerDashboard />} />
              <Route path="/market/order/:listingId" element={<PlaceOrder />} />
              <Route path="/market/track/:orderId" element={<OrderTracking />} />
              <Route path="/market/payments" element={<PaymentHistory />} />
              <Route path="/market/listing/:id" element={<ListingDetail />} />
              <Route path="/market/:id" element={<ListingDetail />} />
              <Route path="/verify" element={<LedgerVerification />} />
              <Route path="/checkout/guest" element={<GuestCheckout />} />
              <Route path="/wallet" element={<Wallet />} />
              <Route path="/farmer/dashboard" element={<FarmerDashboard />} />
              <Route path="/bank/verify" element={<BankVerification />} />
              <Route path="/cart" element={<Cart />} />

              {/* Rental Routes */}
              <Route path="/rentals" element={<Rentals />} />
              <Route path="/rentals/create" element={<CreateRental />} />
              <Route path="/rentals/:id" element={<RentalDetail />} />

              {/* Techniques Routes */}
              <Route path="/techniques" element={<TechniquesList />} />
              <Route path="/technique/:id" element={<TechniqueDetail />} />
            </Routes>

            {/* AI Assistant - Always available */}
            <AIAssistant />
          </div>
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
