# Clinicapharma - Changelog

Formato basado en Keep a Changelog. Este archivo debe actualizarse con cada funcionalidad importante.

## Unreleased

- Corregido: login del admin inicial fallaba con 500 en instalacion limpia porque el permiso `audit` sembrado por `init_db` no estaba en el Literal `StaffModule`; agregado con test de regresion.
- Corregido: `start-local.ps1` y `build-local-release.ps1` ya no abortan por warnings de pip en stderr (PowerShell 5.1 NativeCommandError); ahora validan solo el codigo de salida.
- Validado: smoke test del paquete regenerado sobre base limpia `clinicapharma_smoke`: venv en frio, migraciones, login, reportes avanzados, frontend y fuente Manrope local (ver `beta-deploy-validation.md`).
- Regenerado: paquete `release/clinicapharma-local` con `build-local-release.ps1` incluyendo rediseño de sidebar/tema, fuente Manrope local y reportes avanzados; `API_BASE_URL` compilado a `http://127.0.0.1:8000/api/v1`.
- Mejorado: menu lateral agrupado por secciones (General, Clinica, Farmacia, Administracion) con encabezados, resaltado por barra lateral y logo con marco degradado.
- Mejorado: tema visual con tipografia Manrope empaquetada localmente (sin descarga en runtime, apto offline), color terciario ambar, radios unificados (cards 12px, campos/botones 10px), cards con sombra suave y bordes de campos para estados enabled/disabled/error/focused.
- Corregido: eliminado origen CORS invalido `http://localhost:58461/` de `backend/.env.example`; el regex de `config.py` ya cubre cualquier puerto localhost.
- Agregado: reportes avanzados de ventas/cobros por periodo, modulo, cajero, metodo de pago y documento.
- Agregado: reporte de recibos clinicos por doctor, servicio, cajero y metodo de pago con copia CSV.
- Agregado: exportacion PDF/impresion por seccion en reportes gerenciales.
- Agregado: retiro masivo de lotes vencidos desde Inventario, con movimientos de merma por tienda/bodega y auditoria.
- Agregado: reporte de utilidad real por producto y lote usando asignaciones de venta farmacia.
- Agregado: reportes exportables de stock bajo y vencimientos desde Reportes.
- Agregado: reporte historico de puntos ganados/redimidos por paciente.
- Agregado: reportes de productos top y lotes estancados con copia CSV.
- Mejorado: pantalla Reportes muestra bloques gerenciales avanzados con copia CSV por seccion.
- Pendiente: prueba final del paquete en equipo limpio/VM y validacion con hardware real.
- Mejorado: `roadmap.md` ahora incluye estado de entrega, corte recomendado, backlog ejecutable Beta/Final/SAR, criterios de aceptacion y definicion de terminado.
- Agregado: `build-local-release.ps1`, `start-local.ps1`, `stop-local.ps1` y `health-check.ps1` para paquete local reproducible.
- Agregado: `install-local-services.ps1` y `uninstall-local-services.ps1` para instalar API/frontend como servicios Windows con NSSM.
- Mejorado: `start-local.ps1` e `install-local-services.ps1` bloquean `SECRET_KEY` e `INITIAL_ADMIN_PASSWORD` inseguros antes de arrancar.
- Agregado: `deploy-local.md` con guia de entrega Windows, arranque, parada, verificacion y checklist.
- Agregado: `beta-deploy-validation.md` con resultado de health-check y smoke test del paquete beta local.
- Validado: paquete local arranca API/frontend y permite login, crear paciente y subir adjunto PDF.
- Pendiente: validar servicios Windows en equipo con NSSM instalado.
- Agregado: adjuntos de expediente para PDF/JPG/PNG/WEBP con categorias, descripcion, descarga, borrado logico y auditoria.
- Agregado: tabla `patient_attachments` y almacenamiento local configurable con `ATTACHMENT_STORAGE_DIR`.
- Mejorado: expediente del paciente ahora muestra panel de Adjuntos y evidencias.
- Pendiente: vinculo directo adjunto-venta para descuentos avanzados si el cliente lo pide.
- Agregado: vista admin de Auditoria con filtros por modulo, entidad, id, limite, detalle antes/despues y copia CSV basica.
- Agregado: endpoint `GET /reports/summary` para resumen gerencial reutilizando metricas, alertas y graficos operativos.
- Mejorado: modulo Reportes muestra metricas gerenciales, alertas, graficos, puntos y exportacion CSV basica.
- Mejorado: permisos de personal incluyen modulo `audit` para controlar acceso a Auditoria.
- Agregado: `deploy-readiness-review.md` con estado pre-deploy, validaciones, bloqueantes y ruta recomendada.
- Agregado: migracion Alembic `20260623_current_schema` y registro de modulos recientes en `alembic/env.py`.
- Mejorado: admin inicial configurable por `.env` con `INITIAL_ADMIN_USERNAME` e `INITIAL_ADMIN_PASSWORD`.
- Mejorado: `local_setup.md` documenta `alembic upgrade head` y build web con `API_BASE_URL`.
- Limpieza: `docs/manual_screenshots/chrome-profile/**` sale del indice de Git y queda ignorado.
- Agregado: `sar-compliance-roadmap.md` con brecha, fuentes SAR Honduras, comparacion con ComandaPro, fases y checklist antes de activar factura real.
- Mejorado: requirements, roadmap, API, schema, flujos y guia operativa elevan SAR a bloque obligatorio si el cliente emitira facturas desde el sistema.
- Agregado: `operational-guide.md` adaptado desde aprendizajes de ComandaPro para capacitacion, soporte y flujo operativo de Clinicapharma.
- Agregado: endpoint `GET /inventory/alerts/expiring-lots` para consultar lotes vigentes por vencer por rango de dias.
- Agregado: panel en Inventario para ver lotes por vencer a 30/60/90 dias con ubicacion y stock tienda/bodega.
- Agregado: investigacion `pos-inventory-research.md` comparando POS/inventario con Square, Shopify, Odoo y POS de farmacia.
- Corregido: POS farmacia ahora bloquea lotes vencidos y no los usa para precio, FEFO/FIFO ni venta por scanner.
- Mejorado: lista de traslado bodega-tienda no recomienda lotes vencidos.
- Agregado: cierre de caja formal por modulo/cajero con apertura, monto inicial, cierre, conteo por metodo, esperado, diferencia, nota obligatoria y auditoria.
- Agregado: UI de Cajas para abrir/cerrar sesiones y consultar sesiones recientes.
- Agregado: scripts de backup/restauracion local de PostgreSQL con formato `.dump`, verificacion SHA256 y confirmacion explicita para restaurar.
- Agregado: guia `backup-restore.md` con pasos de respaldo, restauracion y rutina recomendada para cliente.
- Validado: backup real de `clinicapharma` y restauracion en base temporal `clinicapharma_restore_test`; base temporal eliminada al finalizar.
- Agregado: modulo backend de auditoria formal con tabla `audit_events`, endpoint `GET /audit/` y registro de eventos sensibles iniciales.
- Agregado: auditoria para login exitoso/fallido, pacientes, usuarios, configuracion, citas, consultas, recetas, recibos clinicos, ventas farmacia e inventario.
- Agregado: agenda de citas con panel de alertas activas desde 3 dias antes, contadores de hoy/vencidas/proximas 72 horas y permanencia hasta atendida o cancelada.
- Agregado: accion de WhatsApp en citas con mensaje prellenado para recordar fecha, hora y doctor asignado.
- Agregado: numero `+50492398074` como destinatario de recordatorios de WhatsApp en citas.
- Agregado: generador de manual paso a paso por vista con capturas del sistema y exportacion a PDF.
- Agregado: expediente clinico global por paciente con especialidad del doctor, referencia/interconsulta, seguimiento y recetas vinculadas a la consulta.
- Mejorado: inventario muestra guias visibles para frascos/insumos individuales, precio por unidad base y resumen calculado de stock bodega + tienda antes de guardar.
- Mejorado: al crear una receta desde una consulta, el backend marca la consulta como con receta y el expediente la muestra dentro del evento clinico.
- Mejorado: inventario inicia el alta de producto con flujo individual/frasco/insumo y explica stock/precios en unidad base para reducir confusion.
- Mejorado: inventario ahora usa asistente de 3 modulos para producto, venta/precios y lote/stock con resumen antes de guardar.
- Mejorado: inventario evita enviar presentaciones de caja con precio 0 cuando el producto se registra como venta individual.
- Mejorado: POS farmacia con pasos operativos visibles, cabecera responsive, limpieza rapida de busqueda y resumen subtotal/descuento/total dentro del carrito.
- Mejorado: POS farmacia valida descuento/referencia de pago antes de cobrar, permite limpiar la venta en curso y muestra efectivo recibido/cambio para pagos en efectivo.
- Mejorado: POS farmacia con header mas compacto, pasos numerados, tarjetas de producto mas densas, chips de venta rapida, estados de cliente/descuento/pago y total/cobro mas protagonista.
- Corregido: POS farmacia habilita tercera/cuarta edad segun elegibilidad del paciente y calcula descuentos usando precio de venta/vineta del lote activo.
- Corregido: botones de recibo en farmacia y clinica ahora validan la copia al portapapeles y no muestran exito falso si el navegador bloquea la accion.

## 2026-06-12 - MVP local en progreso

### Added

- Documentacion viva en `docs/`: overview, requirements, UI, schema, API, reglas, roadmap y changelog.
- Tema global Flutter claro/oscuro con celadon y azul medico.
- Configuracion de negocio con nombre, logo, fiscal opcional y papel termico.
- POS farmacia redisenado con busqueda, carrito, cliente, descuentos, pagos y ventas recientes.
- Inventario con lotes, presentaciones, precios por lote, bodega/tienda, traslados, mermas y alertas.
- Recetas con via de administracion e impresion/exportacion inicial.
- Dashboard con metricas de clinica/farmacia, alertas y graficos.
- Licencia local offline con firma Ed25519.

### Changed

- El branding puede cargarse antes del login mediante `GET /business/settings`.
- El flujo de farmacia prioriza recibo interno; factura queda opcional por configuracion.
- La documentacion nueva reemplaza a `database_draft.md` como fuente actual del esquema.

### Known gaps

- Adjuntos reales para foto/DNI/receta ya existen en expediente; falta vinculo directo adjunto-venta si se requiere control mas fino.
- Auditoria general ya tiene backend y vista frontend; faltan eventos finos para flujos futuros de anulacion, reimpresion y notas fiscales.
- No hay cierre de caja completo por usuario finalizado.
- Manuales PDF existen, pero deben regenerarse cuando se cierre el MVP.
