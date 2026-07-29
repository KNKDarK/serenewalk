# AI Medical Advisor

A self-improving, multilingual medical advice system with accessibility features. This application provides symptom triage, medical information retrieval, and AI-powered health guidance with support for multiple languages.

## Features

- **Symptom Triage**: Classifies symptoms into 4 severity levels (LOW, MODERATE, HIGH, EMERGENCY) with multilingual keyword matching
- **AI-Powered Analysis**: Local LLM inference using Phi-3 Mini via llama-cpp-python for intelligent medical advice
- **Built-in Knowledge Base**: 94 medical conditions with symptoms, treatments, and "when to see a doctor" guidance (no-LLM fallback)
- **Self-Evolving AI**: Genetic algorithm engine that improves symptom categorization over time using mutation strategies
- **Multilingual Support**: English, Telugu (తెలుగు), Hindi (हिन्दी), and Japanese (日本語)
- **Accessibility**: WCAG compliant with screen reader support, keyboard navigation, ARIA labels, high contrast mode, and reduced motion support
- **Nearby Services**: Integrated geolocation to find nearby hospitals and clinics via OpenStreetMap Overpass API
- **Emergency Detection**: Hardcoded red-flag symptom detection that always overrides other predictions
- **Consultation History**: Session-based chat history with expand/collapse functionality

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io) (Python web framework) |
| **LLM/AI** | [Phi-3 Mini 4K Instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) (GGUF) via [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) |
| **Vector Database** | [ChromaDB](https://www.trychroma.com) (persistent SQLite-based vector store) |
| **Knowledge Base** | Built-in Python dict (94 conditions) + optional CSV import via pandas |
| **Geolocation** | [OpenCage Geocoding API](https://opencagedata.com), [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org), [Overpass API](https://overpass-api.de), [ipapi.co](https://ipapi.co) |
| **Internationalization** | Custom translation engine with JSON locale files (EN, TE, HI, JA) |
| **Accessibility** | Custom CSS via Streamlit markdown injection |
| **Database** | SQLite (evolution logging, ChromaDB persistence) |

## Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **(Optional) Local LLM**: ~2GB free disk space for the Phi-3 Mini GGUF model
- **(Optional) OpenCage API key**: For geocoding and location services
- **Git** (for cloning the repository)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/KNKDarK/serenewalk.git
cd serenewalk
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install heavy dependencies for full features

```bash
pip install llama-cpp-python pandas
```

### 5. (Optional) Download the LLM model

```bash
bash models/download_model.sh
```

### 6. Configure environment variables

Copy the `.env` file and configure:

```env
OPENCAGE_API_KEY=your_api_key_here
MODEL_TEMPERATURE=0.3
MODEL_MAX_TOKENS=400
MODEL_CONTEXT_LENGTH=2048
SEARCH_RADIUS_KM=5
MAX_RESULTS=5
```

## Usage

### Start the application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

### Features at a glance

1. **Select language** from the sidebar (English, Telugu, Hindi, Japanese)
2. **Describe your symptoms** in the chat input
3. **Get triage assessment** with severity classification and medical advice
4. **Use the Medical Translator** tool from the sidebar for translating medical text
5. **View consultation history** with expandable entries

## Project Structure

```
serenewalk/
├── app.py                       # Main Streamlit entry point
├── streamlit_app.py             # Alternative entry point
├── config.py                    # Configuration via environment variables
├── requirements.txt             # Project dependencies
├── .env                         # Environment variables
├── core/                        # Core business logic
│   ├── engine.py                # Unified AI analysis engine
│   ├── triage.py                # Symptom triage & severity classification
│   ├── evolution.py             # Genetic algorithm evolution engine
│   ├── knowledge.py             # Built-in medical knowledge base (94 conditions)
│   └── accessibility.py         # WCAG accessibility utilities
├── i18n/                        # Internationalization
│   ├── translator.py            # Translation helper
│   └── translations.json        # Translations (EN, TE, HI, JA)
├── modules/                     # Legacy modules
│   ├── symptom_parser.py        # Symptom extraction
│   ├── medical_model.py         # LLM model wrapper
│   ├── advisor.py               # Advice generator
│   ├── nearby_services.py       # Nearby hospital/OSM search
│   └── location_permission.py   # IP geolocation
├── utils/
│   └── text_cleaner.py          # Input cleaning & anonymization
├── prompts/
│   ├── system_prompt.txt        # System prompt for LLM
│   └── summary_prompt.txt       # Summary extraction prompt
├── scripts/
│   └── update_knowledge_base.py # KB updater (pandas + CSV)
├── models/
│   └── download_model.sh        # Phi-3 Mini GGUF downloader
├── data/
│   └── kb/                      # ChromaDB persistent storage
├── archive/                     # Archived experimental versions
└── tests/                       # Test files
```

## Language Support

| Language | Code | Region |
|---|---|---|
| **English** | `en` | Default |
| **Telugu** | `te` | Andhra Pradesh, Telangana |
| **Hindi** | `hi` | Northern India |
| **Japanese** | `ja` | Japan |

Select your preferred language from the sidebar.

## Accessibility Features

- Skip-to-content link for keyboard navigation
- High contrast focus indicators
- ARIA labels on all interactive elements
- Screen reader announcements for dynamic content
- Reduced motion support
- High contrast mode support
- 44px minimum touch targets
- WCAG compliant design

## API Reference

### Core Modules

- `core.engine.MedicalEngine` - Unified AI analysis entry point
- `core.triage.triage()` - Symptom triage and severity classification
- `core.evolution.EvolutionEngine` - Self-improving AI evolution via genetic algorithms
- `core.knowledge.MedicalKnowledge` - Built-in medical knowledge base

### Internationalization

- `i18n.translator.t(key, **kwargs)` - Get translated text
- `i18n.translator.set_language(lang)` - Set language (en, te, hi, ja)
- `i18n.translator.get_current_language()` - Get current language

### Utilities

- `utils.text_cleaner.clean_input()` - Sanitize user input
- `utils.text_cleaner.extract_medical_terms()` - Extract medical entities from text

## Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
python -m pytest tests/
```

## Contributing

Contributions are welcome! Here's how you can help:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Guidelines

- Follow existing code style and conventions
- Write clear, descriptive commit messages
- Add tests for new features when possible
- Update documentation for API changes
- Ensure accessibility standards are maintained
- Test multilingual support when adding UI changes

### Areas for Contribution

- **Knowledge Base**: Expand medical conditions and treatment data
- **Translations**: Add or improve translations for supported languages
- **Accessibility**: Enhance WCAG compliance and screen reader support
- **Evolution Engine**: Improve genetic algorithm strategies
- **Tests**: Write unit and integration tests
- **Documentation**: Improve docs and add examples
- **Deployment**: Docker configuration and CI/CD pipelines

## License

MIT License

Copyright (c) 2024 KNKDarK

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Disclaimer

This AI system is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. In case of emergency, call your local emergency number immediately.
