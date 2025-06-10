from django.db import models
from .manager import LeaveManager
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from datetime import timedelta



# Create your models here.
Conge = 'congé'
accident = 'accident de travail'
maladie = 'maladie'
mission = 'mission'
absence = 'absence'

LEAVE_TYPE = (
    (Conge, 'congé annuel'),
    (accident,'accident de travail'),
    (maladie, 'maladie'),
    (mission, 'mission'),
    (absence, 'absence'),
)




class Leave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    startdate = models.DateField(verbose_name=_('Date début'), help_text='Votre congé du ..', null=True, blank=False)
    enddate = models.DateField(verbose_name=_(' Date fin '), help_text='et fini à...', null=True, blank=False)
    leavetype = models.CharField(verbose_name=_(' type congé '), choices=LEAVE_TYPE, max_length=25, default='Congé annuel', null=True, blank=False)
    status = models.CharField(max_length=12, default='pending')  # pending, approved, rejected, cancelled
    is_approved = models.BooleanField(default=False)  # hide
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = LeaveManager()

    class Meta:
        verbose_name = _('Leave')
        verbose_name_plural = _('Leaves')
        ordering = ['-created']  # recent objects

    def droit(self):
        employee = self.user.employee_set.first()
        if employee and employee.employeetype == 'PS':
            defaultdays = 26
        else:
           defaultdays = 40
        return defaultdays

   

    def __str__(self):
        return '{0} - {1}'.format(self.leavetype, self.user)

    @property
    def pretty_leave(self):
        '''
        I don't like the __str__ of leave object - this is a pretty one :-)
        '''
        leave = self.leavetype
        user = self.user
        employee = user.employee_set.first().get_full_name()
        return ('{0} - {1}'.format(employee, leave))

    @property
    def leave_days(self):
        days_count = ''
        startdate = self.startdate
        enddate = self.enddate
        if startdate > enddate:
            return
        dates = (enddate - startdate)
        return dates.days

    @property
    def leave_approved(self):
        return self.is_approved == True

    @property
    def approve_leave(self):
        if not self.is_approved:
            self.is_approved = True
            self.status = 'approved'
            self.save()

    @property
    def unapprove_leave(self):
        if self.is_approved:
            self.is_approved = False
            self.status = 'pending'
            self.save()

    @property
    def leaves_cancel(self):
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.status = 'cancelled'
            self.save()

    @property
    def reject_leave(self):
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.status = 'rejected'
            self.save()

    @property
    def is_rejected(self):
        return self.status == 'rejected'
