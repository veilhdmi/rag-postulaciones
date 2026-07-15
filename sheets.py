import os

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

COLUMNS = [
    "Fecha", "Empresa", "Puesto", "Fuente", "Estado",
    "Version_CV", "Salario", "Contacto", "Link_Oferta",
    "Proxima_accion", "Notas",
]


def fetch_postulaciones() -> list[dict]:
    creds = Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.environ["SPREADSHEET_ID"]).worksheet(
        os.environ["SHEET_NAME"]
    )
    rows = sheet.get_all_values()[1:]  # skip header

    records = []
    for row in rows:
        row = row + [""] * (len(COLUMNS) - len(row))  # pad short rows
        if not row[1].strip():  # no Empresa -> not a real entry
            continue
        records.append(dict(zip(COLUMNS, row)))
    return records
