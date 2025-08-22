#!/usr/bin/env python
"""
Script de test pour les interfaces IA
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrsuit.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .ai_services import ai_services
from .ai_integration import ai_integration

class AIInterfacesTest(TestCase):
    """Tests pour les interfaces IA"""
    
    def setUp(self):
        """Configuration initiale"""
        # Créer un superuser pour les tests
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client = Client()
    
    def test_ai_test_interface_access(self):
        """Test d'accès à l'interface de test IA"""
        # Connexion en tant que superuser
        self.client.login(username='admin', password='admin123')
        
        # Test de l'accès à l'interface
        response = self.client.get(reverse('dashboard:ai_test_interface'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test des Services IA')
    
    def test_ai_batch_processing_access(self):
        """Test d'accès à l'interface de traitement par lot"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.get(reverse('dashboard:ai_batch_processing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Traitement par Lot IA')
    
    def test_ai_realtime_analysis_access(self):
        """Test d'accès à l'interface d'analyse temps réel"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.get(reverse('dashboard:ai_realtime_analysis'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analyse Temps Réel IA')
    
    def test_ai_analytics_dashboard_access(self):
        """Test d'accès au dashboard analytics IA"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.get(reverse('dashboard:ai_analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics IA')
    
    def test_ai_services_availability(self):
        """Test de disponibilité des services IA"""
        self.assertIsNotNone(ai_services)
        self.assertIsNotNone(ai_integration)
    
    def test_sentiment_analysis(self):
        """Test de l'analyse de sentiment"""
        text = "Je suis très satisfait du service"
        result = ai_services.analyze_sentiment(text)
        
        self.assertIn('sentiment', result)
        self.assertIn('score', result)
        self.assertIn('confidence', result)
        self.assertIn(result['sentiment'], ['positive', 'negative', 'neutral'])
    
    def test_priority_prediction(self):
        """Test de la prédiction de priorité"""
        text = "URGENT: Problème critique avec le système"
        result = ai_services.predict_priority(text)
        
        self.assertIn('priority', result)
        self.assertIn('score', result)
        self.assertIn('reason', result)
        self.assertIn(result['priority'], ['urgent', 'high', 'medium', 'low'])
    
    def test_ticket_categorization(self):
        """Test de la catégorisation de tickets"""
        text = "Demande de réservation pour Paris"
        result = ai_services.categorize_ticket(text)
        
        self.assertIn('category', result)
        self.assertIn('confidence', result)
    
    def test_leave_approval_prediction(self):
        """Test de la prédiction d'approbation de congé"""
        employee_data = {'employeetype': 'permanent'}
        leave_data = {
            'leavetype': 'congé',
            'leave_days': 5,
            'startdate': '2024-01-15'
        }
        
        result = ai_services.predict_leave_approval(employee_data, leave_data)
        
        self.assertIn('approval_probability', result)
        self.assertIn('factors', result)
        self.assertIsInstance(result['approval_probability'], float)
        self.assertIsInstance(result['factors'], list)

def run_manual_tests():
    """Tests manuels pour vérifier les fonctionnalités"""
    print("=== Tests des Interfaces IA ===")
    
    # Test des services IA
    print("\n1. Test des services IA...")
    try:
        from .ai_services import ai_services
        print("✅ Services IA disponibles")
        
        # Test d'analyse de sentiment
        result = ai_services.analyze_sentiment("Excellent service!")
        print(f"✅ Analyse de sentiment: {result}")
        
        # Test de prédiction de priorité
        result = ai_services.predict_priority("URGENT: Problème critique")
        print(f"✅ Prédiction de priorité: {result}")
        
    except Exception as e:
        print(f"❌ Erreur services IA: {e}")
    
    # Test d'intégration IA
    print("\n2. Test d'intégration IA...")
    try:
        from .ai_integration import ai_integration
        print("✅ Intégration IA disponible")
        
        # Test d'insights
        insights = ai_integration.get_ai_insights()
        print(f"✅ Insights générés: {len(insights)}")
        
    except Exception as e:
        print(f"❌ Erreur intégration IA: {e}")
    
    # Test des URLs
    print("\n3. Test des URLs...")
    urls_to_test = [
        'dashboard:ai_analytics',
        'dashboard:ai_test_interface', 
        'dashboard:ai_batch_processing',
        'dashboard:ai_realtime_analysis'
    ]
    
    for url_name in urls_to_test:
        try:
            from django.urls import reverse
            url = reverse(url_name)
            print(f"✅ URL {url_name}: {url}")
        except Exception as e:
            print(f"❌ Erreur URL {url_name}: {e}")
    
    print("\n=== Tests terminés ===")

if __name__ == '__main__':
    run_manual_tests() 