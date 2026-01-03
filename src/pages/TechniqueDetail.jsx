import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Volume2, AlertTriangle, CheckCircle, HelpCircle, Droplets, TrendingUp, DollarSign } from 'lucide-react';
import { techniques } from '../data/techniques';
import './TechniqueDetail.css';

const TechniqueDetail = () => {
    const { t, i18n } = useTranslation();
    const { id } = useParams();
    const navigate = useNavigate();

    // Use language from i18n (te or en)
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const technique = techniques.find(t => t.id === id);

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [id]);

    if (!technique) return <div>{t('common.loading', 'Technique not found')}</div>;

    const content = technique.content[lang] || technique.content['en'];

    return (
        <div className="technique-detail-page">
            <div className="detail-header">
                <button className="back-btn" onClick={() => navigate(-1)}>
                    <ArrowLeft size={24} />
                </button>
                <button className="audio-btn">
                    <Volume2 size={24} />
                    <span>{lang === 'te' ? 'వినండి' : 'Listen'}</span>
                </button>
            </div>

            <div className="hero-image">
                <img src={technique.image} alt={technique.title[lang] || technique.title.en} />
                <div className="hero-overlay">
                    <h1>{technique.title[lang] || technique.title.en}</h1>
                </div>
            </div>

            <div className="detail-content container">
                <section className="summary-section">
                    <p className="lead-text">{content.whatIsIt}</p>
                    <div className="why-box">
                        <h3>{lang === 'te' ? 'రైతులకు ఇది ఎందుకు అవసరం?' : 'Why Do Farmers Need This?'}</h3>
                        <p>{content.whyNeedIt}</p>
                    </div>
                </section>

                <section className="stats-grid">
                    <div className="stat-card">
                        <TrendingUp size={20} color="var(--color-primary)" />
                        <span className="stat-label">{lang === 'te' ? 'దిగుబడి పెరుగుదల' : 'Yield Increase'}</span>
                        <span className="stat-value">{content.stats?.yield || 'N/A'}</span>
                    </div>
                    <div className="stat-card">
                        <Droplets size={20} color="#0288D1" />
                        <span className="stat-label">{lang === 'te' ? 'నీరు ఆదా' : 'Water Saved'}</span>
                        <span className="stat-value">{content.stats?.water || 'N/A'}</span>
                    </div>
                    <div className="stat-card">
                        <DollarSign size={20} color="#F57F17" />
                        <span className="stat-label">{lang === 'te' ? 'ఖర్చు తగ్గింపు' : 'Cost Reduction'}</span>
                        <span className="stat-value">{content.stats?.cost || 'N/A'}</span>
                    </div>
                </section>

                <section className="content-section">
                    <h2>{t('techniques.benefits', 'Benefits')}</h2>
                    <ul className="check-list">
                        {content.benefits?.map((item, index) => (
                            <li key={index}><CheckCircle size={16} className="icon-check" /> {item}</li>
                        ))}
                    </ul>
                </section>

                {content.mistakes && (
                    <section className="content-section warning-bg">
                        <h2>{lang === 'te' ? 'సాధారణ తప్పులు' : 'Common Mistakes'}</h2>
                        <ul className="cross-list">
                            {content.mistakes.map((item, index) => (
                                <li key={index}><AlertTriangle size={16} className="icon-alert" /> {item}</li>
                            ))}
                        </ul>
                    </section>
                )}

                {content.implementation && (
                    <section className="content-section">
                        <h2>{t('techniques.steps', 'Implementation Steps')}</h2>
                        <div className="steps-timeline">
                            {content.implementation.map((step, index) => (
                                <div key={index} className="step-item">
                                    <div className="step-number">{index + 1}</div>
                                    <div className="step-content">
                                        <h4>{step.step}</h4>
                                        <p>{step.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                <section className="content-section ap-specifics">
                    <h2>{t('techniques.apSpecifics', 'AP/Telangana Specifics')}</h2>
                    <div className="info-grid">
                        <div className="info-item">
                            <strong>{lang === 'te' ? 'మట్టి రకం:' : 'Soil Type:'}</strong> {content.apSpecifics?.soil || 'N/A'}
                        </div>
                        <div className="info-item">
                            <strong>{lang === 'te' ? 'తగిన పంటలు:' : 'Suitable Crops:'}</strong> {content.apSpecifics?.crops || 'N/A'}
                        </div>
                        <div className="info-item">
                            <strong>{lang === 'te' ? 'వాతావరణం:' : 'Climate:'}</strong> {content.apSpecifics?.climate || 'N/A'}
                        </div>
                    </div>
                </section>

                {content.faq && (
                    <section className="content-section">
                        <h2>{t('techniques.faq', 'FAQ')}</h2>
                        <div className="faq-list">
                            {content.faq.map((item, index) => (
                                <div key={index} className="faq-item">
                                    <div className="question"><HelpCircle size={16} /> {item.q}</div>
                                    <div className="answer">{item.a}</div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                <section className="content-section cost-benefit">
                    <h2>{t('techniques.costBenefit', 'Cost Benefit Analysis')}</h2>
                    <div className="cb-grid">
                        <div className="cb-item">
                            <span>{lang === 'te' ? 'ప్రారంభ ఖర్చు' : 'Initial Cost'}</span>
                            <strong>{content.costBenefit?.cost || 'N/A'}</strong>
                        </div>
                        <div className="cb-item highlight">
                            <span>{lang === 'te' ? 'నికర లాభం' : 'Net Profit'}</span>
                            <strong>{content.costBenefit?.profit || 'N/A'}</strong>
                        </div>
                        <div className="cb-item">
                            <span>{lang === 'te' ? 'తిరిగి పొందే కాలం' : 'Payback Period'}</span>
                            <strong>{content.costBenefit?.payback || 'N/A'}</strong>
                        </div>
                    </div>
                </section>

                {content.finalGuidance && (
                    <div className="final-guidance">
                        <p>{content.finalGuidance}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TechniqueDetail;
