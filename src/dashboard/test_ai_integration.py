"""
Script de test pour vérifier l'intégration des services AI
"""
import os
import sys
import django

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrsuit.settings')
django.setup()

from ticket.models import Ticket
from leave.models import Leave
from dashboard.ai_integration import ai_integration
from dashboard.ai_services import ai_services

def test_ai_services():
    """Test des services AI de base"""
    print("=== Test des services AI de base ===")
    
    # Test d'analyse de sentiment
    text = "J'ai besoin d'un billet urgent pour Paris demain"
    sentiment_result = ai_services.analyze_sentiment(text)
    print(f"Sentiment: {sentiment_result}")
    
    # Test de prédiction de priorité
    priority_result = ai_services.predict_priority(text, user_role='employee')
    print(f"Priorité: {priority_result}")
    
    # Test de catégorisation
    category_result = ai_services.categorize_ticket(text, destination='Paris')
    print(f"Catégorie: {category_result}")
    
    # Test de prédiction d'approbation de congé
    from datetime import datetime
    employee_data = {'employeetype': 'PS', 'user_role': 'employee'}
    leave_data = {'leave_days': 5, 'leavetype': 'congé', 'startdate': datetime(2024, 1, 15)}
    approval_result = ai_services.predict_leave_approval(employee_data, leave_data)
    print(f"Approbation congé: {approval_result}")

def test_ai_integration():
    """Test de l'intégration AI avec les modèles"""
    print("\n=== Test de l'intégration AI ===")
    
    # Créer un ticket de test
    from django.contrib.auth.models import User
    user = User.objects.first()
    
    if not user:
        print("Aucun utilisateur trouvé dans la base de données")
        return
    
    # Test avec un ticket existant
    tickets = Ticket.objects.all()[:1]
    if tickets:
        ticket = tickets[0]
        print(f"Test d'analyse AI pour le ticket {ticket.id}")
        
        # Analyser le ticket
        success = ai_integration.analyze_ticket_ai(ticket)
        print(f"Analyse ticket réussie: {success}")
        
        if success:
            print(f"  - Priorité IA: {ticket.ai_priority}")
            print(f"  - Sentiment IA: {ticket.ai_sentiment}")
            print(f"  - Catégorie IA: {ticket.ai_category}")
    
    # Test avec un congé existant
    leaves = Leave.objects.all()[:1]
    if leaves:
        leave = leaves[0]
        print(f"\nTest d'analyse AI pour le congé {leave.id}")
        
        # Analyser le congé
        success = ai_integration.analyze_leave_ai(leave)
        print(f"Analyse congé réussie: {success}")
        
        if success:
            print(f"  - Probabilité d'approbation: {leave.ai_approval_probability}")
            print(f"  - Priorité IA: {leave.ai_priority}")
            print(f"  - Facteurs: {leave.ai_approval_factors}")

def test_ai_insights():
    """Test de génération d'insights AI"""
    print("\n=== Test de génération d'insights AI ===")
    
    insights = ai_integration.get_ai_insights()
    print(f"Nombre d'insights générés: {len(insights)}")
    
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")

def test_utility_functions():
    """Test des fonctions utilitaires"""
    print("\n=== Test des fonctions utilitaires ===")
    
    # Test des couleurs de priorité
    colors = ['urgent', 'high', 'medium', 'low']
    for priority in colors:
        color = ai_integration.get_priority_color(priority)
        print(f"Priorité '{priority}' -> Couleur: {color}")
    
    # Test des icônes de sentiment
    sentiments = ['positive', 'negative', 'neutral']
    for sentiment in sentiments:
        icon = ai_integration.get_sentiment_icon(sentiment)
        print(f"Sentiment '{sentiment}' -> Icône: {icon}")
    
    # Test du formatage de confiance
    confidences = [0.0, 0.5, 0.75, 1.0]
    for conf in confidences:
        formatted = ai_integration.format_confidence(conf)
        print(f"Confiance {conf} -> {formatted}")

if __name__ == "__main__":
    print("Démarrage des tests d'intégration AI...")
    
    try:
        test_ai_services()
        test_ai_integration()
        test_ai_insights()
        test_utility_functions()
        
        print("\n=== Tous les tests terminés avec succès ===")
        
    except Exception as e:
        print(f"\nErreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc() 