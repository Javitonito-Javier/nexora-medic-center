from pathlib import Path

from app.core.config import settings


def _create_patient(client) -> str:
    response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Paciente Evidencia",
            "phone": "99990000",
            "identity_number": "0801195000001",
            "birth_date": "1950-01-01",
            "sex": "female",
            "address": "Tegucigalpa",
            "allergies": "ninguna",
            "known_conditions": "ninguna",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_patient_attachment_upload_download_and_delete(client, tmp_path: Path) -> None:
    settings.attachment_storage_dir = str(tmp_path / "attachments")
    patient_id = _create_patient(client)

    upload = client.post(
        f"/api/v1/patients/{patient_id}/attachments",
        data={"category": "discount_evidence", "description": "DNI cuarta edad"},
        files={"file": ("dni.pdf", b"%PDF-1.4 prueba", "application/pdf")},
    )
    assert upload.status_code == 201
    attachment = upload.json()
    assert attachment["patient_id"] == patient_id
    assert attachment["category"] == "discount_evidence"
    assert attachment["original_filename"] == "dni.pdf"

    listed = client.get(f"/api/v1/patients/{patient_id}/attachments")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == attachment["id"]

    download = client.get(
        f"/api/v1/patients/{patient_id}/attachments/{attachment['id']}/download"
    )
    assert download.status_code == 200
    assert download.content == b"%PDF-1.4 prueba"

    deleted = client.delete(f"/api/v1/patients/{patient_id}/attachments/{attachment['id']}")
    assert deleted.status_code == 200

    listed_after_delete = client.get(f"/api/v1/patients/{patient_id}/attachments")
    assert listed_after_delete.status_code == 200
    assert listed_after_delete.json() == []
