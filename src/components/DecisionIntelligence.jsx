import React from 'react';
import '../styles/DecisionIntelligence.css';

/**
 * HACKATHON COMPONENT: Risk Indicator
 * Shows loss probability with color-coded visual feedback
 */
export const RiskIndicator = ({ lossProbability, riskLevel, showLabel = true }) => {
    const getRiskClass = () => {
        if (lossProbability < 30) return 'low';
        if (lossProbability < 60) return 'medium';
        return 'high';
    };

    const getRiskDotClass = () => {
        if (lossProbability < 30) return 'risk-low';
        if (lossProbability < 60) return 'risk-medium';
        return 'risk-high';
    };

    const getRiskEmoji = () => {
        if (lossProbability < 30) return '✅';
        if (lossProbability < 60) return '⚠️';
        return '❌';
    };

    return (
        <div className={`risk-indicator ${getRiskClass()}`}>
            <span className={`risk-dot ${getRiskDotClass()}`}></span>
            <span>{getRiskEmoji()} Loss Risk: {lossProbability}%</span>
            {showLabel && riskLevel && (
                <span style={{ opacity: 0.8 }}>({riskLevel})</span>
            )}
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Confidence Badge
 * Shows data quality/confidence with transparency
 */
export const ConfidenceBadge = ({ score, level, source, showTooltip = false }) => {
    const getBadgeClass = () => {
        if (score >= 80) return 'high';
        if (score >= 50) return 'medium';
        return 'low';
    };

    return (
        <div
            className={`confidence-badge ${getBadgeClass()}`}
            title={showTooltip ? source : undefined}
        >
            📊 {score}% {level && `(${level})`}
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Risk Breakdown
 * Detailed breakdown of risk factors
 */
export const RiskBreakdown = ({ riskBreakdown }) => {
    if (!riskBreakdown) return null;

    const getRiskColor = (level) => {
        if (level === 'Low') return '#16A34A';
        if (level === 'Medium') return '#F59E0B';
        return '#DC2626';
    };

    const factors = [
        { key: 'weather_risk', label: 'Weather', icon: '🌦️' },
        { key: 'market_risk', label: 'Market', icon: '💰' },
        { key: 'pest_risk', label: 'Pest', icon: '🐛' },
        { key: 'cost_risk', label: 'Cost', icon: '💸' }
    ];

    return (
        <div className="risk-breakdown">
            <div className="risk-breakdown-title">
                📊 Risk Analysis Breakdown
            </div>
            <div className="risk-factors">
                {factors.map(factor => {
                    const risk = riskBreakdown[factor.key];
                    if (!risk) return null;

                    return (
                        <div key={factor.key} className="risk-factor">
                            <div className="risk-factor-label">
                                {factor.icon} {factor.label}
                            </div>
                            <div className="risk-factor-value">
                                <span
                                    className="risk-factor-score"
                                    style={{ color: getRiskColor(risk.level) }}
                                >
                                    {risk.score}%
                                </span>
                                <span className={`risk-level-badge ${risk.level.toLowerCase()}`}>
                                    {risk.level}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Decision Grade Banner
 * Shows overall recommendation strength
 */
export const DecisionGradeBanner = ({ decisionGrade }) => {
    if (!decisionGrade) return null;

    const getBannerClass = () => {
        const strength = decisionGrade.recommendation_strength || '';
        if (strength.includes('Strongly')) return 'strongly-recommended';
        if (strength.includes('Recommended')) return 'recommended';
        if (strength.includes('Caution')) return 'consider-caution';
        return 'not-recommended';
    };

    return (
        <div className={`decision-grade-banner ${getBannerClass()}`}>
            <span>{decisionGrade.recommendation_strength}</span>
            {decisionGrade.rank && (
                <span className="rank-badge">
                    {decisionGrade.rank === 1 && '🏆'} #{decisionGrade.rank} - {decisionGrade.rank_label}
                </span>
            )}
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Explanation Card
 * Shows farmer-friendly explanations in Telugu/English
 */
export const ExplanationCard = ({ explanation, language = 'en', title }) => {
    if (!explanation) return null;

    const exp = explanation[language === 'te' ? 'explanation_te' : 'explanation_en'];
    if (!exp) return null;

    return (
        <div className="explanation-card">
            {title && (
                <div className="explanation-title">
                    💡 {title}
                </div>
            )}
            <div className={`explanation-text ${language === 'te' ? 'telugu' : ''}`}>
                {exp.short || exp}
            </div>
        </div>
    );
};

/**
 * HACKATHON COMPONENT: What-If Dropdown
 * Interactive scenario simulation interface
 */
export const WhatIfDropdown = ({ crop, recommendation, onScenarioSelect, language = 'en' }) => {
    const [isOpen, setIsOpen] = React.useState(false);

    const scenarios = [
        {
            type: 'sowing_delay',
            icon: '⏰',
            label_en: 'What if I delay sowing by 15 days?',
            label_te: '15 రోజులు ఆలస్యం చేస్తే ఏమౌతుంది?',
            params: { delay_days: 15 }
        },
        {
            type: 'rainfall_failure',
            icon: '🌵',
            label_en: 'What if no rain for 30 days?',
            label_te: '30 రోజులు వర్షం లేకపోతే?',
            params: { failure_days: 30 }
        },
        {
            type: 'fertilizer_reduction',
            icon: '💊',
            label_en: 'What if I use 30% less fertilizer?',
            label_te: '30% తక్కువ ఎరువులు వేస్తే?',
            params: { reduction_percent: 30 }
        },
        {
            type: 'pest_outbreak',
            icon: '🦗',
            label_en: 'What if pest outbreak occurs?',
            label_te: 'తెగులు వస్తే ఏమౌతుంది?',
            params: { outbreak_severity: 'moderate' }
        }
    ];

    return (
        <div className="whatif-dropdown">
            <div
                className="whatif-header"
                onClick={() => setIsOpen(!isOpen)}
            >
                <span>🔮 {language === 'te' ? 'అయితే ఏమౌతుంది?' : 'What if...?'}</span>
                <span>{isOpen ? '▲' : '▼'}</span>
            </div>
            {isOpen && (
                <div className="whatif-content">
                    <div className="whatif-options">
                        {scenarios.map(scenario => (
                            <div
                                key={scenario.type}
                                className="whatif-option"
                                onClick={() => {
                                    onScenarioSelect(scenario.type, scenario.params);
                                    setIsOpen(false);
                                }}
                            >
                                <span className="whatif-icon">{scenario.icon}</span>
                                <span>{language === 'te' ? scenario.label_te : scenario.label_en}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Scenario Result Display
 * Shows impact of what-if scenario
 */
export const ScenarioResult = ({ scenarioData, language = 'en' }) => {
    if (!scenarioData || !scenarioData.scenario) return null;

    const scenario = scenarioData.scenario;
    const explanation = language === 'te' ? scenario.explanation_te : scenario.explanation_en;

    return (
        <div className="scenario-result">
            <div className="scenario-result-title">
                ⚠️ {scenario.type.replace('_', ' ').toUpperCase()} Impact
            </div>
            <div className="scenario-impact">
                {scenario.yield_loss_percent !== undefined && (
                    <div className="impact-metric">
                        <div className="impact-label">Yield Loss</div>
                        <div className="impact-value">-{scenario.yield_loss_percent}%</div>
                    </div>
                )}
                {scenario.risk_increase_percent !== undefined && (
                    <div className="impact-metric">
                        <div className="impact-label">Risk Increase</div>
                        <div className="impact-value">+{scenario.risk_increase_percent}%</div>
                    </div>
                )}
                {scenario.cost_savings !== undefined && (
                    <div className="impact-metric">
                        <div className="impact-label">Cost Savings</div>
                        <div className="impact-value positive">₹{scenario.cost_savings}</div>
                    </div>
                )}
            </div>
            <div className="scenario-explanation">
                {explanation}
            </div>
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Confidence Metadata
 * Shows data source transparency
 */
export const ConfidenceMetadata = ({ confidenceData, language = 'en' }) => {
    if (!confidenceData) return null;

    const sources = [
        { key: 'soil', label: 'Soil', icon: '🌱' },
        { key: 'weather', label: 'Weather', icon: '🌦️' },
        { key: 'ml_prediction', label: 'AI Model', icon: '🤖' }
    ];

    return (
        <div className="confidence-metadata">
            <div className="confidence-metadata-title">
                🔍 {language === 'te' ? 'డేటా నాణ్యత' : 'Data Quality'}
            </div>
            <div className="confidence-sources">
                {sources.map(source => {
                    const data = confidenceData[source.key];
                    if (!data) return null;

                    return (
                        <div key={source.key} className="confidence-source">
                            <div className="confidence-source-label">
                                {source.icon} {source.label}
                            </div>
                            <div className="confidence-source-score">
                                {data.confidence_score}%
                            </div>
                            <div className={`confidence-source-level ${data.confidence_level}`}>
                                {data.confidence_level}
                            </div>
                        </div>
                    );
                })}
            </div>
            {confidenceData.overall && confidenceData.overall.reliability_note && (
                <div className="confidence-note">
                    {confidenceData.overall.reliability_note}
                </div>
            )}
        </div>
    );
};

/**
 * HACKATHON COMPONENT: Risk Comparison Card
 * Used for side-by-side crop comparison
 */
export const RiskComparisonCard = ({ crop, data, isBest, language = 'en', onClick }) => {
    return (
        <div
            className={`risk-comparison-card ${isBest ? 'best' : ''}`}
            onClick={onClick}
        >
            {isBest && <div className="best-badge">✨ {language === 'te' ? 'ఉత్తమం' : 'BEST'}</div>}

            <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '700' }}>
                {crop}
            </h4>

            <RiskIndicator
                lossProbability={data.loss_probability}
                riskLevel={data.risk_level}
            />

            {data.explanation_en && (
                <ExplanationCard
                    explanation={{ explanation_en: data.explanation_en, explanation_te: data.explanation_te }}
                    language={language}
                />
            )}

            <div style={{ marginTop: '10px', fontSize: '12px', color: '#6B7280' }}>
                Suitability Score: <strong>{data.suitability_score}/100</strong>
            </div>
        </div>
    );
};

export default {
    RiskIndicator,
    ConfidenceBadge,
    RiskBreakdown,
    DecisionGradeBanner,
    ExplanationCard,
    WhatIfDropdown,
    ScenarioResult,
    ConfidenceMetadata,
    RiskComparisonCard
};
