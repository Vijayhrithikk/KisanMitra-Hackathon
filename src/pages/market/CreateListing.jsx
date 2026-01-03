import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { marketService } from '../../services/marketService';
import formAutomator from '../../services/formAutomator';
import { Upload, Cpu, ShieldCheck, Loader, CheckCircle, ArrowLeft, Edit2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import FarmerHeader from '../../components/ui/FarmerHeader';
import './Market.css';

const CreateListing = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { user, isLoggedIn } = useAuth();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    // Removed auto-redirect - let user see the form
    // Will check auth when they try to submit

    const [formData, setFormData] = useState({
        crop: '',
        variety: '',
        quantity: '',
        unit: 'Quintal',
        price: '',
        state: 'Andhra Pradesh',
        district: 'Guntur',
        city: '',
        contactName: '',
        contactPhone: '',
        fertilizers: '',
        pesticides: '',
        notes: ''
    });

    // Sync form with user profile when user loads
    useEffect(() => {
        if (user) {
            setFormData(prev => ({
                ...prev,
                state: user.state || prev.state,
                district: user.district || prev.district,
                city: user.village || prev.city,
                contactName: user.name || prev.contactName,
                contactPhone: user.phone || prev.contactPhone
            }));
        }
    }, [user]);

    // Auto-fill from AI Assistant data
    useEffect(() => {
        const pendingData = formAutomator.getPendingListing();
        if (pendingData) {
            setFormData(prev => ({
                ...prev,
                crop: pendingData.crop || prev.crop,
                quantity: pendingData.quantity?.toString() || prev.quantity,
                price: pendingData.price?.toString() || prev.price,
                variety: pendingData.variety || prev.variety,
                unit: pendingData.unit || prev.unit
            }));

            // Clear after filling
            setTimeout(() => {
                formAutomator.clearPendingListing();
            }, 1000);
        }
    }, []);

    const [aiPrice, setAiPrice] = useState(null);
    const [loadingAi, setLoadingAi] = useState(false);
    const [publishing, setPublishing] = useState(false);
    const [publishResult, setPublishResult] = useState(null);
    const [images, setImages] = useState([]);
    const [editMode, setEditMode] = useState(false);
    const [editListingId, setEditListingId] = useState(null);
    const [loadingEdit, setLoadingEdit] = useState(false);
    const [searchParams] = useSearchParams();

    // Check if we're in edit mode - load from database
    useEffect(() => {
        const editId = searchParams.get('edit');

        if (editId) {
            setEditMode(true);
            setEditListingId(editId);
            loadListingFromDatabase(editId);
        }
    }, [searchParams]);

    // Load existing listing from DATABASE for editing
    const loadListingFromDatabase = async (listingId) => {
        setLoadingEdit(true);
        try {
            console.log('📋 Loading listing from database:', listingId);
            const listing = await marketService.getListingById(listingId);

            if (listing) {
                console.log('✅ Loaded listing:', listing);
                setFormData({
                    crop: listing.crop || '',
                    variety: listing.variety || '',
                    quantity: listing.quantity?.toString() || '',
                    unit: listing.unit || 'Quintal',
                    price: listing.price?.toString() || '',
                    state: listing.location?.state || listing.state || 'Andhra Pradesh',
                    district: listing.location?.district || listing.district || 'Guntur',
                    city: listing.location?.city || listing.city || '',
                    contactName: listing.contact?.name || listing.farmerName || '',
                    contactPhone: listing.contact?.phone || listing.farmerPhone || '',
                    fertilizers: listing.fertilizers || '',
                    pesticides: listing.pesticides || '',
                    notes: listing.notes || listing.description || ''
                });

                if (listing.images && listing.images.length > 0) {
                    setImages(listing.images);
                }
            } else {
                alert(lang === 'te' ? 'లిస్టింగ్ కనుగొనబడలేదు' : 'Listing not found');
                navigate('/farmer/dashboard');
            }
        } catch (error) {
            console.error('Error loading listing from database:', error);
            alert(lang === 'te' ? 'లిస్టింగ్ లోడ్ చేయడంలో విఫలమైంది' : 'Failed to load listing');
        } finally {
            setLoadingEdit(false);
        }
    };

    // Handle image upload
    const handleImageUpload = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImages(prev => [...prev, {
                    name: file.name,
                    data: reader.result,
                    type: file.type
                }]);
            };
            reader.readAsDataURL(file);
        });
    };

    // Remove image
    const removeImage = (index) => {
        setImages(prev => prev.filter((_, i) => i !== index));
    };

    // Comprehensive crop options with Telugu translations
    const cropOptions = {
        // Grains
        'Rice': lang === 'te' ? 'వరి (Paddy)' : 'Rice (Paddy)',
        'Wheat': lang === 'te' ? 'గోధుమ' : 'Wheat',
        'Maize': lang === 'te' ? 'మొక్కజొన్న' : 'Maize',
        'Jowar': lang === 'te' ? 'జొన్న' : 'Jowar (Sorghum)',
        'Bajra': lang === 'te' ? 'సజ్జ' : 'Bajra (Pearl Millet)',
        'Ragi': lang === 'te' ? 'రాగి' : 'Ragi (Finger Millet)',

        // Pulses
        'Toor Dal': lang === 'te' ? 'కందిపప్పు' : 'Toor Dal (Pigeon Pea)',
        'Moong Dal': lang === 'te' ? 'పెసలు' : 'Moong Dal (Green Gram)',
        'Urad Dal': lang === 'te' ? 'మినుములు' : 'Urad Dal (Black Gram)',
        'Chana Dal': lang === 'te' ? 'శనగలు' : 'Chana Dal (Bengal Gram)',
        'Red Gram': lang === 'te' ? 'ఎర్ర కందులు' : 'Red Gram',

        // Vegetables
        'Tomato': lang === 'te' ? 'టమాటా' : 'Tomato',
        'Potato': lang === 'te' ? 'ఆలూగడ్డ' : 'Potato',
        'Onion': lang === 'te' ? 'ఉల్లిపాయ' : 'Onion',
        'Cabbage': lang === 'te' ? 'క్యాబేజీ' : 'Cabbage',
        'Cauliflower': lang === 'te' ? 'కాలీఫ్లవర్' : 'Cauliflower',
        'Brinjal': lang === 'te' ? 'వంకాయ' : 'Brinjal (Eggplant)',
        'Okra': lang === 'te' ? 'బెండకాయ' : 'Okra (Ladyfinger)',
        'Carrot': lang === 'te' ? 'క్యారెట్' : 'Carrot',
        'Beetroot': lang === 'te' ? 'బీట్‌రూట్' : 'Beetroot',
        'Radish': lang === 'te' ? 'ముల్లంగి' : 'Radish',
        'Pumpkin': lang === 'te' ? 'గుమ్మడికాయ' : 'Pumpkin',
        'Bottle Gourd': lang === 'te' ? 'సొరకాయ' : 'Bottle Gourd',
        'Ridge Gourd': lang === 'te' ? 'బీరకాయ' : 'Ridge Gourd',
        'Bitter Gourd': lang === 'te' ? 'కాకరకాయ' : 'Bitter Gourd',
        'Cucumber': lang === 'te' ? 'దోసకాయ' : 'Cucumber',
        'Beans': lang === 'te' ? 'బీన్స్' : 'Beans',
        'Spinach': lang === 'te' ? 'పాలకూర' : 'Spinach',
        'Coriander': lang === 'te' ? 'కొత్తిమీర' : 'Coriander',
        'Curry Leaves': lang === 'te' ? 'కరివేపాకు' : 'Curry Leaves',
        'Green Chilli': lang === 'te' ? 'మిర్చి (పచ్చ)' : 'Green Chilli',
        'Capsicum': lang === 'te' ? 'క్యాప్సికం' : 'Capsicum (Bell Pepper)',
        'Drumstick': lang === 'te' ? 'మునగకాయ' : 'Drumstick',

        // Fruits
        'Mango': lang === 'te' ? 'మామిడి' : 'Mango',
        'Banana': lang === 'te' ? 'అరటి' : 'Banana',
        'Papaya': lang === 'te' ? 'బొప్పాయి' : 'Papaya',
        'Guava': lang === 'te' ? 'జామపండు' : 'Guava',
        'Pomegranate': lang === 'te' ? 'దానిమ్మ' : 'Pomegranate',
        'Grapes': lang === 'te' ? 'ద్రాక్ష' : 'Grapes',
        'Orange': lang === 'te' ? 'నారింజ' : 'Orange',
        'Lemon': lang === 'te' ? 'నిమ్మకాయ' : 'Lemon',
        'Watermelon': lang === 'te' ? 'పుచ్చకాయ' : 'Watermelon',
        'Muskmelon': lang === 'te' ? 'ఖర్బూజ' : 'Muskmelon',
        'Apple': lang === 'te' ? 'ఆపిల్' : 'Apple',
        'Custard Apple': lang === 'te' ? 'సీతాఫలం' : 'Custard Apple',
        'Coconut': lang === 'te' ? 'కొబ్బరి' : 'Coconut',
        'Jackfruit': lang === 'te' ? 'పనస' : 'Jackfruit',
        'Pineapple': lang === 'te' ? 'అనాస' : 'Pineapple',
        'Sapota': lang === 'te' ? 'సపోటా' : 'Sapota (Chikoo)',

        // Cash Crops
        'Cotton': lang === 'te' ? 'పత్తి' : 'Cotton',
        'Sugarcane': lang === 'te' ? 'చెరకు' : 'Sugarcane',
        'Turmeric': lang === 'te' ? 'పసుపు' : 'Turmeric',
        'Ginger': lang === 'te' ? 'అల్లం' : 'Ginger',
        'Garlic': lang === 'te' ? 'వెల్లుల్లి' : 'Garlic',
        'Red Chilli': lang === 'te' ? 'ఎర్రమిర్చి' : 'Red Chilli',
        'Groundnut': lang === 'te' ? 'వేరుశనగ' : 'Groundnut (Peanut)',
        'Sunflower': lang === 'te' ? 'సూర్యకాంతి' : 'Sunflower',
        'Castor': lang === 'te' ? 'ఆముదం' : 'Castor'
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleGetAiPrice = async () => {
        if (!formData.crop) return alert(lang === 'te' ? 'దయచేసి ముందుగా పంట ఎంచుకోండి' : 'Please select a crop first');
        setLoadingAi(true);
        try {
            const location = { state: formData.state, district: formData.district };
            const result = await marketService.getAIPriceSuggestion(formData.crop, location, formData.unit);
            setAiPrice(result);
            setFormData(prev => ({ ...prev, price: result.price }));
        } catch (error) {
            console.error(error);
        } finally {
            setLoadingAi(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Check auth when submitting
        if (!isLoggedIn) {
            alert(lang === 'te' ? 'దయచేసి లాగిన్ అవ్వండి' : 'Please login to create a listing');
            navigate('/login');
            return;
        }

        setPublishing(true);

        try {
            const listingPayload = {
                ...formData,
                images: images,
                farmerId: user?.id || 'ANONYMOUS',
                farmerName: user?.name || formData.contactName,
                farmerPhone: user?.phone || formData.contactPhone,
                farmerVerified: user?.verified || false,
                location: {
                    state: formData.state,
                    district: formData.district,
                    city: formData.city
                },
                contact: {
                    name: formData.contactName,
                    phone: formData.contactPhone
                }
            };

            let result;
            if (editMode && editListingId) {
                // UPDATE existing listing in database
                console.log('📝 Updating listing in database:', editListingId);
                result = await marketService.updateListing(editListingId, listingPayload);
                if (result.success) {
                    result.listingId = editListingId;
                    result.hash = 'Updated';
                    result.txHash = `UPDATE-${Date.now()}`;
                }
            } else {
                // CREATE new listing in database
                console.log('➕ Creating new listing in database');
                result = await marketService.createListing(listingPayload);
            }

            setPublishResult(result);
            setTimeout(() => navigate('/farmer/dashboard'), 2000);
        } catch (error) {
            console.error('Submit error:', error);
            alert(lang === 'te' ? 'జాబితా సేవ్ చేయడంలో విఫలమైంది' : 'Failed to save listing');
        } finally {
            setPublishing(false);
        }
    };

    if (publishResult) {
        return (
            <div className="market-container success-view">
                <div className="success-card">
                    <CheckCircle size={64} color="#16a34a" />
                    <h2>{lang === 'te' ? 'లెడ్జర్‌లో జాబితా ప్రచురించబడింది!' : 'Listing Published to Ledger!'}</h2>
                    <div className="hash-display">
                        <p><strong>{lang === 'te' ? 'లిస్టింగ్ ID:' : 'Listing ID:'}</strong> {publishResult.listingId}</p>
                        <p><strong>{lang === 'te' ? 'మార్చలేని హాష్ (SHA-256):' : 'Immutable Hash (SHA-256):'}</strong></p>
                        <code className="hash-code">{publishResult.hash}</code>
                        <p><strong>{lang === 'te' ? 'లావాదేవీ హాష్:' : 'Transaction Hash:'}</strong></p>
                        <code className="hash-code">{publishResult.txHash}</code>
                    </div>
                    <p>{lang === 'te' ? 'మార్కెట్‌ప్లేస్‌కు దారి మళ్ళిస్తోంది...' : 'Redirecting to Marketplace...'}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="market-container">
            {/* Add FarmerHeader for logged-in farmers */}
            {isLoggedIn && <FarmerHeader />}

            <button className="back-btn" onClick={() => navigate('/farmer/dashboard')} style={{ marginTop: isLoggedIn ? '70px' : '0' }}>
                <ArrowLeft size={18} /> {t('common.back', 'Back')}
            </button>

            <header className="market-header">
                <h1>
                    {editMode ? (
                        <><Edit2 size={24} /> {lang === 'te' ? 'లిస్టింగ్ సవరించండి' : 'Edit Listing'}</>
                    ) : (
                        t('market.createListing.title', 'Sell Your Crop')
                    )}
                </h1>
                <p>{editMode
                    ? (lang === 'te' ? 'మీ లిస్టింగ్ వివరాలను నవీకరించండి' : 'Update your listing details')
                    : t('market.createListing.subtitle', 'Create an immutable listing on the decentralized ledger.')}
                </p>
            </header>

            <div className="create-listing-grid">
                <form onSubmit={handleSubmit} className="listing-form-container">
                    {/* Section 1: Crop Details */}
                    <div className="form-card">
                        <h3 className="form-card-title">{t('market.createListing.cropDetails', 'Crop Details')}</h3>
                        <div className="form-group">
                            <label>{t('market.createListing.cropType', 'Crop Type')}</label>
                            <select name="crop" value={formData.crop} onChange={handleChange} required>
                                <option value="">{t('market.createListing.selectCrop', 'Select Crop')}</option>
                                {Object.entries(cropOptions).map(([value, label]) => (
                                    <option key={value} value={value}>{label}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label>{t('market.createListing.variety', 'Variety / Grade')}</label>
                            <input
                                type="text"
                                name="variety"
                                placeholder={lang === 'te' ? 'ఉదా., సోనా మసూరి, గ్రేడ్ A' : 'e.g., Sona Masoori, Grade A'}
                                value={formData.variety}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>{t('market.createListing.quantity', 'Quantity')}</label>
                                <input
                                    type="number"
                                    name="quantity"
                                    value={formData.quantity}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>{t('market.createListing.unit', 'Unit')}</label>
                                <select name="unit" value={formData.unit} onChange={handleChange}>
                                    <option value="Quintal">{lang === 'te' ? 'క్వింటాల్' : 'Quintal'}</option>
                                    <option value="Kg">{lang === 'te' ? 'కేజీ' : 'Kg'}</option>
                                    <option value="Ton">{lang === 'te' ? 'టన్' : 'Ton'}</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Section 2: Location */}
                    <div className="form-card">
                        <h3 className="form-card-title">{t('market.createListing.location', 'Location')}</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label>{t('market.createListing.state', 'State')}</label>
                                <input
                                    type="text"
                                    name="state"
                                    value={formData.state}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>{t('market.createListing.district', 'District')}</label>
                                <input
                                    type="text"
                                    name="district"
                                    value={formData.district}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label>{t('market.createListing.city', 'City / Village')}</label>
                            <input
                                type="text"
                                name="city"
                                placeholder={lang === 'te' ? 'ఉదా., తెనాలి' : 'e.g., Tenali'}
                                value={formData.city}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {/* Section 3: Farming Details */}
                    <div className="form-card">
                        <h3 className="form-card-title">{t('market.createListing.farmingDetails', 'Farming Details')}</h3>
                        <div className="form-group">
                            <label>{t('market.createListing.fertilizers', 'Fertilizers Used')}</label>
                            <textarea
                                name="fertilizers"
                                placeholder={lang === 'te' ? 'ఉదా., యూరియా, DAP, సేంద్రీయ ఎరువులు' : 'e.g., Urea, DAP, Organic Manure'}
                                value={formData.fertilizers}
                                onChange={handleChange}
                                rows="2"
                                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                            />
                        </div>
                        <div className="form-group">
                            <label>{t('market.createListing.pesticides', 'Pesticides Used')}</label>
                            <textarea
                                name="pesticides"
                                placeholder={lang === 'te' ? 'ఉదా., వేప నూనె, రసాయన పురుగుమందులు' : 'e.g., Neem Oil, Chemical Pesticides'}
                                value={formData.pesticides}
                                onChange={handleChange}
                                rows="2"
                                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                            />
                        </div>
                    </div>

                    {/* Section 3: Contact */}
                    <div className="form-card">
                        <h3 className="form-card-title">{t('market.createListing.contactInfo', 'Contact Info')}</h3>
                        <div className="form-group">
                            <label>{t('market.createListing.farmerName', 'Farmer Name')}</label>
                            <input
                                type="text"
                                name="contactName"
                                placeholder={lang === 'te' ? 'మీ పేరు' : 'Your Name'}
                                value={formData.contactName}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>{t('market.createListing.phoneNumber', 'Phone Number')}</label>
                            <input
                                type="tel"
                                name="contactPhone"
                                placeholder="+91 XXXXX XXXXX"
                                value={formData.contactPhone}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {/* Section 4: Price & Media */}
                    <div className="form-card">
                        <h3 className="form-card-title">{t('market.createListing.pricing', 'Pricing & Media')}</h3>
                        <div className="form-group ai-price-section">
                            <label>{t('market.createListing.askingPrice', 'Asking Price (₹)')}</label>
                            <div className="price-input-wrapper">
                                <input
                                    type="number"
                                    name="price"
                                    value={formData.price}
                                    onChange={handleChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="ai-btn"
                                    onClick={handleGetAiPrice}
                                    disabled={loadingAi}
                                >
                                    {loadingAi ? <Loader className="spin" size={16} /> : <Cpu size={16} />}
                                    {t('market.createListing.getAiPrice', 'Get AI Price')}
                                </button>
                            </div>
                            {aiPrice && (
                                <div className="ai-suggestion">
                                    <small>✨ {lang === 'te' ? 'AI సూచన' : 'AI Suggestion'}: ₹{aiPrice.price} ({lang === 'te' ? 'విశ్వాసం' : 'Confidence'}: {(aiPrice.confidence * 100).toFixed(0)}%)</small>
                                    <small>{aiPrice.reasoning}</small>
                                </div>
                            )}
                        </div>

                        <div className="form-group">
                            <label>{t('market.createListing.uploadPhotos', 'Upload Photos')}</label>
                            <div
                                className="file-upload-box"
                                onClick={() => document.getElementById('crop-images').click()}
                            >
                                <input
                                    id="crop-images"
                                    type="file"
                                    accept="image/*"
                                    multiple
                                    onChange={handleImageUpload}
                                    style={{ display: 'none' }}
                                />
                                <Upload size={24} />
                                <p>{lang === 'te' ? 'పంట చిత్రాలను అప్‌లోడ్ చేయడానికి క్లిక్ చేయండి' : 'Click to upload crop images'}</p>
                                <small>{lang === 'te' ? 'JPG, PNG (గరిష్టంగా 5 చిత్రాలు)' : 'JPG, PNG (max 5 images)'}</small>
                            </div>
                            {images.length > 0 && (
                                <div className="image-previews">
                                    {images.map((img, idx) => (
                                        <div key={idx} className="image-preview">
                                            <img src={img.data} alt={img.name} />
                                            <button type="button" onClick={() => removeImage(idx)}>×</button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    <button type="submit" className="submit-btn" disabled={publishing}>
                        {publishing ? (
                            <>
                                <Loader className="spin" size={18} /> {t('market.createListing.hashing', 'Hashing & Pinning...')}
                            </>
                        ) : (
                            <>
                                <ShieldCheck size={18} /> {t('market.createListing.publish', 'Publish to Ledger')}
                            </>
                        )}
                    </button>
                </form>

                <div className="info-sidebar">
                    <div className="info-card">
                        <h3><ShieldCheck size={20} /> {lang === 'te' ? 'వికేంద్రీకృత హామీ' : 'Decentralized Guarantee'}</h3>
                        <p>{lang === 'te' ? 'మీ జాబితా క్రిప్టోగ్రాఫిక్‌గా హాష్ చేయబడి IPFS కు పిన్ చేయబడుతుంది. కొనుగోలుదారులు ధృవీకరించగల మార్చలేని రికార్డును ఇది సృష్టిస్తుంది.' : 'Your listing will be cryptographically hashed and pinned to IPFS. This creates an immutable record that buyers can verify.'}</p>
                    </div>
                    <div className="info-card">
                        <h3><Cpu size={20} /> {lang === 'te' ? 'AI ధర నిర్ణయం' : 'AI Pricing'}</h3>
                        <p>{lang === 'te' ? 'మా AI స్థానిక మార్కెట్ ధోరణులు, వాతావరణ ప్రభావం మరియు చారిత్రక డేతాను విశ్లేషించి మీ పంటకు ఉత్తమ ధరను సూచిస్తుంది.' : 'Our AI analyzes local market trends, weather impact, and historical data to suggest the best price for your crop.'}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CreateListing;
