"""
Services IA pour l'analyse de sentiment et la priorisation automatique
"""
import os
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import numpy as np
from datetime import datetime, timedelta
from .ai_config import ai_config

class AIServices:
    """Services d'intelligence artificielle pour l'application"""
    
    def __init__(self):
        self.priority_keywords = ai_config.get_priority_keywords()
        self.sentiment_keywords = ai_config.get_sentiment_keywords()
    
    def analyze_sentiment(self, text):
        """
        Analyse le sentiment d'un texte
        Returns: {'sentiment': 'positive/negative/neutral', 'score': float, 'confidence': float}
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # Analyse avec TextBlob
        blob = TextBlob(text.lower())
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classification du sentiment
        threshold = ai_config.SENTIMENT_THRESHOLD
        if polarity > threshold:
            sentiment = 'positive'
        elif polarity < -threshold:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calcul de la confiance basé sur la subjectivité
        confidence = abs(polarity) + (subjectivity * 0.5)
        confidence = min(confidence, 1.0)
        
        return {
            'sentiment': sentiment,
            'score': round(polarity, 3),
            'confidence': round(confidence, 3)
        }
    
    def predict_priority(self, text, user_role=None, ticket_type=None):
        """
        Prédit la priorité d'un ticket basé sur le contenu et le contexte
        Returns: {'priority': 'low/medium/high/urgent', 'score': float, 'reason': str}
        """
        if not text:
            return {'priority': 'medium', 'score': 0.5, 'reason': 'Texte vide'}
        
        text_lower = text.lower()
        scores = {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        # Analyse des mots-clés
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[priority] += 1
        
        # Facteurs contextuels
        if user_role == 'admin' or user_role == 'manager':
            scores['high'] += 1
        
        if ticket_type == 'technical':
            scores['high'] += 0.5
        
        # Analyse de sentiment pour ajuster la priorité
        sentiment_analysis = self.analyze_sentiment(text)
        if sentiment_analysis['sentiment'] == 'negative':
            scores['high'] += 1
        elif sentiment_analysis['sentiment'] == 'positive':
            scores['low'] += 0.5
        
        # Détermination de la priorité finale
        max_score = max(scores.values())
        if max_score == 0:
            priority = 'medium'
            score = 0.5
        else:
            for p, s in scores.items():
                if s == max_score:
                    priority = p
                    score = min(s / 3, 1.0)  # Normalisation
                    break
        
        # Raison de la priorité
        reasons = []
        if scores['urgent'] > 0:
            reasons.append("Mots-clés urgents détectés")
        if scores['high'] > 0:
            reasons.append("Priorité élevée détectée")
        if sentiment_analysis['sentiment'] == 'negative':
            reasons.append("Sentiment négatif détecté")
        if user_role in ['admin', 'manager']:
            reasons.append("Utilisateur prioritaire")
        
        reason = "; ".join(reasons) if reasons else "Priorité par défaut"
        
        return {
            'priority': priority,
            'score': round(score, 3),
            'reason': reason
        }
    
    def categorize_ticket(self, text, destination=None):
        """
        Catégorise automatiquement un ticket
        Returns: {'category': str, 'confidence': float}
        """
        categories = ai_config.get_ticket_categories()
        
        text_lower = text.lower()
        scores = {cat: 0 for cat in categories}
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[category] += 1
        
        # Facteur destination
        if destination and 'international' in destination.lower():
            scores['reservation'] += 1
        
        max_score = max(scores.values())
        if max_score == 0:
            return {'category': 'information', 'confidence': 0.5}
        
        for category, score in scores.items():
            if score == max_score:
                confidence = min(score / 3, 1.0)
                return {
                    'category': category,
                    'confidence': round(confidence, 3)
                }
    
    def predict_leave_approval(self, employee_data, leave_data):
        """
        Prédit la probabilité d'approbation d'un congé
        Returns: {'approval_probability': float, 'factors': list}
        """
        factors = []
        probability = 0.5  # Base probability
        approval_factors = ai_config.get_approval_factors()
        
        # Facteur: Type d'employé
        employee_type = employee_data.get('employeetype')
        if employee_type in approval_factors['employee_type']:
            probability += approval_factors['employee_type'][employee_type]
            factors.append(f"Type d'employé: {employee_type}")
        
        # Facteur: Durée du congé
        leave_days = leave_data.get('leave_days', 0)
        if leave_days <= 5:
            probability += approval_factors['duration']['short']
            factors.append("Congé court")
        elif leave_days > 15:
            probability += approval_factors['duration']['long']
            factors.append("Congé long")
        else:
            probability += approval_factors['duration']['medium']
            factors.append("Congé moyen")
        
        # Facteur: Type de congé
        leave_type = leave_data.get('leavetype', '')
        if leave_type in approval_factors['leave_type']:
            probability += approval_factors['leave_type'][leave_type]
            factors.append(f"Type de congé: {leave_type}")
        
        # Facteur: Période de l'année
        start_date = leave_data.get('startdate')
        if start_date:
            month = start_date.month
            if month in [7, 8]:  # Été
                probability += approval_factors['period']['summer']
                factors.append("Période estivale")
            elif month == 12:  # Noël
                probability += approval_factors['period']['christmas']
                factors.append("Période de Noël")
            else:
                probability += approval_factors['period']['normal']
        
        # Normalisation
        probability = max(0.0, min(1.0, probability))
        
        return {
            'approval_probability': round(probability, 3),
            'factors': factors
        }
    
    def detect_anomalies(self, data_series, threshold=2.0):
        """
        Détecte les anomalies dans une série de données
        Returns: list of anomaly indices
        """
        if len(data_series) < 3:
            return []
        
        mean = np.mean(data_series)
        std = np.std(data_series)
        
        if std == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(data_series):
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    def generate_insights(self, leave_data, ticket_data):
        """
        Génère des insights automatiques basés sur les données
        Returns: list of insights
        """
        insights = []
        
        # Analyse des tendances
        if leave_data:
            total_leaves = len(leave_data)
            approved_leaves = len([l for l in leave_data if l.get('status') == 'approved'])
            approval_rate = approved_leaves / total_leaves if total_leaves > 0 else 0
            
            if approval_rate < 0.7:
                insights.append("⚠️ Taux d'approbation des congés faible ({:.1%})".format(approval_rate))
            elif approval_rate > 0.9:
                insights.append("✅ Excellent taux d'approbation des congés ({:.1%})".format(approval_rate))
        
        # Analyse des tickets
        if ticket_data:
            total_tickets = len(ticket_data)
            pending_tickets = len([t for t in ticket_data if t.get('statut') == 'En attente'])
            
            if pending_tickets > total_tickets * 0.3:
                insights.append("⚠️ Nombre élevé de tickets en attente ({}/{})".format(pending_tickets, total_tickets))
            
            # Destinations populaires
            destinations = [t.get('destination') for t in ticket_data if t.get('destination')]
            if destinations:
                from collections import Counter
                dest_counter = Counter(destinations)
                most_common = dest_counter.most_common(1)[0]
                insights.append("🌍 Destination la plus demandée: {} ({} demandes)".format(
                    most_common[0], most_common[1]
                ))
        
        return insights

# Instance globale
ai_services = AIServices() 