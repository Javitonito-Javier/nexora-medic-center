# Clinicapharma - Roadmap SAR Honduras

Ultima revision: 2026-06-23

Este documento deja el criterio de cumplimiento SAR para Clinicapharma. No sustituye revision de contador, asesor fiscal o SAR; antes de emitir facturas reales en produccion, la configuracion debe validarse con el obligado tributario y su contador.

## Fuentes revisadas

- SAR Honduras, Facturacion: https://www.sar.gob.hn/facturacion/
- SAR Honduras, leyes de facturacion: https://www.sar.gob.hn/download-category/leyes-de-facturacion/
- SAR Honduras, preguntas frecuentes de facturacion: https://www.sar.gob.hn/faqs/preguntasfrecuentesfacturacion/
- SAR Honduras, Nueva Oficina Virtual: https://www.sar.gob.hn/ovi/
- SAR Honduras, notificacion de documentos fiscales vencidos y no utilizados: https://www.sar.gob.hn/helpie_faq/como-notificar-los-documentos-fiscales-vencidos-y-no-utilizados/
- SAR Honduras, validador de documentos fiscales: https://www.sar.gob.hn/helpie_faq/como-verificar-si-un-documento-fiscal-es-valido/

## Decision de producto

SAR pasa de "futuro opcional" a "bloque de entrega si el cliente va a emitir facturas desde el sistema".

El sistema puede entregarse con recibos internos si el cliente no usara facturacion fiscal el dia 1. Si se activa factura SAR, no basta imprimir CAI en el recibo: el sistema debe controlar autorizaciones, correlativos, documentos fiscales, anulaciones, notas de credito, reimpresiones, reportes y auditoria.

## Estado actual de Clinicapharma

Clinicapharma ya tiene una base util:

- Configuracion de negocio con RTN, CAI, rango, correlativo, punto de emision, fecha limite y pie de factura.
- Recibos clinicos y ventas de farmacia con `document_type` recibo/factura.
- Impresion de lineas fiscales cuando el negocio lo configura.
- Auditoria general para cambios sensibles.

Brecha critica:

- No existe tabla de autorizaciones SAR versionadas.
- No existe documento fiscal persistido separado del recibo/venta.
- No se consume correlativo de forma atomica.
- No se bloquea emision por CAI vencido, rango agotado o datos incompletos.
- No hay reimpresion idempotente de la misma factura fiscal.
- No hay anulacion fiscal con motivo y estado.
- No hay nota de credito vinculada a factura.
- No hay reporte SAR/fiscal por rango, autorizacion, documento, estado y correlativo.
- No hay flujo de notificacion de documentos fiscales no usados.

Veredicto readiness: rojo para facturacion SAR completa; verde para recibos internos operativos.

## Comparacion con ComandaPro

ComandaPro ya documenta e implementa una linea SAR mas madura:

- `sar_authorizations` para CAI, rango autorizado, correlativo actual, fecha limite y estado.
- `fiscal_documents` para documento fiscal persistente y separado del pedido/venta.
- `fiscal_document_events` para emision, anulacion, reimpresion y nota de credito.
- Emision idempotente: si una orden ya tiene factura, se devuelve la misma.
- Bloqueo cuando SAR esta desactivado, CAI vencido o rango agotado.
- Anulacion con motivo y reporte fiscal.
- Nota de credito vinculada al documento original.

Clinicapharma debe adaptar ese enfoque a dos origenes: `clinic_receipts` y `pharmacy_sales`.

## Alcance minimo obligatorio

### 1. Configuracion SAR

- Registrar una o varias autorizaciones SAR.
- Guardar CAI, tipo de documento, establecimiento, punto de emision, rango inicial, rango final, correlativo actual, fecha limite y estado.
- Marcar una autorizacion activa por tipo de documento y punto de emision.
- Bloquear cambios directos del correlativo sin permiso admin y auditoria.
- Alertar CAI por vencer y rango por agotarse.

### 2. Emision fiscal

- Emitir factura fiscal solo si existe autorizacion activa, vigente y con rango disponible.
- Consumir correlativo de forma transaccional.
- Persistir el documento fiscal con numero completo, CAI, rango, fecha limite, subtotal, descuento, impuesto, total, cliente, RTN si aplica, fuente y usuario.
- Separar recibo interno de factura fiscal.
- Permitir reimpresion sin consumir otro correlativo.
- Bloquear factura si la venta/recibo ya tiene documento fiscal activo.

### 3. Documentos complementarios

- Crear nota de credito vinculada a una factura existente.
- Registrar motivo, monto, usuario, fecha y estado.
- No borrar la factura original; se conserva historial y estado.

### 4. Anulacion y documentos no usados

- Anular documento fiscal con motivo obligatorio y usuario autorizado.
- Mantener registro cronologico del documento anulado.
- Reportar correlativos no usados por autorizacion para apoyar la notificacion en Oficina Virtual cuando aplique.

### 5. Reportes y evidencia

- Reporte fiscal por rango de fechas, tipo de documento, autorizacion, estado y fuente clinica/farmacia.
- Totales por documento, anulados, notas de credito, descuentos e impuestos.
- Exportacion CSV/PDF.
- Auditoria de configuracion, emision, anulacion, reimpresion y nota de credito.

## Modelo de datos propuesto

### `sar_authorizations`

- `id`
- `document_type`: invoice, credit_note, debit_note u otro autorizado
- `cai`
- `establishment_code`
- `emission_point`
- `range_start`
- `range_end`
- `current_number`
- `limit_date`
- `status`: active, exhausted, expired, inactive
- `notes`
- `created_at`, `updated_at`

### `fiscal_documents`

- `id`
- `authorization_id`
- `source_module`: clinic, pharmacy
- `source_id`: id de `clinic_receipts` o `pharmacy_sales`
- `document_type`
- `fiscal_number`
- `cai`
- `range_start`, `range_end`, `limit_date`
- `customer_name`, `customer_rtn`
- `subtotal`, `discount`, `tax_amount`, `total`
- `status`: issued, voided, credited
- `issued_by`, `issued_at`
- `voided_by`, `voided_at`, `void_reason`
- `original_document_id` para notas de credito

### `fiscal_document_events`

- `id`
- `fiscal_document_id`
- `event_type`: issued, reprinted, voided, credit_note_issued, corrected
- `actor_user_id`, `actor_username`
- `reason`
- `metadata`
- `created_at`

## API propuesta

- `GET /sar/authorizations`: lista autorizaciones.
- `POST /sar/authorizations`: crea autorizacion.
- `PATCH /sar/authorizations/{id}`: actualiza estado/notas, no correlativo sin permiso especial.
- `POST /sar/documents/issue`: emite factura desde recibo clinico o venta farmacia.
- `GET /sar/documents`: lista documentos fiscales.
- `GET /sar/documents/{id}/text`: texto fiscal para imprimir/reimprimir.
- `POST /sar/documents/{id}/void`: anula con motivo.
- `POST /sar/documents/{id}/credit-notes`: crea nota de credito.
- `GET /sar/reports/fiscal`: reporte fiscal por rango.
- `GET /sar/reports/unused`: correlativos disponibles/no usados por autorizacion.

## Flujo operativo recomendado

1. Admin registra datos del negocio y RTN.
2. Admin registra autorizacion SAR con CAI, rango y fecha limite.
3. Caja vende en farmacia o cobra en clinica.
4. Si el cliente pide factura, caja selecciona "Emitir factura SAR".
5. Backend valida autorizacion activa, rango y fecha limite.
6. Backend consume correlativo y crea `fiscal_documents`.
7. UI imprime factura con datos fiscales.
8. Si se reimprime, se usa el mismo documento fiscal.
9. Si hay error, usuario autorizado anula con motivo o emite nota de credito segun corresponda.
10. Admin revisa reporte fiscal y correlativos pendientes.

## Criterios de aceptacion

- No se puede emitir factura si CAI esta vencido, incompleto o agotado.
- Dos usuarios no pueden recibir el mismo correlativo.
- Reimprimir no consume correlativo nuevo.
- Anular exige motivo y deja auditoria.
- Nota de credito exige factura original.
- Reporte fiscal cuadra con ventas/recibos fuente.
- Backup/restore conserva autorizaciones, documentos fiscales y eventos.
- UI muestra alertas de CAI por vencer y rango bajo.

## Plan por fases

### SAR 1 - Base segura

- Crear tablas y endpoints de autorizaciones.
- Validar rango, fecha limite y formato de correlativo.
- Alertas de CAI vencido, por vencer y rango bajo.
- Tests unitarios de incremento y rango.

### SAR 2 - Emision

- Emitir factura desde farmacia y clinica.
- Persistir documento fiscal.
- Consumir correlativo en transaccion.
- Reimpresion idempotente.
- Tests de concurrencia funcional y doble emision.

### SAR 3 - Anulacion y notas

- Anular con motivo.
- Crear nota de credito vinculada.
- Auditoria y eventos fiscales.
- Reporte de documentos anulados/acreditados.

### SAR 4 - Reportes y entrega

- Reporte fiscal exportable.
- Correlativos no usados.
- Manual operativo SAR para cliente.
- Checklist final con contador/cliente antes de activar facturas reales.

## Checklist antes de activar factura real

- [ ] RTN, razon social y direccion confirmados por cliente.
- [ ] CAI y rango copiados desde autorizacion oficial.
- [ ] Fecha limite confirmada.
- [ ] Punto de emision y establecimiento confirmados.
- [ ] Impresora y formato probados con factura de prueba.
- [ ] Contador valida campos impresos y reporte.
- [ ] Backup probado despues de emitir documento fiscal de prueba.
- [ ] Usuario admin entiende anulacion, nota de credito y reimpresion.
- [ ] Facturacion en produccion se activa solo despues de firma/aprobacion operativa.
