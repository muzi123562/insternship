"""Google Sheets client with CSV fallback."""
import os
import csv
import pandas as pd

USE_CSV = os.environ.get("USE_CSV", "true").lower() in ("1", "true", "yes")
CSV_OUTPUT_PATH = os.environ.get("CSV_OUTPUT_PATH", "leads_output.csv")

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GS_AVAILABLE = True
except Exception:
    GS_AVAILABLE = False


class StorageClient:
    def __init__(self):
        self.use_csv = USE_CSV or not GS_AVAILABLE
        if not self.use_csv:
            creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
            if not creds_path:
                raise RuntimeError("GOOGLE_SHEETS_CREDENTIALS_JSON must be set for Sheets storage")
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            self.client = gspread.authorize(creds)
            ss_id = os.environ.get("SHEETS_SPREADSHEET_ID")
            if not ss_id:
                raise RuntimeError("SHEETS_SPREADSHEET_ID must be set for Sheets storage")
            self.sheet = self.client.open_by_key(ss_id).sheet1

    def append_row(self, row: dict):
        """Row is a dict; we will write a header if CSV doesn't exist."""
        if self.use_csv:
            write_header = not os.path.exists(CSV_OUTPUT_PATH)
            with open(CSV_OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
        else:
            # Convert dict to list matching current header
            try:
                header = self.sheet.row_values(1)
                if not header:
                    header = list(row.keys())
                    self.sheet.append_row(header)
                values = [row.get(h, "") for h in header]
                self.sheet.append_row(values)
            except Exception as e:
                # fallback to CSV
                self.use_csv = True
                self.append_row(row)

    def append_rows(self, rows: list):
        for r in rows:
            self.append_row(r)

