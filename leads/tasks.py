from celery import shared_task
from .models import Lead
from .lead_enrichment import WebScraper, compute_lead_score, AIMessageGenerator
import time

@shared_task(bind=True, max_retries=3)
def enrich_lead(self, lead_id):
    """
    Enrich a lead with website content and AI-generated message
    Implements retry logic and error handling
    """
    lead = Lead.objects.get(id=lead_id)
    scraper = WebScraper()
    message_generator = AIMessageGenerator()
    
    try:
        # Step 1: Scrape website
        html = scraper.fetch(lead.website)
        if not html:
            raise Exception("Failed to fetch website content")
        
        # Step 2: Extract content and signals
        website_text, contact_email, hardware_mentions, tech_stack = scraper.extract_content(html)
        
        # Step 3: Prepare data for AI
        company_data = {
            "company": lead.company,
            "domain": lead.domain,
            "website": lead.website,
            "employee_count": lead.employee_count,
            "industry": lead.industry,
            "location": lead.location,
            "website_text": website_text,
            "hardware_mentions": hardware_mentions
        }
        
        # Step 4: Generate personalized message
        message, confidence, tags = message_generator.generate_message(company_data)
        
        # Step 5: Extract signals and compute score
        signals = {
            "mentions_hardware": bool(hardware_mentions),
            "mentions_IT": any(term in website_text.lower() for term in ['it ', 'infrastructure', 'technology']),
            "mentions_upgrade": any(term in website_text.lower() for term in ['upgrade', 'modernize', 'improve']),
            "has_tech_stack": bool(tech_stack)
        }
        
        lead_score = compute_lead_score(signals, lead.employee_count, lead.industry)
        
        # Step 6: Update lead with enriched data
        lead.insights = website_text[:250] if website_text else None
        lead.tags = tags
        lead.contact_email = contact_email
        lead.email_found = bool(contact_email)
        lead.personalized_message = message
        lead.lead_score = lead_score
        lead.confidence = confidence
        lead.extracted_signals = signals
        lead.hardware_mentions = hardware_mentions
        lead.tech_stack = tech_stack
        lead.status = "enriched"
        lead.metadata.update({
            "enrichment_timestamp": time.time(),
            "scrape_success": True
        })
        lead.save()
        
    except Exception as exc:
        # Log error and update lead status
        lead.status = "failed"
        lead.error_log.append({
            "timestamp": time.time(),
            "error": str(exc),
            "retry_count": self.request.retries
        })
        lead.save()
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@shared_task
def validate_emails():
    """
    Batch task to validate found email addresses
    """
    leads = Lead.objects.filter(
        email_found=True,
        email_validated=False
    )[:50]  # Process in batches
    
    for lead in leads:
        try:
            # Here you would integrate with email validation service
            # For demo, we'll mark all as valid
            lead.email_validated = True
            lead.save()
        except Exception as e:
            lead.error_log.append({
                "timestamp": time.time(),
                "error": f"Email validation failed: {str(e)}"
            })
            lead.save()
