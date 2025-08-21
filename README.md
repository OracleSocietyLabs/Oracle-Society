
# Oracle Society

[![CI - Python](https://github.com/SpirosTs/oracle-society/actions/workflows/ci-python.yml/badge.svg)](https://github.com/SpirosTs/oracle-society/actions/workflows/ci-python.yml) [![CI - Docker](https://github.com/SpirosTs/oracle-society/actions/workflows/ci-docker.yml/badge.svg)](https://github.com/SpirosTs/oracle-society/actions/workflows/ci-docker.yml) [![Release](https://github.com/SpirosTs/oracle-society/actions/workflows/release.yml/badge.svg)](https://github.com/SpirosTs/oracle-society/actions/workflows/release.yml)

A complete, production-ready toolkit for building a emergent gameplay across **RPG**, **Strategy**, and **MMO**.

- ✅ Unity & Unreal **in-process adapters** (no server required)
- ✅ Optional Python relay: REST/SSE + snapshots/WAL + rate-limits + metrics
- ✅ Designer UI (HTML) for snapshot viewing, controls, DSL load/exec, metrics
- ✅ Docker + Prometheus + Grafana
- ✅ Unit/automation tests for both engine & server

## Quickstarts

### Unity (no server)
- Copy the contents of `unity/` into your project.
- Open `unity/README_DEMO.md` and follow the **Sample Scene** hierarchy.
- Run the NUnit tests from **Window → General → Test Runner**.

### Unreal (no server)
- Copy `unreal/*.h/.cpp` into your module; add deps in `*.Build.cs`: `Json`, `JsonUtilities`, `UMG`.
- Use `unreal/README_DEMO.md` to create a UMG widget (parent `UOracleDemoWidget`).
- Run the automation test from **Session Frontend → Automation**.

### Python relay (optional)
```bash
cd server
python run_demo.py
```
Then open `ui/designer_ui_phase15_plus.html` and set Base URL to `http://127.0.0.1:8011`.

#### Docker
```bash
cd docker
docker-compose up --build
```
- Relay:        http://127.0.0.1:8011
- Prometheus:   http://127.0.0.1:9090
- Grafana:      http://127.0.0.1:3000

## Repo layout
- `server/` — relay (REST/SSE), persistence, rate-limit, metrics, demo runner
- `ui/` — Phase 15+ designer HTML UI (vanilla, no build step)
- `adapters/` — Python in-process RPG & Strategy adapters + demos
- `unity/` — C# adapters, MonoBehaviour demo, NUnit tests, README
- `unreal/` — C++ adapters, UMG demo widget, ASCII blueprint guide, automation test
- `docker/` — Dockerfile, compose, prometheus.yml, Grafana dashboard
- `integrations/` — engine integration notes (Unity, Unreal, Godot)
- `tests/` — Python unittests for server

## License
MIT — see `LICENSE`.


## Linting & coverage
- Pre-commit: black, isort, flake8
- CI uploads coverage to Codecov (from Python 3.11 job)


