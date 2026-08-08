# Clinicapharma - Database Schema

Ultima revision: 2026-06-23

Este documento refleja los modelos SQLAlchemy actuales en `backend/app/modules`. Si cambia un modelo o migracion, actualizar este archivo en el mismo cambio.

## Tablas actuales

### `staff_users`
Usuarios internos. Campos clave: `username`, `password_hash`, `full_name`, `phone`, `roles` JSON, `module_permissions` JSON, `area`, `active`, `on_shift`, timestamps.

### `audit_events`
Auditoria formal de acciones sensibles. Campos clave: usuario actor (`actor_user_id`, `actor_username`, `actor_name`), `module`, `action`, `entity_type`, `entity_id`, `summary`, snapshots JSON `before_data`/`after_data`, `reason` y `created_at`.

### `business_settings`
Configuracion del negocio. Campos clave: nombre comercial/legal, RTN, contacto, logo, factura/fiscal habilitada, CAI, rangos, correlativo, punto de emision, fecha limite, pies de recibo/factura, nota de descuentos y papel termico.

Nota SAR: estos campos sirven para configuracion simple, pero no sustituyen el modulo fiscal completo. El diseno propuesto para `sar_authorizations`, `fiscal_documents` y `fiscal_document_events` vive en `sar-compliance-roadmap.md`.

### `system_licenses`
Licencia local. Campos clave: `customer_name`, `installation_id`, `license_key`, `payload_json`, `status`, `expires_at`, `activated_at`, `last_checked_at`.

### `patients`
Paciente/cliente. Campos clave: `full_name`, `phone`, `identity_number` unico, `birth_date`, `sex`, `address`, `allergies`, `known_conditions`, `available_points`, timestamps.

### `patient_attachments`
Adjuntos del expediente. Relaciona `patient_id`; guarda categoria, nombre original, nombre almacenado, tipo MIME, tamano, descripcion, usuario que subio, fecha de carga y `deleted_at` para borrado logico. Los binarios viven en `ATTACHMENT_STORAGE_DIR`, fuera de Git.

### `appointments`
Citas. Relaciona `patient_id`; guarda `scheduled_at`, `reason`, `doctor_name`, `status`, `notes`, timestamps.

### `consultations`
Consulta clinica. Relaciona `patient_id`; guarda doctor, especialidad, enfermero, referencia/interconsulta (`referred_by_doctor`, `referred_to_specialty`, `referral_reason`), signos vitales, proxima cita, historia clinica, diagnostico, tratamiento, seguimiento para proximos doctores (`follow_up_notes`), notas internas y `has_prescription`.

### `prescriptions`
Receta. Relaciona `patient_id` y opcionalmente `consultation_id`; guarda `doctor_name`, `doctor_specialty`, `general_notes`, `created_at`. Al crearse vinculada a una consulta, la consulta queda marcada con `has_prescription`.

### `prescription_items`
Items de receta. Relaciona `prescription_id`; guarda medicamento, dosis, via de administracion, frecuencia/intervalo, duracion e instrucciones.

### `clinic_receipts`
Recibos clinicos. Relaciona `patient_id` y opcionalmente `consultation_id`; guarda paciente, cajero, doctor, tipo de documento, metodo de pago, referencia, banco, descripcion, subtotal, descuento, total y fecha.

### `cash_register_sessions`
Sesiones formales de caja. Campos clave: `module` clinica/farmacia, `cashier_name`, `status`, `opening_amount`, `opened_at`, `closed_at`, esperados por metodo (`expected_cash`, `expected_card`, `expected_transfer`, `expected_total`), contados por metodo (`counted_cash`, `counted_card`, `counted_transfer`, `counted_total`), `difference`, `notes`, usuario que abre y usuario que cierra.

### `products`
Producto inventariable. Campos clave: nombre, SKU, barcode, descripcion, unidad base, laboratorio, proveedor, unidades por blister, blisters por caja, precios por defecto, stock minimo, activo y timestamps.

### `product_presentations`
Presentaciones de venta por producto. Guarda codigo, nombre, unidades por venta, precio default, precio de vineta/etiqueta y estado activo.

### `inventory_lots`
Lotes. Relaciona `product_id`; guarda lote, barcode de lote, estante, vencimiento, costo unitario de compra, unidades en bodega y unidades en tienda.

### `inventory_lot_prices`
Precio por lote y presentacion. Relaciona lote y presentacion; guarda precio de venta y precio de vineta.

### `inventory_movements`
Movimientos de inventario. Relaciona lote y producto; guarda tipo de movimiento, ubicacion origen/destino, unidades, razon, nota y fecha.

### `pharmacy_sales`
Venta farmacia. Relaciona opcionalmente `patient_id`; guarda cliente, cajero, documento, metodo de pago, referencia, banco, estado, subtotal, descuento, tipo/base/evidencia de descuento, total y fecha.

### `pharmacy_sale_items`
Detalle de venta farmacia. Relaciona venta y producto; guarda presentacion, cantidad, unidades descontadas, precio, total, precio de vineta, costo y utilidad.

### `pharmacy_sale_lot_allocations`
Asignacion de lotes por venta. Relaciona venta, item, producto y lote; guarda lote, unidades, costo unitario, valor de venta, costo total, ingreso y utilidad.

### `point_movements`
Movimientos de puntos. Relaciona paciente y venta; guarda tipo, puntos, balance posterior, nota y fecha.

## Reglas de integridad esperadas

- El stock operativo sale de `inventory_lots.store_units`; bodega se maneja en `warehouse_units`.
- POS considera vendible un lote solo si `expires_at` es nulo o mayor/igual a la fecha actual.
- Toda venta debe crear allocations por lote para utilidad real y trazabilidad.
- Traslados y mermas deben crear `inventory_movements`.
- Retiro masivo de lotes vencidos debe dejar `inventory_movements` de tipo `loss` por cada ubicacion con existencia.
- Toda accion sensible debe crear `audit_events` cuando exista flujo de escritura auditado.
- Cada apertura/cierre de caja debe crear `cash_register_sessions` y evento de auditoria.
- Puntos disponibles viven en `patients.available_points` y su auditoria en `point_movements`.

## Brechas conocidas

- Los adjuntos basicos existen; falta versionado, expiracion y vinculo directo adjunto-venta/documento si el cliente lo pide.
- No hay tablas SAR dedicadas para autorizaciones, documentos fiscales persistidos y eventos fiscales; por eso la facturacion real debe permanecer desactivada hasta implementar `sar-compliance-roadmap.md`.
- No hay tablas separadas de roles/permisos; actualmente roles y modulos viven como JSON en `staff_users`.
- Auditoria general existe con vista UI; falta ampliar eventos finos para anulaciones/reimpresiones cuando esos flujos existan.
- Cierre de caja formal existe en primer corte; falta anulacion/reimpresion auditada y cortes por rango horario si el cliente lo pide.
- `database_draft.md` es historico y no coincide 1:1 con el esquema real.
