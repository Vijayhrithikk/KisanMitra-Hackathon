import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, ChevronRight, Leaf } from 'lucide-react';
import { techniques } from '../data/techniques';
import './TechniquesList.css';

const TechniquesList = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const lang = i18n.language === 'te' ? 'te' : 'en';

    const L = {
        title: lang === 'te' ? 'ఆధునిక వ్యవసాయ పద్ధతులు' : 'Modern Farming Techniques',
        subtitle: lang === 'te' ? 'వ్యవసాయ సాంకేతికత నేర్చుకోండి' : 'Learn farming technology',
        learnMore: lang === 'te' ? 'మరిన్ని చదవండి' : 'Learn More'
    };

    return (
        <div className="techniques-page">
            {/* Header */}
            <header className="page-header">
                <button className="back-btn" onClick={() => navigate('/')}>
                    <ArrowLeft size={20} />
                </button>
                <h1>{L.title}</h1>
                <div style={{ width: 36 }} /> {/* Spacer */}
            </header>

            {/* Hero */}
            <div className="techniques-hero">
                <div className="hero-icon">
                    <Leaf size={32} color="#4CAF50" />
                </div>
                <p>{L.subtitle}</p>
            </div>

            {/* Techniques List */}
            <div className="techniques-list">
                {techniques.map((tech, index) => (
                    <div
                        key={tech.id}
                        className="technique-card"
                        onClick={() => navigate(`/technique/${tech.id}`)}
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        <div className="technique-image">
                            <img
                                src={tech.image}
                                alt={tech.title[lang] || tech.title.en}
                                onError={(e) => e.target.src = 'https://picsum.photos/seed/farm/120/80'}
                            />
                        </div>
                        <div className="technique-content">
                            <h3>{tech.title[lang] || tech.title.en}</h3>
                            <p>{tech.summary[lang] || tech.summary.en}</p>
                        </div>
                        <div className="technique-arrow">
                            <ChevronRight size={18} />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TechniquesList;
