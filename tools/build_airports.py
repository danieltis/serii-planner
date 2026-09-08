#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a base de aerodromos europeus (airports.js) a partir dos CSV da OurAirports.

Uso:
    python3 tools/build_airports.py airports.csv runways.csv > airports.js

Fonte dos dados: https://ourairports.com/data/ (dominio publico).
Filtro aplicado:
  - type em {large_airport, medium_airport, small_airport}
  - codigo = icao_code (ou ident quando vazio); tem de casar ^[A-Z]{4}$
  - Europa: continent == 'EU' ou iso_country em {PT, ES, TR, CY};
    exclui a Russia asiatica (RU com longitude > 60)
  - pista: maior length_ft entre as pistas nao encerradas, convertida a metros
    (0 = desconhecida); guarda tambem a superficie dessa pista
  - elevacao: elevation_ft inteiro (null quando desconhecida)
"""
import csv
import datetime
import json
import re
import sys

TYPES = {"large_airport", "medium_airport", "small_airport"}
EXTRA_COUNTRIES = {"PT", "ES", "TR", "CY"}
CODE_RE = re.compile(r"^[A-Z]{4}$")
FT2M = 0.3048


def is_europe(row):
    """Europa: continente EU mais PT/ES/TR/CY; a Russia so ate 60 E."""
    cc = row["iso_country"]
    if not (row["continent"] == "EU" or cc in EXTRA_COUNTRIES):
        return False
    if cc == "RU":
        try:
            if float(row["longitude_deg"]) > 60:
                return False
        except (TypeError, ValueError):
            return False
    return True


def surface_code(raw):
    """Abrevia a superficie a 3-4 letras maiusculas (TURF -> GRS)."""
    s = (raw or "").strip().upper()
    if not s:
        return ""
    if s.startswith("TURF"):
        return "GRS"
    return s[:4]


def load_runways(path):
    """Para cada airport_ident, a pista mais comprida: (metros, superficie)."""
    best = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("closed", "") == "1":
                continue
            raw_len = (row.get("length_ft") or "").strip()
            if not raw_len:
                continue
            try:
                length_ft = float(raw_len)
            except ValueError:
                continue
            if length_ft <= 0:
                continue
            ident = row.get("airport_ident", "")
            cur = best.get(ident)
            if cur is None or length_ft > cur[0]:
                best[ident] = (length_ft, surface_code(row.get("surface")))
    return {k: (int(round(v[0] * FT2M)), v[1]) for k, v in best.items()}


def clean_name(name):
    """Remove o sufixo ' Airport' quando o que sobra continua legivel."""
    name = (name or "").strip()
    if name.endswith(" Airport"):
        short = name[: -len(" Airport")].strip()
        if len(short) >= 4:
            return short
    return name


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("uso: build_airports.py airports.csv runways.csv > airports.js\n")
        return 2
    airports_csv, runways_csv = argv[1], argv[2]
    rwy = load_runways(runways_csv)

    entries = {}
    exact_ident = {}
    with open(airports_csv, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["type"] not in TYPES:
                continue
            if not is_europe(row):
                continue
            code = (row.get("icao_code") or "").strip().upper() or (row.get("ident") or "").strip().upper()
            if not CODE_RE.match(code):
                continue
            try:
                lat = round(float(row["latitude_deg"]), 4)
                lon = round(float(row["longitude_deg"]), 4)
            except (TypeError, ValueError):
                continue
            elev_raw = (row.get("elevation_ft") or "").strip()
            try:
                elev = int(round(float(elev_raw))) if elev_raw else None
            except ValueError:
                elev = None
            # colisao de codigos (dois registos com o mesmo ICAO): fica o
            # aerodromo cujo ident e o proprio codigo.
            exact = row["ident"].strip().upper() == code
            if code in entries and not exact and exact_ident.get(code):
                continue
            exact_ident[code] = exact
            length_m, surf = rwy.get(row["ident"], (0, ""))
            entries[code] = [
                clean_name(row.get("name")),
                (row.get("municipality") or "").strip(),
                row.get("iso_country", "").strip().upper(),
                lat,
                lon,
                elev,
                length_m,
                surf,
            ]

    out = sys.stdout
    today = datetime.date.today().isoformat()
    out.write(
        "// Base de aerodromos europeus com codigo ICAO — fonte: OurAirports "
        "(https://ourairports.com/data/, dominio publico).\n"
        "// Gerado por tools/build_airports.py em %s · %d entradas · filtro: "
        "large/medium/small_airport, codigo ICAO ^[A-Z]{4}$, continente EU mais PT/ES/TR/CY "
        "(sem RU a leste de 60 E).\n"
        "// Formato: CODE:[nome, municipio, pais, lat, lon, elev_ft|null, pista_m (0=desconhecida), superficie].\n"
        % (today, len(entries))
    )
    out.write("const APTS_DB={\n")
    for code in sorted(entries):
        name, muni, cc, lat, lon, elev, length_m, surf = entries[code]
        out.write(
            "%s:[%s,%s,%s,%s,%s,%s,%d,%s],\n"
            % (
                code,
                json.dumps(name, ensure_ascii=False),
                json.dumps(muni, ensure_ascii=False),
                json.dumps(cc, ensure_ascii=False),
                repr(lat),
                repr(lon),
                "null" if elev is None else str(elev),
                length_m,
                json.dumps(surf, ensure_ascii=False),
            )
        )
    out.write("};\n")
    sys.stderr.write("%d aerodromos\n" % len(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
