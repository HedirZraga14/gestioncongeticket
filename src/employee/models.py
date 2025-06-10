import datetime
from employee.utility import code_format
from django.db import models
from employee.managers import EmployeeManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext as _

from django.contrib.auth.models import User
from leave.models import Leave






class Department(models.Model):


    name = models.CharField(max_length=125)
    service = models.CharField(max_length=125,null=True,blank=True)

    created = models.DateTimeField(verbose_name=_('Created'),auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('Updated'),auto_now=True)


    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['name','created']
    
    def __str__(self):
        return self.name



class Employee(models.Model):

    MALE = 'Homme'
    FEMALE = 'Femme'
    OTHER = 'Autre'
    

    GENDER = (
    (MALE,'Homme'),
    (FEMALE,'Femme'),
    (OTHER,'Autre'),
    
    )




    PS = 'Personnel au sol'
    PNT = 'Personnel navigant technique'
    PNC = 'personnel navigant commerciale'
    

    EMPLOYEETYPE = (
    (PS,'Personnel au sol'),
    (PNT,'Personnel navigant technique'),
    (PNC,'personnel navigant commerciale'),
    
    )


    
    
    # PERSONAL DATA
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    employeeid = models.CharField(verbose_name=_('Employee ID'),max_length=10,null=True,blank=True)
    image = models.FileField(_('Image De Profile '),upload_to='profiles',default='default.png',blank=True,null=True,help_text='upload image size less than 2.0MB')#work on path username-date/image
    
    firstname = models.CharField(verbose_name=_('prénom'),max_length=125,null=False,blank=False)
    lastname = models.CharField(verbose_name=_('Nom'),max_length=125,null=False,blank=False)
    email = models.EmailField(verbose_name=_('Email'),max_length=125,null=True,blank=True)
    birthday = models.DateField(verbose_name=_('Date de naissance'),blank=False,null=False)
    department =  models.ForeignKey(Department,verbose_name =_('Départment'),on_delete=models.SET_NULL,null=True,default=None)
    employeetype = models.CharField(verbose_name=_('Type '),max_length=100,default=PS,choices=EMPLOYEETYPE,blank=False,null=True)
    
   

    # app related
    is_blocked = models.BooleanField(_('Is Blocked'),help_text='button to toggle employee block and unblock',default=False)
    is_deleted = models.BooleanField(_('Is Deleted'),help_text='button to toggle employee deleted and undelete',default=False)
 
    created = models.DateTimeField(verbose_name=_('Created'),auto_now_add=True,null=True)
    updated = models.DateTimeField(verbose_name=_('Updated'),auto_now=True,null=True)


    #PLUG MANAGERS
    objects = EmployeeManager()

    
    
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['-created']



    def __str__(self):
        return self.get_full_name

    

    @property
    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"


    @property
    def get_age(self):
        current_year = datetime.date.today().year
        dateofbirth_year = self.birthday.year
        if dateofbirth_year:
            return current_year - dateofbirth_year
        return



    @property
    def can_apply_leave(self):
        pass





   

    





    def save(self,*args,**kwargs):
        '''
        overriding the save method - for every instance that calls the save method 
        perform this action on its employee_id
        added : March, 03 2019 - 11:08 PM

        '''
        get_id = self.employeeid #grab employee_id number from submitted form field
        data = code_format(get_id)
        self.employeeid = data #pass the new code to the employee_id as its orifinal or actual code
        super().save(*args,**kwargs) # call the parent save method
        # print(self.employeeid)









