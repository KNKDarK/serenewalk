# AI Medical Advisor

A self-improving, multilingual medical advice system with accessibility features.

## Features

- 🌍 **Multilingual Support**: English, Telugu (తెలుగు), Hindi (हिन्दी)
- ♿ **Accessibility**: WCAG compliant, screen reader ready, keyboard navigation
- 🧬 **Self-Evolving AI**: Uses genetic algorithms to improve over time
- 📚 **Knowledge Base**: ChromaDB vector search for medical information
- 🤖 **Modern Architecture**: Modular design with clean separation of concerns

## Project Structure

```
medical-advisor/
├── app.py                  # Main Streamlit entry point
├── config.py               # Configuration settings
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables
├── core/                   # Core business logic
│   ├── __init__.py
│   ├── engine.py           # Unified AI engine
│   ├── triage.py           # Triage logic
│   ├── evolution.py        # Evolution engine
│   ├── knowledge.py        # Knowledge base management
│   └── accessibility.py    # Accessibility utilities
├── i18n/                   # Internationalization
│   ├── __init__.py
│   ├── translator.py       # Translation helper
│   └── translations.json   # Translations (EN, TE, HI)
├── modules/                # Legacy modules
├── data/                   # Databases and logs
├── models/                 # AI model files
├── prompts/                # Prompt templates
├── utils/                  # Utility functions
├── tests/                  # Test files
└── archive/                # Old versions (15 files archived)
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Language Support

- **English**: Default language
- ** Telugu (తెలుగు)**: Andhra Pradesh, Telangana
- **Hindi (हिन्दी)**: Northern India

Select your preferred language from the sidebar.

## Accessibility Features

- Skip-to-content link for keyboard navigation
- High contrast focus indicators
- ARIA labels on all interactive elements
- Screen reader announcements for dynamic content
- Reduced motion support
- High contrast mode support
- 44px minimum touch targets

## Running Tests

```bash
python -m pytest tests/
```

## API Reference

### Core Modules

- `core.engine.MedicalEngine` - Unified AI analysis engine
- `core.triage.triage()` - Symptom triage and severity classification
- `core.evolution.EvolutionEngine` - Self-improving AI evolution

### Internationalization

- `i18n.translator.t(key, **kwargs)` - Get translated text
- `i18n.translator.set_language(lang)` - Set language (en, te, hi)
- `i18n.translator.get_current_language()` - Get current language

## License

MIT License
