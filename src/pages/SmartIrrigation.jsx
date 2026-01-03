/**
 * Smart Irrigation - NodeMCU WiFi-Based Automatic Irrigation System
 * Supports both Serial/USB Arduino and WiFi/NodeMCU connections
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    ArrowLeft, Droplets, Zap, Activity, AlertTriangle,
    Power, Settings, Wifi, WifiOff, Gauge,
    Timer, TrendingUp, Bell, CheckCircle, ChevronRight, RefreshCw
} from 'lucide-react';
import LanguageSelector from '../components/LanguageSelector';
import './SmartIrrigation.css';

const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

const SmartIrrigation = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    // Connection state
    const [isConnected, setIsConnected] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [connectionMode, setConnectionMode] = useState('wifi'); // 'wifi' or 'serial'
    const portRef = useRef(null);
    const readerRef = useRef(null);

    // Sensor data
    const [sensorData, setSensorData] = useState({
        moisture: 0,
        moistureRaw: 0,
        status: 'unknown',
        motorOn: false,
        lastUpdate: null,
        activatedBy: '',
        alertActive: false,
        countdownRemaining: 0
    });

    // All connected devices
    const [devices, setDevices] = useState({});
    const [selectedDevice, setSelectedDevice] = useState('nodemcu-wifi');

    // Settings
    const [threshold, setThreshold] = useState(40);
    const [autoMode, setAutoMode] = useState(true);
    const [showSettings, setShowSettings] = useState(false);

    // History for chart
    const [moistureHistory, setMoistureHistory] = useState([]);
    const [alerts, setAlerts] = useState([]);

    // Demo mode
    const [demoMode, setDemoMode] = useState(false);

    const L = {
        title: lang === 'te' ? 'స్మార్ట్ నీటిపారుదల' : 'Smart Irrigation',
        subtitle: lang === 'te' ? 'IoT ఆధారిత ఆటోమేషన్' : 'IoT-Based Automation',
        connect: lang === 'te' ? 'కనెక్ట్' : 'Connect',
        disconnect: lang === 'te' ? 'డిస్‌కనెక్ట్' : 'Disconnect',
        connected: lang === 'te' ? 'కనెక్ట్ అయింది' : 'Connected',
        disconnected: lang === 'te' ? 'కనెక్ట్ కాలేదు' : 'Not Connected',
        moisture: lang === 'te' ? 'మట్టి తేమ' : 'Soil Moisture',
        pumpStatus: lang === 'te' ? 'మోటార్ స్థితి' : 'Pump Status',
        pumpOn: lang === 'te' ? 'ఆన్' : 'ON',
        pumpOff: lang === 'te' ? 'ఆఫ్' : 'OFF',
        dry: lang === 'te' ? 'పొడిగా ఉంది' : 'Dry',
        wet: lang === 'te' ? 'తడిగా ఉంది' : 'Sufficient',
        threshold: lang === 'te' ? 'థ్రెషోల్డ్' : 'Threshold',
        autoMode: lang === 'te' ? 'ఆటో' : 'Auto',
        manualMode: lang === 'te' ? 'మాన్యువల్' : 'Manual',
        turnOnPump: lang === 'te' ? 'మోటార్ ఆన్' : 'Turn ON Pump',
        turnOffPump: lang === 'te' ? 'మోటార్ ఆఫ్' : 'Turn OFF Pump',
        lastUpdate: lang === 'te' ? 'చివరి' : 'Last',
        demoMode: lang === 'te' ? 'డెమో' : 'Demo',
        history: lang === 'te' ? 'చరిత్ర' : 'History',
        settings: lang === 'te' ? 'సెట్టింగ్స్' : 'Settings',
        howToConnect: lang === 'te' ? 'కనెక్ట్ ఎలా?' : 'How to Connect',
        rawValue: lang === 'te' ? 'రా విలువ' : 'Raw Value',
        mode: lang === 'te' ? 'మోడ్' : 'Mode',
        wifiMode: lang === 'te' ? 'వైఫై (NodeMCU)' : 'WiFi (NodeMCU)',
        serialMode: lang === 'te' ? 'USB (Arduino)' : 'USB (Arduino)',
        liveData: lang === 'te' ? 'లైవ్ డేటా' : 'Live Data',
        deviceId: lang === 'te' ? 'పరికర ID' : 'Device ID',
        countdown: lang === 'te' ? 'ఆటో-స్టార్ట్' : 'Auto-start in',
        activatedBy: lang === 'te' ? 'ద్వారా' : 'By'
    };

    // NodeMCU direct connection - Fetch directly from device
    const NODEMCU_IP = '172.20.128.39';

    const connectWiFi = async () => {
        setConnectionStatus('connecting');
        setConnectionMode('wifi');
        try {
            // Fetch directly from NodeMCU
            const response = await fetch(`http://${NODEMCU_IP}/api`);
            const data = await response.json();
            if (data.moisture !== undefined) {
                updateFromNodeMCU(data);
                setIsConnected(true);
                setConnectionStatus('connected');
                // Start polling directly from NodeMCU
                startPolling();
            } else {
                throw new Error('Invalid data from NodeMCU');
            }
        } catch (error) {
            console.error('NodeMCU connection error:', error);
            // Try backend as fallback
            try {
                const backupResponse = await fetch(`${API_BASE}/irrigation`);
                const backupData = await backupResponse.json();
                if (backupData.success) {
                    setIsConnected(true);
                    setConnectionStatus('connected');
                    startBackendPolling();
                }
            } catch (e) {
                setConnectionStatus('error');
                setIsConnected(false);
            }
        }
    };

    // Update sensor data from NodeMCU response
    const updateFromNodeMCU = (data) => {
        setSensorData({
            moisture: data.moisture || 0,
            moistureRaw: data.moistureRaw || Math.floor((100 - (data.moisture || 0)) * 10.23),
            status: data.status || (data.moisture < threshold ? 'dry' : 'wet'),
            motorOn: data.motorStatus || false,
            lastUpdate: new Date(),
            activatedBy: data.activatedBy || '',
            alertActive: data.alertActive || false,
            countdownRemaining: data.countdownRemaining || 0
        });
        setMoistureHistory(prev => [...prev, { time: new Date(), value: data.moisture }].slice(-30));

        // Add alert if active
        if (data.alertActive) {
            addAlert('warning', lang === 'te' ? 'తక్కువ తేమ హెచ్చరిక!' : 'Low moisture alert!');
        }
    };

    // Poll NodeMCU directly for live data
    const pollingRef = useRef(null);
    const startPolling = () => {
        if (pollingRef.current) clearInterval(pollingRef.current);
        pollingRef.current = setInterval(async () => {
            try {
                const response = await fetch(`http://${NODEMCU_IP}/api`);
                const data = await response.json();
                if (data.moisture !== undefined) {
                    updateFromNodeMCU(data);
                }
            } catch (error) {
                console.error('NodeMCU polling error:', error);
            }
        }, 2000);
    };

    // Fallback: Poll backend API
    const startBackendPolling = () => {
        if (pollingRef.current) clearInterval(pollingRef.current);
        pollingRef.current = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE}/irrigation`);
                const data = await response.json();
                if (data.success && data.devices) {
                    setDevices(data.devices);
                    const deviceData = data.devices[selectedDevice];
                    if (deviceData) {
                        setSensorData({
                            moisture: deviceData.moisture || 0,
                            moistureRaw: Math.floor((100 - (deviceData.moisture || 0)) * 10.23),
                            status: deviceData.status || 'unknown',
                            motorOn: deviceData.motor || false,
                            lastUpdate: deviceData.updatedAt ? new Date(deviceData.updatedAt) : new Date(),
                            activatedBy: deviceData.activatedBy || '',
                            alertActive: deviceData.alertActive || false,
                            countdownRemaining: deviceData.countdownRemaining || 0
                        });
                        setMoistureHistory(prev => [...prev, { time: new Date(), value: deviceData.moisture }].slice(-30));
                    }
                }
            } catch (error) {
                console.error('Backend polling error:', error);
            }
        }, 2000);
    };

    // Web Serial API connection (Arduino USB)
    const connectToArduino = async () => {
        setConnectionMode('serial');
        if (!('serial' in navigator)) {
            alert('Web Serial API not supported. Use Chrome/Edge.');
            return;
        }
        try {
            setConnectionStatus('connecting');
            const port = await navigator.serial.requestPort();
            await port.open({ baudRate: 9600 });
            portRef.current = port;
            setIsConnected(true);
            setConnectionStatus('connected');
            const reader = port.readable.getReader();
            readerRef.current = reader;
            readSerialData(reader);
        } catch (error) {
            console.error('Connection error:', error);
            setConnectionStatus('error');
            setIsConnected(false);
        }
    };

    const readSerialData = async (reader) => {
        const decoder = new TextDecoder();
        let buffer = '';
        try {
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();
                for (const line of lines) {
                    parseArduinoData(line.trim());
                }
            }
        } catch (error) {
            disconnect();
        }
    };

    const parseArduinoData = (data) => {
        try {
            const parts = data.split(',');
            const moistureMatch = parts[0]?.match(/MOISTURE:(\d+)/);
            const rawMatch = parts[1]?.match(/RAW:(\d+)/);
            const motorMatch = parts[2]?.match(/MOTOR:(ON|OFF)/);

            if (moistureMatch) {
                const moisture = parseInt(moistureMatch[1]);
                const raw = rawMatch ? parseInt(rawMatch[1]) : 0;
                const motorOn = motorMatch ? motorMatch[1] === 'ON' : false;

                setSensorData({
                    moisture,
                    moistureRaw: raw,
                    status: moisture < threshold ? 'dry' : 'wet',
                    motorOn,
                    lastUpdate: new Date()
                });

                setMoistureHistory(prev => [...prev, { time: new Date(), value: moisture }].slice(-30));

                if (moisture < 20) {
                    addAlert('critical', lang === 'te' ? 'మట్టి చాలా పొడిగా!' : 'Critically dry!');
                }
            }
        } catch (e) { }
    };

    const disconnect = async () => {
        try {
            if (pollingRef.current) clearInterval(pollingRef.current);
            if (readerRef.current) await readerRef.current.cancel();
            if (portRef.current) await portRef.current.close();
        } catch (e) { }
        setIsConnected(false);
        setConnectionStatus('disconnected');
    };

    const sendCommand = async (command) => {
        if (!portRef.current || !isConnected) return;
        try {
            const encoder = new TextEncoder();
            const writer = portRef.current.writable.getWriter();
            await writer.write(encoder.encode(command + '\n'));
            writer.releaseLock();
        } catch (e) { }
    };

    // Direct NodeMCU pump control via HTTP
    const [pumpLoading, setPumpLoading] = useState(false);

    const turnPumpOn = async () => {
        setPumpLoading(true);
        try {
            await fetch(`http://${NODEMCU_IP}/motor/on`);
            // Immediately update local state
            setSensorData(prev => ({ ...prev, motorOn: true, activatedBy: 'FARMER' }));
            addAlert('info', lang === 'te' ? '✅ పంప్ ఆన్!' : '✅ Pump turned ON!');
        } catch (error) {
            console.error('Failed to turn on pump:', error);
            addAlert('critical', lang === 'te' ? '❌ పంప్ కనెక్ట్ కాలేదు' : '❌ Failed to connect');
        }
        setPumpLoading(false);
    };

    const turnPumpOff = async () => {
        setPumpLoading(true);
        try {
            await fetch(`http://${NODEMCU_IP}/motor/off`);
            // Immediately update local state
            setSensorData(prev => ({ ...prev, motorOn: false, activatedBy: '' }));
            addAlert('info', lang === 'te' ? '✅ పంప్ ఆఫ్!' : '✅ Pump turned OFF!');
        } catch (error) {
            console.error('Failed to turn off pump:', error);
            addAlert('critical', lang === 'te' ? '❌ పంప్ కనెక్ట్ కాలేదు' : '❌ Failed to connect');
        }
        setPumpLoading(false);
    };

    // Toggle pump (for manual mode or serial connection)
    const togglePump = () => {
        if (connectionMode === 'wifi') {
            // Use direct HTTP control for WiFi/NodeMCU
            if (sensorData.motorOn) {
                turnPumpOff();
            } else {
                turnPumpOn();
            }
        } else {
            // Use serial command for Arduino
            if (autoMode) return;
            sendCommand(sensorData.motorOn ? 'PUMP_OFF' : 'PUMP_ON');
        }
    };

    const addAlert = (type, message) => {
        setAlerts(prev => [{ id: Date.now(), type, message, time: new Date() }, ...prev].slice(0, 5));
    };

    // Demo mode
    useEffect(() => {
        if (!demoMode) return;
        const interval = setInterval(() => {
            const moisture = Math.floor(Math.random() * 100);
            setSensorData({
                moisture,
                moistureRaw: Math.floor((100 - moisture) * 10.23),
                status: moisture < threshold ? 'dry' : 'wet',
                motorOn: moisture < threshold,
                lastUpdate: new Date()
            });
            setMoistureHistory(prev => [...prev, { time: new Date(), value: moisture }].slice(-30));
        }, 2000);
        return () => clearInterval(interval);
    }, [demoMode, threshold]);

    // Auto-connect to WiFi on mount
    useEffect(() => {
        connectWiFi();
        return () => {
            if (pollingRef.current) clearInterval(pollingRef.current);
            disconnect();
        };
    }, []);

    const getMoistureColor = (value) => {
        if (value < 20) return '#EF4444';
        if (value < 40) return '#F59E0B';
        if (value < 60) return '#EAB308';
        return '#4CAF50';
    };

    return (
        <div className="irrigation-page">
            {/* Header - matches Home */}
            <header className="app-header">
                <div className="header-left">
                    <button className="back-btn" onClick={() => navigate('/home')}>
                        <ArrowLeft size={20} />
                    </button>
                    <div className="app-title">
                        <span className="title-main">💧 {L.title}</span>
                        <span className="title-sub">{L.subtitle}</span>
                    </div>
                </div>
                <div className="header-right">
                    <LanguageSelector />
                    <button className="settings-btn" onClick={() => setShowSettings(true)}>
                        <Settings size={18} />
                    </button>
                </div>
            </header>

            {/* Connection Status */}
            <div className={`connection-section ${connectionStatus}`}>
                <div className="connection-info">
                    {isConnected || demoMode ? <Wifi size={18} /> : <WifiOff size={18} />}
                    <span>{isConnected ? L.connected : demoMode ? L.demoMode : L.disconnected}</span>
                </div>
                <div className="connection-actions">
                    {isConnected || demoMode ? (
                        <>
                            <button className="refresh-btn" onClick={connectWiFi} title="Refresh">
                                <RefreshCw size={16} />
                            </button>
                            <button onClick={demoMode ? () => setDemoMode(false) : disconnect}>
                                {L.disconnect}
                            </button>
                        </>
                    ) : (
                        <>
                            <button className="primary-btn" onClick={connectWiFi}>{L.wifiMode}</button>
                            <button className="secondary-btn" onClick={connectToArduino}>{L.serialMode}</button>
                            <button className="demo-btn" onClick={() => setDemoMode(true)}>{L.demoMode}</button>
                        </>
                    )}
                </div>
            </div>

            {/* Alert Banner for Low Moisture - With Urgent Pump Control */}
            {sensorData.alertActive && (
                <div className="alert-banner">
                    <div className="alert-info">
                        <AlertTriangle size={20} />
                        <span>{lang === 'te' ? '🚨 తక్కువ తేమ!' : '🚨 LOW MOISTURE!'}</span>
                        <span className="countdown-badge">⏱️ {sensorData.countdownRemaining}s</span>
                    </div>
                    <button
                        className="urgent-pump-btn"
                        onClick={turnPumpOn}
                        disabled={pumpLoading}
                    >
                        {pumpLoading ? '⏳' : '💧'} {lang === 'te' ? 'ఇప్పుడే ఆన్!' : 'TURN ON NOW!'}
                    </button>
                </div>
            )}

            {/* Manual Pump Control Section - Always Visible */}
            {(isConnected || demoMode) && (
                <div className="pump-control-section">
                    <div className="pump-status-card">
                        <div className="pump-header">
                            <Power size={20} />
                            <span>{lang === 'te' ? 'పంప్ నియంత్రణ' : 'Pump Control'}</span>
                            {sensorData.activatedBy && (
                                <span className="activated-badge">
                                    {sensorData.activatedBy === 'AUTO' ? '🤖 Auto' :
                                        sensorData.activatedBy === 'FARMER' ? '👨‍🌾 Manual' :
                                            sensorData.activatedBy === 'MANUAL' ? '🔧 Local' : sensorData.activatedBy}
                                </span>
                            )}
                        </div>
                        <div className="pump-buttons">
                            <button
                                className={`pump-btn on ${sensorData.motorOn ? 'active' : ''}`}
                                onClick={turnPumpOn}
                                disabled={pumpLoading || sensorData.motorOn}
                            >
                                {pumpLoading ? '⏳' : '💧'} {lang === 'te' ? 'ఆన్' : 'ON'}
                            </button>
                            <button
                                className={`pump-btn off ${!sensorData.motorOn ? 'active' : ''}`}
                                onClick={turnPumpOff}
                                disabled={pumpLoading || !sensorData.motorOn}
                            >
                                {pumpLoading ? '⏳' : '🛑'} {lang === 'te' ? 'ఆఫ్' : 'OFF'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div className="irrigation-content">
                {/* Moisture Card */}
                <div className="moisture-main-card">
                    <div className="moisture-gauge" style={{ '--color': getMoistureColor(sensorData.moisture) }}>
                        <div className="gauge-circle">
                            <svg viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="45" className="gauge-bg" />
                                <circle
                                    cx="50" cy="50" r="45"
                                    className="gauge-fill"
                                    style={{ strokeDashoffset: 283 - (283 * sensorData.moisture / 100) }}
                                />
                            </svg>
                            <div className="gauge-center">
                                <Droplets size={24} color={getMoistureColor(sensorData.moisture)} />
                                <span className="gauge-value">{sensorData.moisture}%</span>
                                <span className="gauge-label">{L.moisture}</span>
                            </div>
                        </div>
                    </div>
                    <div className={`status-pill ${sensorData.status}`}>
                        {sensorData.status === 'dry' ? <AlertTriangle size={14} /> : <CheckCircle size={14} />}
                        <span>{sensorData.status === 'dry' ? L.dry : L.wet}</span>
                    </div>
                    {sensorData.lastUpdate && (
                        <p className="last-update">
                            <Timer size={12} /> {L.lastUpdate}: {sensorData.lastUpdate.toLocaleTimeString()}
                        </p>
                    )}
                </div>

                {/* Stats Cards */}
                <div className="stats-row">
                    <div className={`stat-card ${sensorData.motorOn ? 'active' : ''}`}>
                        <div className="stat-icon pump">
                            <Power size={20} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">{L.pumpStatus}</span>
                            <span className="stat-value">{sensorData.motorOn ? L.pumpOn : L.pumpOff}</span>
                        </div>
                        {sensorData.motorOn && <span className="pulse-dot" />}
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon threshold">
                            <Gauge size={20} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">{L.threshold}</span>
                            <span className="stat-value">{threshold}%</span>
                        </div>
                    </div>
                </div>

                <div className="stats-row">
                    <div className="stat-card">
                        <div className="stat-icon mode">
                            <Zap size={20} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">{L.mode}</span>
                            <span className="stat-value">{autoMode ? L.autoMode : L.manualMode}</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon raw">
                            <Activity size={20} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">{L.rawValue}</span>
                            <span className="stat-value">{sensorData.moistureRaw}</span>
                        </div>
                    </div>
                </div>

                {/* Manual Pump Control */}
                {!autoMode && (isConnected || demoMode) && (
                    <button className={`pump-control-btn ${sensorData.motorOn ? 'stop' : 'start'}`} onClick={togglePump}>
                        <Power size={20} />
                        {sensorData.motorOn ? L.turnOffPump : L.turnOnPump}
                    </button>
                )}

                {/* History Chart */}
                {moistureHistory.length > 0 && (
                    <div className="section-card">
                        <h3><TrendingUp size={16} /> {L.history}</h3>
                        <div className="mini-chart">
                            {moistureHistory.slice(-15).map((r, i) => (
                                <div
                                    key={i}
                                    className="chart-bar"
                                    style={{
                                        height: `${r.value}%`,
                                        background: getMoistureColor(r.value)
                                    }}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Alerts Section */}
                {alerts.length > 0 && (
                    <div className="section-card alerts">
                        <h3><Bell size={16} /> {lang === 'te' ? 'హెచ్చరికలు' : 'Alerts'}</h3>
                        <div className="alerts-list">
                            {alerts.map(alert => (
                                <div key={alert.id} className={`alert-item ${alert.type}`}>
                                    <AlertTriangle size={14} />
                                    <span className="alert-msg">{alert.message}</span>
                                    <span className="alert-time">{alert.time.toLocaleTimeString()}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* How to Connect */}
                {!isConnected && !demoMode && (
                    <div className="section-card help">
                        <h3>{L.howToConnect}</h3>
                        <div className="help-steps">
                            <div className="help-step">
                                <span className="step-num">1</span>
                                <p>{lang === 'te' ? 'Arduino USB కేబుల్ తో కనెక్ట్' : 'Connect Arduino via USB'}</p>
                            </div>
                            <div className="help-step">
                                <span className="step-num">2</span>
                                <p>{lang === 'te' ? '"కనెక్ట్" బటన్ నొక్కండి' : 'Click Connect button'}</p>
                            </div>
                            <div className="help-step">
                                <span className="step-num">3</span>
                                <p>{lang === 'te' ? 'COM పోర్ట్ ఎంచుకోండి' : 'Select COM port'}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Settings Modal */}
            {showSettings && (
                <div className="modal-overlay" onClick={() => setShowSettings(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <h2><Settings size={20} /> {L.settings}</h2>

                        <div className="setting-group">
                            <label>{L.threshold}</label>
                            <div className="slider-row">
                                <input
                                    type="range"
                                    min="10" max="90"
                                    value={threshold}
                                    onChange={e => setThreshold(parseInt(e.target.value))}
                                />
                                <span>{threshold}%</span>
                            </div>
                        </div>

                        <div className="setting-group">
                            <label>{L.mode}</label>
                            <div className="toggle-btns">
                                <button className={autoMode ? 'active' : ''} onClick={() => setAutoMode(true)}>
                                    {L.autoMode}
                                </button>
                                <button className={!autoMode ? 'active' : ''} onClick={() => setAutoMode(false)}>
                                    {L.manualMode}
                                </button>
                            </div>
                        </div>

                        <button className="save-btn" onClick={() => setShowSettings(false)}>
                            ✓ {lang === 'te' ? 'సేవ్' : 'Save'}
                        </button>
                    </div>
                </div>
            )}

            {/* Bottom Nav */}
            <nav className="bottom-nav">
                <button className="nav-item" onClick={() => navigate('/')}>
                    <span className="nav-icon">🏠</span>
                    <span>{lang === 'te' ? 'హోమ్' : 'Home'}</span>
                </button>
                <button className="nav-item" onClick={() => navigate('/my-crops')}>
                    <span className="nav-icon">🌾</span>
                    <span>{lang === 'te' ? 'పంటలు' : 'Crops'}</span>
                </button>
                <button className="nav-item active">
                    <span className="nav-icon">💧</span>
                    <span>{lang === 'te' ? 'నీటిపారుదల' : 'Irrigation'}</span>
                </button>
                <button className="nav-item" onClick={() => navigate('/market')}>
                    <span className="nav-icon">🛒</span>
                    <span>{lang === 'te' ? 'మార్కెట్' : 'Market'}</span>
                </button>
            </nav>
        </div>
    );
};

export default SmartIrrigation;
