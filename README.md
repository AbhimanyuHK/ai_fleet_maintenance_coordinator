# AI Fleet Maintenance Coordinator

AI-powered Fleet Maintenance Operations Automation Platform.

## Vision

Reduce preventable breakdowns, improve fleet uptime and safety, reduce maintenance cost leakage, recover warranty value, and reduce manual coordination work.

## MVP

- Preventive maintenance monitoring with a 5-day scheduling rule
- Fault prioritization and maintenance risk scoring
- Work-order aging detection
- AI-generated daily maintenance priority queue
- Synthetic fleet data for local development
- Production-oriented API and service boundaries
- Human-in-the-loop controls for safety, compliance, and financial decisions

## Architecture

```text
External Systems
  -> Integration Layer
  -> Event / Data Layer
  -> Fleet Maintenance Domain
  -> Rules + AI/ML + RAG
  -> Workflow Orchestrator
  -> Human Approval / Safe Automation
  -> Dashboard / Notifications / TMT
```

See [HLD.md](HLD.md) for the high-level design and [docs/roadmap.md](docs/roadmap.md) for implementation phases.

## Safety Principle

AI is the intelligence layer, not the authority layer. Safety-critical, compliance-sensitive, financial, and return-to-service decisions remain subject to deterministic policy controls and required human approval.

## Local Development

The initial implementation uses Python and synthetic data so the project can be demonstrated without proprietary TMT, OEM, ELD, or PFJ credentials.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m app.main
```

## Project Status

Phase 1 foundation: repository, architecture, domain models, PM/fault/work-order rules, risk scoring, API skeleton, tests, Docker, and CI are being implemented incrementally.
