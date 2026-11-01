# Contributing to PrecipiCast AI

Thank you for your interest in contributing to **PrecipiCast AI & Rainwater Harvesting Engine**! We welcome improvements to machine learning pipelines, hydrological models, UI components, and API optimizations.

## Getting Started

1. **Fork the Repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/PrecipiCast-AI.git
   cd PrecipiCast-AI
   ```
3. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/macOS
   source venv/bin/activate
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

- **Branching**: Create a feature branch with a descriptive name:
  ```bash
  git checkout -b feature/improved-feature-engineering
  ```
- **Running Tests**: Ensure all automated tests pass before committing:
  ```bash
  python -m unittest discover -s tests
  ```
- **Code Style**: Follow PEP 8 guidelines for Python code and maintain clean, semantic HTML/CSS/JS.

## Submitting Pull Requests

1. Commit your changes with meaningful commit messages:
   ```bash
   git commit -m "feat: add evapotranspiration index to RWH sizing"
   ```
2. Push to your fork:
   ```bash
   git push origin feature/improved-feature-engineering
   ```
3. Open a Pull Request against the `main` branch with a summary of changes, rationale, and test results.

---
*Questions or bug reports? Open an [Issue](https://github.com/ritesh0w0/PrecipiCast-AI/issues).*

