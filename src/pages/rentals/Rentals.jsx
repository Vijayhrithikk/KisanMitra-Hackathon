import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { rentalService, RENTAL_CATEGORIES } from '../../services/rentalService';
import { ArrowLeft, MapPin, Search, Filter, Phone, Clock, ChevronRight, Navigation, Loader2 } from 'lucide-react';
import './Rentals.css';

const Rentals = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [userLocation, setUserLocation] = useState(null);
    const [rentals, setRentals] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('ALL');
    const [isSearching, setIsSearching] = useState(false);
    const [searchPhase, setSearchPhase] = useState(0);
    const [locationError, setLocationError] = useState(null);
    const [searchRadius] = useState(200);

    const searchPhases = [
        t('rentals.searchPhases.detecting', 'Detecting your location...'),
        t('rentals.searchPhases.scanning', 'Scanning 200km radius...'),
        t('rentals.searchPhases.finding', 'Finding available rentals...'),
        t('rentals.searchPhases.matching', 'Matching equipment nearby...'),
        t('rentals.searchPhases.almost', 'Almost there...')
    ];

    useEffect(() => {
        detectLocation();
    }, []);

    const detectLocation = () => {
        setIsSearching(true);
        setSearchPhase(0);
        setRentals([]);

        const phaseInterval = setInterval(() => {
            setSearchPhase(prev => {
                if (prev < searchPhases.length - 1) return prev + 1;
                return prev;
            });
        }, 500);

        if (!navigator.geolocation) {
            clearInterval(phaseInterval);
            setLocationError('Geolocation not supported');
            setIsSearching(false);
            performSearch(17.3850, 78.4867);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                clearInterval(phaseInterval);
                const { latitude, longitude } = position.coords;
                setUserLocation({ lat: latitude, lng: longitude });
                performSearch(latitude, longitude);
            },
            (error) => {
                clearInterval(phaseInterval);
                console.error('Location error:', error);
                setLocationError('Location access denied. Showing results from Hyderabad.');
                setUserLocation({ lat: 17.3850, lng: 78.4867 });
                performSearch(17.3850, 78.4867);
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    };

    const performSearch = async (lat, lng, category = selectedCategory) => {
        setIsSearching(true);
        try {
            const results = await rentalService.searchNearby(lat, lng, searchRadius, category === 'ALL' ? null : category);
            setRentals(results);
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            setIsSearching(false);
        }
    };

    const handleCategoryChange = (categoryId) => {
        setSelectedCategory(categoryId);
        if (userLocation) {
            performSearch(userLocation.lat, userLocation.lng, categoryId);
        }
    };

    const getCategoryInfo = (categoryId) => {
        return RENTAL_CATEGORIES[categoryId] || { icon: '📦', name: categoryId, color: '#666' };
    };

    const getCategoryName = (categoryId) => {
        const categoryKeys = {
            'TRACTOR': 'rentals.categories.tractor',
            'EQUIPMENT': 'rentals.categories.equipment',
            'COLD_STORAGE': 'rentals.categories.coldStorage',
            'GODOWN': 'rentals.categories.godown',
            'DRONE': 'rentals.categories.drone',
            'TRANSPORT': 'rentals.categories.transport',
            'HARVESTER': 'rentals.categories.harvester',
            'IRRIGATION': 'rentals.categories.irrigation'
        };
        return t(categoryKeys[categoryId] || categoryId, getCategoryInfo(categoryId).name);
    };

    return (
        <div className="rentals-container">
            {/* Header */}
            <header className="rentals-header">
                <button className="back-btn" onClick={() => navigate('/home')}>
                    <ArrowLeft size={18} />
                </button>
                <div className="header-content">
                    <h1>{t('rentals.title', 'Kisan Rentals')}</h1>
                    <p>{t('rentals.subtitle', 'Farm equipment & services near you')}</p>
                </div>
                <button className="add-btn" onClick={() => navigate('/rentals/create')}>
                    {t('rentals.list', '+ List')}
                </button>
            </header>

            {/* Location Bar */}
            <div className="location-bar">
                <div className="location-info">
                    <Navigation size={16} />
                    <span>
                        {userLocation ?
                            t('rentals.searchingRadius', 'Searching within 200km') :
                            t('rentals.detectingLocation', 'Detecting location...')
                        }
                    </span>
                </div>
                <button className="refresh-location" onClick={detectLocation}>
                    <MapPin size={14} /> {t('common.refresh', 'Refresh')}
                </button>
            </div>

            {locationError && (
                <div className="location-error">
                    <span>{locationError}</span>
                </div>
            )}

            {/* Rapido-style Search Animation */}
            {isSearching && (
                <div className="search-animation">
                    <div className="radar-container">
                        <div className="radar-ring ring-1"></div>
                        <div className="radar-ring ring-2"></div>
                        <div className="radar-ring ring-3"></div>
                        <div className="radar-center">
                            <MapPin size={24} />
                        </div>
                        <div className="radar-sweep"></div>

                        <div className="rental-dot dot-1">🚜</div>
                        <div className="rental-dot dot-2">❄️</div>
                        <div className="rental-dot dot-3">🚁</div>
                        <div className="rental-dot dot-4">🏭</div>
                    </div>
                    <p className="search-status">{searchPhases[searchPhase]}</p>
                    <div className="search-progress">
                        <div className="progress-bar" style={{ width: `${(searchPhase + 1) / searchPhases.length * 100}%` }}></div>
                    </div>
                </div>
            )}

            {/* Category Filters */}
            {!isSearching && (
                <>
                    <div className="category-filters">
                        <button
                            className={`category-chip ${selectedCategory === 'ALL' ? 'active' : ''}`}
                            onClick={() => handleCategoryChange('ALL')}
                        >
                            {t('common.all', 'All')}
                        </button>
                        {Object.values(RENTAL_CATEGORIES).map(cat => (
                            <button
                                key={cat.id}
                                className={`category-chip ${selectedCategory === cat.id ? 'active' : ''}`}
                                onClick={() => handleCategoryChange(cat.id)}
                                style={{ '--cat-color': cat.color }}
                            >
                                <span>{cat.icon}</span> {getCategoryName(cat.id)}
                            </button>
                        ))}
                    </div>

                    {/* Results Count */}
                    <div className="results-header">
                        <span className="results-count">
                            {rentals.length} {t('rentals.foundNearby', 'rentals found nearby')}
                        </span>
                    </div>

                    {/* Rental Cards */}
                    <div className="rentals-list">
                        {rentals.length === 0 ? (
                            <div className="no-results">
                                <p>{t('rentals.noRentals', 'No rentals found in your area.')}</p>
                                <button onClick={() => navigate('/rentals/create')}>
                                    {t('rentals.beFirst', 'Be the first to list!')}
                                </button>
                            </div>
                        ) : (
                            rentals.map(rental => (
                                <Link
                                    key={rental.id}
                                    to={`/rentals/${rental.id}`}
                                    className="rental-card"
                                >
                                    <div className="rental-category-badge" style={{ background: getCategoryInfo(rental.category).color }}>
                                        <span>{getCategoryInfo(rental.category).icon}</span>
                                    </div>

                                    <div className="rental-content">
                                        <div className="rental-top">
                                            <h3>{rental.title}</h3>
                                            <span className={`availability-badge ${rental.available ? 'available' : 'unavailable'}`}>
                                                {rental.available ? t('common.available', 'Available') : t('common.booked', 'Booked')}
                                            </span>
                                        </div>

                                        <p className="rental-desc">{rental.description}</p>

                                        <div className="rental-meta">
                                            <span className="distance">
                                                <MapPin size={12} /> {rental.distance} {t('common.kmAway', 'km away')}
                                            </span>
                                            <span className="location">
                                                {rental.location.city}, {rental.location.district}
                                            </span>
                                        </div>

                                        <div className="rental-pricing">
                                            <div className="price-tag daily">
                                                <span className="price">₹{rental.dailyRate?.toLocaleString()}</span>
                                                <span className="period">{t('common.perDay', '/day')}</span>
                                            </div>
                                            {rental.monthlyRate && (
                                                <div className="price-tag monthly">
                                                    <span className="price">₹{rental.monthlyRate?.toLocaleString()}</span>
                                                    <span className="period">{t('common.perMonth', '/month')}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div className="rental-arrow">
                                        <ChevronRight size={20} />
                                    </div>
                                </Link>
                            ))
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

export default Rentals;
