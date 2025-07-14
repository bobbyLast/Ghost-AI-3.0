# Ghost AI 3.0

## Overview
Ghost AI 3.0 is a fully modular, sportsbook-grade AI brain for prop betting (MLB, WNBA, and more). It features advanced memory, duplicate prevention, confidence scoring, trap detection, trend tracking, synergy modeling, CLV analysis, and self-auditing. The system is designed for maximum extensibility, maintainability, and future AI/ML upgrades.

---

## System Architecture
- **Controller:** `ghost_brain.py` orchestrates all intelligence features, calling modular subcomponents for memory, scoring, ticket building, posting, and self-audit.
- **Core Modules:** Memory management, prop intake, confidence scoring, fade detection, fantasy calculation, ticket builder, reverse engine integration, posting, self-audit.
- **Expanded/Elite Modules:** Book trap radar, meta trend tracker, synergy model, CLV boost, team memory, opponent modifier, and more.
- **Fail-Safe Systems:** Overconfidence throttle, auto-pause, false positive detector, confidence re-roll, daily auto-clean, streak-aware posting.

---

## Feature Mapping
See the top docstring in `ghost_brain.py` for a full feature-to-file mapping. Every intelligence feature is modular and documented.

---

## Usage
1. **Run the Controller:**
   ```bash
   python ghost_brain.py
   ```
2. **Configure Features:**
   - Edit the `FEATURES` dict at the top of `ghost_brain.py` to toggle any feature ON/OFF.
   - Example: `FEATURES['book_trap_radar'] = False` disables trap detection.
3. **Data:**
   - Place prop/ticket data in the appropriate `data/` or `ghost_ai_core_memory/` subfolders.
   - The system will auto-load, process, and archive as needed.

---

## Testing
- A `tests/` directory contains unit and integration tests for all core and advanced features.
- To run all tests:
  ```bash
  python -m unittest discover tests
  ```
- Example tests cover: duplicate prevention, trap detection, trend/CLV/penalty logic, synergy, memory resets, and more.

---

## Extension & Customization
- **Add New Features:**
  - Implement new methods in `ghost_brain.py` or the relevant module.
  - Add a toggle to the `FEATURES` dict for runtime control.
- **ML/AI Integration:**
  - Use the provided hooks (e.g., in `book_trap_radar`, `meta_trend_tracker`, `confidence_scoring`) to plug in ML models for trap detection, trend prediction, or scoring.
  - All data is structured for easy model training and inference.
- **Data Sources:**
  - Integrate new sportsbooks, stat providers, or odds APIs by extending the prop intake and reverse engine modules.

---

## Troubleshooting
- **No Duplicates:** All duplicate prevention is centralized and enforced at every step.
- **Feature Not Working:** Ensure it is enabled in the `FEATURES` dict and that required data is present.
- **Debugging:** Use the detailed logs and self-audit outputs for diagnosis. Each feature logs its actions and decisions.
- **Testing:** Run the test suite after any major change to ensure system integrity.

---

## Example Data & Mocks
- Example prop and ticket data are provided in the `tests/` and `data/` directories for testing and development.
- You can add your own mock data to simulate new scenarios or edge cases.

---

## Future-Proof & ML-Ready
- All advanced features are modular and ready for ML/AI upgrades.
- The system is designed for continuous learning, self-correction, and easy integration with new models or data sources.

---

## Contact & Support
For questions, feature requests, or contributions, open an issue or contact the maintainer. 