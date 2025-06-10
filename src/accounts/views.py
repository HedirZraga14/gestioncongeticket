from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from employee.models import *
from .forms import UserLogin,UserAddForm



def changepassword(request):
	if not request.user.is_authenticated:
		return redirect('/')
	'''
	Please work on me -> success & error messages & style templates
	'''
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save(commit=True)
			update_session_auth_hash(request,user)

			messages.success(request,'mot de passe changé avec succé',extra_tags = 'alert alert-success alert-dismissible show' )
			return redirect('accounts:changepassword')
		else:
			messages.error(request,'erreur, mot de passe invalide',extra_tags = 'alert alert-warning alert-dismissible show' )
			return redirect('accounts:changepassword')
			
	form = PasswordChangeForm(request.user)
	return render(request,'accounts/change_password_form.html',{'form':form})




def register_user_view(request):
	# WORK ON (MESSAGES AND UI) & extend with email field
	if request.method == 'POST':
		form = UserAddForm(data = request.POST)
		if form.is_valid():
			instance = form.save(commit = False)
			instance.save()
			username = form.cleaned_data.get("username")

			messages.success(request,'compte crée pour {0} !!!'.format(username),extra_tags = 'alert alert-success alert-dismissible show' )
			return redirect('accounts:register')
		else:
			messages.error(request,'Username ou password est invalide',extra_tags = 'alert alert-warning alert-dismissible show')
			return redirect('accounts:register')


	form = UserAddForm()
	dataset = dict()
	dataset['form'] = form
	dataset['title'] = 'register users'
	return render(request,'accounts/register.html',dataset)



def login_view(request):
    '''
    work on me - needs messages and redirects

    '''
    if request.method == 'POST':
        form = UserLogin(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user and user.is_active:
                login(request, user)
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'compte est invalide', extra_tags='alert alert-error alert-dismissible show')
                return redirect('accounts:login')

    dataset = dict()
    form = UserLogin()

    dataset['form'] = form
    return render(request, 'accounts/login.html', dataset)

def user_profile_view(request):
    if request.user.is_authenticated:
        employee = Employee.objects.filter(user=request.user).first()
        if employee is not None:
            return render(request, 'accounts/user_profile_page.html', {'employee': employee})
        else:
            return HttpResponse("Aucun profil d'employé trouvé pour cet utilisateur.")
    else:
        return HttpResponse("Désolé, vous n'êtes pas authentifié pour accéder à cette page.")


def logout_view(request):
	logout(request)
	return redirect('accounts:login')


def users_list(request):
    users = User.objects.all()
    return render(request, 'accounts/users_table.html', {'users': users, 'title': 'Users List'})

def users_unblock(request,id):
	user = get_object_or_404(User,id = id)
	emp = Employee.objects.filter(user = user).first()
	emp.is_blocked = False
	emp.save()
	user.is_active = True
	user.save()

	return redirect('accounts:users')


def users_block(request,id):
	user = get_object_or_404(User,id = id)
	emp = Employee.objects.filter(user = user).first()
	emp.is_blocked = True
	emp.save()
	
	user.is_active = False
	user.save()
	
	return redirect('accounts:users')



def users_blocked_list(request):
	blocked_employees = Employee.objects.all_blocked_employees()
	return render(request,'accounts/all_deleted_users.html',{'employees':blocked_employees,'title':'blocked users list'})