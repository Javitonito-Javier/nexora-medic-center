# Clinicapharma - Roadmap de entrega

Ultima revision: 2026-06-24

Este roadmap es la guia viva para llevar Clinicapharma a entrega local. Si cambia una funcion, pantalla, endpoint, tabla, flujo operativo o regla de negocio, este archivo debe actualizarse en el mismo cambio.

Documentos que siempre deben moverse juntos:

- `requirements.md`: fuente principal de verdad funcional.
- `module-flows.md`: flujo detallado por modulo y funcion.
- `operational-guide.md`: guia tutorial del por que y como se usa cada modulo.
- `api-contract.md`: endpoints reales.
- `database-schema.md`: tablas/modelos reales.
- `pos-inventory-research.md`: comparacion web y decisiones POS/inventario.
- `sar-compliance-roadmap.md`: brecha, alcance y plan SAR Honduras.
- `roadmap.md`: estado y prioridades.
- `changelog.md`: resumen de cambios importantes.

## Estado de producto

Clinicapharma esta en MVP funcional local para una clinica medica con farmacia integrada. Cubre el ciclo principal: usuario entra, recepcion registra paciente, agenda cita, doctor atiende, receta queda vinculada, clinica cobra, farmacia vende, inventario descuenta, puntos se calculan, caja revisa, admin consulta reportes y configura negocio.

## Estado de entrega 2026-06-24

- Beta local controlada sin factura SAR real: 93%.
- Entrega local final sin factura SAR real: 84%.
- Entrega con factura SAR real completa: 62%.
- Ultimo checkpoint local: `e8cf2a5 Add expired lot bulk retirement`.
- Estado Git: commit local listo, sin `git push` por instruccion del cliente.
- Paquete local generado: `release/clinicapharma-local` (no versionado).
- Validaciones tecnicas: backend lint OK, backend tests OK, frontend analyze OK, build web OK, paquete local OK.
- Validaciones funcionales del paquete: health-check, login admin, crear paciente y subir adjunto PDF OK.

## Corte actual recomendado

El corte recomendado para entrega inmediata es **Beta local controlada sin factura SAR real**.

Alcance permitido:

- Operar pacientes, citas, consultas, recetas, recibos internos, farmacia POS, inventario, adjuntos, caja, auditoria, reportes iniciales y backup.
- Usar configuracion fiscal solo como datos informativos del negocio.
- No emitir factura SAR real desde el sistema hasta completar Sprint SAR.

Condiciones antes de dejarlo en uso diario:

- Validar paquete en PC limpia o VM.
- Validar servicios Windows con NSSM o tarea programada.
- Probar impresora real.
- Ejecutar flujo completo con usuarios reales.
- Confirmar por escrito si la beta opera solo con recibos internos.

## Completado en MVP actual

- [x] Estructura FastAPI + Flutter Web.
- [x] PostgreSQL local con inicializacion automatica.
- [x] Login JWT.
- [x] Usuarios con roles, permisos por modulo y turno activo.
- [x] Layout con menu lateral, dashboard y tema claro/oscuro.
- [x] Branding basico: nombre, logo y configuracion del negocio.
- [x] Pacientes/clientes con busqueda y expediente.
- [x] Citas y agenda.
- [x] Agenda con alertas desde 3 dias antes.
- [x] Citas visibles hasta atendida o cancelada.
- [x] Mensaje de WhatsApp prellenado para recordatorio.
- [x] Consultas con signos vitales, historia clinica, diagnostico y tratamiento.
- [x] Preconsulta flexible por enfermero o doctor.
- [x] Expediente clinico global por paciente.
- [x] Interconsulta/referencia entre doctores o especialidades.
- [x] Recetas vinculables a consulta.
- [x] Recetas con via, dosis, frecuencia/intervalo, duracion e instrucciones.
- [x] Impresion/exportacion inicial de recetas y recibos.
- [x] Recibos clinicos con efectivo, tarjeta y transferencia.
- [x] POS farmacia con busqueda, carrito, cliente, descuentos, pagos y recibo.
- [x] Transferencias con banco y referencia.
- [x] Lista de bancos de Honduras en UI.
- [x] Inventario por producto, presentacion, lote, costo, vencimiento, bodega y tienda.
- [x] Alta guiada de inventario por tipo de producto.
- [x] Soporte para frascos, insumos, pastillas, blisters, cajas, guantes y unidades.
- [x] Traslado bodega a tienda.
- [x] Merma/perdida por lote.
- [x] Venta con descuento por FEFO/FIFO.
- [x] POS bloquea lotes vencidos y no los usa para precio/descuento de stock.
- [x] Trazabilidad por lote en venta farmacia.
- [x] Descuento de tercera/cuarta edad desde precio de vineta.
- [x] Puntos de farmacia.
- [x] Dashboard con metricas, alertas y graficos.
- [x] Reportes iniciales con resumen gerencial, alertas y exportacion CSV basica.
- [x] Reportes avanzados: ventas/cobros por periodo, cajero, metodo y documento.
- [x] Reportes avanzados: recibos clinicos por doctor, servicio, cajero y metodo de pago.
- [x] Reportes avanzados: utilidad real por producto y lote.
- [x] Reportes avanzados: stock bajo y vencimientos exportables.
- [x] Reportes avanzados: puntos ganados/redimidos con detalle historico.
- [x] Reportes avanzados: productos top y productos estancados.
- [x] Adjuntos en expediente para DNI, recetas externas, estudios y evidencia de descuentos.
- [x] Configuracion fiscal opcional.
- [x] Licencia local opcional.
- [x] Manuales PDF/capturas iniciales.
- [x] Documentacion base: requirements, API, schema, roadmap, overview y reglas.
- [x] Guia operativa viva para capacitacion y soporte.
- [x] Audit comparativo de brechas: `functional-gap-audit.md`.
- [x] Limpieza de perfiles temporales de navegador en `docs/manual_screenshots`.
- [x] Vista admin de auditoria con filtros y exportacion CSV basica.

## Prioridad antes de entrega local

Orden recomendado para cerrar con confianza:

1. Prueba integral en equipo limpio o VM.
2. Instalar servicios Windows y validar arranque despues de reinicio.
3. Validar impresora real y formato de recibos.
4. Probar backup/restore local en equipo limpio.
5. Validar flujo completo con usuario real de recepcion, doctor, farmacia, caja y admin.
6. Definir si el cliente emitira factura SAR desde el sistema en dia 1.
7. Si factura SAR va activa, completar SAR 1 y SAR 2 antes de entrega.
8. Ampliar auditoria formal para anulaciones/reimpresiones cuando esos flujos queden activos.
9. Reportes gerenciales avanzados de utilidad por lote, inventario, vencimientos y puntos.

## Backlog ejecutable para cerrar Beta 100%

Capacidad sugerida: ejecutar en un sprint corto de estabilizacion. Prioridad Critical/High se debe cerrar antes de entregar beta diaria.

| ID | Prioridad | Puntos | Historia | Criterios de aceptacion |
| --- | --- | ---: | --- | --- |
| BETA-01 | Critical | 5 | Como tecnico, quiero probar el paquete en una PC limpia o VM para confirmar que la entrega no depende del entorno de desarrollo. | Dado un Windows limpio, cuando se configura `.env` y PostgreSQL, entonces `start-local.ps1` arranca API/frontend; `health-check.ps1` pasa; login admin funciona; Alembic aplica migraciones. |
| BETA-02 | Critical | 3 | Como administrador, quiero que Clinicapharma arranque solo al reiniciar el servidor para no depender de consola manual. | Dado NSSM instalado, cuando se ejecuta `install-local-services.ps1`, entonces existen `ClinicapharmaAPI` y `ClinicapharmaWeb`; despues de reiniciar ambos quedan activos; health-check pasa. |
| BETA-03 | High | 3 | Como cajero, quiero imprimir recibos reales para confirmar que el formato funciona en hardware del cliente. | Dado una impresora 58mm/80mm, cuando se imprime recibo clinico y farmacia, entonces el texto cabe, no corta campos criticos y muestra negocio, fecha, paciente/cliente, total y metodo de pago. |
| BETA-04 | High | 5 | Como equipo operativo, quiero validar el flujo completo para asegurar que los roles entienden el sistema. | Dado usuarios de prueba por rol, cuando se ejecuta paciente -> cita -> consulta -> receta -> cobro -> venta farmacia -> inventario -> adjunto -> caja -> reporte -> auditoria, entonces cada paso queda registrado y sin errores bloqueantes. |
| BETA-05 | Critical | 3 | Como responsable de datos, quiero backup/restore probado en el equipo destino para poder recuperar la operacion. | Dado datos de prueba, cuando se ejecuta backup y restore en base limpia, entonces login y datos principales se recuperan; se genera `.sha256`; adjuntos se respaldan aparte. |
| BETA-06 | High | 2 | Como administrador, quiero claves iniciales seguras para evitar entregar credenciales por defecto. | Dado `.env` de entrega, cuando `SECRET_KEY` o `INITIAL_ADMIN_PASSWORD` tienen valores de ejemplo, entonces el arranque se bloquea; con valores seguros el sistema inicia. |
| BETA-07 | High | 3 | Como cliente, quiero confirmar el modo fiscal de beta para no usar facturas SAR incompletas. | Dado la decision fiscal, cuando SAR no esta listo, entonces la beta queda documentada como recibos internos; si SAR se requiere, el Sprint SAR pasa a Critical antes de produccion. |

## Backlog para entrega final sin SAR

| ID | Prioridad | Puntos | Historia | Criterios de aceptacion |
| --- | --- | ---: | --- | --- |
| FINAL-01 | Done | 5 | Como administrador, quiero reportes diarios completos para cerrar ventas y caja con confianza. | Ventas por dia, usuario, modulo y metodo de pago; exportacion CSV; totales coinciden con ventas/recibos. |
| FINAL-02 | Done | 5 | Como administrador de farmacia, quiero utilidad por producto/lote para saber ganancia real. | Reporte muestra costo, precio, cantidad vendida, utilidad bruta y filtro por fecha/lote. |
| FINAL-03 | Done | 3 | Como encargado de inventario, quiero exportar vencimientos y stock bajo para planificar compras/retiros. | Exporta CSV de vencimientos por rango y stock bajo por bodega/tienda. |
| FINAL-04 | Medium | 3 | Como administrador, quiero auditoria de anulaciones/reimpresiones si se habilitan esos flujos. | Toda anulacion/reimpresion guarda usuario, fecha, motivo, documento y antes/despues cuando aplique. |
| FINAL-05 | Medium | 5 | Como tecnico, quiero refactorizar pantallas grandes para reducir riesgo de cambios de UI. | Farmacia/inventario se separan en componentes sin cambiar comportamiento; `flutter analyze` sigue OK. |
| FINAL-06 | Medium | 3 | Como cliente, quiero manual final actualizado con capturas despues de cerrar beta. | Manual refleja pantallas finales y flujo de entrega; capturas no incluyen datos sensibles reales. |

## Backlog SAR si factura real entra en alcance

| ID | Prioridad | Puntos | Historia | Criterios de aceptacion |
| --- | --- | ---: | --- | --- |
| SAR-01 | Critical | 8 | Como administrador fiscal, quiero registrar autorizaciones CAI para emitir documentos controlados. | Tabla/endpoints de autorizaciones; rango, fecha limite, establecimiento, punto de emision, tipo documento y estado. |
| SAR-02 | Critical | 8 | Como cajero, quiero emitir factura fiscal desde clinica y farmacia consumiendo correlativo seguro. | Factura se genera en transaccion; bloquea CAI vencido/agotado/incompleto; recibo interno no consume correlativo. |
| SAR-03 | Critical | 5 | Como administrador, quiero reimprimir sin consumir correlativo nuevo. | Reimpresion mantiene numero original, registra evento de auditoria y no crea documento fiscal adicional. |
| SAR-04 | Critical | 5 | Como administrador autorizado, quiero anular factura con motivo. | Anulacion requiere permiso, motivo, auditoria y estado fiscal; no borra documento original. |
| SAR-05 | Critical | 5 | Como administrador fiscal, quiero notas de credito vinculadas a factura. | Nota de credito referencia factura original, ajusta totales segun regla definida y queda auditada. |
| SAR-06 | High | 3 | Como contador, quiero reporte de correlativos usados/no usados. | Reporte permite revisar emitidos, anulados, disponibles y no usados para apoyo de Oficina Virtual. |

## Definicion de terminado para cualquier historia

- Codigo implementado y revisado contra patrones existentes.
- `requirements.md` actualizado si cambia regla de negocio.
- `module-flows.md` actualizado si cambia pantalla, flujo o validacion.
- `api-contract.md` actualizado si cambia endpoint/payload/respuesta.
- `database-schema.md` actualizado si cambia modelo, tabla o campo.
- `roadmap.md` actualizado con estado real.
- `changelog.md` actualizado si el cambio afecta entrega o usuario.
- Tests automatizados o validacion manual documentada.
- Sin secretos reales en Git.
- Sin `git push` hasta autorizacion explicita del cliente.

## Sprint 1 - Control y trazabilidad

- [x] Crear tabla de auditoria general.
- [x] Crear endpoint para consultar auditoria con filtros.
- [x] Auditar login fallido/exitoso y cambios de usuarios.
- [x] Auditar pacientes: crear, editar, cambios de identidad/telefono.
- [x] Auditar consultas y recetas: crear.
- [x] Auditar inventario: producto, traslado, merma y venta farmacia.
- [x] Auditar configuracion fiscal y datos del negocio.
- [x] Auditar caja: apertura, cierre y diferencia.
- [x] Mostrar en reportes o vista admin los eventos relevantes.
- [ ] Ampliar auditoria cuando existan flujos de anulacion, reimpresion, cierres completos y ajustes de inventario avanzados.

Minimo de aceptacion:

- Cada accion sensible debe guardar usuario, modulo, accion, entidad, id, fecha, resumen antes/despues cuando aplique y motivo si existe.
- Ningun ajuste de inventario o caja debe quedar sin rastro.

## Sprint 2 - Backup y recuperacion

- [x] Completar script de backup PostgreSQL con nombre por fecha/hora.
- [x] Crear carpeta local recomendada para respaldos.
- [x] Documentar restauracion paso a paso.
- [x] Agregar verificacion basica de archivo generado.
- [x] Agregar SHA256 por backup.
- [x] Crear script de restauracion con confirmacion explicita.
- [x] Probar restauracion en base limpia temporal `clinicapharma_restore_test`.
- [x] Definir rutina diaria/semanal para cliente.

Minimo de aceptacion:

- Un tecnico puede respaldar y restaurar siguiendo `docs/local_setup.md` sin adivinar comandos.
- El sistema restaurado debe permitir login y consulta de datos principales.

## Sprint 3 - Cajas completas

- [x] Apertura de caja por usuario y modulo: clinica/farmacia.
- [x] Monto inicial.
- [x] Cierre con conteo efectivo, tarjeta y transferencia.
- [x] Calculo de esperado vs contado.
- [x] Diferencias y nota obligatoria si no coincide.
- [x] Historial de sesiones por usuario, modulo y estado.
- [x] Auditoria de apertura/cierre.
- [x] UI inicial para abrir/cerrar caja.
- [ ] Control de recibos anulados si se habilita anulacion.
- [ ] Reporte diario avanzado para admin.
- [ ] Validacion operativa con usuario real de caja.

Minimo de aceptacion:

- Recepcion/farmacia puede cerrar el dia sin calculadora externa.
- Admin puede saber quien cobro, cuanto cobro, por que metodo y si hubo diferencia.

## Sprint 4 - Adjuntos y evidencias

- [x] Definir tabla de archivos/adjuntos.
- [x] Adjuntar DNI/receta/evidencia para descuentos de cuarta edad.
- [x] Adjuntar estudios, imagenes o documentos al expediente del paciente.
- [x] Validar tipos permitidos y tamano maximo.
- [x] Mostrar adjuntos desde expediente.
- [x] Registrar auditoria al subir/eliminar adjuntos.
- [ ] Vincular adjunto especifico a una venta con descuento cuando se habilite el flujo avanzado.

Minimo de aceptacion:

- Una venta con cuarta edad debe tener evidencia textual o archivo.
- Un expediente puede guardar documentos clinicos sin mezclarlos con inventario o ventas.

## Sprint 5 - Reportes gerenciales

- [x] Ventas por dia, mes, usuario, metodo de pago y documento.
- [x] Utilidad real por producto y lote.
- [x] Productos top y productos estancados.
- [x] Resumen gerencial inicial con metricas operativas, alertas y graficos del dashboard.
- [x] Endpoint de vencimientos por rango para inventario.
- [x] Vista de vencimientos por rango en Inventario.
- [x] Exportacion de vencimientos por rango.
- [x] Retiro/merma masiva de lotes vencidos desde reporte.
- [x] Stock bajo por tienda/bodega.
- [x] Puntos por paciente con exportacion CSV basica desde Reportes.
- [x] Puntos ganados/redimidos por paciente con detalle historico avanzado.
- [x] Recibos clinicos por doctor/servicio.
- [x] Exportacion CSV basica desde Reportes.
- [x] Exportacion PDF de reportes.

Minimo de aceptacion:

- Admin puede responder cuanto vendio, que gano, que vence, que falta comprar y quien cobro.

## Sprint SAR - Regimen de facturacion Honduras

- [x] Auditar brecha entre configuracion fiscal actual y regimen SAR completo.
- [x] Comparar Clinicapharma con el modulo SAR de ComandaPro.
- [x] Crear `sar-compliance-roadmap.md` con alcance, fuentes y fases.
- [ ] Crear tablas `sar_authorizations`, `fiscal_documents` y `fiscal_document_events`.
- [ ] Crear endpoints `/sar/authorizations`, `/sar/documents`, `/sar/reports/fiscal` y anulaciones/notas de credito.
- [ ] Emitir factura fiscal desde `clinic_receipts` y `pharmacy_sales` consumiendo correlativo en transaccion.
- [ ] Bloquear factura si CAI esta incompleto, vencido o agotado.
- [ ] Reimprimir sin consumir correlativo nuevo.
- [ ] Anular con motivo y usuario autorizado.
- [ ] Crear nota de credito vinculada a factura.
- [ ] Reporte de correlativos no usados para apoyar notificacion en Oficina Virtual.
- [ ] Checklist de validacion con contador/cliente antes de activar facturas reales.

Minimo de aceptacion:

- Si se usa factura SAR real, el sistema debe controlar autorizacion, correlativo, documento fiscal, anulacion, nota de credito, reporte y auditoria. Si no se completa, operar solo con recibos internos.

## Sprint 6 - Instalacion y entrega

- [x] Definir carpeta final de instalacion para paquete: `release/clinicapharma-local`.
- [x] Scripts de paquete local reproducible.
- [x] Scripts de arranque, parada y health-check local.
- [x] Smoke test de paquete beta local: health, login, paciente y adjunto.
- [x] Scripts de instalacion/desinstalacion de servicios Windows con NSSM.
- [ ] Backend/frontend como servicios Windows automaticos validados en equipo destino.
- [x] Frontend web compilado.
- [ ] PostgreSQL instalado/configurado en equipo destino.
- [x] Variables `.env` documentadas.
- [x] Usuario admin inicial configurable por `.env`.
- [x] Migracion Alembic de esquema actual.
- [ ] Prueba en equipo limpio.
- [x] Manual de arranque, parada, backup y restauracion.
- [ ] Validar red local si varias computadoras entran al servidor.

Minimo de aceptacion:

- El sistema inicia despues de reiniciar la computadora servidor.
- Un cliente puede abrir la app desde navegador local o red interna.

## Validacion de flujo intuitivo

Revision web 2026-06-22:

- Salesforce describe clinic management como agenda, EHR, billing/claims y patient engagement en un flujo unificado: https://www.salesforce.com/healthcare/providers/clinic-management-software/
- DrChrono enfatiza el viaje completo del paciente: intake, scheduling, documentacion clinica, billing y pagos: https://www.drchrono.com/practice-management/
- Zoho resume clinic management como citas, registros de pacientes, facturacion y reportes desde un sistema coordinado: https://www.zoho.com/healthcare/digest/clinic-management-software.html
- NN/g recomienda visibilidad de estado, lenguaje real del usuario, control/libertad, consistencia, prevencion de errores y reconocimiento antes que memorizacion: https://www.nngroup.com/articles/ten-usability-heuristics/

Revision SAR 2026-06-23:

- SAR lista comprobantes fiscales como factura, ticket, recibo por honorarios y otros autorizados; tambien documentos complementarios como notas de credito, notas de debito, guias de remision y comprobantes de retencion: https://www.sar.gob.hn/facturacion/
- SAR mantiene el Reglamento del Regimen de Facturacion, otros documentos fiscales y Registro Fiscal de Imprentas en su biblioteca de leyes de facturacion: https://www.sar.gob.hn/download-category/leyes-de-facturacion/
- La Nueva Oficina Virtual incluye inscripcion al regimen, notificacion de documentos fiscales no utilizados y validador de documentos fiscales: https://www.sar.gob.hn/ovi/

Lectura para Clinicapharma:

- El flujo actual es intuitivo para entrega local porque sigue el orden real del negocio: recepcion -> cita -> consulta -> receta/cobro -> farmacia -> inventario -> caja -> reportes.
- Lo que puede confundir al cliente no es el orden general, sino acciones delicadas sin confirmacion clara: anulaciones, descuentos especiales, mermas, cierres, transferencias y facturacion fiscal.
- El sistema debe mostrar estados claros: cita pendiente/atendida/cancelada, caja abierta/cerrada, producto bajo/vencido, venta cobrada, recibo generado, licencia valida/vencida.
- Las pantallas deben usar palabras del negocio: paciente, cita, consulta, receta, recibo, caja, bodega, tienda, lote, vencimiento, vineta, transferencia, banco y referencia.

## Riesgos antes de entrega

- [ ] SAR completo pendiente si el cliente emitira facturas reales desde el sistema: riesgo alto de cumplimiento.
- [ ] Falta auditoria formal para anulaciones/reimpresiones futuras: riesgo medio si se habilitan esos flujos sin completar auditoria.
- [ ] Falta backup/restore probado: riesgo alto ante dano de disco o mala configuracion.
- [ ] Cierre de caja debe validarse con usuario real: riesgo medio en control de dinero.
- [x] Adjuntos basicos implementados: riesgo principal reducido para descuentos y expedientes.
- [ ] Impresion termica no validada con hardware real: riesgo medio en dia de entrega.
- [x] Reportes avanzados base implementados: ventas/cobros, utilidad por lote, stock bajo y vencimientos.
- [ ] Instalacion final no probada en equipo limpio: riesgo alto para entrega.

## Futuro V1

- [ ] Completar modulo formal de facturacion SAR si el cliente lo activa para produccion.
- [ ] Plantillas configurables de impresion/PDF.
- [ ] Adjuntos clinicos avanzados con versionado, vencimiento y vinculo directo a venta/documento.
- [ ] Portal del paciente para citas, documentos, pagos o acceso controlado a registros.
- [ ] Formularios de admision digital y consentimientos firmados.
- [ ] Mensajeria segura paciente-clinica.
- [ ] Laboratorios/ordenes de estudios como modulo interno o integracion futura.
- [ ] Lector de codigo de barras probado con hardware.
- [ ] Dashboard por rol mas configurable.
- [x] Exportaciones PDF de reportes.

## Futuro SaaS

- [ ] Multi-tenant por empresa/sucursal.
- [ ] Licenciamiento online.
- [ ] Backups en nube.
- [ ] Facturacion por plan.
- [ ] Seguridad reforzada, logs de auditoria y monitoreo.
- [ ] Deploy cloud con dominio, HTTPS y base de datos administrada.

## Regla de cierre por cambio

Ningun cambio funcional debe considerarse completo si no se revisaron estos puntos:

- [ ] `requirements.md` actualizado si cambia la regla de negocio.
- [ ] `module-flows.md` actualizado si cambia pantalla, flujo, funcion o validacion.
- [ ] `api-contract.md` actualizado si cambia endpoint/payload/respuesta.
- [ ] `database-schema.md` actualizado si cambia modelo, tabla o campo.
- [ ] `roadmap.md` actualizado si se completa o agrega trabajo.
- [ ] `changelog.md` actualizado si el cambio es visible para usuario o entrega.
- [ ] Tests o validacion manual documentada.
