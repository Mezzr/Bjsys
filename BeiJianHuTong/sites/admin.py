from django.contrib import admin
from .models import Site

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'address', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code', 'address')
    ordering = ('code',)

