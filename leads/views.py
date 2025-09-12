import csv
import json
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Lead
from .serializers import LeadSerializer
from .tasks import enrich_lead

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='search', url_name='lead-search')
    def search(self, request):
        """
        Search for leads based on criteria:
        {
            "industry": "software",
            "employee_min": 50,
            "employee_max": 200,
            "location": "India",
            "keywords": ["hardware", "infrastructure"],
            "run_sync": false
        }
        """
        industry = request.data.get('industry')
        employee_min = request.data.get('employee_min', 0)
        employee_max = request.data.get('employee_max', 1000)
        location = request.data.get('location')
        keywords = request.data.get('keywords', [])
        run_sync = request.data.get('run_sync', False)
        
        # Here you would integrate with Apollo API
        # For demo, we'll create sample leads
        sample_companies = [
            {
                "company": "TechCorp Solutions",
                "domain": "techcorp.com",
                "website": "https://techcorp.com",
                "employee_count": 150,
                "industry": "software",
                "location": "Mumbai, India"
            },
            {
                "company": "ManufactureX",
                "domain": "manufacturex.com",
                "website": "https://manufacturex.com",
                "employee_count": 80,
                "industry": "manufacturing",
                "location": "Pune, India"
            }
        ]
        
        created_leads = []
        for company in sample_companies:
            lead, created = Lead.objects.get_or_create(
                domain=company['domain'],
                source='apollo',
                defaults={
                    'company': company['company'],
                    'website': company['website'],
                    'employee_count': company['employee_count'],
                    'industry': company['industry'],
                    'location': company['location'],
                    'status': 'pending'
                }
            )
            
            if created or lead.status == 'failed':
                # Enqueue enrichment task
                if run_sync:
                    enrich_lead(lead.id)
                else:
                    enrich_lead.delay(lead.id)
            
            created_leads.append(lead.id)
        
        return Response({
            "message": f"Created/Updated {len(created_leads)} leads",
            "lead_ids": created_leads,
            "status": "completed" if run_sync else "pending"
        })
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export leads to CSV with detailed information"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Company', 'Domain', 'Industry', 'Employee Count',
            'Location', 'Lead Score', 'Contact Email',
            'Email Validated', 'Insights', 'Personalized Message',
            'Hardware Mentions', 'Status'
        ])
        
        for lead in Lead.objects.all():
            writer.writerow([
                lead.company,
                lead.domain,
                lead.industry,
                lead.employee_count,
                lead.location,
                lead.lead_score,
                lead.contact_email,
                lead.email_validated,
                lead.insights,
                lead.personalized_message,
                ', '.join(lead.hardware_mentions),
                lead.status
            ])
            
        return response
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get enrichment pipeline statistics"""
        total_leads = Lead.objects.count()
        enriched_leads = Lead.objects.filter(status='enriched').count()
        failed_leads = Lead.objects.filter(status='failed').count()
        high_score_leads = Lead.objects.filter(lead_score__gte=80).count()
        
        return Response({
            "total_leads": total_leads,
            "enriched_leads": enriched_leads,
            "failed_leads": failed_leads,
            "high_score_leads": high_score_leads,
            "success_rate": f"{(enriched_leads/total_leads)*100:.1f}%" if total_leads > 0 else "0%"
        })
    
    @action(detail=False, methods=['get'])
    def top_leads(self, request):
        """Get top scored leads"""
        top_leads = Lead.objects.filter(
            status='enriched',
            lead_score__isnull=False
        ).order_by('-lead_score')[:10]
        
        serializer = self.get_serializer(top_leads, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry_enrichment(self, request, pk=None):
        """Retry enrichment for a failed lead"""
        lead = self.get_object()
        if lead.status == 'failed':
            lead.status = 'pending'
            lead.retry_count += 1
            lead.save()
            enrich_lead.delay(lead.id)
            return Response({"status": "Enrichment queued"})
        return Response(
            {"error": "Can only retry failed leads"},
            status=status.HTTP_400_BAD_REQUEST
        )
