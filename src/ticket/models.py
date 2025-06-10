from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from employee.models import Employee
from ticket.manager import ticketManager
from datetime import datetime



class Beneficiaire(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Utilisateur'))
    nom_et_prenom = models.CharField(max_length=255, verbose_name=_('Nom et prénom'))
    date_naissance = models.DateField(verbose_name=_('Date de naissance'))


    class Meta:
        verbose_name = _('Bénéficiaire')
    def __str__(self):
        return self.nom_et_prenom

# Create your models here.
accepte = 'Accepté'
refuse = 'Refusé'
attente = 'En attente'

STATUT_CHOICES = (
    (accepte, 'Accepté'),
    (refuse, 'Refusé'),
    (attente, 'En attente'),
)

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    date = models.DateField(verbose_name=_('Date'), default=datetime.today)
    destination = models.CharField(max_length=255, verbose_name=_('Destination'))
    compagnie = models.CharField(max_length=20, verbose_name=_('Compagnie'), choices=[
        ('Tunisair', _('Tunisair')),
        ('Tunisair Express', _('Tunisair Express')),], default='Tunisair')
    
    vous = models.BooleanField(default=False, verbose_name=_('Est-ce que le bénéficiaire est vous-même ?'))
    beneficiaires = models.ManyToManyField(Beneficiaire, verbose_name=_('Beneficiaires'), default='sans bénéficiaire', blank=True)
    retraité = models.BooleanField(default=False, verbose_name=_('Est-ce que le demandeur est retraité ?'))
    statut = models.CharField(choices=STATUT_CHOICES, max_length=20, default=attente, verbose_name=_('En attente'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Est approuvé'))  
    created_at = models.DateTimeField(auto_now_add=True)
    

     
    objects = ticketManager()

    
    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        ordering = ['date'] # recent objects

   

    def __str__(self):
        return f"Demande de billet - {self.date}"

    @property
    def billets_utilisateurs(self):
        return self.beneficiaire_set.all()


    @property
    def ticket_approved(self):
        return self.is_approved == True
    
    @property
    def approve_ticket(self):
        if not self.is_approved:
            self.is_approved = True
            self.statut = 'accepte'
            self.save()


    @property
    def unapprove_ticket(self):
        if self.is_approved:
            self.is_approved = False
            self.statut = 'attente'
            self.save()

    @property
    def reject_ticket(self):
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.statut = 'refuse'
            self.save()

    @property
    def is_rejected(self):
        return self.statut == 'refuse'

    @property
    def is_retired_yes(self):
        return self.is_retired == True

    @property
    def is_retired_no(self):
        return self.is_retired == False

    @property
    def approve_retired(self):
        if not self.is_retired:
            self.is_retired = True
            self.save()

    @property
    def unapprove_retired(self):
        if self.is_retired:
            self.is_retired = False
            self.save()    
  