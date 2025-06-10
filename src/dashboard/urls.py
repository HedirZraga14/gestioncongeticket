from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('welcome/', views.dashboard, name='dashboard'),
    path('acceuil/', views.acceuil, name='acceuil'),
    path('calendrier/', views.calendrier, name='calendrier'),
    path('help/', views.help, name='help'),
    path('add_note/', views.add_note, name='add_note'),
    
    # Employee
    path('employees/', views.employees, name='employees'),
    path('employees/all/', views.dashboard_employees, name='employees'),
    path('beneficiaires/', views.beneficiaires, name='beneficiaires'),
    path('beneficiaire/create/', views.dashboard_beneficiaire_create, name='beneficiairecreate'),
    path('employee/create/', views.dashboard_employees_create, name='employeecreate'),
    path('employee/profile/<int:user_id>/', views.dashboard_employee_info, name='employeeinfo'),
    path('employee/profile/edit/<int:id>/', views.employee_edit_data, name='edit'),
    path('employee/profile/edit/<int:id>/form/', views.employee_edit, name='editform'),
    path('user/profile/<int:user_id>/', views.dashboard_employee_info, name='user_profile'),

    # Leave
    path('leave/apply/', views.leave_creation, name='createleave'),
    path('leaves/pending/all/', views.leaves_list, name='leaveslist'),
    path('leaves/all/', views.leaves, name='leaves'),
    path('leaves/approved/all/', views.leaves_approved_list, name='approvedleaveslist'),
    path('leaves/cancel/all/', views.cancel_leaves_list, name='canceleaveslist'),
    path('leaves/all/view/<int:id>/', views.leaves_view, name='userleaveview'),
    path('leaves/view/table/', views.view_my_leave_table, name='staffleavetable'),
    path('leave/approve/<int:id>/', views.approve_leave, name='userleaveapprove'),
    path('leave/unapprove/<int:id>/', views.unapprove_leave, name='userleaveunapprove'),
    path('leave/cancel/<int:id>/', views.cancel_leave, name='userleasvecancel'),
    path('leave/uncancel/<int:id>/', views.uncancel_leave, name='userleaveuncancel'),
    path('leaves/rejected/all/', views.leave_rejected_list, name='leavesrejected'),
    path('leave/reject/<int:id>/', views.reject_leave, name='reject'),
    path('leave/unreject/<int:id>/', views.unreject_leave, name='unreject'),

    # Tickets
    path('ticket/create/', views.ticket_creation, name='ticketcreate'),
    path('tickets/pending/all/', views.tickets_list, name='ticketslist'),
    path('tickets/all/', views.tickets, name='tickets'),
    path('tickets/approved/all/', views.tickets_approved_list, name='approvedticketslist'),
    path('tickets/cancel/all/', views.cancel_tickets_list, name='canceleticketslist'),
    path('tickets/all/view/<int:id>/', views.tickets_view, name='userticketview'),
    path('tickets/view/table/', views.view_my_ticket_table, name='stafftickettable'),
    path('ticket/approve/<int:id>/', views.approve_ticket, name='userticketapprove'),
    path('ticket/unapprove/<int:id>/', views.unapprove_ticket, name='userticketunapprove'),
    path('ticket/cancel/<int:id>/', views.cancel_ticket, name='userticketcancel'),
    path('ticket/uncancel/<int:id>/', views.uncancel_ticket, name='userticketuncancel'),
    path('tickets/rejected/all/', views.ticket_rejected_list, name='ticketsrejected'),
    path('ticket/reject/<int:id>/', views.reject_ticket, name='rejectticket'),
    path('ticket/unreject/<int:id>/', views.unreject_ticket, name='unrejectticket'),

    #---work-on-edit-view------#
    # path('bank/edit/<int:id>/',views.employee_bank_account_update,name='accountedit'),
    path('leave/apply/',views.leave_creation,name='createleave'),
    path('leaves/pending/all/',views.leaves_list,name='leaveslist'),
    path('leaves/all/',views.leaves,name='leaves'),
    path('leaves/approved/all/',views.leaves_approved_list,name='approvedleaveslist'),
    path('leaves/cancel/all/',views.cancel_leaves_list,name='canceleaveslist'),
    path('leaves/all/view/<int:id>/',views.leaves_view,name='userleaveview'),
    path('leaves/view/table/',views.view_my_leave_table,name='staffleavetable'),
    path('leave/approve/<int:id>/',views.approve_leave,name='userleaveapprove'),
    path('leave/unapprove/<int:id>/',views.unapprove_leave,name='userleaveunapprove'),
    path('leave/cancel/<int:id>/',views.cancel_leave,name='userleasvecancel'),
    path('leave/uncancel/<int:id>/',views.uncancel_leave,name='userleaveuncancel'),
    path('leaves/rejected/all/',views.leave_rejected_list,name='leavesrejected'),
    path('leave/reject/<int:id>/',views.reject_leave,name='reject'),
    path('leave/unreject/<int:id>/',views.unreject_leave,name='unreject'),
    path('dashboard/print_leave/<int:leave_id>/', views.print_leave, name='print_leave'),

    # BIRTHDAY ROUTE
    # path('birthdays/all/',views.birthday_this_month,name='birthdays'),
    path('ticket/apply/',views.ticket_creation,name='createticket'),
    path('tickets/pending/all/',views.tickets_list,name='ticketslist'),
    path('tickets/all/',views.tickets,name='tickets'),
    path('tickets/approved/all/',views.tickets_approved_list,name='approvedticketslist'),
    path('tickets/all/view/<int:id>/',views.tickets_view,name='user_ticket_view'),
    path('tickets/view/table/',views.view_my_ticket_table,name='stafftickettable'),
    path('ticket/approve/<int:id>/',views.approve_ticket,name='userticketapprove'),
    path('ticket/unapprove/<int:id>/',views.unapprove_ticket,name='userticketunapprove'),
    path('tickets/rejected/all/',views.ticket_rejected_list,name='ticketsrejected'),
    path('ticket/reject/<int:id>/', views.reject_ticket, name='reject_ticket'),
    path('ticket/unreject/<int:id>/',views.unreject_ticket,name='unreject_ticket'),
    path('dashboard/print_ticket/<int:ticket_id>/', views.print_ticket, name='print_ticket'),
    
]
