import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.graph.workflow import run_financial_summary_pipeline

client = TestClient(app)


def test_workflow_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_file = Path(tmp_dir) / "salary_slip.pdf"
        xlsx_file = Path(tmp_dir) / "bank_statement.xlsx"
        csv_file = Path(tmp_dir) / "transactions.csv"
        invalid_file = Path(tmp_dir) / "script.exe"

        pdf_file.write_bytes(b"pdf content")
        xlsx_file.write_bytes(b"xlsx content")
        csv_file.write_bytes(b"date,amount\n2026-01-01,5000")
        invalid_file.write_bytes(b"binary content")

        file_paths = [str(pdf_file), str(xlsx_file), str(csv_file), str(invalid_file)]

        result = run_financial_summary_pipeline(file_paths)

        assert result["status"] == "VALIDATED"
        assert len(result["validated_files"]) == 3
        assert len(result["validation_results"]["invalid_files"]) == 1


def test_fastapi_upload_endpoint():
    files = [
        ("files", ("salary_jan.pdf", b"dummy pdf content", "application/pdf")),
        ("files", ("financials.xlsx", b"dummy excel content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ("files", ("data.csv", b"a,b\n1,2", "text/csv")),
    ]

    response = client.post("/upload", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert "files" in json_data
    assert "workflow_result" in json_data
    assert json_data["workflow_result"]["status"] == "VALIDATED"
    assert len(json_data["workflow_result"]["validated_files"]) == 3
