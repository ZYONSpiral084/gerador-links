#!/usr/bin/env python3
"""
gerador_links_advanced_auth.py

Helpers for generating links (html/csv/json/ndjson/txt).
This module is imported by the CLI and by the Flask app.
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
                f"Campo de template proibido ou inseguro: "
                f"'{field_name}'"
            )


def ensure_scheme(url_template: str) -> str:
    parsed = urlparse(
        url_template.replace("{", "X").replace("}", "X")
    )
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
    if no
