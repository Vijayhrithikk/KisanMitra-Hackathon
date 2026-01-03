import React, { useState, useRef } from 'react';
import { Camera, Upload, CheckCircle, Circle, Loader2, Send, Image, X } from 'lucide-react';
import './DailyChecklist.css';

const API_BASE = import.meta.env.VITE_MARKET_API_URL || 'http://localhost:5000/api';

const DailyChecklist = ({ subscriptionId, farmerId, todayTasks = [], onSubmitSuccess }) => {
    const [tasks, setTasks] = useState(
        todayTasks.map(t => ({ ...t, completed: false, notes: '' }))
    );
    const [cropImage, setCropImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [notes, setNotes] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const fileInputRef = useRef(null);

    // Toggle task completion
    const toggleTask = (taskId) => {
        setTasks(prev => prev.map(t =>
            t.id === taskId ? { ...t, completed: !t.completed } : t
        ));
    };

    // Handle image upload
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setCropImage(reader.result);
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    // Remove image
    const removeImage = () => {
        setCropImage(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // Submit daily log
    const handleSubmit = async () => {
        if (!cropImage) {
            alert('Please upload a crop image');
            return;
        }

        setIsSubmitting(true);
        try {
            const response = await fetch(`${API_BASE}/monitoring/daily-log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subscriptionId,
                    farmerId,
                    date: new Date().toISOString().split('T')[0],
                    cropImage,
                    tasks: tasks.map(t => ({
                        id: t.id,
                        name: t.name || t.title,
                        completed: t.completed,
                        completedAt: t.completed ? new Date().toISOString() : null,
                        notes: t.notes
                    })),
                    notes,
                    weather: {} // Will be captured from monitoring data
                })
            });

            const data = await response.json();
            if (data.success) {
                setSubmitted(true);
                onSubmitSuccess?.(data.log);
            } else {
                alert('Failed to submit: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Submit error:', error);
            alert('Failed to submit daily log');
        } finally {
            setIsSubmitting(false);
        }
    };

    const completedCount = tasks.filter(t => t.completed).length;
    const progress = tasks.length > 0 ? (completedCount / tasks.length) * 100 : 0;

    if (submitted) {
        return (
            <div className="daily-checklist submitted">
                <div className="success-message">
                    <CheckCircle size={48} />
                    <h3>Daily Log Submitted!</h3>
                    <p>Your progress has been recorded</p>
                </div>
            </div>
        );
    }

    return (
        <div className="daily-checklist">
            <div className="checklist-header">
                <h3>📋 Today's Checklist</h3>
                <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
                <span className="progress-text">{completedCount}/{tasks.length} tasks</span>
            </div>

            {/* Crop Image Upload */}
            <div className="image-upload-section">
                <h4><Camera size={18} /> Upload Crop Photo</h4>

                {imagePreview ? (
                    <div className="image-preview">
                        <img src={imagePreview} alt="Crop" />
                        <button className="remove-image" onClick={removeImage}>
                            <X size={16} />
                        </button>
                    </div>
                ) : (
                    <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
                        <Upload size={32} />
                        <p>Tap to upload or take photo</p>
                    </div>
                )}

                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handleImageUpload}
                    style={{ display: 'none' }}
                />
            </div>

            {/* Tasks Checklist */}
            <div className="tasks-section">
                <h4>Tasks</h4>
                {tasks.length === 0 ? (
                    <p className="no-tasks">No tasks scheduled for today</p>
                ) : (
                    <ul className="task-list">
                        {tasks.map(task => (
                            <li key={task.id} className={task.completed ? 'completed' : ''}>
                                <button
                                    className="task-toggle"
                                    onClick={() => toggleTask(task.id)}
                                >
                                    {task.completed ? (
                                        <CheckCircle size={24} className="checked" />
                                    ) : (
                                        <Circle size={24} />
                                    )}
                                </button>
                                <div className="task-content">
                                    <span className="task-name">{task.name || task.title}</span>
                                    {task.description && (
                                        <span className="task-desc">{task.description}</span>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Notes */}
            <div className="notes-section">
                <h4>📝 Notes (Optional)</h4>
                <textarea
                    placeholder="Add any observations about your crop..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={3}
                />
            </div>

            {/* Submit Button */}
            <button
                className="submit-btn"
                onClick={handleSubmit}
                disabled={isSubmitting || !cropImage}
            >
                {isSubmitting ? (
                    <>
                        <Loader2 size={20} className="spin" />
                        Submitting...
                    </>
                ) : (
                    <>
                        <Send size={20} />
                        Submit Daily Log
                    </>
                )}
            </button>
        </div>
    );
};

export default DailyChecklist;
