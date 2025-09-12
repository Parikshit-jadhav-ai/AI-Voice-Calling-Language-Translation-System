from django.db import models

class Lead(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('enriched', 'Enriched'),
        ('failed', 'Failed'),
    ]

    # Basic company information
    company = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, db_index=True)
    website = models.URLField(blank=True, null=True)
    employee_count = models.IntegerField(null=True, blank=True)
    industry = models.CharField(max_length=120, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    
    # Enrichment data
    insights = models.TextField(null=True, blank=True)
    tags = models.JSONField(default=list)
    
    # Contact information
    contact_email = models.EmailField(null=True, blank=True)
    email_found = models.BooleanField(default=False)
    email_validated = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    contact_title = models.CharField(max_length=255, null=True, blank=True)
    
    # Outreach content
    personalized_message = models.TextField(null=True, blank=True)
    
    # Scoring and signals
    lead_score = models.IntegerField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    extracted_signals = models.JSONField(null=True, blank=True)
    website_signals = models.JSONField(default=dict, help_text='Signals extracted from website content')
    hardware_mentions = models.JSONField(default=list, help_text='List of hardware-related terms found')
    tech_stack = models.JSONField(default=list, help_text='Detected technology stack')
    
    # Meta information
    source = models.CharField(max_length=50, default='mock')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    metadata = models.JSONField(default=dict, blank=True)
    error_log = models.JSONField(default=list, help_text='List of errors during enrichment')
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['domain', 'source']),
            models.Index(fields=['lead_score']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['domain', 'source'], name='unique_domain_source')
        ]
        
    def __str__(self):
        return f"{self.company} ({self.domain})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['domain', 'source'], name='unique_domain_source')
        ]

    def __str__(self):
        return f"{self.company} ({self.domain})"
