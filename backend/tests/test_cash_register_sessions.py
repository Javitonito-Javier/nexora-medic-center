from fastapi.testclient import TestClient


def test_open_and_close_clinic_cash_register(client: TestClient) -> None:
    open_response = client.post(
        "/api/v1/cash-registers/sessions/open",
        json={
            "module": "clinic",
            "cashier_name": "Recepcion",
            "opening_amount": 100,
        },
    )
    assert open_response.status_code == 201
    session = open_response.json()
    assert session["status"] == "open"

    patient_response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Paciente Caja",
            "phone": "9999-2222",
            "identity_number": "CASH-001",
            "birth_date": "1990-01-01",
            "sex": "female",
            "address": "",
        },
    )
    assert patient_response.status_code == 201
    patient = patient_response.json()

    receipt_response = client.post(
        "/api/v1/receipts/clinic",
        json={
            "patient_id": patient["id"],
            "cashier_name": "Recepcion",
            "doctor_name": "Dra Caja",
            "document_type": "receipt",
            "payment_method": "cash",
            "description": "Consulta general",
            "subtotal": 500,
            "discount": 50,
        },
    )
    assert receipt_response.status_code == 201

    close_response = client.post(
        f"/api/v1/cash-registers/sessions/{session['id']}/close",
        json={
            "counted_cash": 550,
            "counted_card": 0,
            "counted_transfer": 0,
            "notes": "",
        },
    )
    assert close_response.status_code == 200
    closed = close_response.json()
    assert closed["status"] == "closed"
    assert closed["expected_cash"] == 550
    assert closed["expected_total"] == 550
    assert closed["counted_total"] == 550
    assert closed["difference"] == 0
