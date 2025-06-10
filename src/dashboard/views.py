from django.core.paginator import  Paginator
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q, Count
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
     return render(request, 'dashboard/acceuil.html')
     
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
        'leave_labels': leave_labels,
        'leave_counts': leave_counts,
        'destination_labels': destination_labels,
        'destination_counts': destination_counts,
        'total_admin_notifications': total_admin_notifications if request.user.is_superuser else 0,
        'total_staff_notifications': total_staff_notifications if request.user.is_staff else 0,
        'total_user_notifications': total_user_notifications if not (request.user.is_superuser or request.user.is_staff) else 0,
        'total_notifications': total_notifications
    }

    if request.user.is_superuser and request.user.is_staff:
        return render(request, 'dashboard/dashboard_index.html', dataset)
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
    return render(request, 'dashboard/leave_detail_view.html', {'leave': leave, 'employee': employee, 'title': '{0}-{1} leave'.format(leave.user.username, leave.status)})

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
        dataset['leave_list'] = leaves
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

            messages.success(request, 'Demande de billet envoyée, veuillez attendre la réponse des gestionnaires de OEBTR de TUNISAIR Express', extra_tags='alert alert-success alert-dismissible show')
            return redirect('dashboard:createticket')

    form = ticketForm()
    dataset = {'form': form, 'title': 'demander une billet'}

    return render(request, 'dashboard/create_ticket.html', dataset)



def tickets_list(request):
	if not (request.user.is_staff and request.user.is_superuser):
		return redirect('/')
	tickets = Ticket.objects.all_pending_tickets()
	return render(request,'dashboard/tickets_recent.html',{'ticket_list':tickets,'title':' liste de billets -En attente'})

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
	return render(request,'dashboard/ticket_detail_view.html',{'ticket':ticket,'employee':employee,'title':'{0}-{1} billet'.format(ticket.user.username,ticket.statut)})


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
        dataset['ticket_list'] = tickets
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
