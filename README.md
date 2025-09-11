# Lead Generation & Enrichment System

A sophisticated B2B lead generation and enrichment system built with Django REST Framework, designed for hardware computer store owners to find and engage potential business clients.

## 🚀 Features

### Lead Generation & Search
- Search companies by industry, size, and location
- Configurable search criteria and filters
- Mock data provider (easily replaceable with Apollo.io integration)

### Automated Enrichment Pipeline
- Website scraping for company insights
- Hardware mention detection
- Technology stack identification
- Contact information extraction
- Lead scoring algorithm
- AI-powered personalized message generation

### AI-Powered Personalization
- GPT-4 integration for message generation
- Context-aware outreach messages
- Industry-specific customization
- Automatic pain point identification
- Smart solution recommendations

### Analytics & Reporting
- Lead enrichment statistics
- Success rate tracking
- Top leads identification
- CSV export functionality

## 🛠️ Technology Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL
- **Task Queue**: Celery with RabbitMQ
- **AI Integration**: OpenAI GPT-4
- **Web Scraping**: BeautifulSoup4
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: Built-in DRF documentation

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL
- RabbitMQ
- OpenAI API key

## 🔧 Installation

1. Clone the repository
```bash
git clone <repository-url>
cd outreach_agent
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Start the development server
```bash
python manage.py runserver
```

8. Start Celery worker
```bash
celery -A outreach_agent worker --loglevel=info
```

## 🔑 Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=leadsdb
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your-openai-key-here
APOLLO_API_KEY=optional-apollo-key
HUNTER_API_KEY=optional-hunter-key
```

## 🚀 API Endpoints

### Authentication
- POST `/api/auth/token/` - Get JWT token
- POST `/api/auth/token/refresh/` - Refresh JWT token

### Lead Management
- POST `/api/leads/search/` - Search for leads
- GET `/api/leads/` - List all leads
- GET `/api/leads/{id}/` - Get lead details
- GET `/api/leads/stats/` - Get enrichment statistics
- GET `/api/leads/top_leads/` - Get highest scoring leads
- GET `/api/leads/export_csv/` - Export leads to CSV
- POST `/api/leads/{id}/retry_enrichment/` - Retry failed enrichment

## 📊 Lead Search Example

```json
POST /api/leads/search/
{
    "industry": "software",
    "employee_min": 50,
    "employee_max": 200,
    "location": "India",
    "keywords": ["hardware", "infrastructure"],
    "run_sync": false
}
```

## 💡 Lead Enrichment Process

1. **Initial Data Collection**
   - Basic company information
   - Industry and size details
   - Website and contact information

2. **Website Analysis**
   - Content scraping
   - Hardware mention detection
   - Technology stack identification
   - Contact information extraction

3. **AI Processing**
   - Context analysis
   - Pain point identification
   - Solution matching
   - Message generation

4. **Scoring & Prioritization**
   - Multi-factor lead scoring
   - Priority assignment
   - Opportunity assessment

## 🤖 AI Message Generation

The system uses GPT-4 to generate personalized outreach messages considering:
- Company profile
- Industry context
- Detected hardware usage
- Technology stack
- Business scale
- Location factors

## 📈 Lead Scoring Factors

- Hardware mentions
- Company size
- Industry relevance
- Technology signals
- Upgrade indicators
- Infrastructure mentions

## 🔒 Security Features

- JWT Authentication
- Permission-based access
- Secure password handling
- API rate limiting
- CORS configuration

## 🛠️ Development

```bash
# Run tests
python manage.py test

# Generate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Start Celery worker
celery -A outreach_agent worker --loglevel=info
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🙋‍♂️ Support

For support, email support@example.com or create an issue in the repository.
# outreach_agent
