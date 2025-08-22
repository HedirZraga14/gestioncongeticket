"""
Script pour créer des données de test pour les congés et tickets
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrsuit.settings')
django.setup()

from ticket.models import Ticket
from leave.models import Leave
from employee.models import Employee
from django.contrib.auth.models import User

def create_test_data():
    """Créer des données de test"""
    print("=== Création de données de test ===")
    
    # Récupérer le premier utilisateur
    users = User.objects.all()
    if not users.exists():
        print("Aucun utilisateur trouvé")
        return
    
    user = users.first()
    employee = Employee.objects.filter(user=user).first()
    
    if not employee:
        print("Aucun employé trouvé pour l'utilisateur")
        return
    
    print(f"Utilisation de l'utilisateur: {user.username}")
    print(f"Employé: {employee.firstname} {employee.lastname}")
    
    # Créer des congés de test
    leave_types = ['congé', 'maladie', 'formation', 'maternité']
    statuses = ['pending', 'approved', 'rejected']
    
    for i in range(3):
        start_date = datetime.now().date() + timedelta(days=i * 7)
        end_date = start_date + timedelta(days=i + 1)
        
        leave = Leave.objects.create(
            user=user,
            leavetype=leave_types[i % len(leave_types)],
            startdate=start_date,
            enddate=end_date,
            status=statuses[i % len(statuses)]
        )
        print(f"  - Congé créé: {leave.leavetype} ({leave.leave_days} jours)")
    
    # Créer des tickets de test
    destinations = ['Paris', 'Londres', 'New York', 'Tokyo', 'Sydney']
    
    for i in range(3):
        ticket = Ticket.objects.create(
            user=user,
            destination=destinations[i % len(destinations)],
            date=datetime.now().date() + timedelta(days=i * 14),
            statut=statuses[i % len(statuses)]
        )
        print(f"  - Ticket créé: {ticket.destination}")
    
    print(f"\nDonnées créées avec succès!")
    print(f"  - Congés: {Leave.objects.filter(user=user).count()}")
    print(f"  - Tickets: {Ticket.objects.filter(user=user).count()}")

if __name__ == "__main__":
    print("Création de données de test...")
    
    try:
        create_test_data()
        print("\n=== Création terminée avec succès ===")
        
    except Exception as e:
        print(f"\nErreur lors de la création: {str(e)}")
        import traceback
        traceback.print_exc() 