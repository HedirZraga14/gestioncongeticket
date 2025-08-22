/**
 * Script JavaScript pour les fonctionnalités IA
 * TUNISAIR Express - Système de Gestion des Congés et Tickets
 */

class AIAnalytics {
    constructor() {
        this.csrfToken = this.getCSRFToken();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeRealTimeAnalysis();
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    setupEventListeners() {
        // Analyse en temps réel lors de la saisie
        const textInputs = document.querySelectorAll('textarea[name="reason"], textarea[name="destination"]');
        textInputs.forEach(input => {
            input.addEventListener('input', this.debounce(() => {
                this.analyzeTextInRealTime(input);
            }, 1000));
        });

        // Boutons d'analyse IA
        const analyzeButtons = document.querySelectorAll('.ai-analyze-btn');
        analyzeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.performAnalysis(button.dataset.type, button.dataset.id);
            });
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async analyzeTextInRealTime(input) {
        const text = input.value;
        if (text.length < 10) return; // Analyse seulement si le texte est suffisamment long

        try {
            const response = await fetch('/dashboard/ai/analyze-sentiment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ text: text })
            });

            if (response.ok) {
                const result = await response.json();
                this.displaySentimentAnalysis(result, input);
            }
        } catch (error) {
            console.error('Erreur lors de l\'analyse en temps réel:', error);
        }
    }

    displaySentimentAnalysis(result, input) {
        // Créer ou mettre à jour l'indicateur de sentiment
        let indicator = input.parentNode.querySelector('.sentiment-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'sentiment-indicator alert alert-sm mt-2';
            input.parentNode.appendChild(indicator);
        }

        const sentimentIcons = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        };

        const sentimentColors = {
            'positive': 'success',
            'negative': 'danger',
            'neutral': 'info'
        };

        indicator.className = `sentiment-indicator alert alert-${sentimentColors[result.sentiment]} alert-sm mt-2`;
        indicator.innerHTML = `
            <i class="fas fa-robot"></i> 
            Sentiment: ${sentimentIcons[result.sentiment]} ${result.sentiment} 
            (Confiance: ${Math.round(result.confidence * 100)}%)
        `;
    }

    async performAnalysis(type, id) {
        const button = document.querySelector(`[data-id="${id}"]`);
        const originalText = button.innerHTML;
        
        try {
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyse en cours...';
            button.disabled = true;

            let url, data;
            
            if (type === 'leave') {
                url = '/dashboard/ai/predict-leave-approval/';
                data = this.getLeaveAnalysisData(id);
            } else if (type === 'ticket') {
                url = '/dashboard/ai/predict-priority/';
                data = this.getTicketAnalysisData(id);
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.displayAnalysisResult(result, type, id);
                this.showSuccessMessage('Analyse IA terminée avec succès');
            } else {
                throw new Error('Erreur lors de l\'analyse');
            }

        } catch (error) {
            console.error('Erreur lors de l\'analyse IA:', error);
            this.showErrorMessage('Erreur lors de l\'analyse IA');
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    getLeaveAnalysisData(leaveId) {
        // Récupérer les données du formulaire de congé
        const form = document.querySelector(`form[data-leave-id="${leaveId}"]`);
        if (!form) return {};

        const formData = new FormData(form);
        return {
            employee_data: {
                employeetype: formData.get('employeetype') || 'employee'
            },
            leave_data: {
                leave_days: this.calculateLeaveDays(formData.get('startdate'), formData.get('enddate')),
                leavetype: formData.get('leavetype'),
                startdate: formData.get('startdate'),
                enddate: formData.get('enddate')
            }
        };
    }

    getTicketAnalysisData(ticketId) {
        // Récupérer les données du formulaire de ticket
        const form = document.querySelector(`form[data-ticket-id="${ticketId}"]`);
        if (!form) return {};

        const formData = new FormData(form);
        return {
            text: `${formData.get('destination')} ${formData.get('compagnie')}`,
            user_role: 'employee',
            ticket_type: 'reservation'
        };
    }

    calculateLeaveDays(startDate, endDate) {
        if (!startDate || !endDate) return 0;
        
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays + 1;
    }

    displayAnalysisResult(result, type, id) {
        const resultContainer = document.querySelector(`#ai-result-${id}`);
        if (!resultContainer) return;

        let html = '<div class="ai-analysis-result">';
        
        if (type === 'leave') {
            html += `
                <div class="alert alert-info">
                    <h6><i class="fas fa-chart-line"></i> Prédiction d'approbation</h6>
                    <p><strong>Probabilité:</strong> ${Math.round(result.approval_probability * 100)}%</p>
                    <p><strong>Facteurs:</strong> ${result.factors.join(', ')}</p>
                </div>
            `;
        } else if (type === 'ticket') {
            html += `
                <div class="alert alert-info">
                    <h6><i class="fas fa-exclamation-triangle"></i> Analyse de priorité</h6>
                    <p><strong>Priorité:</strong> <span class="badge badge-${this.getPriorityColor(result.priority)}">${result.priority}</span></p>
                    <p><strong>Score:</strong> ${Math.round(result.score * 100)}%</p>
                    <p><strong>Raison:</strong> ${result.reason}</p>
                </div>
            `;
        }

        html += '</div>';
        resultContainer.innerHTML = html;
        resultContainer.style.display = 'block';
    }

    getPriorityColor(priority) {
        const colors = {
            'urgent': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'success'
        };
        return colors[priority] || 'secondary';
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'danger');
    }

    showMessage(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        `;

        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    initializeRealTimeAnalysis() {
        // Initialiser les graphiques si Chart.js est disponible
        if (typeof Chart !== 'undefined') {
            this.initializeCharts();
        }
    }

    initializeCharts() {
        // Graphique des priorités IA
        const priorityChart = document.getElementById('priorityChart');
        if (priorityChart) {
            this.createPriorityChart(priorityChart);
        }

        // Graphique des sentiments IA
        const sentimentChart = document.getElementById('sentimentChart');
        if (sentimentChart) {
            this.createSentimentChart(sentimentChart);
        }
    }

    createPriorityChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createSentimentChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Nombre de tickets',
                    data: data.values || [],
                    backgroundColor: ['#4BC0C0', '#FF6384', '#36A2EB']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialiser l'analytics IA quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    new AIAnalytics();
});

// Fonction globale pour actualiser les insights IA
function refreshAIInsights() {
    location.reload();
}

// Fonction pour afficher/masquer les détails IA
function toggleAIDetails(elementId) {
    const details = document.getElementById(elementId);
    if (details) {
        details.style.display = details.style.display === 'none' ? 'block' : 'none';
    }
} 