from datetime import UTC, date, datetime, timedelta

from app.modules.inventory.models import InventoryLot
from app.modules.receipts.models import ClinicReceipt


def test_reports_summary_reuses_operational_dashboard(client) -> None:
    response = client.get("/api/v1/reports/summary")

    assert response.status_code == 200
    data = response.json()
    metric_titles = [metric["title"] for metric in data["metrics"]]
    assert "Ventas farmacia hoy" in metric_titles
    assert "Consultas pagadas hoy" in metric_titles
    assert "Utilidad farmacia mes" in metric_titles
    assert data["alerts"]


def test_reports_include_sales_profit_and_inventory_exports(client, db_session) -> None:
    patient_response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Paciente Reportes",
            "phone": "9999-1111",
            "identity_number": "REP-001",
            "birth_date": "1985-01-01",
            "sex": "female",
            "address": "",
        },
    )
    assert patient_response.status_code == 201
    patient = patient_response.json()

    db_session.add(
        ClinicReceipt(
            patient_id=patient["id"],
            patient_name=patient["full_name"],
            cashier_name="Caja Clinica",
            doctor_name="Dra Demo",
            payment_method="card",
            document_type="receipt",
            description="Consulta general",
            subtotal=500,
            discount=50,
            total=450,
        )
    )
    db_session.commit()

    expires_at = date.today() + timedelta(days=120)
    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Reporte Vitaminas",
            "sku": "REP-VIT",
            "unit_price": 100,
            "min_stock_units": 5,
            "lot": {
                "lot_number": "R001",
                "expires_at": expires_at.isoformat(),
                "purchase_unit_cost": 40,
                "warehouse_units": 3,
                "store_units": 2,
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "cashier_name": "Caja Farmacia",
            "payment_method": "cash",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert sale_response.status_code == 201

    points_sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "patient_id": patient["id"],
            "customer_name": patient["full_name"],
            "cashier_name": "Caja Farmacia",
            "payment_method": "cash",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert points_sale_response.status_code == 201

    sales_response = client.get("/api/v1/reports/sales")
    assert sales_response.status_code == 200
    sales = sales_response.json()
    assert any(row["module"] == "clinic" and row["total"] == 450 for row in sales)
    assert any(row["module"] == "pharmacy" and row["total"] == 200 for row in sales)

    clinic_receipts_response = client.get("/api/v1/reports/clinic-receipts")
    assert clinic_receipts_response.status_code == 200
    clinic_receipts = clinic_receipts_response.json()
    assert clinic_receipts[0]["doctor_name"] == "Dra Demo"
    assert clinic_receipts[0]["service_description"] == "Consulta general"
    assert clinic_receipts[0]["cashier_name"] == "Caja Clinica"
    assert clinic_receipts[0]["receipts_count"] == 1
    assert clinic_receipts[0]["total"] == 450

    profit_response = client.get("/api/v1/reports/profit-by-lot")
    assert profit_response.status_code == 200
    profit = profit_response.json()
    assert profit[0]["lot_number"] == "R001"
    assert profit[0]["revenue_total"] == 200
    assert profit[0]["cost_total"] == 80
    assert profit[0]["profit_total"] == 120

    low_stock_response = client.get("/api/v1/reports/inventory/low-stock")
    assert low_stock_response.status_code == 200
    low_stock = low_stock_response.json()
    assert low_stock[0]["product_name"] == "Reporte Vitaminas"
    assert low_stock[0]["store_units"] == 0
    assert low_stock[0]["warehouse_units"] == 3

    expiring_response = client.get("/api/v1/reports/inventory/expiring-stock?days=365")
    assert expiring_response.status_code == 200
    expiring = expiring_response.json()
    assert expiring[0]["lot_number"] == "R001"
    assert expiring[0]["total_units"] == 3

    point_movements_response = client.get("/api/v1/reports/points/movements")
    assert point_movements_response.status_code == 200
    movements = point_movements_response.json()
    assert movements[0]["patient_name"] == "Paciente Reportes"
    assert movements[0]["movement_type"] == "earn"
    assert movements[0]["points"] == 0.2

    top_products_response = client.get("/api/v1/reports/pharmacy/top-products")
    assert top_products_response.status_code == 200
    top_products = top_products_response.json()
    assert top_products[0]["product_name"] == "Reporte Vitaminas"
    assert top_products[0]["units_deducted"] == 2
    assert top_products[0]["revenue_total"] == 200

    stagnant_product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Reporte Estancado",
            "sku": "REP-STAG",
            "unit_price": 50,
            "min_stock_units": 1,
            "lot": {
                "lot_number": "S001",
                "purchase_unit_cost": 20,
                "warehouse_units": 0,
                "store_units": 5,
            },
        },
    )
    assert stagnant_product_response.status_code == 201
    stagnant_lot_id = stagnant_product_response.json()["lots"][0]["id"]
    stagnant_lot = db_session.get(InventoryLot, stagnant_lot_id)
    assert stagnant_lot is not None
    stagnant_lot.updated_at = datetime.now(UTC) - timedelta(days=30)
    db_session.add(stagnant_lot)
    db_session.commit()

    stagnant_response = client.get("/api/v1/reports/inventory/stagnant-lots?days=15")
    assert stagnant_response.status_code == 200
    stagnant = stagnant_response.json()
    assert stagnant[0]["product_name"] == "Reporte Estancado"
    assert stagnant[0]["days_without_movement"] >= 29
