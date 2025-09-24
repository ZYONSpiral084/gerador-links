# Gerador de Links Avançado 🔗

[![CI](https://github.com/nycolas-salvego/gerador-links-repo/actions/workflows/python-ci.yml/badge.svg)](https://github.com/nycolas-salvego/gerador-links-repo/actions/workflows/python-ci.yml)
![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)
![Flask](https://img.shields.io/badge/flask-2.x-black?logo=flask)

A multilingual project (🇬🇧 English, 🇧🇷 Português, 🇨🇳 中文) for generating sequential links with support for CLI, Flask web app (with Basic Auth), multiple output formats, and Docker deployment.

---

## 🌍 Multilingual Summary

| Topic | English (British) 🇬🇧 | Português (Brasil) 🇧🇷 | 中文 (简体) 🇨🇳 |
|-------|------------------------|--------------------------|--------------------------|
| **Description** | Generate sequential links (HTML, CSV, JSON, TXT) with templates and optional zero-padding. | Gere links sequenciais (HTML, CSV, JSON, TXT) com templates e preenchimento opcional de zeros. | 生成顺序链接（HTML、CSV、JSON、TXT），支持模板和可选零填充。 |
| **CLI Usage** | `python src/gerador_links_advanced.py` prompts for base URL and range. | `python src/gerador_links_advanced.py` solicita URL base e intervalo. | 使用 `python src/gerador_links_advanced.py` 输入基础 URL 和范围。 |
| **Web App** | Flask app with Basic Auth: `/generate?url=...&start=...&end=...&format=html|csv|json|ndjson|txt` | App Flask com autenticação básica: `/generate?url=...&start=...&end=...&format=html|csv|json|ndjson|txt` | Flask 应用，基本身份验证：`/generate?url=...&start=...&end=...&format=html|csv|json|ndjson|txt` |
| **Security** | Basic Auth via env vars: `BASIC_AUTH_USER` / `BASIC_AUTH_PASS`. | Autenticação básica via variáveis de ambiente: `BASIC_AUTH_USER` / `BASIC_AUTH_PASS`. | 通过环境变量实现基本身份验证：`BASIC_AUTH_USER` / `BASIC_AUTH_PASS`。 |
| **Docker** | Build and run with `docker-compose up --build -d`. | Construa e execute com `docker-compose up --build -d`. | 使用 `docker-compose up --build -d` 构建并运行。 |
| **Tests** | Run `pytest tests/` to validate functionality. | Execute `pytest tests/` para validar funcionalidades. | 使用 `pytest tests/` 进行功能验证。 |
| **Example** | Example file in `examples/links_example.html`. | Arquivo de exemplo em `examples/links_example.html`. | 示例文件位于 `examples/links_example.html`。 |

---

## 🚀 Quick Start

### CLI
```bash
python src/gerador_links_advanced.py
```

### Flask Web App
```bash
export BASIC_AUTH_USER=admin
export BASIC_AUTH_PASS=changeme
python src/gerador_links_advanced_auth.py
```

Then open [http://localhost:5000](http://localhost:5000).

### Docker
```bash
docker-compose up --build -d
```

---

## 🧪 Running Tests
```bash
pytest tests/
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
