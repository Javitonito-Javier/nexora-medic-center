# Clinicapharma - Functional Gap Audit

Ultima revision: 2026-06-22

## Resumen ejecutivo

Clinicapharma cubre bien el flujo operativo local de una clinica pequena con farmacia integrada: pacientes, agenda, consulta, expediente, receta, recibos, caja, farmacia POS, inventario por lote, puntos, reportes, configuracion y licencia local.

Comparado con sistemas comerciales de EHR/practice management, el MVP no esta obviando lo esencial para operar localmente. Las brechas estan en funciones de madurez, automatizacion, comunicacion con paciente, cumplimiento/auditoria y crecimiento a nube.

## Comparacion con sistemas de referencia

Fuentes revisadas:

- DrChrono describe un EHR todo-en-uno con scheduling, documentacion clinica, billing, patient engagement, e-prescribing, telehealth y patient messaging: https://www.drchrono.com/ehr/
- Tebra posiciona su plataforma como EHR + practice management con care, billing, scheduling, patient engagement y growth tools: https://www.tebra.com/
- PracticeEHR destaca EHR, practice management, RCM, reporting, televisit y e-prescribing con checks de interacciones: https://www.practiceehr.com/
- Salesforce resume clinic management como unificacion de scheduling, billing y patient engagement: https://www.salesforce.com/healthcare/providers/clinic-management-software/
- Zoho Healthcare describe clinic management alrededor de appointments, patient records, billing y outpatient workflows: https://www.zoho.com/healthcare/digest/clinic-management-software.html

## Lo necesario que ya esta cubierto

- Pacientes/clientes con datos demograficos, identidad, contacto, alergias y antecedentes.
- Agenda con citas, estados, doctor, motivo y recordatorios operativos.
- Expediente clinico global por paciente.
- Consulta con signos vitales, historia, diagnostico, tratamiento, seguimiento y notas.
- Referencias/interconsultas vinculadas al mismo expediente.
- Recetas con items, dosis, via, frecuencia, duracion e instrucciones.
- Cobro clinico con recibo interno.
- Farmacia POS con cliente, carrito, pagos, descuento, puntos y recibo.
- Inventario por producto, presentacion, lote, vencimiento, costo, bodega y tienda.
- Descuento de stock por FEFO/FIFO y trazabilidad por lote.
- Traslados, mermas y movimientos de inventario.
- Dashboard y reportes iniciales.
- Roles, permisos por modulo y licencia local.
- Configuracion fiscal opcional para recibos/facturas.

## Brechas funcionales importantes antes de producto final

Estas no impiden operar el MVP local, pero conviene priorizarlas antes de venderlo como sistema completo:

- Auditoria formal: ya existe primer corte backend con tabla de eventos y endpoint de consulta; falta vista UI y ampliar eventos finos para caja completa, anulaciones, reimpresiones, licencia y flujos futuros.
- Backup/restore guiado: respaldo diario, restauracion probada y verificacion de integridad.
- Cierre de caja completo: apertura, conteo, diferencias, arqueo por usuario, anulaciones y reimpresiones auditadas.
- Adjuntos: DNI/receta para cuarta edad, documentos clinicos, estudios, consentimientos o archivos del paciente.
- Seguridad operativa: cambio obligatorio de password inicial, expiracion/rotacion de tokens, bloqueo por intentos fallidos y politicas de contrasena.
- Reportes de gestion: utilidad real por lote/producto, ventas top, vencimientos, rotacion, puntos, recibos anulados y movimientos por usuario.
- Impresion real: validacion con impresoras termicas 58/80mm y formatos configurables.
- Instalador/deploy local: backend como servicio, frontend compilado, PostgreSQL, backups y arranque automatico.

## Brechas futuras frente a EHR comerciales

Estas son de V1/SaaS o nichos mas avanzados, no obligatorias para el MVP local:

- Portal del paciente para citas, pagos, documentos y acceso a registros.
- Formularios de admision digital y consentimientos firmados.
- Mensajeria segura paciente-clinica.
- Teleconsulta.
- E-prescribing real con red externa y validaciones de interacciones.
- Laboratorios/ordenes de estudios e integraciones externas.
- Seguros, claims, elegibilidad y revenue cycle management.
- Multi-sucursal, multi-tenant, nube, HTTPS, monitoreo y soporte remoto.

## Recomendacion de continuidad

El siguiente bloque de trabajo recomendado no deberia ser agregar mas pantallas, sino cerrar operacion y confianza:

1. Completar auditoria formal con vista UI y eventos restantes.
2. Backup/restore.
3. Cierre de caja completo.
4. Adjuntos.
5. Reportes gerenciales.
6. Instalador/deploy local.
