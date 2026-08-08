# Clinicapharma - Project Overview

Ultima revision: 2026-06-23

## Proposito

Clinicapharma es una web app local para una clinica medica con farmacia integrada. El sistema busca cubrir el flujo diario: pacientes, citas, consulta medica, recetas, cobros de clinica, farmacia POS, inventario por lotes, puntos, reportes, configuracion de negocio, recibos e impresion.

Debe servir tanto para negocios pequenos, donde una persona puede hacer varios roles, como para operaciones con recepcionista, enfermero, doctor, cajero de farmacia y administrador.

## Stack actual

- Frontend: Flutter Web.
- Estado: Riverpod.
- Routing: GoRouter.
- Persistencia ligera frontend: SharedPreferences.
- Backend: FastAPI.
- Base de datos: PostgreSQL.
- ORM: SQLAlchemy 2.
- Tests backend: pytest + httpx.
- Lint backend: Ruff.
- Autenticacion: JWT simple con middleware global.
- Licencia local: firma Ed25519 opcional.

## Estructura principal

- `frontend/lib/core`: tema, layout, configuracion API y widgets compartidos.
- `frontend/lib/features`: pantallas y APIs por modulo.
- `backend/app/api/routes`: endpoints FastAPI por modulo.
- `backend/app/modules`: modelos, schemas y servicios por dominio.
- `backend/app/db`: sesion e inicializacion de base de datos.
- `docs`: documentacion de continuidad, manuales y capturas.
- `scripts`: herramientas auxiliares, incluyendo licencias.
- `release/clinicapharma-local`: paquete local generado para entrega; no debe versionarse si contiene `.env` o datos.

## Modulos implementados en el MVP actual

- Login y sesion.
- Usuarios/personal con roles, permisos por modulo y turno activo.
- Dashboard operativo con metricas, alertas y graficos.
- Pacientes/clientes con busqueda y expediente.
- Adjuntos de expediente para DNI, recetas externas, estudios, consentimientos y evidencia de descuentos.
- Citas.
- Consultas medicas con signos vitales, especialidad, referencia/interconsulta, historia clinica, diagnostico, tratamiento, seguimiento y proxima cita.
- Recetas con items, dosis, via de administracion, intervalo/frecuencia, impresion/exportacion y enlace opcional a la consulta del expediente.
- Caja clinica con recibos.
- Cajas formales por modulo/cajero con apertura, cierre, conteo, diferencia y auditoria.
- Farmacia POS con busqueda, carrito, cliente, descuentos, pagos, recibos y bloqueo de lotes vencidos.
- Inventario con productos, presentaciones, lotes, costos, vencimientos, bodega, tienda, traslados, mermas y movimientos.
- Puntos de farmacia.
- Reportes iniciales con resumen gerencial, alertas, puntos y CSV basico.
- Configuracion de negocio, logo, recibos, factura opcional y papel termico.
- Licencia local opcional.
- Auditoria para acciones sensibles con vista admin, filtros y CSV basico.

## Estado general

El proyecto esta en MVP funcional local y beta local controlada sin factura SAR real. Ya tiene flujo completo basico entre frontend, backend y PostgreSQL, paquete local reproducible, scripts de arranque/parada/health-check y scripts para servicios Windows con NSSM. Aun faltan endurecimientos de producto final: prueba en equipo limpio, validacion de servicios tras reinicio, pruebas end-to-end con usuarios reales, validacion completa de impresoras reales, reportes avanzados/PDF, vinculo adjunto-venta para descuentos avanzados y SAR completo si el cliente emitira factura real.

## Documentos fuente

- `requirements.md` es la fuente principal de verdad funcional.
- `module-flows.md` documenta cada modulo, funcion, flujo, datos minimos, reglas y criterios de aceptacion.
- `operational-guide.md` explica el por que y el flujo de uso de cada modulo para entrega, capacitacion y soporte.
- `database-schema.md` describe el esquema real de modelos SQLAlchemy.
- `api-contract.md` lista los endpoints reales del backend.
- `roadmap.md` marca completado/parcial/pendiente.
- `functional-gap-audit.md` compara el MVP contra sistemas de clinica/EHR y prioriza brechas.
- `backup-restore.md` describe respaldo y restauracion local de PostgreSQL.
- `deploy-local.md` describe paquete local, arranque, parada y verificacion.
- `pos-inventory-research.md` compara POS/inventario con referencias externas y registra decisiones de farmacia.
- `sar-compliance-roadmap.md` define brecha, alcance, fases y checklist SAR Honduras para facturacion fiscal completa.
- Los archivos antiguos `project_notes.md`, `mvp.md` y `database_draft.md` quedan como referencia historica.
