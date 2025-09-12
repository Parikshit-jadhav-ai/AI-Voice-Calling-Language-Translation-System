from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('company', 'domain', 'industry', 'location', 'status', 'lead_score', 'created_at')
    list_filter = ('status', 'industry', 'source')
    search_fields = ('company', 'domain', 'industry', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'domain', 'website', 'employee_count', 'industry', 'location')
        }),
        ('Contact Details', {
            'fields': ('contact_email', 'email_found', 'email_validated', 'contact_name', 'contact_title')
        }),
        ('Enrichment Data', {
            'fields': ('insights', 'tags', 'personalized_message', 'lead_score', 'confidence')
        }),
        ('Technical Details', {
            'fields': ('hardware_mentions', 'tech_stack', 'website_signals', 'extracted_signals')
        }),
        ('Status & Metadata', {
            'fields': ('status', 'source', 'retry_count', 'error_log', 'metadata', 'created_at', 'updated_at')
        }),
    )
