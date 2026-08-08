from collections.abc import Generator
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.inventory import InventoryLot, InventoryLotPrice, Product  # noqa: F401
from app.modules.patients import Patient  # noqa: F401
from app.modules.pharmacy import PharmacySale, PharmacySaleItem, PharmacySaleLotAllocation  # noqa: F401
from app.modules.points import PointMovement  # noqa: F401


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_inventory_product_transfer_and_pharmacy_sale() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Acetaminofen 500 mg",
            "sku": "ACETA500",
            "barcode": "742000000001",
            "units_per_blister": 10,
            "blisters_per_box": 2,
            "unit_price": 2.5,
            "blister_price": 22,
            "box_price": 40,
            "min_stock_units": 5,
            "lot": {
                "lot_number": "L001",
                "expires_at": "2027-01-30",
                "purchase_unit_cost": 1.1,
                "warehouse_units": 100,
                "store_units": 20,
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()
    assert product["barcode"] == "742000000001"
    assert product["total_store_units"] == 20
    lot_id = product["lots"][0]["id"]

    transfer_response = client.patch(
        f"/api/v1/inventory/lots/{lot_id}/transfer-to-store",
        json={"units": 10},
    )
    assert transfer_response.status_code == 200
    assert transfer_response.json()["store_units"] == 30

    movements_response = client.get(f"/api/v1/inventory/movements?lot_id={lot_id}")
    assert movements_response.status_code == 200
    assert movements_response.json()[0]["movement_type"] == "transfer"

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "cashier_name": "Ana Caja",
            "document_type": "receipt",
            "payment_method": "transfer",
            "payment_reference": "TRX-FARMACIA-001",
            "bank_name": "BAC Credomatic",
            "discount": 0,
            "items": [{"product_id": product["id"], "presentation": "blister", "quantity": 1}],
        },
    )
    assert sale_response.status_code == 201
    sale = sale_response.json()
    assert sale["subtotal"] == 22
    assert sale["cashier_name"] == "Ana Caja"
    assert sale["payment_reference"] == "TRX-FARMACIA-001"
    assert sale["bank_name"] == "BAC Credomatic"
    assert sale["items"][0]["units_deducted"] == 10
    assert sale["items"][0]["cost_total"] == 11
    assert sale["items"][0]["profit_total"] == 11
    assert sale["profit_total"] == 11
    assert sale["items"][0]["allocations"][0]["lot_number"] == "L001"

    receipt_response = client.get(f"/api/v1/pharmacy/sales/{sale['id']}/receipt")
    assert receipt_response.status_code == 200
    assert "RECIBO" in receipt_response.json()["content"]
    assert "Banco: BAC Credomatic" in receipt_response.json()["content"]
    assert "Comprobante: TRX-FARMACIA-001" in receipt_response.json()["content"]

    cash_summary_response = client.get(
        "/api/v1/cash-registers/pharmacy/summary",
        params={"cashier_name": "Ana Caja", "summary_date": sale["created_at"][:10]},
    )
    assert cash_summary_response.status_code == 200
    assert cash_summary_response.json()["sales_count"] == 1
    assert cash_summary_response.json()["by_payment_method"]["transfer"] == 22
    assert cash_summary_response.json()["profit_total"] == 11

    products_response = client.get("/api/v1/inventory/products")
    assert products_response.status_code == 200
    assert products_response.json()[0]["total_store_units"] == 20

    loss_response = client.patch(
        f"/api/v1/inventory/lots/{lot_id}/loss",
        json={
            "location": "store",
            "units": 1,
            "reason": "Producto danado",
            "note": "Merma en conteo ciclico",
        },
    )
    assert loss_response.status_code == 200
    assert loss_response.json()["store_units"] == 19

    app.dependency_overrides.clear()


def test_pharmacy_sale_cascades_lots_and_tracks_real_profit() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Suero oral",
            "sku": "SUERO",
            "unit_price": 10,
            "presentations": [
                {
                    "code": "unit",
                    "name": "Unidad",
                    "units_per_sale": 1,
                    "default_price": 10,
                    "label_price": 12,
                }
            ],
            "min_stock_units": 1,
            "lot": {
                "lot_number": "A",
                "lot_barcode": "LOT-A",
                "shelf_location": "Estante 1",
                "expires_at": "2026-09-01",
                "purchase_unit_cost": 4,
                "warehouse_units": 0,
                "store_units": 4,
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()

    # Second lot is added directly in this test to verify FEFO cascade across batches.
    db = testing_session()
    try:
        db.add(
            InventoryLot(
                product_id=product["id"],
                lot_number="B",
                lot_barcode="LOT-B",
                shelf_location="Estante 2",
                expires_at=date(2027, 1, 1),
                purchase_unit_cost=6,
                warehouse_units=0,
                store_units=6,
            )
        )
        db.commit()
    finally:
        db.close()

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "cashier_name": "Caja",
            "payment_method": "cash",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 9}],
        },
    )
    assert sale_response.status_code == 201
    sale = sale_response.json()
    assert sale["items"][0]["label_unit_price"] == 12
    assert sale["items"][0]["label_line_total"] == 108
    allocations = sale["items"][0]["allocations"]
    assert [allocation["lot_number"] for allocation in allocations] == ["A", "B"]
    assert [allocation["units"] for allocation in allocations] == [4, 5]
    assert sale["cost_total"] == 46
    assert sale["profit_total"] == 44

    strict_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "cashier_name": "Caja",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product["id"],
                    "presentation": "unit",
                    "lot_barcode": "LOT-B",
                    "quantity": 1,
                }
            ],
        },
    )
    assert strict_response.status_code == 201
    assert strict_response.json()["items"][0]["allocations"][0]["lot_number"] == "B"

    app.dependency_overrides.clear()


def test_pharmacy_sale_blocks_expired_lots_even_when_they_have_stock() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Antibiotico control vencimiento",
            "sku": "ABX-VENCE",
            "unit_price": 30,
            "presentations": [
                {"code": "unit", "name": "Unidad", "units_per_sale": 1, "default_price": 30}
            ],
            "min_stock_units": 1,
            "lot": {
                "lot_number": "EXP",
                "lot_barcode": "LOT-EXP",
                "expires_at": (date.today() - timedelta(days=1)).isoformat(),
                "purchase_unit_cost": 12,
                "warehouse_units": 0,
                "store_units": 4,
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()

    db = testing_session()
    try:
        db.add(
            InventoryLot(
                product_id=product["id"],
                lot_number="OK",
                lot_barcode="LOT-OK",
                expires_at=date.today() + timedelta(days=90),
                purchase_unit_cost=14,
                warehouse_units=0,
                store_units=5,
            )
        )
        db.commit()
    finally:
        db.close()

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "cashier_name": "Caja",
            "payment_method": "cash",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 3}],
        },
    )
    assert sale_response.status_code == 201
    sale = sale_response.json()
    assert [allocation["lot_number"] for allocation in sale["items"][0]["allocations"]] == ["OK"]
    assert sale["items"][0]["allocations"][0]["units"] == 3

    expiring_response = client.get("/api/v1/inventory/alerts/expiring-lots?days=120")
    assert expiring_response.status_code == 200
    expiring_lots = expiring_response.json()
    assert [alert["lot_number"] for alert in expiring_lots] == ["OK"]
    assert expiring_lots[0]["days_to_expire"] >= 89

    expired_scan_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "cashier_name": "Caja",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product["id"],
                    "presentation": "unit",
                    "lot_barcode": "LOT-EXP",
                    "quantity": 1,
                }
            ],
        },
    )
    assert expired_scan_response.status_code == 400
    assert "vigente" in expired_scan_response.json()["detail"]

    app.dependency_overrides.clear()


def test_retire_expired_lots_moves_all_expired_stock_to_loss(client) -> None:
    expired_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Producto Vencido Retiro",
            "sku": "RET-EXP",
            "unit_price": 25,
            "lot": {
                "lot_number": "EXP-001",
                "expires_at": (date.today() - timedelta(days=1)).isoformat(),
                "purchase_unit_cost": 10,
                "warehouse_units": 4,
                "store_units": 3,
            },
        },
    )
    assert expired_response.status_code == 201
    expired_lot_id = expired_response.json()["lots"][0]["id"]

    active_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Producto Vigente Retiro",
            "sku": "RET-OK",
            "unit_price": 25,
            "lot": {
                "lot_number": "OK-001",
                "expires_at": (date.today() + timedelta(days=30)).isoformat(),
                "purchase_unit_cost": 10,
                "warehouse_units": 5,
                "store_units": 6,
            },
        },
    )
    assert active_response.status_code == 201
    active_lot_id = active_response.json()["lots"][0]["id"]

    retire_response = client.patch(
        "/api/v1/inventory/lots/expired/retire",
        json={
            "reason": "Retiro por vencimiento",
            "note": "Prueba automatica",
        },
    )
    assert retire_response.status_code == 200
    result = retire_response.json()
    assert result["retired_lots"] == 1
    assert result["store_units"] == 3
    assert result["warehouse_units"] == 4
    assert result["total_units"] == 7

    products_response = client.get("/api/v1/inventory/products?search=Retiro")
    assert products_response.status_code == 200
    products = products_response.json()
    lots = [lot for product in products for lot in product["lots"]]
    expired_lot = next(lot for lot in lots if lot["id"] == expired_lot_id)
    active_lot = next(lot for lot in lots if lot["id"] == active_lot_id)
    assert expired_lot["store_units"] == 0
    assert expired_lot["warehouse_units"] == 0
    assert active_lot["store_units"] == 6
    assert active_lot["warehouse_units"] == 5

    movements_response = client.get(f"/api/v1/inventory/movements?lot_id={expired_lot_id}")
    assert movements_response.status_code == 200
    movements = movements_response.json()
    assert sorted(movement["from_location"] for movement in movements) == [
        "store",
        "warehouse",
    ]
    assert sum(movement["units"] for movement in movements) == 7


def test_flexible_pharmacy_presentations_use_lot_price_and_fifo() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Jarabe pediatrico",
            "sku": "JAR-01",
            "base_unit_name": "Frasco",
            "laboratory_name": "Laboratorio Demo",
            "supplier_name": "Proveedor Demo",
            "unit_price": 95,
            "box_price": 900,
            "blisters_per_box": 12,
            "presentations": [
                {"code": "bottle", "name": "Frasco", "units_per_sale": 1, "default_price": 95},
                {"code": "box", "name": "Caja", "units_per_sale": 12, "default_price": 900},
            ],
            "lot": {
                "lot_number": "J001",
                "expires_at": "2026-12-30",
                "purchase_unit_cost": 60,
                "warehouse_units": 24,
                "store_units": 6,
                "presentation_prices": [
                    {"presentation_code": "bottle", "sale_price": 99},
                    {"presentation_code": "box", "sale_price": 950},
                ],
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()
    bottle = next(
        presentation
        for presentation in product["presentations"]
        if presentation["code"] == "bottle"
    )

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "payment_method": "cash",
            "discount": 0,
            "items": [
                {
                    "product_id": product["id"],
                    "presentation": "bottle",
                    "presentation_id": bottle["id"],
                    "quantity": 2,
                }
            ],
        },
    )
    assert sale_response.status_code == 201
    sale = sale_response.json()
    assert sale["subtotal"] == 198
    assert sale["items"][0]["presentation"] == "Frasco"
    assert sale["items"][0]["units_deducted"] == 2

    app.dependency_overrides.clear()


def test_pharmacy_sale_earns_and_redeems_patient_points() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    patient_response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Cliente Puntos",
            "phone": "9999-0000",
            "identity_number": "POINTS-001",
            "birth_date": "1980-01-01",
            "sex": "female",
            "address": "",
        },
    )
    assert patient_response.status_code == 201
    patient = patient_response.json()

    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Vitaminas",
            "sku": "VIT",
            "unit_price": 1000,
            "min_stock_units": 1,
            "lot": {
                "lot_number": "P001",
                "purchase_unit_cost": 400,
                "warehouse_units": 0,
                "store_units": 3,
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "patient_id": patient["id"],
            "customer_name": patient["full_name"],
            "payment_method": "cash",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert sale_response.status_code == 201
    points_response = client.get("/api/v1/points/")
    assert points_response.status_code == 200
    assert points_response.json()[0]["available_points"] == 2

    db = testing_session()
    try:
        db_patient = db.get(Patient, patient["id"])
        assert db_patient is not None
        db_patient.available_points = 60
        db.add(db_patient)
        db.commit()
    finally:
        db.close()

    redeem_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "patient_id": patient["id"],
            "customer_name": patient["full_name"],
            "payment_method": "cash",
            "discount": 50,
            "discount_type": "points",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert redeem_response.status_code == 201
    assert redeem_response.json()["total"] == 950

    movements_response = client.get(
        "/api/v1/points/movements", params={"patient_id": patient["id"]}
    )
    assert movements_response.status_code == 200
    movement_types = [movement["movement_type"] for movement in movements_response.json()]
    assert movement_types == ["redeem", "earn"]

    points_response = client.get("/api/v1/points/")
    assert points_response.json()[0]["available_points"] == 10

    app.dependency_overrides.clear()


def test_strict_lot_sale_uses_scanned_lot_price(client: TestClient, db_session: Session) -> None:
    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Antibiotico prueba",
            "sku": "ABX",
            "unit_price": 10,
            "presentations": [
                {"code": "unit", "name": "Unidad", "units_per_sale": 1, "default_price": 10}
            ],
            "lot": {
                "lot_number": "A",
                "lot_barcode": "LOT-A",
                "expires_at": "2026-10-01",
                "purchase_unit_cost": 4,
                "warehouse_units": 0,
                "store_units": 2,
                "presentation_prices": [{"presentation_code": "unit", "sale_price": 10}],
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()
    presentation = product["presentations"][0]

    lot_b = InventoryLot(
        product_id=product["id"],
        lot_number="B",
        lot_barcode="LOT-B",
        expires_at=date(2027, 1, 1),
        purchase_unit_cost=7,
        warehouse_units=0,
        store_units=2,
    )
    db_session.add(lot_b)
    db_session.flush()
    db_session.add(
        InventoryLotPrice(
            lot_id=lot_b.id,
            presentation_id=presentation["id"],
            sale_price=20,
            label_price=25,
        )
    )
    db_session.commit()

    sale_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product["id"],
                    "presentation": "unit",
                    "presentation_id": presentation["id"],
                    "lot_barcode": "LOT-B",
                    "quantity": 1,
                }
            ],
        },
    )

    assert sale_response.status_code == 201
    sale = sale_response.json()
    assert sale["subtotal"] == 20
    assert sale["items"][0]["label_line_total"] == 25
    assert sale["items"][0]["allocations"][0]["lot_number"] == "B"


def test_pharmacy_sale_rejects_invalid_mvp_checkout_rules(client: TestClient) -> None:
    product_response = client.post(
        "/api/v1/inventory/products",
        json={
            "name": "Vitaminas validacion",
            "sku": "VIT-VAL",
            "unit_price": 100,
            "min_stock_units": 1,
            "lot": {
                "lot_number": "VAL",
                "purchase_unit_cost": 40,
                "warehouse_units": 0,
                "store_units": 4,
            },
        },
    )
    assert product_response.status_code == 201
    product = product_response.json()

    missing_reference_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "payment_method": "transfer",
            "bank_name": "BAC Credomatic",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert missing_reference_response.status_code == 400
    assert "comprobante" in missing_reference_response.json()["detail"]

    points_without_customer_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "payment_method": "cash",
            "discount": 50,
            "discount_type": "points",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert points_without_customer_response.status_code == 400
    assert "cliente" in points_without_customer_response.json()["detail"]

    excessive_discount_response = client.post(
        "/api/v1/pharmacy/sales",
        json={
            "customer_name": "Consumidor final",
            "payment_method": "cash",
            "discount": 150,
            "discount_type": "general",
            "items": [{"product_id": product["id"], "presentation": "unit", "quantity": 1}],
        },
    )
    assert excessive_discount_response.status_code == 400
    assert "subtotal" in excessive_discount_response.json()["detail"]
