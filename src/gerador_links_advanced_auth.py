#!/usr/bin/env python3
"""
gerador_links_advanced_auth.py

Helpers for generating links (html/csv/json/ndjson/txt).
This module is imported by CLI and by the Flask app.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import string
from typing import Any, Dict, Iterable, Iterator, Optional
from urllib.parse import urlparse

import html as html_lib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gerador_auth")


class UnsafeTemplateError(ValueError):
    """Raised when a template contains disallowed fields."""
    pass


def _validate_template_allowed_fields(
    template: str, allowed_fields: Optional[set[str]] = None
) -> None:
    allowed = allowed_fields or {"n", ""}
    fmt = string.Formatter()
    for _, field_name, _, _ in fmt.parse(template):
        if field_name is None:
            continue
        if field_name not in allowed or any(ch in field_name for ch in ".[]"):
            raise UnsafeTemplateError(
                f"Campo de template proibido ou inseguro: '{field_name}'"
            )


def ensure_scheme(url_template: str) -> str:
    parsed = urlparse(url_template.replace("{", "X").replace("}", "X"))
    if parsed.scheme == "":
        return "http://" + url_template
    return url_template


def safe_format(template: str, n: int, pad: int = 0) -> str:
    """Safely format templates like {n}, {n:03d} or {}."""

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
        except Exception as exc:
            raise ValueError(
                f"Erro ao formatar template com spec: {exc}"
            ) from exc

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


def gerar_links_iter(
    template_base: str,
    start: int,
    end: int,
    pad: int = 0,
    step: int = 1,
    label_template: str = "Capítulo {n}",
) -> Iterator[Dict[str, Any]]:
    if start > end:
        raise ValueError("start deve ser <= end")
    if step <= 0:
        raise ValueError("step deve ser >= 1")

    # Abuse protection: MAX_RANGE can be set as env var.
    max_range_env = os.environ.get("MAX_RANGE")
    if max_range_env:
        try:
            max_range = int(max_range_env)
        except ValueError:
            max_range = None
    else:
        max_range = None

    if max_range is not None and (end - start + 1) > max_range:
        raise ValueError(
            f"Range muito grande: {(end - start + 1)} entradas "
            f"(máx {max_range})"
        )

    if "{}" in label_template:
        label_template = label_template.replace("{}", "{n}")

    _validate_template_allowed_fields(label_template, allowed_fields={"n", ""})
    _validate_template_allowed_fields(
        template_base.replace("{}", "{n}"), allowed_fields={"n", ""}
    )

    for n in range(start, end + 1, step):
        url = build_url_from_template(template_base, n, pad)
        label = safe_format(label_template, n, pad)
        yield {"n": n, "url": url, "label": html_lib.escape(label)}


# Writers (streaming)


def write_html_stream(
    items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase,
    title: str = "Links"
) -> None:
    file_obj.write(
        "<!doctype html>\n<html lang='pt-BR'>\n<head>\n<meta charset='utf-8'>\n"
    )
    file_obj.write(
        f"<title>{html_lib.escape(title)}</title>\n"
        "</head>\n<body>\n<ul>\n"
    )
    for it in items:
        file_obj.write(
            f'  <li><a href="{html_lib.escape(it["url"])}">'
            f'{it["label"]}</a></li>\n'
        )
    file_obj.write("</ul>\n</body>\n</html>\n")


def write_csv_stream(items: Iterable[Dict[str, Any]], file_obj: io.TextIOBase) -> None:
    writer = csv.writer(file_obj)
    writer.writerow(["n", "url", "label"])
    for it in items:
        writer.writerow([it["n"], it["url"], it["label"]])


def write_ndjson_stream(items: Iterable[Dict[str, Any)], file]()
