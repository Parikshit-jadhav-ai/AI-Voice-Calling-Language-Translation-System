import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from openai import OpenAI

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'HardwareLeadBot/1.0 (admin@example.com)'
        }
        self.hardware_keywords = [
            'server', 'workstation', 'pc', 'hardware', 'gpu', 'pos', 'kiosk',
            'data center', 'infrastructure', 'IT', 'cloud', 'network',
            'computers', 'systems', 'equipment'
        ]
        
    def fetch(self, url: str) -> Optional[str]:
        """Fetch website content with retry logic"""
        try:
            response = requests.get(url, headers=self.headers, timeout=6)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return None
            
    def extract_content(self, html: str) -> Tuple[str, Optional[str], List[str], List[str]]:
        """Extract text content, email, hardware mentions, and tech stack"""
        if not html:
            return '', None, [], []
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
            
        # Extract main content
        text_parts = []
        
        # Meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            text_parts.append(meta_desc['content'])
            
        # Main content sections
        for tag in soup.find_all(['h1', 'h2', 'p']):
            text = tag.get_text().strip()
            if len(text) > 20:  # Skip very short sections
                text_parts.append(text)
                
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, html)
        email = emails[0] if emails else None
        
        # Find hardware mentions
        content_text = ' '.join(text_parts).lower()
        hardware_mentions = [
            keyword for keyword in self.hardware_keywords
            if keyword.lower() in content_text
        ]
        
        # Extract potential tech stack (simplified)
        tech_stack = []
        tech_indicators = ['powered by', 'built with', 'using', 'technologies']
        for indicator in tech_indicators:
            if indicator in content_text:
                # Extract 3 words after the indicator
                idx = content_text.find(indicator) + len(indicator)
                tech_stack.extend(content_text[idx:idx+50].split()[:3])
        
        return ' '.join(text_parts[:10]), email, hardware_mentions, tech_stack

def compute_lead_score(signals: Dict, employee_count: int, industry: str) -> int:
    """
    Compute lead score based on multiple factors
    Returns score between 0-100
    """
    score = 20  # Base score
    
    # Hardware signals
    if signals.get('mentions_hardware'):
        score += 30
    if signals.get('mentions_IT'):
        score += 20
    if signals.get('mentions_upgrade'):
        score += 10
        
    # Company size scoring
    if employee_count:
        if 50 <= employee_count <= 200:
            score += 10
        elif 201 <= employee_count <= 500:
            score += 5
            
    # Industry scoring
    target_industries = {'manufacturing', 'retail', 'logistics', 'education', 'healthcare'}
    if industry and industry.lower() in target_industries:
        score += 5
        
    # Technology signals
    if signals.get('has_tech_stack'):
        score += 5
        
    return min(score, 100)

class AIMessageGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def generate_message(self, company_data: Dict) -> Tuple[str, float, List[str]]:
        """
        Generate personalized message using AI
        Returns: (message, confidence_score, tags)
        """
        system_prompt = """You are OutreachAgent, an expert sales consultant for a premium hardware computer store. Your goal is to craft highly personalized B2B outreach messages.

        Guidelines:
        1. Analyze the company's current hardware needs based on their profile and website content
        2. Identify pain points or upgrade opportunities
        3. Reference specific details about their business
        4. Suggest relevant hardware solutions
        5. Keep the tone professional but conversational
        6. Include a clear value proposition
        7. End with a soft call to action

        Format your response as JSON with:
        {
            "personalized_message": "The outreach message",
            "confidence": 0.0 to 1.0,
            "tags": ["relevant", "tags"],
            "analysis": {
                "pain_points": ["list", "of", "identified", "issues"],
                "opportunities": ["potential", "solutions"],
                "hardware_needs": ["specific", "hardware", "requirements"]
            }
        }
        """
        
        user_message = f"""
        Company Analysis:
        - Name: {company_data['company']}
        - Industry: {company_data['industry']}
        - Scale: {company_data['employee_count']} employees
        - Location: {company_data['location']}
        
        Technical Context:
        - Hardware Mentions: {', '.join(company_data['hardware_mentions'])}
        
        Website Content Analysis:
        {company_data['website_text'][:500]}...
        
        Generate a personalized outreach message that:
        1. Shows understanding of their industry challenges
        2. References their specific hardware environment
        3. Proposes relevant solutions from our hardware store
        4. Includes a clear next step
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,  # Increased for more creative messages
                max_tokens=800
            )
            
            result = response.choices[0].message.content
            
            try:
                import json
                result_json = json.loads(result)
                
                # Store detailed analysis in metadata
                analysis = {
                    'pain_points': result_json.get('analysis', {}).get('pain_points', []),
                    'opportunities': result_json.get('analysis', {}).get('opportunities', []),
                    'hardware_needs': result_json.get('analysis', {}).get('hardware_needs', [])
                }
                
                return (
                    result_json['personalized_message'],
                    result_json['confidence'],
                    result_json['tags']
                )
            except Exception as e:
                # Fallback template if JSON parsing fails
                fallback_message = f"""
Hi {company_data['company']} team,

I noticed your company is doing impressive work in the {company_data['industry']} sector{
f' and your use of ' + ', '.join(company_data['hardware_mentions'][:2]) if company_data['hardware_mentions'] else ''}.

As a specialized hardware solutions provider, we've helped similar {company_data['industry']} companies optimize their IT infrastructure with premium hardware solutions.

Would you be open to a brief call next week to discuss how we could support your hardware needs?

Best regards,
Your Hardware Solutions Team
                """.strip()
                
                return (
                    fallback_message,
                    0.5,
                    [company_data['industry'], 'fallback_template']
                )
        except Exception as e:
            # Final fallback for complete failure
            return (
                f"Hi {company_data['company']},\n\nI noticed your company operates in the {company_data['industry']} sector. I'd love to discuss how our hardware solutions could benefit your business. Could we schedule a brief call next week?\n\nBest regards",
                0.4,
                [company_data['industry']]
            )
