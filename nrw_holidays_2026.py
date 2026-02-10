#!/usr/bin/env python3
"""
Erstellt eine Excel-Datei mit allen Schulferien und Feiertagen für NRW 2026.
Quellen:
  - Schulministerium NRW: Ferienordnung bis 2029/30
  - Gesetzliche Feiertage NRW (Feiertagsgesetz NRW)
"""

import datetime
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Datendefinition
# ---------------------------------------------------------------------------

FEIERTAGE_2026 = [
    (datetime.date(2026, 1, 1),  "Neujahr",                   "Gesetzlicher Feiertag"),
    (datetime.date(2026, 4, 3),  "Karfreitag",                "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 4, 5),  "Ostersonntag",              "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 4, 6),  "Ostermontag",               "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 5, 1),  "Tag der Arbeit",            "Gesetzlicher Feiertag"),
    (datetime.date(2026, 5, 14), "Christi Himmelfahrt",       "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 5, 24), "Pfingstsonntag",            "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 5, 25), "Pfingstmontag",             "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 6, 4),  "Fronleichnam",              "Gesetzlicher Feiertag (beweglich)"),
    (datetime.date(2026, 10, 3), "Tag der Deutschen Einheit", "Gesetzlicher Feiertag"),
    (datetime.date(2026, 11, 1), "Allerheiligen",             "Gesetzlicher Feiertag"),
    (datetime.date(2026, 12, 25),"1. Weihnachtstag",          "Gesetzlicher Feiertag"),
    (datetime.date(2026, 12, 26),"2. Weihnachtstag",          "Gesetzlicher Feiertag"),
]

SCHULFERIEN_2026 = [
    # Name, Beginn, Ende, Hinweis
    ("Weihnachtsferien 2025/26 (Restlaufzeit)",
     datetime.date(2026, 1, 1), datetime.date(2026, 1, 6),
     "Ferien begannen am 22.12.2025"),

    ("Osterferien",
     datetime.date(2026, 3, 30), datetime.date(2026, 4, 11),
     "Unterrichtsbeginn: 13.04.2026"),

    ("Pfingstferien",
     datetime.date(2026, 5, 26), datetime.date(2026, 5, 26),
     "1 freier Tag (Dienstag nach Pfingsten)"),

    ("Sommerferien",
     datetime.date(2026, 7, 20), datetime.date(2026, 9, 1),
     "Letzter Ferientag: 01.09.2026 | Schulbeginn: 02.09.2026"),

    ("Herbstferien",
     datetime.date(2026, 10, 17), datetime.date(2026, 10, 31),
     "Letzter Schultag: 16.10.2026 | Schulbeginn: 02.11.2026"),

    ("Weihnachtsferien 2026/27",
     datetime.date(2026, 12, 23), datetime.date(2026, 12, 31),
     "Ferien enden am 06.01.2027"),
]

WOCHENTAGE_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                 "Freitag", "Samstag", "Sonntag"]
MONATE_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def fmt_date(d: datetime.date) -> str:
    return f"{WOCHENTAGE_DE[d.weekday()]}, {d.day:02d}.{d.month:02d}.{d.year}"


def thin_border():
    thin = Side(border_style="thin", color="CCCCCC")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def header_fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def set_col_widths(ws, widths: dict):
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width


# ---------------------------------------------------------------------------
# Sheet 1 – Jahresübersicht (Kalenderblatt)
# ---------------------------------------------------------------------------

def build_ferien_lookup(ferien):
    """Gibt für jeden Datum-String im Jahr 2026 den Feriennamen zurück."""
    lookup = {}
    for name, start, end, _ in ferien:
        d = start
        while d <= end:
            if d.year == 2026:
                lookup[d] = name
            d += datetime.timedelta(days=1)
    return lookup


def build_feiertag_lookup(feiertage):
    return {d: name for d, name, _ in feiertage}


def create_calendar_sheet(wb, ferien_lookup, feiertag_lookup):
    ws = wb.create_sheet("Jahreskalender 2026")

    # Farben
    COLOR_HEADER      = "1F4E79"   # Dunkelblau
    COLOR_MONAT       = "2E75B6"   # Blau
    COLOR_WOCHENENDE  = "D6E4F0"   # Hellblau
    COLOR_FERIEN      = "E2EFDA"   # Hellgrün
    COLOR_FEIERTAG    = "FCE4D6"   # Hellrot/Orange
    COLOR_BEIDES      = "FFF2CC"   # Hellgelb (Ferien + Feiertag)
    COLOR_HEUTE       = "FFFFFF"

    # Kopfzeile
    ws.merge_cells("A1:F1")
    title_cell = ws["A1"]
    title_cell.value = "Schulferien & Feiertage NRW 2026"
    title_cell.font = Font(bold=True, size=16, color="FFFFFF", name="Calibri")
    title_cell.fill = header_fill(COLOR_HEADER)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    # Spalten-Header
    headers = ["Datum", "Wochentag", "Monat", "Schulferien", "Feiertag", "Typ"]
    col_fills = ["2E75B6"] * 6
    for col, (h, fc) in enumerate(zip(headers, col_fills), start=1):
        cell = ws.cell(row=2, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF", name="Calibri")
        cell.fill = header_fill(fc)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border()
    ws.row_dimensions[2].height = 20

    # Alle Tage 2026 eintragen
    start = datetime.date(2026, 1, 1)
    end   = datetime.date(2026, 12, 31)
    row = 3
    d = start
    while d <= end:
        ferien_name  = ferien_lookup.get(d, "")
        feiertag_name = feiertag_lookup.get(d, "")
        is_weekend   = d.weekday() >= 5
        is_ferien    = bool(ferien_name)
        is_feiertag  = bool(feiertag_name)

        # Zellfarbe bestimmen
        if is_ferien and is_feiertag:
            bg = COLOR_BEIDES
        elif is_feiertag:
            bg = COLOR_FEIERTAG
        elif is_ferien:
            bg = COLOR_FERIEN
        elif is_weekend:
            bg = COLOR_WOCHENENDE
        else:
            bg = "FFFFFF"

        fill = PatternFill("solid", fgColor=bg)

        # Typ-Text
        typ_parts = []
        if is_feiertag: typ_parts.append("Feiertag")
        if is_ferien:   typ_parts.append("Schulferien")
        if is_weekend and not typ_parts:
            typ_parts.append("Wochenende")
        elif is_weekend:
            typ_parts.append("Wochenende")
        typ = " & ".join(typ_parts) if typ_parts else "Schultag"

        values = [
            f"{d.day:02d}.{d.month:02d}.{d.year}",
            WOCHENTAGE_DE[d.weekday()],
            MONATE_DE[d.month - 1],
            ferien_name,
            feiertag_name,
            typ,
        ]
        for col, val in enumerate(values, start=1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.fill = fill
            cell.border = thin_border()
            cell.alignment = Alignment(vertical="center")
            if col == 1:
                cell.font = Font(bold=True, name="Calibri", size=10)
            else:
                cell.font = Font(name="Calibri", size=10)

        ws.row_dimensions[row].height = 16
        row += 1
        d += datetime.timedelta(days=1)

    # Spaltenbreiten
    set_col_widths(ws, {
        "A": 14, "B": 14, "C": 12, "D": 30, "E": 24, "F": 20
    })
    ws.freeze_panes = "A3"


# ---------------------------------------------------------------------------
# Sheet 2 – Schulferien-Übersicht
# ---------------------------------------------------------------------------

def create_ferien_sheet(wb):
    ws = wb.create_sheet("Schulferien 2026")

    COLOR_HEADER = "1F4E79"
    COLOR_ROW    = ["E2EFDA", "C6EFCE"]

    ws.merge_cells("A1:E1")
    t = ws["A1"]
    t.value = "Schulferien Nordrhein-Westfalen 2026"
    t.font = Font(bold=True, size=15, color="FFFFFF", name="Calibri")
    t.fill = header_fill(COLOR_HEADER)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    src_cell = ws["A2"]
    src_cell.value = "Quelle: Schulministerium NRW – Ferienordnung bis 2029/30"
    src_cell.font = Font(italic=True, size=9, color="595959")
    ws.merge_cells("A2:E2")
    ws.row_dimensions[2].height = 16

    headers = ["Ferienbezeichnung", "Beginn", "Ende", "Dauer (Tage)", "Hinweis"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF", name="Calibri")
        cell.fill = header_fill("2E75B6")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border()
    ws.row_dimensions[3].height = 20

    for i, (name, start, end, hint) in enumerate(SCHULFERIEN_2026):
        row = 4 + i
        dauer = (end - start).days + 1
        fill = PatternFill("solid", fgColor=COLOR_ROW[i % 2])
        vals = [name, fmt_date(start), fmt_date(end), dauer, hint]
        for col, val in enumerate(vals, start=1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.fill = fill
            cell.border = thin_border()
            cell.alignment = Alignment(vertical="center", wrap_text=(col == 5))
            if col == 1:
                cell.font = Font(bold=True, name="Calibri")
            elif col == 4:
                cell.font = Font(bold=True, name="Calibri")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.font = Font(name="Calibri")
        ws.row_dimensions[row].height = 20

    # Gesamtsumme
    total_row = 4 + len(SCHULFERIEN_2026)
    total_days_2026 = sum(
        sum(1 for k in range((e - s).days + 1)
            if (s + datetime.timedelta(k)).year == 2026)
        for _, s, e, _ in SCHULFERIEN_2026
    )
    ws.cell(row=total_row, column=1, value="Gesamt Ferientage in 2026") \
      .font = Font(bold=True, name="Calibri")
    ws.cell(row=total_row, column=1).fill = header_fill("BDD7EE")
    ws.cell(row=total_row, column=1).border = thin_border()
    for c in range(2, 5):
        ws.cell(row=total_row, column=c).fill = header_fill("BDD7EE")
        ws.cell(row=total_row, column=c).border = thin_border()
    days_cell = ws.cell(row=total_row, column=4, value=total_days_2026)
    days_cell.font = Font(bold=True, name="Calibri")
    days_cell.fill = header_fill("BDD7EE")
    days_cell.border = thin_border()
    days_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=total_row, column=5).fill = header_fill("BDD7EE")
    ws.cell(row=total_row, column=5).border = thin_border()

    set_col_widths(ws, {
        "A": 34, "B": 36, "C": 36, "D": 16, "E": 45
    })


# ---------------------------------------------------------------------------
# Sheet 3 – Feiertage-Übersicht
# ---------------------------------------------------------------------------

def create_feiertage_sheet(wb):
    ws = wb.create_sheet("Feiertage 2026")

    COLOR_HEADER = "1F4E79"
    COLOR_ROW    = ["FCE4D6", "F8CBAD"]

    ws.merge_cells("A1:D1")
    t = ws["A1"]
    t.value = "Gesetzliche Feiertage Nordrhein-Westfalen 2026"
    t.font = Font(bold=True, size=15, color="FFFFFF", name="Calibri")
    t.fill = header_fill(COLOR_HEADER)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    src_cell = ws["A2"]
    src_cell.value = "Quelle: Feiertagsgesetz NRW | Gesamt: 11 gesetzliche Feiertage"
    src_cell.font = Font(italic=True, size=9, color="595959")
    ws.merge_cells("A2:D2")
    ws.row_dimensions[2].height = 16

    headers = ["Datum", "Wochentag", "Feiertag", "Art"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF", name="Calibri")
        cell.fill = header_fill("C00000")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border()
    ws.row_dimensions[3].height = 20

    for i, (datum, name, art) in enumerate(FEIERTAGE_2026):
        row = 4 + i
        fill = PatternFill("solid", fgColor=COLOR_ROW[i % 2])
        vals = [
            f"{datum.day:02d}.{datum.month:02d}.{datum.year}",
            WOCHENTAGE_DE[datum.weekday()],
            name,
            art,
        ]
        for col, val in enumerate(vals, start=1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.fill = fill
            cell.border = thin_border()
            cell.alignment = Alignment(vertical="center")
            if col == 3:
                cell.font = Font(bold=True, name="Calibri")
            else:
                cell.font = Font(name="Calibri")
        ws.row_dimensions[row].height = 18

    set_col_widths(ws, {"A": 16, "B": 14, "C": 28, "D": 35})


# ---------------------------------------------------------------------------
# Sheet 4 – Monatsübersicht (kompakte Tabelle)
# ---------------------------------------------------------------------------

def create_monthly_sheet(wb, ferien_lookup, feiertag_lookup):
    ws = wb.create_sheet("Monatsübersicht 2026")

    COLOR_HEADER   = "1F4E79"
    COLOR_MONAT_H  = "2E75B6"
    COLOR_FERIEN   = "E2EFDA"
    COLOR_FEIERTAG = "FCE4D6"
    COLOR_BEIDES   = "FFF2CC"
    COLOR_WE       = "D6E4F0"

    ws.merge_cells("A1:H1")
    t = ws["A1"]
    t.value = "Monatsübersicht – Schulferien & Feiertage NRW 2026"
    t.font = Font(bold=True, size=15, color="FFFFFF", name="Calibri")
    t.fill = header_fill(COLOR_HEADER)
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Legende
    legend_row = 2
    legend = [
        ("Schulferien", "E2EFDA"),
        ("Feiertag",    "FCE4D6"),
        ("Ferien + Feiertag", "FFF2CC"),
        ("Wochenende",  "D6E4F0"),
    ]
    ws.cell(row=legend_row, column=1, value="Legende:").font = Font(bold=True, name="Calibri", size=9)
    for idx, (label, color) in enumerate(legend):
        col = 2 + idx
        cell = ws.cell(row=legend_row, column=col, value=label)
        cell.fill = PatternFill("solid", fgColor=color)
        cell.border = thin_border()
        cell.font = Font(name="Calibri", size=9)
        cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[legend_row].height = 16

    row = 3
    for month_idx in range(1, 13):
        # Monatskopf
        ws.merge_cells(
            start_row=row, start_column=1,
            end_row=row,   end_column=8
        )
        m_cell = ws.cell(row=row, column=1,
                         value=f"{MONATE_DE[month_idx-1]} 2026")
        m_cell.font = Font(bold=True, size=12, color="FFFFFF", name="Calibri")
        m_cell.fill = header_fill(COLOR_MONAT_H)
        m_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[row].height = 22
        row += 1

        # Wochen-Header
        for col, h in enumerate(
            ["KW", "Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"], start=1
        ):
            cell = ws.cell(row=row, column=col, value=h)
            cell.font = Font(bold=True, name="Calibri", size=9)
            cell.fill = header_fill("BDD7EE")
            cell.border = thin_border()
            cell.alignment = Alignment(horizontal="center")
        ws.row_dimensions[row].height = 16
        row += 1

        # Kalenderwochen des Monats
        first_day = datetime.date(2026, month_idx, 1)
        last_day  = (datetime.date(2026, month_idx % 12 + 1, 1)
                     - datetime.timedelta(days=1)) if month_idx < 12 else datetime.date(2026, 12, 31)

        # Start-Montag der ersten Woche
        cur = first_day - datetime.timedelta(days=first_day.weekday())
        while cur <= last_day:
            kw = cur.isocalendar()[1]
            kw_cell = ws.cell(row=row, column=1, value=kw)
            kw_cell.font = Font(bold=True, name="Calibri", size=9, color="595959")
            kw_cell.alignment = Alignment(horizontal="center")
            kw_cell.border = thin_border()

            for wd in range(7):
                d = cur + datetime.timedelta(days=wd)
                col = 2 + wd
                if d.month != month_idx:
                    cell = ws.cell(row=row, column=col, value="")
                    cell.fill = PatternFill("solid", fgColor="F2F2F2")
                    cell.border = thin_border()
                else:
                    ferien   = ferien_lookup.get(d, "")
                    feiertag = feiertag_lookup.get(d, "")
                    is_we    = d.weekday() >= 5
                    if ferien and feiertag:
                        bg = COLOR_BEIDES
                    elif feiertag:
                        bg = COLOR_FEIERTAG
                    elif ferien:
                        bg = COLOR_FERIEN
                    elif is_we:
                        bg = COLOR_WE
                    else:
                        bg = "FFFFFF"

                    disp = str(d.day)
                    cell = ws.cell(row=row, column=col, value=disp)
                    cell.fill = PatternFill("solid", fgColor=bg)
                    cell.border = thin_border()
                    cell.alignment = Alignment(horizontal="center")
                    cell.font = Font(
                        name="Calibri", size=9,
                        bold=bool(feiertag),
                        color="C00000" if feiertag else "000000"
                    )
                    # Tooltip via comment würde openpyxl unterstützen, lass hier den Namen
                    if feiertag:
                        cell.comment = None  # Platzhalter

            ws.row_dimensions[row].height = 16
            row += 1
            cur += datetime.timedelta(days=7)

        row += 1  # Abstand zwischen Monaten

    set_col_widths(ws, {
        "A": 5, "B": 7, "C": 7, "D": 7,
        "E": 7, "F": 7, "G": 7, "H": 7
    })


# ---------------------------------------------------------------------------
# Hauptprogramm
# ---------------------------------------------------------------------------

def main():
    wb = Workbook()
    # Standard-Sheet entfernen
    del wb["Sheet"]

    ferien_lookup   = build_ferien_lookup(SCHULFERIEN_2026)
    feiertag_lookup = build_feiertag_lookup(FEIERTAGE_2026)

    # Sheets erstellen
    create_ferien_sheet(wb)
    create_feiertage_sheet(wb)
    create_monthly_sheet(wb, ferien_lookup, feiertag_lookup)
    create_calendar_sheet(wb, ferien_lookup, feiertag_lookup)

    # Erstes Sheet aktivieren
    wb.active = wb["Schulferien 2026"]

    outfile = "NRW_Schulferien_Feiertage_2026.xlsx"
    wb.save(outfile)
    print(f"Excel-Datei erstellt: {outfile}")


if __name__ == "__main__":
    main()
