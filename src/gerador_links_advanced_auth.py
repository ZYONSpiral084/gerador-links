#!/usr/bin/env python3
"""gerador_links_advanced_auth.py
 - App Flask com geração de links (html/csv/json/ndjson/txt)
 - Autenticação básica HTTP (usuário/senha via variáveis de ambiente)
 - Limite configurável de tamanho máximo (MAX_RANGE) para evitar abuso
"""
from __future__ import annotations
import os, io, csv, json, html as html_lib, logging
from urllib.parse import urlparse
from typing import Iterable, Dict, Any, Iterator, Optional
from flask import Flask, request, send_file, abort
import string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gerador_auth")

# Configurações por ambiente (são lidas do Docker/Compose ou do shell)
BASIC_USER = os.environ.get("BASIC_AUTH_USER", "admin")
BASIC_PASS = os.environ.get("BASIC_AUTH_PASS", "changeme")
MAX_RANGE = int(os.environ.get("MAX_RANGE", "10000"))  # default máximo de entradas permitidas

app = Flask(__name__)

class UnsafeTemplateError(ValueError):
    pass

def _validate_template_allowed_fields(template: str, allowed_fields: Optional[set[str]] = None) -> None:
    allowed = allowed_fields or {"n", ""}
    fmt = string.Formatter()
    for literal_text, field_name, format_spec, conversion in fmt.parse(template):
        if field_name is None:
            continue
        if field_name not in allowed or any(ch in field_name for ch in ".[]"):
            raise UnsafeTemplateError(f"Campo de template proibido ou inseguro: '{field_name}'")

def ensure_scheme(url_template: str) -> str:
    parsed = urlparse(url_template.replace("{", "X").replace("}", "X"))
    if parsed.scheme == "":
        return "http://" + url_template
    return url_template

def safe_format(template: str, n: int, pad: int = 0) -> str:
    if "{}" in template:
        template = template.replace("{}", "{n}")
    _validate_template_allowed_fields(template, allowed_fields={"n", ""})
    fmt = string.Formatter()
    has_spec = False
    for _, field_name, format_spec, _ in fmt.parse(template):
        if field_name is not None and format_spec:
            has_spec = True
            break
    if has_spec:
        try:
            return template.format(n=n)
        except Exception as e:
            raise ValueError(f"Erro ao formatar template com spec: {e}") from e
    else:
        if pad and pad > 0:
            return template.format(n=f"{n:0{pad}d}")
        return template.format(n=str(n))

def build_url_from_template(template_base: str, n: int, pad: int) -> str:
    template_with_scheme = ensure_scheme(template_base)
    url = safe_format(template_with_scheme, n, pad)
    url = url.strip()
    parsed = urlparse(url.replace("{", "").replace("}", ""))
    if not parsed.scheme:
        url = "http://" + url
    return url

def gerar_links_iter(template_base: str, start: int, end: int, pad: int = 0, step: int = 1, label_template: str = "Capítulo {n}") -> Iterator[Dict[str, Any]]:
    if start > end:
        raise ValueError("start deve ser <= end")
    if step <= 0:
        raise ValueError("step deve ser >= 1")
    if (end - start + 1) > MAX_RANGE:
        raise ValueError(f"Range muito grande: {(end - start + 1)} entradas (máx {MAX_RANGE})")
    if "{}" in label_template:
        label_template = label_template.replace("{}", "{n}")
    _validate_template_allowed_fields(label_template, allowed_fields={"n", ""})
    _validate_template_allowed_fields(template_base.replace("{}", "{n}"), allowed_fields={"n", ""})
    for n in range(start, end + 1, step):
        url = build_url_from_template(template_base, n, pad)
        label = safe_format(label_template, n, pad)
        yield {"n": n, "url": url, "label": html_lib.escape(label)}

# Writers
def write_html_stream(items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase, title: str = "Links"):
    file_obj.write(f"<!doctype html>\n<html lang='pt-BR'>\n<head>\n<meta charset='utf-8'>\n<title>{html_lib.escape(title)}</title>\n</head>\n<body>\n<ul>\n")
    for it in items:
        file_obj.write(f'  <li><a href="{html_lib.escape(it["url"])}">{it["label"]}</a></li>\n')
    file_obj.write("</ul>\n</body>\n</html>\n")

def write_csv_stream(items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase):
    writer = csv.writer(file_obj)
    writer.writerow(["n","url","label"])
    for it in items:
        writer.writerow([it["n"], it["url"], it["label"]])

def write_ndjson_stream(items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase):
    for it in items:
        file_obj.write(json.dumps(it, ensure_ascii=False) + "\n")

def write_json_array_stream(items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase):
    first = True
    file_obj.write("[\n")
    for it in items:
        if not first:
            file_obj.write(",\n")
        file_obj.write(json.dumps(it, ensure_ascii=False))
        first = False
    file_obj.write("\n]\n")

def write_txt_stream(items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase):
    for it in items:
        file_obj.write(f"{it['label']} -> {it['url']}\n")

def route_writer(format_name: str):
    mapping = {"html": write_html_stream, "csv": write_csv_stream, "ndjson": write_ndjson_stream, "json": write_json_array_stream, "txt": write_txt_stream}
    fmt = format_name.lower()
    if fmt not in mapping:
        raise ValueError(f"Formato de saída desconhecido: {format_name}")
    return mapping[fmt]

# --- Basic HTTP Auth helper
def check_auth():
    auth = request.authorization
    if not auth:
        return False
    return auth.username == BASIC_USER and auth.password == BASIC_PASS

def require_auth():
    if not check_auth():
        return abort(401, "Unauthorized", {"WWW-Authenticate": "Basic realm='Login Required'"})

# Routes
@app.route("/generate", methods=["GET"])
def generate_endpoint():
    require_auth()
    url = request.args.get("url")
    if not url:
        return abort(400, "Parâmetro 'url' obrigatório")
    try:
        start = int(request.args.get("start", "1"))
        end = int(request.args.get("end", "10"))
        pad = int(request.args.get("pad", "0"))
        step = int(request.args.get("step", "1"))
    except ValueError:
        return abort(400, "start/end/pad/step precisam ser inteiros válidos")
    label_template = request.args.get("label", "Capítulo {n}")
    out_format = request.args.get("format", "html").lower()
    if out_format not in {"html","csv","json","ndjson","txt"}:
        return abort(400, "Formato inválido")
    # generate
    buf = io.StringIO()
    try:
        items = gerar_links_iter(url, start, end, pad=pad, step=step, label_template=label_template)
        writer = route_writer(out_format)
        writer(items, buf)
        buf.seek(0)
        ext = out_format if out_format != "ndjson" else "ndjson"
        return send_file(io.BytesIO(buf.getvalue().encode("utf-8")),
                         mimetype="application/octet-stream",
                         as_attachment=True,
                         download_name=f"links.{ext}")
    except UnsafeTemplateError as e:
        return abort(400, f"Template inválido: {e}")
    except ValueError as e:
        return abort(400, str(e))
    except Exception as e:
        logger.exception("Erro interno")
        return abort(500, "Erro interno")

@app.route("/")
def index():
    return {
        "message":"Use /generate?url=...&start=...&end=...&format=html|csv|json|ndjson|txt&label=...&pad=...&step=...",
        "auth":"basic (user/pass via BASIC_AUTH_USER/BASIC_AUTH_PASS env vars)"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))