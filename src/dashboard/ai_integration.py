"""
Module d'intégration IA pour connecter les services IA avec les vues et modèles
"""
from django.utils import timezone
from django.contrib import messages
from .ai_services import ai_services
from .ai_config import ai_config
import json
from django.db.models import Count

class AIIntegration:
    """Classe d'intégration IA pour l'application"""
    
    def __init__(self):
        self.ai_services = ai_services
    
    def analyze_leave_ai(self, leave_instance):
        """
        Analyse automatique d'un congé avec l'IA
        """
        try:
            # Préparer les données pour l'analyse
            employee_data = self._get_employee_data(leave_instance.user)
            leave_data = self._get_leave_data(leave_instance)
            
            # Prédiction d'approbation
            approval_result = self.ai_services.predict_leave_approval(employee_data, leave_data)
            
            # Analyse de priorité basée sur le type de congé et la durée
            priority_text = f"{leave_instance.leavetype} - {leave_instance.leave_days} jours"
            priority_result = self.ai_services.predict_priority(priority_text, employee_data.get('employeetype'))
            
            # Mise à jour du modèle
            leave_instance.ai_approval_probability = approval_result['approval_probability']
            leave_instance.ai_approval_factors = json.dumps(approval_result['factors'], ensure_ascii=False)
            leave_instance.ai_priority = priority_result['priority']
            leave_instance.ai_priority_score = priority_result['score']
            leave_instance.ai_analysis_date = timezone.now()
            leave_instance.save()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'analyse IA du congé: {str(e)}")
            return False
    
    def analyze_ticket_ai(self, ticket_instance):
        """
        Analyse automatique d'un ticket avec l'IA
        """
        try:
            # Préparer le texte pour l'analyse
            analysis_text = f"Destination: {ticket_instance.destination}, Compagnie: {ticket_instance.compagnie}"
            if ticket_instance.retraité:
                analysis_text += ", Retraité"
            
            # Analyse de sentiment
            sentiment_result = self.ai_services.analyze_sentiment(analysis_text)
            
            # Prédiction de priorité
            priority_result = self.ai_services.predict_priority(
                analysis_text, 
                self._get_user_role(ticket_instance.user),
                'ticket'
            )
            
            # Catégorisation automatique
            category_result = self.ai_services.categorize_ticket(
                analysis_text, 
                ticket_instance.destination
            )
            
            # Mise à jour du modèle
            ticket_instance.ai_sentiment = sentiment_result['sentiment']
            ticket_instance.ai_sentiment_score = sentiment_result['score']
            ticket_instance.ai_priority = priority_result['priority']
            ticket_instance.ai_priority_score = priority_result['score']
            ticket_instance.ai_priority_reason = priority_result['reason']
            ticket_instance.ai_category = category_result['category']
            ticket_instance.ai_category_confidence = category_result['confidence']
            ticket_instance.ai_analysis_date = timezone.now()
            ticket_instance.save()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'analyse IA du ticket: {str(e)}")
            return False
    
    def _get_employee_data(self, user):
        """Récupère les données de l'employé"""
        try:
            employee = user.employee_set.first()
            if employee:
                return {
                    'employeetype': employee.employeetype,
                    'department': employee.department.name if employee.department else None,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
        except Exception:
            pass
        return {}
    
    def _get_leave_data(self, leave_instance):
        """Récupère les données du congé pour l'analyse"""
        return {
            'leave_days': leave_instance.leave_days or 0,
            'leavetype': leave_instance.leavetype,
            'startdate': leave_instance.startdate,
            'enddate': leave_instance.enddate
        }
    
    def _get_user_role(self, user):
        """Détermine le rôle de l'utilisateur"""
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'manager'
        else:
            return 'employee'
    
    def get_priority_color(self, priority):
        """Retourne la couleur CSS pour la priorité"""
        colors = {
            'urgent': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'success'
        }
        return colors.get(priority, 'secondary')
    
    def get_sentiment_icon(self, sentiment):
        """Retourne l'icône pour le sentiment"""
        icons = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        }
        return icons.get(sentiment, '😐')
    
    def format_confidence(self, confidence):
        """Formate la confiance en pourcentage"""
        if confidence is None:
            return "0%"
        return f"{int(confidence * 100)}%"
    
    def get_ai_insights(self):
        """Génère des insights IA basés sur les données actuelles"""
        try:
            from leave.models import Leave
            from ticket.models import Ticket
            
            # Récupérer les données récentes
            recent_leaves = Leave.objects.filter(
                created__gte=timezone.now() - timezone.timedelta(days=30)
            ).values()
            
            recent_tickets = Ticket.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).values()
            
            # Générer les insights
            insights = self.ai_services.generate_insights(
                list(recent_leaves), 
                list(recent_tickets)
            )
            
            return insights
            
        except Exception as e:
            print(f"Erreur lors de la génération d'insights: {str(e)}")
            return []
    
    def get_analytics_data(self):
        """Récupère les données pour les analytics avancés"""
        try:
            from leave.models import Leave
            from ticket.models import Ticket
            from employee.models import Employee
            
            # Données pour les graphiques
            leave_status_data = Leave.objects.values('status').annotate(
                count=Count('id')
            )
            
            ticket_destination_data = Ticket.objects.values('destination').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            # Anomalies détectées
            leave_counts = [item['count'] for item in leave_status_data]
            anomalies = self.ai_services.detect_anomalies(leave_counts)
            
            return {
                'leave_status_data': list(leave_status_data),
                'ticket_destination_data': list(ticket_destination_data),
                'anomalies': anomalies
            }
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données analytics: {str(e)}")
            return {}

# Instance globale
ai_integration = AIIntegration() 