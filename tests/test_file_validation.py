import tempfile
from pathlib import Path
import pytest
from app.services.file_validation import validate_files, ALLOWED_EXTENSIONS


def test_excel_and_csv_file_validation_success():
    with tempfile.TemporaryDirectory() as tmp_dir:
        xlsx_file = Path(tmp_dir) / "financial_statement.xlsx"
        xls_file = Path(tmp_dir) / "legacy_statement.xls"
        csv_file = Path(tmp_dir) / "transactions.csv"

        xlsx_file.write_bytes(b"dummy excel content")
        xls_file.write_bytes(b"dummy legacy content")
        csv_file.write_bytes(b"date,amount\n2026-01-01,1000")

        response = validate_files([xlsx_file, xls_file, csv_file])

        assert response.status == "SUCCESS"
        assert len(response.valid_files) == 3
        assert len(response.invalid_files) == 0

        valid_extensions = {f.extension for f in response.valid_files}
        assert valid_extensions == {".xlsx", ".xls", ".csv"}


def test_allowed_extensions_set():
    assert ".xlsx" in ALLOWED_EXTENSIONS
    assert ".xls" in ALLOWED_EXTENSIONS
    assert ".csv" in ALLOWED_EXTENSIONS
