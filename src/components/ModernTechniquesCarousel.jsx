import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronRight } from 'lucide-react';
import { techniques } from '../data/techniques';
import './ModernTechniquesCarousel.css';

const ModernTechniquesCarousel = () => {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const [currentIndex, setCurrentIndex] = useState(0);

    const lang = i18n.language === 'te' ? 'te' : 'en';

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % techniques.length);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleCardClick = (id) => {
        navigate(`/technique/${id}`);
    };

    return (
        <div className="techniques-carousel-container">
            <div className="carousel-header">
                <h2>{t('home.modernTechniques', 'Modern Farming Techniques')}</h2>
            </div>

            <div className="carousel-viewport">
                <div
                    className="carousel-track"
                    style={{ transform: `translateX(-${currentIndex * 100}%)` }}
                >
                    {techniques.map((tech) => (
                        <div
                            key={tech.id}
                            className="carousel-card"
                            onClick={() => handleCardClick(tech.id)}
                        >
                            <div className="card-image-wrapper">
                                <img src={tech.image} alt={tech.title[lang] || tech.title.en} />
                                <div className="card-overlay">
                                    <h3>{tech.title[lang] || tech.title.en}</h3>
                                    <p>{tech.summary[lang] || tech.summary.en}</p>
                                    <button className="learn-more-btn">
                                        {t('techniques.learnMore', 'Learn More')} <ChevronRight size={16} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="carousel-dots">
                {techniques.map((_, index) => (
                    <span
                        key={index}
                        className={`dot ${index === currentIndex ? 'active' : ''}`}
                        onClick={() => setCurrentIndex(index)}
                    />
                ))}
            </div>
        </div>
    );
};

export default ModernTechniquesCarousel;
