# Contributing to NASA ADS Skill & Python Toolkit

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/hcli0228/ads_skill.git
   cd ads_skill
   ```

2. Create a virtual environment and install development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Set up your `.env` file with your NASA ADS Developer API token:
   ```bash
   cp .env.example .env
   # Edit .env and fill in ADS_DEV_KEY
   ```

## Running Tests

Run the test suite with pytest:
```bash
pytest tests/ -v -p no:cacheprovider
```

## Submitting Pull Requests

1. Fork the repo and create a new feature branch (`git checkout -b feature/amazing-feature`).
2. Make your changes and add tests where appropriate.
3. Verify all tests pass.
4. Commit and push your branch, then open a Pull Request.
