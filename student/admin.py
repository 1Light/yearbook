# Register your models here.
from django.contrib import admin
from .models import RSVPToken

@admin.register(RSVPToken)
class RSVPTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'responded', 'response')
    search_fields = ('user__email',)
    list_filter = ('responded', 'response')
