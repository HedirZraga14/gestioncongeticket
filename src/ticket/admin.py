from django.contrib import admin
from .models import Ticket
from .models import Beneficiaire


# Register your models here.


admin.site.register(Ticket)
admin.site.register(Beneficiaire)


