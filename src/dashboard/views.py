from django.core.paginator import  Paginator
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q, Count, Avg, Sum, F, Min, Max, ExpressionWrapper, IntegerField, DurationField
from datetime import timedelta
import datetime
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from employee.forms import EmployeeCreateForm
from leave.models import Leave
from ticket.models import Ticket
from ticket.models import Beneficiaire
from employee.models import *
from leave.forms import LeaveCreationForm
from ticket.forms import ticketForm
from ticket.forms import BeneficiaireCreateForm
from django.template.loader import get_template
from xhtml2pdf import pisa
from calendar import monthrange
from datetime import datetime
from django.shortcuts import render
import json
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from django.contrib.auth.decorators import login_required
# Import des services IA et reporting
try:
    from .ai_services import ai_services
    from .ai_integration import ai_integration
    from .reporting import reporting_service
except ImportError:
    # Fallback si les modules n'existent pas encore
    ai_services = None
    ai_integration = None
    reporting_service = None


@login_required
def custom_login_redirect(request):
    if request.user.is_authenticated and request.user.is_superuser and request.user.is_staff:
        return redirect('dashboard:analytics')  # Page analytics pour superuser
    elif request.user.is_authenticated and not request.user.is_superuser and not request.user.is_staff:
        return redirect('dashboard:acceuil')  # Page acceuil pour utilisateurs normaux
    else:
        return redirect('dashboard:acceuil')  # Fallback par défaut 

def help(request):
     return render(request, 'dashboard/help.html')

from datetime import datetime, timedelta
from leave.models import Leave
from ticket.models import Ticket

from django.shortcuts import redirect
from django.contrib import messages
from .models import Note

def calendrier(request):
    # Get current date and start of the month
    today = datetime.now()
    start_of_month = today.replace(day=1)
    
    # Get current day in French
    days = {
        0: 'Lundi',
        1: 'Mardi',
        2: 'Mercredi',
        3: 'Jeudi',
        4: 'Vendredi',
        5: 'Samedi',
        6: 'Dimanche'
    }
    current_day = days[today.weekday()]
    
    # Get pending leaves for current user
    pending_leaves = Leave.objects.filter(
        user=request.user,
        status='pending',
        startdate__gte=start_of_month
    ).count()
    
    # Get pending tickets for current user
    pending_tickets = Ticket.objects.filter(
        user=request.user,
        statut='pending',
        created_at__gte=start_of_month
    ).count()
    
    # Get user's notes for this month
    notes = Note.objects.filter(user=request.user, date__gte=start_of_month)
    
    context = {
        'pending_leaves': pending_leaves,
        'pending_tickets': pending_tickets,
        'current_month': today.strftime('%B %Y'),
        'current_day': current_day,
        'today': today,
        'notes': notes
    }
    
    return render(request, 'dashboard/calendrier.html', context)

def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        date_str = request.POST.get('date')
        
        if not all([title, content, date_str]):
            messages.error(request, 'Veuillez remplir tous les champs')
            return redirect('calendrier')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            note = Note.objects.create(
                user=request.user,
                title=title,
                content=content,
                date=date
            )
            messages.success(request, 'Note ajoutée avec succès!')
        except Exception as e:
            messages.error(request, "Erreur lors de l'ajout de la note")
            
        return redirect('dashboard:calendrier')
    return redirect('dashboard:calendrier')

def acceuil(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Récupérer les données de l'employé
    employee = Employee.objects.filter(user=request.user).first()
    
    # Calculer le solde de congés restants (26 jours - congés utilisés)
    total_leave_days = 26  # Solde annuel par défaut
    used_leave_days = 0
    
    # Calculer les congés utilisés (approuvés) pour l'année en cours
    current_year = timezone.now().year
    approved_leaves = Leave.objects.filter(
        user=request.user,
        status='approved',
        startdate__year=current_year
    )
    
    for leave in approved_leaves:
        if leave.startdate and leave.enddate:
            days = (leave.enddate - leave.startdate).days + 1
            used_leave_days += days
    
    remaining_leave_days = total_leave_days - used_leave_days
    
    # Calculer le solde de billets restants (4 billets annuels)
    total_tickets = 4  # Solde annuel de billets
    used_tickets = Ticket.objects.filter(
        user=request.user,
        statut='Accepté',
        created_at__year=current_year
    ).count()
    
    remaining_tickets = total_tickets - used_tickets
    
    # Récupérer les congés en cours (pending)
    pending_leaves = Leave.objects.filter(
        user=request.user,
        status='pending'
    ).count()
    
    # Récupérer les tickets en cours (pending)
    pending_tickets = Ticket.objects.filter(
        user=request.user,
        statut='En attente'
    ).count()
    
    # Données pour les graphiques miniatures (7 derniers jours)
    from datetime import timedelta
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    # Congés des 7 derniers jours
    recent_leaves = Leave.objects.filter(
        user=request.user,
        created__date__gte=start_date
    ).values('created__date').annotate(count=Count('id')).order_by('created__date')
    
    # Tickets des 7 derniers jours
    recent_tickets = Ticket.objects.filter(
        user=request.user,
        created_at__date__gte=start_date
    ).values('created_at__date').annotate(count=Count('id')).order_by('created_at__date')
    
    # Préparer les données pour les graphiques
    leave_dates = []
    leave_counts = []
    ticket_dates = []
    ticket_counts = []
    
    for i in range(7):
        date = start_date + timedelta(days=i)
        leave_count = next((item['count'] for item in recent_leaves if item['created__date'] == date), 0)
        ticket_count = next((item['count'] for item in recent_tickets if item['created_at__date'] == date), 0)
        
        leave_dates.append(date.strftime('%d/%m'))
        leave_counts.append(leave_count)
        ticket_dates.append(date.strftime('%d/%m'))
        ticket_counts.append(ticket_count)
    
    # Statistiques de validation
    total_leaves = Leave.objects.filter(user=request.user).count()
    approved_leaves_count = Leave.objects.filter(user=request.user, status='approved').count()
    approval_rate = (approved_leaves_count / total_leaves * 100) if total_leaves > 0 else 0
    
    total_tickets_count = Ticket.objects.filter(user=request.user).count()
    approved_tickets_count = Ticket.objects.filter(user=request.user, statut='Accepté').count()
    ticket_approval_rate = (approved_tickets_count / total_tickets_count * 100) if total_tickets_count > 0 else 0
    
    # Calculer la valeur restante pour le graphique
    remaining_rate = 100 - approval_rate - ticket_approval_rate
    if remaining_rate < 0:
        remaining_rate = 0
    
    context = {
        'employee': employee,
        'remaining_leave_days': remaining_leave_days,
        'remaining_tickets': remaining_tickets,
        'pending_leaves': pending_leaves,
        'pending_tickets': pending_tickets,
        'leave_dates': leave_dates,
        'leave_counts': leave_counts,
        'ticket_dates': ticket_dates,
        'ticket_counts': ticket_counts,
        'approval_rate': round(approval_rate, 1),
        'ticket_approval_rate': round(ticket_approval_rate, 1),
        'remaining_rate': round(remaining_rate, 1),
        'total_leave_days': total_leave_days,
        'total_tickets': total_tickets,
        'used_leave_days': used_leave_days,
        'used_tickets': used_tickets,
    }
    
    return render(request, 'dashboard/acceuil.html', context)
     
def print_leave(request, leave_id):
    leave = Leave.objects.get(id=leave_id)
    context = {'leave': leave}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="leave_{leave.id}.pdf"'

    template_path = 'dashboard/leave_template.html'
    template = get_template(template_path)
    html = template.render(context, request)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response

def print_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    context = {'ticket': ticket}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="billet_{ticket.id}.pdf"'

    template_path = 'dashboard/ticket_template.html'
    template = get_template(template_path)
    html = template.render(context, request)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response

def statistiques_view(request):
    # Données pour le pie chart (répartition des congés par utilisateur)
    conges_par_user = Leave.objects.values('user__username').annotate(nombre=Count('id'))

    # Données pour le bar chart (comparaison congés vs tickets)
    users = User.objects.all()
    conges_data = []
    tickets_data = []
    labels = []

    for user in users:
        labels.append(user.username)
        conges_data.append(Leave.objects.filter(user=user).count())
        tickets_data.append(Ticket.objects.filter(user=user).count())

    context = {
        'labels': labels,
        'conges_data': conges_data,
        'tickets_data': tickets_data,
        'conges_par_user': list(conges_par_user),
    }

    return render(request, 'dashboard/dashboard_index.html', context)
    
#------------dashboard------------------------------------
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    employees = Employee.objects.all()
    leaves = Leave.objects.all_pending_leaves()
    tickets = Ticket.objects.all_pending_tickets()
    staff_leaves = Leave.objects.filter(user=request.user)
    staff_tickets = Ticket.objects.filter(user=request.user)

    # Get leave data for the chart (by status)
    leave_statuses = Leave.objects.values('status').annotate(count=Count('id'))
    leave_labels = [item['status'] for item in leave_statuses]
    leave_counts = [item['count'] for item in leave_statuses]

    # Get destination data for the ticket chart
    destination_data = Ticket.objects.values('destination').annotate(count=Count('id'))
    destination_labels = [item['destination'] for item in destination_data]
    destination_counts = [item['count'] for item in destination_data]
                                
    # Initialize notification variables
    total_admin_notifications = 0
    total_staff_notifications = 0
    total_user_notifications = 0
    total_notifications = 0

    # Calculate notification counts based on user type
    if request.user.is_superuser:
        total_admin_notifications = leaves.count() + tickets.count()
        total_notifications = total_admin_notifications
    elif request.user.is_staff:
        total_staff_notifications = staff_leaves.count() + staff_tickets.count()
        total_notifications = total_staff_notifications
    else:
        total_user_notifications = staff_leaves.count() + staff_tickets.count()
        total_notifications = total_user_notifications
    
    dataset = {
        'employees': employees, 
        'leaves': leaves, 
        'tickets': tickets, 
        'staff_leaves': staff_leaves, 
        'staff_tickets': staff_tickets, 
        'title': 'summary',
        'leave_labels': json.dumps(leave_labels),
        'leave_counts': json.dumps(leave_counts),
        'destination_labels': json.dumps(destination_labels),
        'destination_counts': json.dumps(destination_counts),
        'total_admin_notifications': total_admin_notifications if request.user.is_superuser else 0,
        'total_staff_notifications': total_staff_notifications if request.user.is_staff else 0,
        'total_user_notifications': total_user_notifications if not (request.user.is_superuser or request.user.is_staff) else 0,
        'total_notifications': total_notifications
    }

    if request.user.is_superuser and request.user.is_staff:
        return render(request, 'dashboard/advanced_analytics.html', dataset)
    else:
        return render(request, 'dashboard/acceuil.html', dataset)

def dashboard_employees(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    departments = Department.objects.all()
    employees = Employee.objects.all()

    query = request.GET.get('search')
    if query:
        employees = employees.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query)
        )

    paginator = Paginator(employees, 10)
    page = request.GET.get('page')
    employees_paginated = paginator.get_page(page)

    blocked_employees = Employee.objects.all_blocked_employees()

    dataset = {'departments': departments, 'employees': employees_paginated, 'blocked_employees': blocked_employees, 'title': 'employees'}

    return render(request, 'dashboard/employee_app.html', dataset)

def dashboard_employees_create(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            user_id = request.POST.get('user')
            assigned_user = User.objects.get(id=user_id)
            instance.user = assigned_user
            instance.employeeid = request.POST.get('employeeid')
            instance.image = request.FILES.get('image')
            instance.firstname = request.POST.get('firstname')
            instance.lastname = request.POST.get('lastname')
            instance.birthday = request.POST.get('birthday')
            instance.employeetype = request.POST.get('employeetype')
            instance.save()
            messages.success(request, 'Employé ajouté avec succès.')
            return redirect('dashboard:employeecreate')

    form = EmployeeCreateForm()
    dataset = {'form': form, 'title': 'enregistrer employé'}

    return render(request, 'dashboard/employee_create.html', dataset)

def employee_edit(request, id):
    employee = Employee.objects.get(id=id)
    form = EmployeeCreateForm(instance=employee)
    dataset = {'form': form, 'title': 'Modifier - {0}'.format(employee.get_full_name)}
    return render(request, 'dashboard/employee_edit.html', dataset)
    

def employee_edit_data(request, id): 
    if not (request.user.is_superuser and request.user.is_staff):
        messages.error(request, 'Vous n\'avez pas les permissions nécessaires pour modifier les employés.')
        return redirect('dashboard:employees')

    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            instance = form.save(commit=False)

            # Récupération et assignation explicite du user si nécessaire
            user_id = request.POST.get('user')
            if user_id:
                try:
                    instance.user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    messages.warning(request, 'Utilisateur assigné non trouvé. L\'assignation a été ignorée.')

            instance.save()
            messages.success(request, 'Les informations de l\'employé ont été mises à jour avec succès.')
            return redirect('dashboard:employees')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = EmployeeCreateForm(instance=employee)

    context = {
        'form': form,
        'title': f'Modifier - {employee.get_full_name}',
    }
    return render(request, 'dashboard/employee_edit.html', context)

def dashboard_employee_info(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/')

    try:
        user = User.objects.get(id=user_id)
        employee = Employee.objects.get(user=user)
    except (User.DoesNotExist, Employee.DoesNotExist):
        return redirect('/')

    dataset = {'employee': employee, 'title': 'profile - {0}'.format(employee.get_full_name)}

    return render(request, 'dashboard/user_profile_page.html', dataset)

def employees(request, user_id):
    if not request.user.is_authenticated:
        return redirect('/')

    employees = Employee.objects.all()
    dataset = {'employees': employees, 'title': 'employees'}

    return render(request, 'dashboard/employees.html', dataset)

#---------------------beneficiaire----------------------------

def dashboard_beneficiaire_create(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    if request.method == 'POST':
        form = BeneficiaireCreateForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            user_id = request.POST.get('user')
            assigned_user = User.objects.get(id=user_id)
            instance.utilisateur = assigned_user
            instance.nom_et_prenom = request.POST.get('nom_et_prenom')
            instance.date_naissance = request.POST.get('date_naissance')
            instance.save()
            messages.success(request, 'Bénéficiaire ajouté avec succès.')
            return redirect('dashboard:beneficiairecreate')

    form = BeneficiaireCreateForm()
    dataset = {'form': form, 'title': 'Créer bénéficiaire'}

    return render(request, 'dashboard/beneficiaire_create.html', dataset)

def beneficiaires(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    beneficiaires = Beneficiaire.objects.all()

    dataset = {'beneficiaires': beneficiaires, 'title': 'vos bénéficiaires'}

    return render(request, 'dashboard/beneficiaires.html', dataset)

# ---------------------LEAVE-------------------------------------------

def leave_creation(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        form = LeaveCreationForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            user = request.user
            instance.user = user
            instance.save()

            # Analyse AI automatique
            if ai_integration:
                try:
                    ai_integration.analyze_leave_ai(instance)
                    messages.info(request, '✅ Analyse IA effectuée automatiquement - Priorité: {}, Probabilité d\'approbation: {}%'.format(
                        instance.ai_priority or 'Non définie',
                        int((instance.ai_approval_probability or 0) * 100)
                    ), extra_tags='alert alert-info alert-dismissible show')
                except Exception as e:
                    messages.warning(request, '⚠️ Analyse IA non disponible - Demande traitée normalement', extra_tags='alert alert-warning alert-dismissible show')

            messages.success(request, 'Demande de congé envoyée, veuillez attendre la réponse des gestionnaires de congé de TUNISAIR Express', extra_tags='alert alert-success alert-dismissible show')
            return redirect('dashboard:createleave')

    form = LeaveCreationForm()
    dataset = {'form': form, 'title': 'Demandez un congé'}

    return render(request, 'dashboard/create_leave.html', dataset)

def leaves_list(request):
    if not (request.user.is_staff and request.user.is_superuser):
        return redirect('/')

    leaves = Leave.objects.all_pending_leaves()

    return render(request, 'dashboard/leaves_recent.html', {'leave_list': leaves, 'title': ' liste de congés - en attente'})

def leaves_approved_list(request):
    if not (request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    leaves = Leave.objects.all_approved_leaves()
    return render(request, 'dashboard/leaves_approved.html', {'leave_list': leaves, 'title': ' liste de congés approuvés'})

def leaves(request):
    if not (request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    leaves = Leave.objects.all()

    return render(request, 'dashboard/leaves.html', {'leave_list': leaves, 'title': ' liste de congés approuvés'})

def leaves_view(request, id):

    if not request.user.is_authenticated:
        return redirect('/')

    leave = get_object_or_404(Leave, id=id)
    print(leave.user)
    employee = None
    if Employee.objects.filter(user=leave.user).exists():
        employee = Employee.objects.get(user=leave.user)
    print(employee)
    
    # Ajouter les données AI au contexte
    ai_data = {}
    if ai_integration:
        ai_data = {
            'priority_color': ai_integration.get_priority_color(leave.ai_priority),
            'approval_percentage': ai_integration.format_confidence(leave.ai_approval_probability),
            'priority_percentage': ai_integration.format_confidence(leave.ai_priority_score),
        }
    
    context = {
        'leave': leave, 
        'employee': employee, 
        'ai_data': ai_data,
        'title': '{0}-{1} leave'.format(leave.user.username, leave.status)
    }
    return render(request, 'dashboard/leave_detail_view.html', context)

def approve_leave(request, id):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')

    leave = get_object_or_404(Leave, id=id)
    user = leave.user
    employee = Employee.objects.filter(user = user)[0]

    leave.approve_leave

    messages.success(request, 'Congé approuvé avec succès pour {}'.format(employee.get_full_name), extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:userleaveview', id = id)

def cancel_leaves_list(request):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')

    leaves = Leave.objects.all_cancel_leaves()

    return render(request, 'dashboard/leaves_cancel.html', {'leave_list_cancel': leaves, 'title': ' liste des congés annulés'})

def unapprove_leave(request, id):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect('/')

    leave = get_object_or_404(Leave, id=id)
    leave.unapprove_leave

    return redirect('dashboard:leaveslist')

def cancel_leave(request, id):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')

    leave = get_object_or_404(Leave, id=id)
    leave.leaves_cancel

    messages.success(request, 'Congé annulé', extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:canceleaveslist')

def uncancel_leave(request, id):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')

    leave = get_object_or_404(Leave, id=id)
    leave.status = 'pending'
    leave.is_approved = False
    leave.save()

    messages.success(request, 'Congé annulé, Désormais dans la liste en attente', extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:canceleaveslist')

def leave_rejected_list(request):
    dataset = dict()
    leave = Leave.objects.all_rejected_leaves()

    dataset['leave_list_rejected'] = leave
    return render(request, 'dashboard/rejected_leaves_list.html', dataset)

def reject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    leave.reject_leave

    messages.success(request, 'congé refusé', extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:leavesrejected')

def unreject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    leave.status = 'pending'
    leave.is_approved = False
    leave.save()

    messages.success(request, 'Désormais dans la liste en attente ', extra_tags='alert alert-success alert-dismissible show')

    return redirect('dashboard:leavesrejected')

#  staffs leaves table user only
def view_my_leave_table(request):
    if request.user.is_authenticated:
        user = request.user
        leaves = Leave.objects.filter(user=user)
        employee = Employee.objects.filter(user=user).first()

        dataset = dict()
        dataset['leaves'] = leaves
        dataset['employee'] = employee
        dataset['title'] = 'Leaves List'
    else:
        return redirect('accounts:login')

    return render(request, 'dashboard/staff_leaves_table.html', dataset)

#----------------ticket--------------
def ticket_creation(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        form = ticketForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            user = request.user
            instance.user = user
            instance.save()

            # Analyse AI automatique
            if ai_integration:
                try:
                    ai_integration.analyze_ticket_ai(instance)
                    messages.info(request, '✅ Analyse IA effectuée automatiquement - Priorité: {}, Catégorie: {}, Sentiment: {}'.format(
                        instance.ai_priority or 'Non définie',
                        instance.ai_category or 'Non définie',
                        instance.ai_sentiment or 'Neutre'
                    ), extra_tags='alert alert-info alert-dismissible show')
                except Exception as e:
                    messages.warning(request, '⚠️ Analyse IA non disponible - Demande traitée normalement', extra_tags='alert alert-warning alert-dismissible show')

            messages.success(request, 'Demande de billet envoyée, veuillez attendre la réponse des gestionnaires de OEBTR de TUNISAIR Express', extra_tags='alert alert-success alert-dismissible show')
            return redirect('dashboard:createticket')

    form = ticketForm()
    dataset = {'form': form, 'title': 'demander une billet'}

    return render(request, 'dashboard/create_ticket.html', dataset)



def tickets_list(request):
	if not (request.user.is_staff and request.user.is_superuser):
		return redirect('/')
	tickets = Ticket.objects.all_pending_tickets()
	return render(request,'dashboard/tickets_attente.html',{'ticket_list':tickets,'title':' liste de billets -En attente'})

def tickets(request):
	if not (request.user.is_staff and request.user.is_superuser):
		return redirect('/')
	tickets = Ticket.objects.all()
	return render(request,'dashboard/tickets_recent.html',{'ticket_list':tickets,'title':' liste de billets'})



def tickets_approved_list(request):
	if not (request.user.is_superuser and request.user.is_staff):
		return redirect('/')
	tickets = Ticket.objects.all_approved_tickets() 
	return render(request,'dashboard/tickets_approved.html',{'ticket_list':tickets,'title':'liste de billets approuvés'})


def tickets_view(request,id):
	if not (request.user.is_authenticated):
		return redirect('/')

	ticket = get_object_or_404(Ticket, id = id)
	print(ticket.user)
	employees = Employee.objects.filter(user = ticket.user)
	if employees.exists():
		employee = employees.first()
	else:
		employee = None
	print(employee)
	
	# Ajouter les données AI au contexte
	ai_data = {}
	if ai_integration:
		ai_data = {
			'priority_color': ai_integration.get_priority_color(ticket.ai_priority),
			'sentiment_icon': ai_integration.get_sentiment_icon(ticket.ai_sentiment),
			'category_confidence': ai_integration.format_confidence(ticket.ai_category_confidence),
			'priority_percentage': ai_integration.format_confidence(ticket.ai_priority_score),
			'sentiment_percentage': ai_integration.format_confidence(ticket.ai_sentiment_score),
		}
	
	context = {
		'ticket': ticket,
		'employee': employee,
		'ai_data': ai_data,
		'title': '{0}-{1} billet'.format(ticket.user.username,ticket.statut)
	}
	return render(request,'dashboard/ticket_detail_view.html', context)


def approve_ticket(request,id):
	if not (request.user.is_superuser and request.user.is_authenticated):
		return redirect('/')
     
	ticket = get_object_or_404(Ticket, id = id)
	user = ticket.user
	employee = Employee.objects.filter(user = user)[0]
	ticket.approve_ticket

	messages.success(request,'demande de billet approuvé avec succès pour {0}'.format(employee.get_full_name),extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('dashboard:user_ticket_view', id = id)



def unapprove_ticket(request,id):
	if not (request.user.is_authenticated and request.user.is_superuser):
		return redirect('/')
     
	ticket = get_object_or_404(Ticket, id = id)
	ticket.unapprove_ticket
     
	return redirect('dashboard:ticketslist') #redirect to unapproved list






def ticket_rejected_list(request):

	dataset = dict()
	ticket = Ticket.objects.all_rejected_tickets()

	dataset['ticket_list_rejected'] = ticket
	return render(request,'dashboard/rejected_tickets_list.html',dataset)



def reject_ticket(request,id):
	ticket = get_object_or_404(Ticket, id = id)
	ticket.reject_ticket
     
	messages.success(request,' demande de billet refusé',extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('dashboard:ticketsrejected')

	# return HttpResponse(id)


def unreject_ticket(request,id):
	ticket = get_object_or_404(Ticket, id = id)
	ticket.statut = 'En attente'
	ticket.is_approved = False
	ticket.save()
     
	messages.success(request,'Désormais dans la liste en attente ',extra_tags = 'alert alert-success alert-dismissible show')

	return redirect('dashboard:ticketsrejected')


def view_my_ticket_table(request):
    if request.user.is_authenticated:
        user = request.user
        tickets = Ticket.objects.filter(user=user)
        employee = Employee.objects.filter(user=user).first()
        print(tickets)
        dataset = dict()
        dataset['tickets'] = tickets
        dataset['employee'] = employee
        dataset['title'] = 'Tickets List'
    else:
        return redirect('accounts:login')
    
    return render(request,'dashboard/staff_tickets_table.html',dataset)

# Ticket cancellation views
def cancel_tickets_list(request):
    tickets = Ticket.objects.filter(status='cancelled')
    return render(request, 'dashboard/cancelled_tickets.html', {'tickets': tickets})

def cancel_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    ticket.status = 'cancelled'
    ticket.save()
    messages.success(request, 'Ticket has been cancelled successfully.')
    return redirect('dashboard:tickets')

def uncancel_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    ticket.status = 'pending'
    ticket.save()
    messages.success(request, 'Ticket has been uncancelled successfully.')
    return redirect('dashboard:tickets')

def advanced_analytics_dashboard(request):
    """Dashboard analytics avancé avec KPI RH et support"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Période d'analyse (mois en cours)
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = start_of_month.replace(day=calendar.monthrange(today.year, today.month)[1])
    
    # === KPI CONGÉS ===
    # Taux d'absentéisme par département
    departments = Department.objects.all()
    absenteeism_data = []
    for dept in departments:
        employees_in_dept = Employee.objects.filter(department=dept).count()
        if employees_in_dept > 0:
            # Utiliser toutes les données, pas seulement le mois en cours
            leaves_in_dept = Leave.objects.filter(
                user__employee__department=dept,
                status='approved'
            ).count()
            absenteeism_rate = (leaves_in_dept / employees_in_dept) * 100
            absenteeism_data.append({
                'department': dept.name,
                'rate': round(absenteeism_rate, 2)
            })
    
    # Fallback si pas de données d'absentéisme
    if not absenteeism_data:
        absenteeism_data = [{'department': 'Aucun département', 'rate': 0}]
    
    # Délai moyen de validation des congés
    avg_approval_result = Leave.objects.filter(
        status='approved',
        created__gte=start_of_month
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_time=Avg('response_time')
    )['avg_time']
    avg_approval_time = avg_approval_result.days if avg_approval_result else 0
    
    # Temps de réponse moyen des congés (en jours)
    avg_leave_response_result = Leave.objects.filter(
        status__in=['approved', 'rejected']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_response_time=Avg('response_time')
    )['avg_response_time']
    avg_leave_response_time = avg_leave_response_result.days if avg_leave_response_result else 0
    
    # Temps de réponse moyen des tickets (en jours)
    avg_ticket_response_result = Ticket.objects.filter(
        statut__in=['Accepté', 'Refusé']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created_at'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_response_time=Avg('response_time')
    )['avg_response_time']
    avg_ticket_response_time = avg_ticket_response_result.days if avg_ticket_response_result else 0
    
    # Temps de réponse moyen global (congés + tickets)
    avg_global_response_time = 0
    total_responded_items = 0
    
    leave_response_count = Leave.objects.filter(
        status__in=['approved', 'rejected']
    ).count()
    
    ticket_response_count = Ticket.objects.filter(
        statut__in=['Accepté', 'Refusé']
    ).count()
    
    total_responded_items = leave_response_count + ticket_response_count
    
    if total_responded_items > 0:
        leave_total = Leave.objects.filter(
            status__in=['approved', 'rejected']
        ).annotate(
            response_time=ExpressionWrapper(
                F('updated') - F('created'),
                output_field=DurationField()
            )
        ).aggregate(total=Sum('response_time'))['total']
        
        ticket_total = Ticket.objects.filter(
            statut__in=['Accepté', 'Refusé']
        ).annotate(
            response_time=ExpressionWrapper(
                F('updated') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(total=Sum('response_time'))['total']
        
        # Convertir en jours pour le calcul
        leave_days = leave_total.days if leave_total else 0
        ticket_days = ticket_total.days if ticket_total else 0
        
        total_response_time_days = leave_days + ticket_days
        avg_global_response_time = total_response_time_days / total_responded_items if total_responded_items > 0 else 0
    
    # Répartition par type de congé
    leave_types = Leave.objects.values('leavetype').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Fallback si pas de types de congés
    if not leave_types:
        leave_types = [{'leavetype': 'Aucun type', 'count': 0}]
    
    # === KPI TICKETS ===
    # Taux d'annulation/modification
    total_tickets = Ticket.objects.filter(created_at__gte=start_of_month).count()
    cancelled_tickets = Ticket.objects.filter(
        created_at__gte=start_of_month,
        statut='refuse'
    ).count()
    cancellation_rate = (cancelled_tickets / total_tickets * 100) if total_tickets > 0 else 0
    
    # Destinations les plus populaires
    popular_destinations = Ticket.objects.values('destination').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Fallback si pas de destinations
    if not popular_destinations:
        popular_destinations = [{'destination': 'Aucune destination', 'count': 0}]
    
    # Délai moyen de traitement
    avg_processing_result = Ticket.objects.filter(
        statut__in=['Accepté', 'Refusé'],
        created_at__gte=start_of_month
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created_at'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_time=Avg('response_time')
    )['avg_time']
    avg_processing_time = avg_processing_result.days if avg_processing_result else 0
    
    # === Données pour graphiques ===
    # Données pour les diagrammes du dashboard
    # Répartition par statut de congés
    leave_status_data = Leave.objects.values('status').annotate(count=Count('id'))
    leave_labels = [item['status'] for item in leave_status_data]
    leave_counts = [item['count'] for item in leave_status_data]
    
    # Distribution des destinations
    destination_data = Ticket.objects.values('destination').annotate(count=Count('id')).order_by('-count')[:6]
    destination_labels = [item['destination'] for item in destination_data]
    destination_counts = [item['count'] for item in destination_data]
    
    # Vérification et fallback si pas de données
    if not leave_labels:
        leave_labels = ['Aucun congé']
        leave_counts = [0]
    
    if not destination_labels:
        destination_labels = ['Aucune destination']
        destination_counts = [0]
    
    # Évolution temporelle des congés (6 derniers mois)
    monthly_leaves = []
    for i in range(6):
        month_start = today - timedelta(days=30*i)
        month_start = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
        
        count = Leave.objects.filter(
            startdate__gte=month_start,
            startdate__lte=month_end
        ).count()
        monthly_leaves.append({
            'month': month_start.strftime('%B %Y'),
            'count': count
        })
    
    # Évolution temporelle des tickets
    monthly_tickets = []
    for i in range(6):
        month_start = today - timedelta(days=30*i)
        month_start = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
        
        count = Ticket.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        monthly_tickets.append({
            'month': month_start.strftime('%B %Y'),
            'count': count
        })
    
    # Évolution des temps de réponse (6 derniers mois)
    response_time_trend = []
    for i in range(6):
        month_start = today - timedelta(days=30*i)
        month_start = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
        
        # Temps de réponse moyen des congés pour ce mois
        avg_leave_response_result = Leave.objects.filter(
            updated__gte=month_start,
            updated__lte=month_end,
            status__in=['approved', 'rejected']
        ).annotate(
            response_time=ExpressionWrapper(
                F('updated') - F('created'),
                output_field=DurationField()
            )
        ).aggregate(avg=Avg('response_time'))['avg']
        avg_leave_response = avg_leave_response_result.days if avg_leave_response_result else 0
        
        # Temps de réponse moyen des tickets pour ce mois
        avg_ticket_response_result = Ticket.objects.filter(
            updated__gte=month_start,
            updated__lte=month_end,
            statut__in=['Accepté', 'Refusé']
        ).annotate(
            response_time=ExpressionWrapper(
                F('updated') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(avg=Avg('response_time'))['avg']
        avg_ticket_response = avg_ticket_response_result.days if avg_ticket_response_result else 0
        
        response_time_trend.append({
            'month': month_start.strftime('%B %Y'),
            'leave_response': round(avg_leave_response, 1),
            'ticket_response': round(avg_ticket_response, 1)
        })
    
    # Insights AI
    ai_insights = []
    ai_analytics_data = {}
    
    # Statistiques IA
    total_leaves_analyzed = Leave.objects.filter(ai_analysis_date__isnull=False).count()
    total_tickets_analyzed = Ticket.objects.filter(ai_analysis_date__isnull=False).count()
    
    # Moyennes des scores IA
    avg_approval_prob = Leave.objects.filter(ai_approval_probability__gt=0).aggregate(
        avg=Avg('ai_approval_probability')
    )['avg'] or 0
    
    avg_priority_score = Ticket.objects.filter(ai_priority_score__gt=0).aggregate(
        avg=Avg('ai_priority_score')
    )['avg'] or 0
    
    # Distribution des priorités IA
    priority_distribution = Ticket.objects.values('ai_priority').annotate(
        count=Count('id')
    ).filter(ai_priority__isnull=False)
    
    # Distribution des sentiments IA
    sentiment_distribution = Ticket.objects.values('ai_sentiment').annotate(
        count=Count('id')
    ).filter(ai_sentiment__isnull=False)
    
    # Distribution des catégories IA
    category_distribution = Ticket.objects.values('ai_category').annotate(
        count=Count('id')
    ).filter(ai_category__isnull=False)
    
    if ai_integration:
        try:
            ai_insights = ai_integration.get_ai_insights()
            ai_analytics_data = ai_integration.get_analytics_data()
        except Exception as e:
            ai_insights = []
            ai_analytics_data = {}
    
    # Génération d'insights IA supplémentaires
    additional_ai_insights = []
    
    # Insight sur l'analyse des congés
    if total_leaves_analyzed > 0:
        analysis_rate = (total_leaves_analyzed / Leave.objects.count()) * 100
        additional_ai_insights.append(f"📊 {total_leaves_analyzed} congés analysés par IA ({analysis_rate:.1f}%)")
        
        if avg_approval_prob > 0:
            additional_ai_insights.append(f"🎯 Probabilité moyenne d'approbation: {avg_approval_prob*100:.1f}%")
    
    # Insight sur l'analyse des tickets
    if total_tickets_analyzed > 0:
        analysis_rate = (total_tickets_analyzed / Ticket.objects.count()) * 100
        additional_ai_insights.append(f"📊 {total_tickets_analyzed} tickets analysés par IA ({analysis_rate:.1f}%)")
        
        if avg_priority_score > 0:
            additional_ai_insights.append(f"🎯 Score de priorité moyen: {avg_priority_score*100:.1f}%")
    
    # Insight sur les sentiments
    if sentiment_distribution:
        positive_tickets = sum(item['count'] for item in sentiment_distribution if item['ai_sentiment'] == 'positive')
        negative_tickets = sum(item['count'] for item in sentiment_distribution if item['ai_sentiment'] == 'negative')
        total_sentiment = sum(item['count'] for item in sentiment_distribution)
        
        if total_sentiment > 0:
            positive_rate = (positive_tickets / total_sentiment) * 100
            negative_rate = (negative_tickets / total_sentiment) * 100
            additional_ai_insights.append(f"😊 Sentiment positif: {positive_rate:.1f}% | 😞 Sentiment négatif: {negative_rate:.1f}%")
    
    # Combiner les insights
    all_ai_insights = ai_insights + additional_ai_insights
    
    context = {
        'absenteeism_data': absenteeism_data,
        'avg_approval_time': avg_approval_time,
        'leave_types': list(leave_types),
        'cancellation_rate': round(cancellation_rate, 2),
        'popular_destinations': list(popular_destinations),
        'avg_processing_time': avg_processing_time,
        'monthly_leaves': monthly_leaves,
        'monthly_tickets': monthly_tickets,
        'total_employees': Employee.objects.count(),
        'total_leaves_month': Leave.objects.filter(startdate__gte=start_of_month).count(),
        'total_tickets_month': total_tickets,
        'pending_leaves': Leave.objects.filter(status='pending').count(),
        'pending_tickets': Ticket.objects.filter(statut='En attente').count(),
        # Données pour les diagrammes du dashboard
        'leave_labels': leave_labels,
        'leave_counts': leave_counts,
        'destination_labels': destination_labels,
        'destination_counts': destination_counts,
        # Insights AI
        'ai_insights': all_ai_insights,
        'ai_analytics_data': ai_analytics_data,
        'total_leaves_analyzed': total_leaves_analyzed,
        'total_tickets_analyzed': total_tickets_analyzed,
        'avg_approval_probability': round(avg_approval_prob * 100, 1),
        'avg_priority_score': round(avg_priority_score * 100, 1),
        'priority_distribution': list(priority_distribution),
        'sentiment_distribution': list(sentiment_distribution),
        'category_distribution': list(category_distribution),
        # Métriques de temps de réponse
        'avg_leave_response_time': round(avg_leave_response_time, 1),
        'avg_ticket_response_time': round(avg_ticket_response_time, 1),
        'avg_global_response_time': round(avg_global_response_time, 1),
        'total_responded_items': total_responded_items,
        'response_time_trend': response_time_trend,
    }
    
    return render(request, 'dashboard/advanced_analytics.html', context)

def monthly_report(request):
    """Vue pour afficher le rapport mensuel"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if reporting_service is None:
        messages.error(request, 'Le service de reporting n\'est pas encore disponible.')
        return redirect('dashboard:dashboard')
    
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        report_data = reporting_service.generate_monthly_report_data(int(month), int(year))
    else:
        report_data = reporting_service.generate_monthly_report_data()
    
    # Ajout des données IA au rapport mensuel
    ai_report_data = {}
    
    # Statistiques IA pour le mois
    if month and year:
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1)
    else:
        today = timezone.now()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(day=calendar.monthrange(today.year, today.month)[1])
    
    # Congés analysés par IA ce mois
    leaves_analyzed_this_month = Leave.objects.filter(
        ai_analysis_date__gte=start_date,
        ai_analysis_date__lt=end_date
    ).count()
    
    # Tickets analysés par IA ce mois
    tickets_analyzed_this_month = Ticket.objects.filter(
        ai_analysis_date__gte=start_date,
        ai_analysis_date__lt=end_date
    ).count()
    
    # Moyennes des scores IA pour le mois
    avg_approval_prob_month = Leave.objects.filter(
        ai_approval_probability__gt=0,
        ai_analysis_date__gte=start_date,
        ai_analysis_date__lt=end_date
    ).aggregate(avg=Avg('ai_approval_probability'))['avg'] or 0
    
    avg_priority_score_month = Ticket.objects.filter(
        ai_priority_score__gt=0,
        ai_analysis_date__gte=start_date,
        ai_analysis_date__lt=end_date
    ).aggregate(avg=Avg('ai_priority_score'))['avg'] or 0
    
    # Distribution des sentiments pour le mois
    sentiment_distribution_month = Ticket.objects.filter(
        ai_sentiment__isnull=False,
        ai_analysis_date__gte=start_date,
        ai_analysis_date__lt=end_date
    ).values('ai_sentiment').annotate(count=Count('id'))
    
    ai_report_data = {
        'leaves_analyzed_this_month': leaves_analyzed_this_month,
        'tickets_analyzed_this_month': tickets_analyzed_this_month,
        'avg_approval_probability_month': round(avg_approval_prob_month * 100, 1),
        'avg_priority_score_month': round(avg_priority_score_month * 100, 1),
        'sentiment_distribution_month': list(sentiment_distribution_month),
        'ai_insights': []
    }
    
    # Génération d'insights IA pour le rapport
    if leaves_analyzed_this_month > 0:
        ai_report_data['ai_insights'].append(f"🤖 {leaves_analyzed_this_month} congés analysés par IA ce mois")
        if avg_approval_prob_month > 0:
            ai_report_data['ai_insights'].append(f"🎯 Probabilité d'approbation moyenne: {avg_approval_prob_month*100:.1f}%")
    
    if tickets_analyzed_this_month > 0:
        ai_report_data['ai_insights'].append(f"🤖 {tickets_analyzed_this_month} tickets analysés par IA ce mois")
        if avg_priority_score_month > 0:
            ai_report_data['ai_insights'].append(f"🎯 Score de priorité moyen: {avg_priority_score_month*100:.1f}%")
    
    # Analyse des sentiments
    if sentiment_distribution_month:
        positive_count = sum(item['count'] for item in sentiment_distribution_month if item['ai_sentiment'] == 'positive')
        negative_count = sum(item['count'] for item in sentiment_distribution_month if item['ai_sentiment'] == 'negative')
        total_sentiment = sum(item['count'] for item in sentiment_distribution_month)
        
        if total_sentiment > 0:
            positive_rate = (positive_count / total_sentiment) * 100
            negative_rate = (negative_count / total_sentiment) * 100
            ai_report_data['ai_insights'].append(f"😊 Sentiment positif: {positive_rate:.1f}% | 😞 Sentiment négatif: {negative_rate:.1f}%")
    
    context = {
        'report_data': report_data,
        'ai_report_data': ai_report_data
    }
    
    return render(request, 'dashboard/monthly_report.html', context)
    
def export_excel_report(request):
    """Export du rapport en Excel"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if reporting_service is None:
        messages.error(request, 'Le service de reporting n\'est pas encore disponible.')
        return redirect('dashboard:dashboard')
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        report_data = reporting_service.generate_monthly_report_data(int(month), int(year))
    else:
        report_data = reporting_service.generate_monthly_report_data()
    
    return reporting_service.export_excel_report(report_data)

def export_pdf_report(request):
    """Export du rapport en PDF"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if reporting_service is None:
        messages.error(request, 'Le service de reporting n\'est pas encore disponible.')
        return redirect('dashboard:dashboard')
    
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        report_data = reporting_service.generate_monthly_report_data(int(month), int(year))
    else:
        report_data = reporting_service.generate_monthly_report_data()
    
    return reporting_service.export_pdf_report(report_data)

def export_analytics_excel(request):
    """Export du rapport analytics en Excel"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if reporting_service is None:
        messages.error(request, 'Le service de reporting n\'est pas encore disponible.')
        return redirect('dashboard:dashboard')
    
    report_data = reporting_service.generate_analytics_report_data()
    return reporting_service.export_analytics_excel_report(report_data)

def export_analytics_pdf(request):
    """Export du rapport analytics en PDF"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if reporting_service is None:
        messages.error(request, 'Le service de reporting n\'est pas encore disponible.')
        return redirect('dashboard:dashboard')
    
    report_data = reporting_service.generate_analytics_report_data()
    return reporting_service.export_analytics_pdf_report(report_data)

def analyze_sentiment(request):
    """API pour l'analyse de sentiment"""
    if ai_services is None:
        return JsonResponse({'error': 'Service IA non disponible'}, status=503)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            
            if not text:
                return JsonResponse({'error': 'Texte requis'}, status=400)
            
            sentiment_result = ai_services.analyze_sentiment(text)
            return JsonResponse(sentiment_result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def predict_priority(request):
    """API pour la prédiction de priorité"""
    if ai_services is None:
        return JsonResponse({'error': 'Service IA non disponible'}, status=503)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            user_role = data.get('user_role')
            ticket_type = data.get('ticket_type')
            
            if not text:
                return JsonResponse({'error': 'Texte requis'}, status=400)
            
            priority_result = ai_services.predict_priority(text, user_role, ticket_type)
            return JsonResponse(priority_result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def categorize_ticket(request):
    """API pour la catégorisation automatique"""
    if ai_services is None:
        return JsonResponse({'error': 'Service IA non disponible'}, status=503)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            destination = data.get('destination')
            
            if not text:
                return JsonResponse({'error': 'Texte requis'}, status=400)
            
            category_result = ai_services.categorize_ticket(text, destination)
            return JsonResponse(category_result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def predict_leave_approval(request):
    """API pour la prédiction d'approbation de congé en temps réel"""
    if ai_services is None:
        return JsonResponse({'error': 'Service IA non disponible'}, status=503)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            employee_data = data.get('employee_data', {})
            leave_data = data.get('leave_data', {})
            
            if not leave_data:
                return JsonResponse({'error': 'Données de congé requises'}, status=400)
            
            prediction_result = ai_services.predict_leave_approval(employee_data, leave_data)
            return JsonResponse(prediction_result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Erreur de prédiction: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



# === GESTION DES DÉPARTEMENTS ===
@login_required
def departments_list(request):
    """Liste des départements - accessible uniquement aux superusers"""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard:acceuil')
    
    departments = Department.objects.all().order_by('name')
    context = {
        'departments': departments,
        'title': 'Gestion des Départements'
    }
    return render(request, 'dashboard/departments_list.html', context)

@login_required
def department_create(request):
    """Créer un nouveau département - accessible uniquement aux superusers"""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard:acceuil')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        service = request.POST.get('service', '')
        
        if name:
            try:
                department = Department.objects.create(
                    name=name,
                    service=service
                )
                messages.success(request, f'Département "{name}" créé avec succès!')
                return redirect('dashboard:departments_list')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
        else:
            messages.error(request, 'Le nom du département est obligatoire')
    
    context = {
        'title': 'Créer un Département'
    }
    return render(request, 'dashboard/department_form.html', context)

@login_required
def department_edit(request, department_id):
    """Modifier un département - accessible uniquement aux superusers"""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard:acceuil')
    
    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        messages.error(request, "Département non trouvé")
        return redirect('dashboard:departments_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        service = request.POST.get('service', '')
        
        if name:
            try:
                department.name = name
                department.service = service
                department.save()
                messages.success(request, f'Département "{name}" modifié avec succès!')
                return redirect('dashboard:departments_list')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        else:
            messages.error(request, 'Le nom du département est obligatoire')
    
    context = {
        'department': department,
        'title': 'Modifier le Département'
    }
    return render(request, 'dashboard/department_form.html', context)

@login_required
def department_delete(request, department_id):
    """Supprimer un département - accessible uniquement aux superusers"""
    if not request.user.is_superuser:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard:acceuil')
    
    try:
        department = Department.objects.get(id=department_id)
        
        # Vérifier s'il y a des employés dans ce département
        employees_count = Employee.objects.filter(department=department).count()
        
        if employees_count > 0:
            messages.error(request, f'Impossible de supprimer le département "{department.name}" car il contient {employees_count} employé(s)')
        else:
            department_name = department.name
            department.delete()
            messages.success(request, f'Département "{department_name}" supprimé avec succès!')
            
    except Department.DoesNotExist:
        messages.error(request, "Département non trouvé")
    
    return redirect('dashboard:departments_list')

# === INTERFACES IA ===

def response_time_analytics(request):
    """Vue dédiée aux analytics de temps de réponse"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Période d'analyse
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Statistiques détaillées des temps de réponse
    leave_response_stats = Leave.objects.filter(
        status__in=['approved', 'rejected']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_response=Avg('response_time'),
        min_response=Min('response_time'),
        max_response=Max('response_time'),
        total_count=Count('id')
    )
    
    ticket_response_stats = Ticket.objects.filter(
        statut__in=['Accepté', 'Refusé']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created_at'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_response=Avg('response_time'),
        min_response=Min('response_time'),
        max_response=Max('response_time'),
        total_count=Count('id')
    )
    
    # Distribution des temps de réponse par plages
    def get_response_time_distribution(model_class, status_field, status_values, date_field):
        distribution = []
        ranges = [
            (0, 1, 'Moins de 1 jour'),
            (1, 3, '1-3 jours'),
            (3, 7, '3-7 jours'),
            (7, 14, '1-2 semaines'),
            (14, 30, '2-4 semaines'),
            (30, float('inf'), 'Plus de 1 mois')
        ]
        
        for min_days, max_days, label in ranges:
            if max_days == float('inf'):
                count = model_class.objects.filter(
                    **{status_field + '__in': status_values}
                ).annotate(
                    response_time=ExpressionWrapper(
                        F('updated') - F(date_field),
                        output_field=DurationField()
                    )
                ).filter(response_time__gte=timedelta(days=min_days)).count()
            else:
                count = model_class.objects.filter(
                    **{status_field + '__in': status_values}
                ).annotate(
                    response_time=ExpressionWrapper(
                        F('updated') - F(date_field),
                        output_field=DurationField()
                    )
                ).filter(response_time__gte=timedelta(days=min_days), response_time__lt=timedelta(days=max_days)).count()
            
            distribution.append({
                'range': label,
                'count': count
            })
        
        return distribution
    
    leave_distribution = get_response_time_distribution(Leave, 'status', ['approved', 'rejected'], 'created')
    ticket_distribution = get_response_time_distribution(Ticket, 'statut', ['Accepté', 'Refusé'], 'created_at')
    
    # Top 10 des demandes les plus rapides et les plus lentes
    fastest_leaves = Leave.objects.filter(
        status__in=['approved', 'rejected']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created'),
            output_field=DurationField()
        )
    ).order_by('response_time')[:10]
    
    slowest_leaves = Leave.objects.filter(
        status__in=['approved', 'rejected']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created'),
            output_field=DurationField()
        )
    ).order_by('-response_time')[:10]
    
    fastest_tickets = Ticket.objects.filter(
        statut__in=['Accepté', 'Refusé']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created_at'),
            output_field=DurationField()
        )
    ).order_by('response_time')[:10]
    
    slowest_tickets = Ticket.objects.filter(
        statut__in=['Accepté', 'Refusé']
    ).annotate(
        response_time=ExpressionWrapper(
            F('updated') - F('created_at'),
            output_field=DurationField()
        )
    ).order_by('-response_time')[:10]
    
    context = {
        'leave_response_stats': leave_response_stats,
        'ticket_response_stats': ticket_response_stats,
        'leave_distribution': leave_distribution,
        'ticket_distribution': ticket_distribution,
        'fastest_leaves': fastest_leaves,
        'slowest_leaves': slowest_leaves,
        'fastest_tickets': fastest_tickets,
        'slowest_tickets': slowest_tickets,
    }
    
    return render(request, 'dashboard/response_time_analytics.html', context)





