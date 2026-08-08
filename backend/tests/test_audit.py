from fastapi.testclient import TestClient


def test_patient_create_writes_audit_event(client: TestClient) -> None:
    response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Paciente Auditado",
            "phone": "92398074",
            "identity_number": "AUD-001",
            "birth_date": "1980-01-01",
            "sex": "male",
            "address": "No registrada",
            "allergies": "ninguna",
            "known_conditions": "ninguna",
        },
    )

    assert response.status_code == 201
    patient_id = response.json()["id"]

    audit_response = client.get(
        f"/api/v1/audit/?module=patients&entity_type=patient&entity_id={patient_id}"
    )

    assert audit_response.status_code == 200
    events = audit_response.json()
    assert len(events) == 1
    assert events[0]["action"] == "create"
    assert events[0]["entity_id"] == patient_id
    assert events[0]["after_data"]["full_name"] == "Paciente Auditado"
