"""
Configuration des services AI
"""
import os
from django.conf import settings

class AIConfig:
    """Configuration centralisée pour les services AI"""
    
    # Activation des services AI
    AI_SERVICES_ENABLED = getattr(settings, 'AI_SERVICES_ENABLED', True)
    AI_ANALYSIS_ENABLED = getattr(settings, 'AI_ANALYSIS_ENABLED', True)
    
    # Configuration des seuils
    SENTIMENT_THRESHOLD = getattr(settings, 'AI_SENTIMENT_THRESHOLD', 0.1)
    PRIORITY_THRESHOLD = getattr(settings, 'AI_PRIORITY_THRESHOLD', 0.5)
    CONFIDENCE_THRESHOLD = getattr(settings, 'AI_CONFIDENCE_THRESHOLD', 0.7)
    
    # Configuration des mots-clés
    PRIORITY_KEYWORDS = {
        'urgent': ['urgent', 'urgente', 'immédiat', 'immédiate', 'critique', 'important'],
        'high': ['priorité', 'prioritaire', 'nécessaire', 'essentiel', 'vital'],
        'medium': ['normal', 'standard', 'régulier', 'habituel'],
        'low': ['non urgent', 'peut attendre', 'flexible', 'optionnel']
    }
    
    SENTIMENT_KEYWORDS = {
        'positive': ['merci', 'remerciements', 'satisfait', 'content', 'heureux', 'excellent'],
        'negative': ['problème', 'difficile', 'compliqué', 'frustré', 'déçu', 'insatisfait'],
        'neutral': ['information', 'demande', 'question', 'renseignement']
    }
    
    # Configuration des catégories
    TICKET_CATEGORIES = {
        'reservation': ['réservation', 'réserver', 'billet', 'vol', 'compagnie'],
        'modification': ['modifier', 'changer', 'modification', 'annuler', 'rembourser'],
        'information': ['information', 'renseignement', 'question', 'demande'],
        'technical': ['problème', 'erreur', 'bug', 'technique', 'système'],
        'complaint': ['plainte', 'réclamation', 'insatisfait', 'déçu', 'problème']
    }
    
    # Configuration des facteurs d'approbation
    LEAVE_APPROVAL_FACTORS = {
        'employee_type': {
            'PS': 0.1,  # Personnel au sol
            'PNT': 0.15,  # Personnel navigant technique
            'PNC': 0.15,  # Personnel navigant commercial
        },
        'leave_type': {
            'maladie': 0.2,
            'accident de travail': 0.2,
            'mission': 0.15,
            'congé': 0.0,
            'absence': -0.1,
        },
        'duration': {
            'short': 0.1,  # <= 5 jours
            'medium': 0.0,  # 6-15 jours
            'long': -0.1,   # > 15 jours
        },
        'period': {
            'summer': -0.1,  # Juillet-Août
            'christmas': -0.1,  # Décembre
            'normal': 0.0,
        }
    }
    
    # Configuration des couleurs UI
    PRIORITY_COLORS = {
        'urgent': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'success'
    }
    
    SENTIMENT_ICONS = {
        'positive': '😊',
        'negative': '😞',
        'neutral': '😐'
    }
    
    # Configuration des insights
    INSIGHT_THRESHOLDS = {
        'approval_rate_low': 0.7,
        'approval_rate_high': 0.9,
        'pending_tickets_ratio': 0.3,
    }
    
    # Configuration du logging
    LOG_LEVEL = getattr(settings, 'AI_LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def is_enabled(cls):
        """Vérifie si les services AI sont activés"""
        return cls.AI_SERVICES_ENABLED and cls.AI_ANALYSIS_ENABLED
    
    @classmethod
    def get_priority_keywords(cls):
        """Retourne les mots-clés de priorité"""
        return cls.PRIORITY_KEYWORDS
    
    @classmethod
    def get_sentiment_keywords(cls):
        """Retourne les mots-clés de sentiment"""
        return cls.SENTIMENT_KEYWORDS
    
    @classmethod
    def get_ticket_categories(cls):
        """Retourne les catégories de tickets"""
        return cls.TICKET_CATEGORIES
    
    @classmethod
    def get_approval_factors(cls):
        """Retourne les facteurs d'approbation"""
        return cls.LEAVE_APPROVAL_FACTORS
    
    @classmethod
    def get_priority_color(cls, priority):
        """Retourne la couleur CSS pour une priorité"""
        return cls.PRIORITY_COLORS.get(priority, 'secondary')
    
    @classmethod
    def get_sentiment_icon(cls, sentiment):
        """Retourne l'icône pour un sentiment"""
        return cls.SENTIMENT_ICONS.get(sentiment, '😐')
    
    @classmethod
    def get_insight_thresholds(cls):
        """Retourne les seuils pour les insights"""
        return cls.INSIGHT_THRESHOLDS

# Instance globale de configuration
ai_config = AIConfig() 