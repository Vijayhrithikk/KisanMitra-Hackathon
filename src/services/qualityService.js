// Quality Certification Service
const QUALITY_KEY = 'kisanmitra_quality_certs';

class QualityService {
    constructor() {
        if (!localStorage.getItem(QUALITY_KEY)) {
            localStorage.setItem(QUALITY_KEY, JSON.stringify([]));
        }
    }

    _getCerts() {
        return JSON.parse(localStorage.getItem(QUALITY_KEY) || '[]');
    }

    _saveCerts(certs) {
        localStorage.setItem(QUALITY_KEY, JSON.stringify(certs));
    }

    // Quality grades
    getGrades() {
        return [
            { id: 'A', en: 'Grade A - Premium', te: 'గ్రేడ్ A - ప్రీమియం', color: '#16a34a' },
            { id: 'B', en: 'Grade B - Standard', te: 'గ్రేడ్ B - స్టాండర్డ్', color: '#3b82f6' },
            { id: 'C', en: 'Grade C - Economy', te: 'గ్రేడ్ C - ఎకానమీ', color: '#f59e0b' }
        ];
    }

    // Certification types
    getCertificationTypes() {
        return [
            { id: 'NONE', en: 'No Certification', te: 'సర్టిఫికేషన్ లేదు', icon: '📋' },
            { id: 'FSSAI', en: 'FSSAI Certified', te: 'FSSAI సర్టిఫైడ్', icon: '✅' },
            { id: 'ORGANIC', en: 'India Organic', te: 'ఇండియా ఆర్గానిక్', icon: '🌿' },
            { id: 'NPOP', en: 'NPOP Organic', te: 'NPOP ఆర్గానిక్', icon: '🍃' },
            { id: 'GAP', en: 'Good Agriculture Practice', te: 'గుడ్ అగ్రికల్చర్', icon: '🏆' }
        ];
    }

    // Add quality info to listing
    addQualityInfo(listingId, qualityData) {
        const certs = this._getCerts();

        const cert = {
            certId: `CERT-${Date.now().toString(36).toUpperCase()}`,
            listingId,
            grade: qualityData.grade || 'B',
            organic: qualityData.organic || false,
            certification: qualityData.certification || 'NONE',
            certificationNumber: qualityData.certificationNumber || '',
            harvestDate: qualityData.harvestDate || '',
            moisturePercent: qualityData.moisturePercent || 12,
            labReport: qualityData.labReport || null,
            createdAt: new Date().toISOString(),
            verified: false
        };

        certs.push(cert);
        this._saveCerts(certs);

        return { success: true, cert };
    }

    // Get quality info for listing
    getQualityInfo(listingId) {
        const certs = this._getCerts();
        return certs.find(c => c.listingId === listingId);
    }

    // Upload lab report (mock - stores base64)
    uploadLabReport(listingId, reportData) {
        const certs = this._getCerts();
        const index = certs.findIndex(c => c.listingId === listingId);

        if (index === -1) {
            // Create new cert with report
            return this.addQualityInfo(listingId, { labReport: reportData });
        }

        certs[index].labReport = {
            fileName: reportData.fileName,
            uploadDate: new Date().toISOString(),
            fileType: reportData.fileType,
            // In real app, upload to cloud storage
            url: reportData.base64 || null
        };
        this._saveCerts(certs);

        return { success: true, cert: certs[index] };
    }

    // Verify certification (mock)
    verifyCertification(certId) {
        const certs = this._getCerts();
        const index = certs.findIndex(c => c.certId === certId);

        if (index === -1) return { success: false, error: 'Certificate not found' };

        // Mock verification - in real app, call FSSAI/organic database API
        certs[index].verified = true;
        certs[index].verifiedAt = new Date().toISOString();
        this._saveCerts(certs);

        return { success: true, cert: certs[index] };
    }

    // Get quality badge for display
    getQualityBadge(listing) {
        const cert = this.getQualityInfo(listing.listingId);
        if (!cert) return null;

        const badges = [];

        if (cert.grade) {
            const gradeInfo = this.getGrades().find(g => g.id === cert.grade);
            badges.push({ type: 'grade', label: cert.grade, color: gradeInfo?.color });
        }

        if (cert.organic) {
            badges.push({ type: 'organic', label: '🌿 Organic', color: '#16a34a' });
        }

        if (cert.certification && cert.certification !== 'NONE') {
            const certInfo = this.getCertificationTypes().find(c => c.id === cert.certification);
            badges.push({ type: 'cert', label: certInfo?.icon + ' ' + cert.certification, color: '#3b82f6' });
        }

        return badges;
    }
}

export const qualityService = new QualityService();
