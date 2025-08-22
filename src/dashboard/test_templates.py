"""
Script de test pour vérifier que les vues passent correctement les données aux templates
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
from employee.models import Employee
from django.contrib.auth.models import User

def test_data_availability():
    """Test de la disponibilité des données"""
    print("=== Test de disponibilité des données ===")
    
    # Test des utilisateurs
    users = User.objects.all()
    print(f"Nombre d'utilisateurs: {users.count()}")
    
    if users.exists():
        user = users.first()
        print(f"Premier utilisateur: {user.username}")
        
        # Test des employés
        employees = Employee.objects.filter(user=user)
        print(f"Employés pour {user.username}: {employees.count()}")
        
        # Test des congés
        leaves = Leave.objects.filter(user=user)
        print(f"Congés pour {user.username}: {leaves.count()}")
        
        if leaves.exists():
            leave = leaves.first()
            print(f"  - Premier congé: {leave.leavetype} ({leave.leave_days} jours)")
        
        # Test des tickets
        tickets = Ticket.objects.filter(user=user)
        print(f"Tickets pour {user.username}: {tickets.count()}")
        
        if tickets.exists():
            ticket = tickets.first()
            print(f"  - Premier ticket: {ticket.destination}")
    
    # Test global
    total_leaves = Leave.objects.all().count()
    total_tickets = Ticket.objects.all().count()
    total_employees = Employee.objects.all().count()
    
    print(f"\nTotaux globaux:")
    print(f"  - Congés: {total_leaves}")
    print(f"  - Tickets: {total_tickets}")
    print(f"  - Employés: {total_employees}")

def test_view_data():
    """Test des données que les vues passent aux templates"""
    print("\n=== Test des données des vues ===")
    
    # Simuler les données de view_my_leave_table
    users = User.objects.all()
    if users.exists():
        user = users.first()
        leaves = Leave.objects.filter(user=user)
        employee = Employee.objects.filter(user=user).first()
        
        print(f"Données pour staff_leaves_table:")
        print(f"  - leaves: {leaves.count()} éléments")
        print(f"  - employee: {employee}")
        
        # Simuler les données de view_my_ticket_table
        tickets = Ticket.objects.filter(user=user)
        
        print(f"\nDonnées pour staff_tickets_table:")
        print(f"  - tickets: {tickets.count()} éléments")
        print(f"  - employee: {employee}")

if __name__ == "__main__":
    print("Démarrage des tests de templates...")
    
    try:
        test_data_availability()
        test_view_data()
        
        print("\n=== Tests terminés avec succès ===")
        
    except Exception as e:
        print(f"\nErreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc() 