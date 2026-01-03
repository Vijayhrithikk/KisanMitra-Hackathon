import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    ArrowLeft, Loader2, AlertTriangle, Calendar, CheckCircle,
    ChevronDown, ChevronUp, Droplets, Thermometer, Wind, Cloud,
    Search, HelpCircle, Bell, RefreshCw, Leaf, Sun, CloudRain
} from 'lucide-react';
import './CropMonitor.css';

const API_BASE = import.meta.env.VITE_ML_API_URL || 'http://localhost:8001';

const CropMonitor = () => {
    const { subscriptionId } = useParams();
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [weeklyPlan, setWeeklyPlan] = useState(null);
    const [selectedDay, setSelectedDay] = useState(0);
    const [error, setError] = useState(null);
    const [expandedSections, setExpandedSections] = useState({
        alerts: true,
        weekly: true,
        faqs: false
    });
    const [faqSearch, setFaqSearch] = useState('');
    const [searchResults, setSearchResults] = useState([]);

    // Crop icons
    const cropIcons = {
        'Paddy': '🌾', 'Rice': '🌾', 'Cotton': '🧶', 'Maize': '🌽',
        'Chilli': '🌶️', 'Groundnut': '🥜', 'Ground Nuts': '🥜',
        'Wheat': '🌾', 'Sugarcane': '🎋', 'Tomato': '🍅', 'Onion': '🧅',
        'Banana': '🍌', 'Potato': '🥔', 'Soybean': '🫘', 'Turmeric': '🌿'
    };

    // Labels
    const L = {
        loading: lang === 'te' ? 'లోడ్ అవుతోంది...' : 'Loading...',
        todayPlan: lang === 'te' ? "📋 ఈరోజు ప్లాన్" : "📋 Today's Plan",
        weatherAlerts: lang === 'te' ? '⚠️ వాతావరణ హెచ్చరికలు' : '⚠️ Weather Alerts',
        noAlerts: lang === 'te' ? 'ప్రస్తుతం హెచ్చరికలు లేవు' : 'No alerts at this time',
        weeklyPlan: lang === 'te' ? '📅 7 రోజుల ప్లాన్' : '📅 7-Day Plan',
        faqs: lang === 'te' ? '❓ సమస్యలు & పరిష్కారాలు' : '❓ Problems & Solutions',
        searchFaqs: lang === 'te' ? 'సమస్య వెతకండి...' : 'Search problems...',
        irrigation: lang === 'te' ? '💧 నీటిపారుదల' : '💧 Irrigation',
        refresh: lang === 'te' ? 'రిఫ్రెష్' : 'Refresh',
        day: lang === 'te' ? 'రోజు' : 'Day',
        action: lang === 'te' ? 'చర్య' : 'Action',
        risk: lang === 'te' ? 'ప్రమాదం' : 'Risk',
        tasks: lang === 'te' ? 'పనులు' : 'Tasks'
    };

    useEffect(() => {
        fetchMonitoringData();
    }, [subscriptionId]);

    const fetchMonitoringData = async () => {
        setLoading(true);
        try {
            // Fetch both monitoring data and weekly plan in parallel
            const [monitorRes, weeklyRes] = await Promise.all([
                fetch(`${API_BASE}/crop-monitoring/${subscriptionId}`),
                fetch(`${API_BASE}/weekly-plan/${subscriptionId}`)
            ]);

            const monitorResult = await monitorRes.json();
            const weeklyResult = await weeklyRes.json();

            if (monitorResult.success) {
                setData(monitorResult);
            }
            if (weeklyResult.success) {
                setWeeklyPlan(weeklyResult.weekly_plan);
            }

            if (!monitorResult.success && !weeklyResult.success) {
                setError('Failed to load monitoring data');
            }
        } catch (err) {
            console.error(err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const handleFaqSearch = async () => {
        if (!faqSearch.trim()) return;
        try {
            const crop = data?.subscription?.crop;
            const res = await fetch(`${API_BASE}/search-faqs?query=${encodeURIComponent(faqSearch)}&crop=${crop}`);
            const result = await res.json();
            if (result.success) {
                setSearchResults(result.results);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const toggleSection = (section) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'high': return '#ef4444';
            case 'critical': return '#dc2626';
            case 'medium': return '#f59e0b';
            default: return '#22c55e';
        }
    };

    const getWeatherIcon = (day) => {
        if (day?.weather?.rainfall_mm > 10) return '🌧️';
        if (day?.weather?.rainfall_mm > 0) return '🌦️';
        if (day?.weather?.temp_max > 38) return '🔥';
        if (day?.weather?.temp_max > 32) return '☀️';
        return '⛅';
    };

    if (loading) {
        return (
            <div className="monitor-container">
                <div className="loading-state">
                    <Loader2 className="spinner" size={48} />
                    <p>{L.loading}</p>
                </div>
            </div>
        );
    }

    if (error || (!data && !weeklyPlan)) {
        return (
            <div className="monitor-container">
                <div className="error-state">
                    <AlertTriangle size={48} />
                    <p>{error || 'Something went wrong'}</p>
                    <button onClick={() => navigate('/my-crops')}>
                        {lang === 'te' ? 'వెనుకకు వెళ్ళండి' : 'Go Back'}
                    </button>
                </div>
            </div>
        );
    }

    const { subscription, action_plan, relevant_faqs } = data || {};
    const { stage_info, alerts, today_tasks, irrigation_advice, current_weather } = action_plan || {};
    const selectedDayData = weeklyPlan?.days?.[selectedDay];

    return (
        <div className="monitor-container">
            {/* Header */}
            <div className="monitor-header">
                <button className="back-btn" onClick={() => navigate('/my-crops')}>
                    <ArrowLeft size={20} />
                </button>
                <div className="header-info">
                    <div className="crop-badge">
                        <span className="crop-icon">{cropIcons[subscription?.crop] || '🌱'}</span>
                        <div>
                            <h1>{subscription?.crop}</h1>
                            <span>{subscription?.location?.name || subscription?.locationName}</span>
                        </div>
                    </div>
                </div>
                <button className="refresh-btn" onClick={fetchMonitoringData}>
                    <RefreshCw size={18} />
                </button>
            </div>

            {/* Stage Progress Card */}
            <div className="stage-card">
                <div className="stage-header">
                    <div>
                        <span className="stage-name">{stage_info?.stage_name || weeklyPlan?.stage_info?.stage_name}</span>
                        <span className="day-badge">{L.day} {stage_info?.days_after_sowing || weeklyPlan?.stage_info?.days_after_sowing}</span>
                    </div>
                    <span className="progress-text">{stage_info?.progress_percent || 0}%</span>
                </div>
                <div className="progress-bar">
                    <div
                        className="progress-fill"
                        style={{ width: `${stage_info?.progress_percent || 0}%` }}
                    />
                </div>
                <div className="stage-dates">
                    <span>🌱 {stage_info?.sowing_date}</span>
                    <span>🌾 {stage_info?.harvest_expected}</span>
                </div>
            </div>

            {/* Current Weather Strip */}
            <div className="weather-strip">
                <div className="weather-item">
                    <Thermometer size={18} />
                    <span>{Math.round(current_weather?.temp || weeklyPlan?.current_weather?.temp || 28)}°C</span>
                </div>
                <div className="weather-item">
                    <Droplets size={18} />
                    <span>{current_weather?.humidity || weeklyPlan?.current_weather?.humidity || 60}%</span>
                </div>
                <div className="weather-item">
                    <Wind size={18} />
                    <span>{Math.round(current_weather?.wind_speed || 10)} km/h</span>
                </div>
                <div className="weather-item">
                    <Cloud size={18} />
                    <span>{current_weather?.description || 'Clear'}</span>
                </div>
            </div>

            {/* Week Summary Banner */}
            {weeklyPlan && (
                <div className={`summary-banner ${alerts?.length > 0 ? 'has-alerts' : 'no-alerts'}`}>
                    {lang === 'te' ? weeklyPlan.week_summary_te : weeklyPlan.week_summary_en}
                </div>
            )}

            {/* 7-Day Weekly Plan */}
            {weeklyPlan && (
                <div className="section">
                    <div className="section-header" onClick={() => toggleSection('weekly')}>
                        <h2>{L.weeklyPlan}</h2>
                        {expandedSections.weekly ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </div>
                    {expandedSections.weekly && (
                        <div className="section-content">
                            {/* Day Pills Navigation */}
                            <div className="day-pills">
                                {weeklyPlan.days?.map((day, i) => (
                                    <div
                                        key={i}
                                        className={`day-pill ${selectedDay === i ? 'active' : ''} ${day.weather?.rainfall_mm > 10 ? 'has-rain' : ''} ${day.priority === 'high' ? 'has-warning' : ''}`}
                                        onClick={() => setSelectedDay(i)}
                                    >
                                        <span className="day-label">{lang === 'te' ? day.day_label_te : day.day_label_en}</span>
                                        <span className="day-name">{day.day_name?.substring(0, 3)}</span>
                                        <span className="weather-icon">{getWeatherIcon(day)}</span>
                                    </div>
                                ))}
                            </div>

                            {/* Selected Day Detail Card */}
                            {selectedDayData && (
                                <div className="day-detail-card">
                                    <div className="day-detail-header">
                                        <div className="day-detail-title">
                                            <h3>{lang === 'te' ? selectedDayData.day_label_te : selectedDayData.day_label_en} - {selectedDayData.day_name}</h3>
                                            <span>{selectedDayData.date} • DAS {selectedDayData.das}</span>
                                        </div>
                                        <div className="day-weather-summary">
                                            <span className="icon">{getWeatherIcon(selectedDayData)}</span>
                                            <span className="temp">{selectedDayData.weather?.temp_max}°</span>
                                        </div>
                                    </div>

                                    {/* Daily Advice */}
                                    <div className="day-advice">
                                        <p>{lang === 'te' ? selectedDayData.advice_te : selectedDayData.advice_en}</p>
                                    </div>

                                    {/* Weather Warning */}
                                    {selectedDayData.weather_warning && (
                                        <div className="alert-card" style={{ borderLeftColor: '#ef4444', marginBottom: '1rem' }}>
                                            <div className="alert-header">
                                                <span className="alert-icon">{selectedDayData.weather_warning.icon}</span>
                                                <h3>{lang === 'te' ? selectedDayData.weather_warning.message_te : selectedDayData.weather_warning.message_en}</h3>
                                            </div>
                                        </div>
                                    )}

                                    {/* Tasks for the Day */}
                                    <div className="day-tasks-grid">
                                        {selectedDayData.tasks?.map((task, ti) => (
                                            <div key={ti} className={`day-task-item ${task.type || ''}`}>
                                                <span className="task-icon">
                                                    {task.type === 'weather' ? '🌤️' :
                                                        task.type === 'critical' ? '⚠️' :
                                                            task.type === 'scouting' ? '🔍' :
                                                                task.priority === 'high' ? '❗' : '✅'}
                                                </span>
                                                <div className="task-content">
                                                    <p>{lang === 'te' ? task.task_te : task.task_en}</p>
                                                </div>
                                            </div>
                                        ))}

                                        {/* Irrigation */}
                                        {selectedDayData.irrigation?.needed && (
                                            <div className="day-task-item weather">
                                                <span className="task-icon">💧</span>
                                                <div className="task-content">
                                                    <p>{lang === 'te' ? selectedDayData.irrigation.reason_te : selectedDayData.irrigation.reason_en}</p>
                                                    <span className="task-badge irrigation">{L.irrigation}</span>
                                                </div>
                                            </div>
                                        )}

                                        {/* Fertilizer */}
                                        {selectedDayData.fertilizer?.due && (
                                            <div className="day-task-item important">
                                                <span className="task-icon">🌱</span>
                                                <div className="task-content">
                                                    <p>{lang === 'te' ? selectedDayData.fertilizer.message_te : selectedDayData.fertilizer.message_en}</p>
                                                    <span className="task-badge fertilizer">Fertilizer</span>
                                                </div>
                                            </div>
                                        )}

                                        {/* Pest Alert */}
                                        {selectedDayData.pest_alert?.has_alert && (
                                            <div className="day-task-item critical">
                                                <span className="task-icon">🐛</span>
                                                <div className="task-content">
                                                    <p>{lang === 'te' ? selectedDayData.pest_alert.message_te : selectedDayData.pest_alert.message_en}</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Weather Alerts Section */}
            {alerts?.length > 0 && (
                <div className="section">
                    <div className="section-header" onClick={() => toggleSection('alerts')}>
                        <h2>{L.weatherAlerts}</h2>
                        {expandedSections.alerts ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </div>
                    {expandedSections.alerts && (
                        <div className="section-content">
                            {alerts.map((alert, i) => (
                                <div
                                    key={i}
                                    className="alert-card"
                                    style={{ borderLeftColor: getSeverityColor(alert.severity) }}
                                >
                                    <div className="alert-header">
                                        <span className="alert-icon">{alert.icon}</span>
                                        <h3>{lang === 'te' ? alert.title_te : alert.title_en}</h3>
                                    </div>
                                    <div className="alert-risks">
                                        <strong>{L.risk}:</strong>
                                        <ul>
                                            {(lang === 'te' ? alert.risks_te : alert.risks_en)?.map((risk, ri) => (
                                                <li key={ri}>{risk}</li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div className="alert-actions">
                                        <strong>{L.action}:</strong>
                                        <ul>
                                            {(lang === 'te' ? alert.actions_te : alert.actions_en)?.map((action, ai) => (
                                                <li key={ai}>{action}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Irrigation Card */}
            <div className="irrigation-card">
                <div className="irrigation-header">
                    <Droplets size={26} />
                    <h3>{L.irrigation}</h3>
                </div>
                <p>{lang === 'te' ? irrigation_advice?.reason_te : irrigation_advice?.reason_en}</p>
                <div className="irrigation-schedule">
                    <span>{lang === 'te' ? 'తదుపరి నీరు' : 'Next irrigation'}</span>
                    <strong>{irrigation_advice?.next_irrigation}</strong>
                </div>
            </div>

            {/* FAQs Section */}
            <div className="section">
                <div className="section-header" onClick={() => toggleSection('faqs')}>
                    <h2>{L.faqs}</h2>
                    {expandedSections.faqs ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
                {expandedSections.faqs && (
                    <div className="section-content">
                        {/* FAQ List - All FAQs displayed as accordion */}
                        <div className="faq-list">
                            {relevant_faqs?.length > 0 ? (
                                relevant_faqs.map((faq, i) => (
                                    <details key={i} className="faq-item">
                                        <summary>
                                            <HelpCircle size={16} />
                                            <span>{lang === 'te' ? faq.question_te : faq.question_en}</span>
                                        </summary>
                                        <div className="faq-answer">
                                            <p>{lang === 'te' ? faq.answer_te : faq.answer_en}</p>
                                            {faq.action_en && (
                                                <div className="faq-action">
                                                    <strong>{lang === 'te' ? 'చర్య:' : 'Action:'}</strong>
                                                    <p>{lang === 'te' ? faq.action_te : faq.action_en}</p>
                                                </div>
                                            )}
                                            {faq.urgency === 'high' && (
                                                <div className="urgency-badge">
                                                    ⚠️ {lang === 'te' ? 'అత్యవసరం' : 'Urgent'}
                                                </div>
                                            )}
                                        </div>
                                    </details>
                                ))
                            ) : (
                                <p className="no-faqs">{lang === 'te' ? 'ఈ దశకు సంబంధించిన FAQలు లేవు' : 'No FAQs for this stage'}</p>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CropMonitor;
