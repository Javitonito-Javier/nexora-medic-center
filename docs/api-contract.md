# Clinicapharma - API Contract

Ultima revision: 2026-06-24

Base URL local: `http://127.0.0.1:8000/api/v1`

La API requiere `Authorization: Bearer <token>` salvo login, licencia, health y `GET /business/settings`.

## Sistema

- `GET /health`: estado simple del backend.

## Auth

- `POST /auth/login`: inicia sesion con usuario y password; devuelve token y datos de usuario.

## Auditoria

- `GET /audit/`: lista eventos de auditoria; filtros opcionales `module`, `entity_type`, `entity_id` y `limit`. La UI admin consume este endpoint para revisar eventos y copiar CSV basico.

Eventos auditados en el primer corte: login exitoso/fallido, pacientes, usuarios, configuracion del negocio, citas, consultas, recetas, recibos clinicos, ventas farmacia, productos de inventario, traslados bodega-tienda y mermas/perdidas.

## Licencia

- `GET /license/status`: obtiene estado de licencia.
- `POST /license/activate`: carga/renueva licencia local.

## Configuracion de negocio

- `GET /business/settings`: obtiene configuracion y branding; publico para pintar login.
- `PUT /business/settings`: actualiza negocio, logo, fiscal, recibos, factura y papel.

## SAR Honduras / facturacion fiscal propuesta

Estado: pendiente de implementar. El alcance completo esta en `sar-compliance-roadmap.md`.

- `GET /sar/authorizations`: lista autorizaciones SAR.
- `POST /sar/authorizations`: crea autorizacion con CAI, rango, correlativo, punto de emision y fecha limite.
- `PATCH /sar/authorizations/{authorization_id}`: actualiza estado/notas de una autorizacion.
- `POST /sar/documents/issue`: emite documento fiscal desde `clinic_receipts` o `pharmacy_sales`.
- `GET /sar/documents`: lista documentos fiscales por fecha, estado, autorizacion, fuente y tipo.
- `GET /sar/documents/{document_id}/text`: obtiene texto de factura/nota para imprimir o reimprimir sin consumir correlativo.
- `POST /sar/documents/{document_id}/void`: anula documento fiscal con motivo obligatorio.
- `POST /sar/documents/{document_id}/credit-notes`: crea nota de credito vinculada.
- `GET /sar/reports/fiscal`: reporte fiscal por rango.
- `GET /sar/reports/unused`: correlativos no usados por autorizacion.

## Usuarios / personal

- `GET /users/`: lista usuarios; filtros por area/rol/turno segun ruta.
- `POST /users/`: crea usuario.
- `PATCH /users/{staff_user_id}`: actualiza usuario, roles, permisos, password, turno o estado.

## Pacientes

- `GET /patients/?q=`: lista/busca pacientes.
- `POST /patients/`: crea paciente.
- `GET /patients/{patient_id}`: obtiene paciente.
- `PATCH /patients/{patient_id}`: actualiza paciente.

## Adjuntos de expediente

- `GET /patients/{patient_id}/attachments`: lista adjuntos activos del expediente.
- `POST /patients/{patient_id}/attachments`: sube archivo multipart con `category`, `description` y `file`. Acepta PDF, JPG, PNG y WEBP hasta el maximo configurado.
- `GET /patients/{patient_id}/attachments/{attachment_id}/download`: descarga archivo autenticado.
- `DELETE /patients/{patient_id}/attachments/{attachment_id}`: elimina adjunto de forma logica y registra auditoria.

## Citas

- `GET /appointments/`: lista citas por fecha/estado cuando aplique.
- `POST /appointments/`: crea cita.
- `PATCH /appointments/{appointment_id}`: actualiza cita o estado.

## Consultas

- `GET /consultations/?patient_id=`: lista consultas; soporta historial global por paciente e incluye especialidad, referencia/interconsulta, seguimiento y bandera de receta.
- `POST /consultations/`: crea consulta clinica con doctor, especialidad, referencia/interconsulta, signos vitales, diagnostico, tratamiento y seguimiento.

## Recetas

- `GET /prescriptions/?patient_id=`: lista recetas, incluyendo especialidad del doctor y `consultation_id` cuando aplica.
- `POST /prescriptions/`: crea receta con items; si se envia `consultation_id`, queda vinculada a esa consulta y marca la consulta con receta.

## Recibos clinicos

- `GET /receipts/clinic`: lista recibos clinicos.
- `POST /receipts/clinic`: crea recibo de consulta/servicio.
- `GET /receipts/clinic/{receipt_id}/text`: obtiene version texto para copiar/imprimir.

## Farmacia

- `GET /pharmacy/sales`: lista ventas.
- `POST /pharmacy/sales`: crea venta, descuenta inventario vigente por FEFO/FIFO, bloquea lotes vencidos, registra lotes, puntos y totales.
- `GET /pharmacy/sales/{sale_id}`: obtiene venta.
- `GET /pharmacy/sales/{sale_id}/receipt`: obtiene recibo texto.

## Inventario

- `GET /inventory/products?q=`: lista/busca productos.
- `POST /inventory/products`: crea producto con presentaciones, lote inicial y precios por lote.
- `GET /inventory/movements`: lista movimientos.
- `GET /inventory/pick-list`: sugerencias para surtir tienda desde bodega con lotes vigentes.
- `GET /inventory/alerts/expiring-lots`: lotes vigentes por vencer; query `days` entre 1 y 365.
- `GET /inventory/alerts/stagnant-lots`: lotes estancados.
- `PATCH /inventory/lots/{lot_id}/transfer-to-store`: mueve unidades de bodega a tienda.
- `PATCH /inventory/lots/{lot_id}/loss`: registra merma o perdida por lote.
- `PATCH /inventory/lots/expired/retire`: registra merma masiva para toda existencia vencida en tienda y bodega. Payload: `reason`, `note`. Respuesta: lotes retirados, unidades tienda, unidades bodega y total.

## Puntos

- `GET /points/`: listado de pacientes/clientes con puntos.
- `GET /points/movements`: movimientos de puntos.

## Cajas

- `GET /cash-registers/`: estado general.
- `GET /cash-registers/sessions`: lista sesiones de caja; filtros opcionales `module`, `status` y `cashier_name`.
- `POST /cash-registers/sessions/open`: abre caja por modulo y cajero con monto inicial.
- `POST /cash-registers/sessions/{session_id}/close`: cierra caja, calcula esperado/contado/diferencia y exige nota si hay diferencia.
- `GET /cash-registers/pharmacy/summary`: resumen de caja farmacia.
- `GET /cash-registers/clinic/summary`: resumen de caja clinica.

## Dashboard y reportes

- `GET /dashboard/`: ping/resumen simple.
- `GET /dashboard/summary`: metricas, alertas y datos para dashboard.
- `GET /reports/`: indice de reportes disponibles.
- `GET /reports/summary`: resumen gerencial con las mismas metricas, alertas y graficos operativos usados por dashboard.
- `GET /reports/sales`: ventas/cobros agrupados por dia o mes, modulo, cajero, metodo de pago y tipo de documento. Query opcional: `date_from`, `date_to`, `group_by=day|month`.
- `GET /reports/clinic-receipts`: recibos clinicos agrupados por dia o mes, doctor, servicio, cajero, metodo de pago y tipo de documento. Query opcional: `date_from`, `date_to`, `group_by=day|month`.
- `GET /reports/profit-by-lot`: utilidad farmacia por producto y lote usando asignaciones reales de venta. Query opcional: `date_from`, `date_to`.
- `GET /reports/inventory/low-stock`: productos activos con stock de tienda igual o menor al minimo, incluyendo existencia en bodega.
- `GET /reports/inventory/expiring-stock`: lotes vigentes con unidades disponibles por vencer. Query `days` entre 1 y 365.
- `GET /reports/points/movements`: movimientos de puntos ganados/redimidos por paciente. Query opcional: `date_from`, `date_to`.
- `GET /reports/pharmacy/top-products`: ranking de productos farmacia por unidades vendidas. Query opcional: `date_from`, `date_to`, `limit`.
- `GET /reports/inventory/stagnant-lots`: lotes en tienda sin movimiento reciente. Query `days` entre 1 y 365.

## Errores comunes

- `401`: token requerido, invalido o expirado.
- `402`: licencia bloquea escrituras.
- `404`: recurso no encontrado.
- `422`: payload invalido.
