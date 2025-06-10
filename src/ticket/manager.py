from django.db import models
import datetime

class ticketManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def all_pending_tickets(self):
        return super().get_queryset().filter(statut='attente').order_by('-date')

    def all_approved_tickets(self):
        return super().get_queryset().filter(statut='accepte').order_by('-date')

    def all_rejected_tickets(self):
        return super().get_queryset().filter(statut='refuse').order_by('-date')

    def current_year_tickets(self):
        return super().get_queryset().filter(date__year=datetime.date.today().year)

