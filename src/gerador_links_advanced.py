#!/usr/bin/env python3
"""
CLI helper that uses the advanced generator functions
(without running the Flask server).
"""
from __future__ import annotations

import argparse
import sys

from src.gerador_links_advanced_auth import gerar_links_iter, route_writer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gerador avançado de links (CLI)"
    )
    parser.add_argument(
        "--url", "-u", required=True,
        help="Template de URL (use {n} ou {n:03d} ou {} como placeholder)."
    )
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--pad", type=int, default=0)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument(
        "--label-template", default="Capítulo {n}"
    )
    parser.add_argument(
        "--format", "-f", dest="out_format", default="html",
        choices=["html", "csv", "json", "ndjson", "txt"]
    )
    parser.add_argument(
        "--output", "-o",
        help="Arquivo de saída. Omita para imprimir em stdout."
    )
    args = parser.parse_args()

    items = gerar_links_iter(
        args.url, args.start, args.end, pad=args.pad,
        step=args.step, label_template=args.label_template
    )
    writer = route_writer(args.out_format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            writer(items, f)
        print(f"Arquivo salvo: {args.output}")
    else:
        writer(items, sys.stdout)


if __name__ == "__main__":
    main()
