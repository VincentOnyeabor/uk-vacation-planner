
```
# AI-Powered UK Vacation Planner 🇬🇧

An intelligent vacation planning app that uses OpenAI GPT-4 to create personalised UK travel itineraries.

## Features
- Multi-city UK trip planning
- AI-generated itineraries, dining recommendations, and packing lists
- Budget calculations based on travel style
- Rate limiting to control API costs
- Caching for improved performance
- Responsive UI with progress tracking

## Setup

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VincentOnyeabor/uk-vacation-planner.git
   cd uk-vacation-planner
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create `.streamlit/secrets.toml` file
   - Add your API key:
     ```toml
     OPENAI_API_KEY = "your-actual-api-key-here"
     ```

5. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Configuration
- Rate limits: 10 requests per 5 minutes (configurable in `utils/rate_limiter.py`)
- Caching: 1 hour TTL for AI responses
- Model: GPT-4 (configurable in `utils/llm.py`)

## Project Structure
```
uk-vacation-planner/
├── .streamlit/
│   ├── config.toml          # App configuration
│   └── secrets.toml         # API keys (local only)
├── utils/
│   ├── data.py             # UK cities data and calculations
│   ├── llm.py              # LLM interaction logic
│   ├── prompts.py          # Prompt templates
│   └── rate_limiter.py     # API rate limiting
├── streamlit_app.py        # Main application
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Features Overview

### 🏛️ Destination Research
- Information about 20 major UK cities
- Key highlights and attractions
- Local transport options

### 💰 Budget Calculator
- Estimates based on travel style (budget/mid-range/luxury)
- Group size discounts
- Cost breakdown by category

### 🤖 AI-Powered Features
- **Personalised Itineraries**: Day-by-day schedule with timings
- **Dining Recommendations**: Local restaurants and specialties
- **Packing Lists**: Season and activity-specific suggestions

### 🛡️ Safety Features
- Rate limiting prevents excessive API usage
- Secure API key handling via Streamlit secrets
- Input validation for all user entries

## Deployment

### Deploy to Streamlit Cloud
1. Push your code to GitHub (without secrets.toml)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your OpenAI API key in the Streamlit Cloud secrets management

## Security
- API keys are stored in `.streamlit/secrets.toml` (never commit this file)
- Rate limiting prevents excessive API usage
- All user inputs are validated

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
MIT

## Support
For issues or questions, please open an issue on GitHub.
```