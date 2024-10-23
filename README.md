# Data Scrapping System

Automated system for collecting data from multiple sources (Google Places, Facebook, YouTube, Twitter, and News API) for company analysis.

## Project Structure

```
.
├── collectors/
│   ├── __init__.py
│   ├── places_collector.py
│   ├── facebook_collector.py
│   ├── youtube_collector.py
│   ├── twitter_collector.py
│   └── news_collector.py
├── core/
│   ├── __init__.py
│   ├── api.py
│   └── orchestrator.py
├── config/
│   └── settings.py
├── data/
│   ├── places/
│   ├── facebook/
│   ├── youtube/
│   ├── twitter/
│   └── news/
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── start.sh
└── README.md
```

## Requirements

- Python 3.10+
- Docker and Docker Compose
- Redis

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/data_scrapping.git
cd data_scrapping
```

2. Copy the environment variables example file:
```bash
cp .env.example .env
```

3. Configure your API keys in the .env file:
```
api_key_google_3=your_google_places_api_key
YOUTUBE_API_KEY=your_youtube_api_key
bearer_token=your_twitter_bearer_token
NEWS_API_KEY=your_news_api_key
OUTSCRAPPER=your_outscrapper_api_key
```

## Installation

### Using Docker (Recommended)

```bash
docker-compose build
docker-compose up -d
```

### Local Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Redis locally:
```bash
redis-server
```

4. Start the application:
```bash
./start.sh
```

## Usage

### API Endpoints

The API is available at `http://localhost:8000` with the following endpoints:

- `POST /companies/`: Add new company
- `GET /companies/`: List all companies
- `GET /companies/{name}`: Get company details
- `PUT /companies/{name}`: Update company
- `DELETE /companies/{name}`: Delete company
- `GET /collectors/status`: View collectors status
- `POST /collectors/{name}/force-run`: Force collector execution

### API Documentation

Interactive documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Usage Example

To add a new company:

```bash
curl -X POST "http://localhost:8000/companies/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Tesla", "country": "United States", "active": true}'
```

Or using Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/companies/",
    json={
        "name": "Tesla",
        "country": "United States",
        "active": true
    }
)
print(response.json())
```

## Scheduling

Collectors run automatically according to the following intervals:

| Collector | Interval (hours) |
|-----------|------------------|
| Places    | 24              |
| Facebook  | 12              |
| YouTube   | 48              |
| Twitter   | 0.5             |
| News      | 6               |

Intervals can be modified in `config/settings.py`.

## Data Structure

Collected data is stored in CSV files in their respective directories:

- `data/places/`: Google Places location data
- `data/facebook/`: Facebook reviews
- `data/youtube/`: Related videos
- `data/twitter/`: Tweets
- `data/news/`: News articles

## Monitoring

- Logs are stored in `app.log`
- Collectors status can be checked at `/collectors/status`
- Errors and warnings are automatically logged

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

