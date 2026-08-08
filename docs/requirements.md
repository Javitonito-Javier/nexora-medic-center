# Clinicapharma - Requirements

Ultima revision: 2026-06-24

Este archivo es la fuente principal de verdad del proyecto. Si una decision funcional cambia, primero debe actualizarse aqui y luego reflejarse en codigo, API, base de datos, UI, `module-flows.md`, `roadmap.md` y `changelog.md`.

## Objetivo del MVP

Crear un sistema local estable para clinica + farmacia que permita operar pacientes, consultas, recetas, cobros, inventario, ventas, puntos, reportes y configuracion basica sin depender de internet.

## Roles y permisos

- Admin: acceso total, usuarios, configuracion, reportes, inventario, cajas y licencia.
- Recepcionista: pacientes, citas, cobros clinicos si esta autorizado.
- Enfermero: signos vitales, preconsulta y notas esenciales.
- Doctor: consultas, historia clinica, diagnostico, tratamiento, recetas y cobros si esta autorizado.
- Farmacia/cajero: POS, ventas, recibos, clientes y puntos.
- Cajero: cajas y cierres segun modulo asignado.

Un usuario puede tener varios roles y permisos por modulo. La UI debe ocultar modulos no autorizados.

## Clinica

- Registrar pacientes/clientes con identidad, telefono, nacimiento, sexo, direccion, alergias y antecedentes.
- La agenda debe mostrar citas pendientes de forma operativa, con recordatorios desde 3 dias antes de la fecha programada.
- Los recordatorios de citas deben permanecer visibles hasta que la cita sea marcada como atendida o cancelada.
- Las citas deben permitir abrir WhatsApp al numero `+50492398074` con un mensaje prellenado para recordar al paciente la fecha, hora y doctor asignado.
- Abrir expediente con historial por fecha; un paciente puede tener muchas consultas al ano.
- El expediente clinico debe ser global por paciente: cualquier doctor autorizado debe poder ver consultas previas, especialidad del doctor, referencias/interconsultas, diagnosticos, tratamientos, seguimiento y recetas vinculadas.
- Si un medico general refiere a internista u otro especialista, la consulta del especialista y su receta deben quedar enlazadas al mismo expediente para continuidad cuando el paciente vuelva con el medico general.
- Registrar signos vitales: presion arterial, frecuencia cardiaca, SpO2, peso y temperatura.
- Registrar historia clinica, diagnostico, tratamiento, notas internas y proxima cita.
- La preconsulta puede llenarla enfermero o doctor.
- Generar receta impresa/exportable con doctor, paciente, medicamento, dosis, via, frecuencia/intervalo, duracion e instrucciones.
- Cobrar consulta o servicios extras con recibo interno. Factura fiscal es opcional.

## Farmacia POS

- Buscar cliente/paciente o vender a consumidor final.
- Buscar productos por nombre, SKU, codigo de barras o lote.
- Agregar productos al carrito con cantidad y presentacion.
- Cobrar con efectivo, tarjeta o transferencia.
- Para transferencia se debe guardar banco y referencia.
- Bancos de Honduras deben estar disponibles como lista en UI.
- Generar recibo interno por defecto.
- Generar factura solo si el admin habilita el modulo de facturacion.
- Copiar comprobante y permitir impresion/exportacion cuando el flujo lo soporte.
- Mostrar historial/ventas recientes y accesos rapidos a productos mas vendidos o recientes.

## Inventario

- Soportar productos de farmacia que no siempre son pastillas: frascos, guantes, cajas, blisters, unidades, insumos y otros.
- La UI de creacion debe separar claramente producto individual/frasco/insumo, pastilla/blister/caja y guantes/par/caja.
- El alta de producto debe operar como flujo guiado de hasta 3 modulos: producto, venta/precios y lote/stock.
- Para productos individuales como frascos o insumos, el stock debe capturarse en unidades individuales y la caja debe ser opcional.
- Para productos individuales, la UI debe explicar que cada frasco/pieza/insumo equivale a 1 unidad base, que el precio principal es el individual y que el stock se captura como piezas totales en bodega y tienda.
- Producto debe tener nombre, SKU, codigo de barras, unidad base, laboratorio y proveedor.
- Manejar presentaciones: unidad, blister, caja u otras.
- Cada lote guarda costo de compra individual, precio de venta y precio de vineta/etiqueta.
- Cada lote guarda vencimiento, ubicacion/estante, codigo de lote, stock en bodega y stock en tienda.
- Ventas descuentan de tienda usando FEFO/FIFO solo sobre lotes vigentes.
- POS debe bloquear el lote vencido si el cajero lo escanea o si es la unica existencia disponible.
- Si una venta agota un lote, el backend descuenta en cascada del siguiente lote elegible.
- Traslados de bodega a tienda no son ventas; deben quedar como movimientos.
- Mermas/ajustes deben afectar el lote especifico y crear movimiento auditable.
- El retiro masivo de lotes vencidos debe descontar solo existencias ya vencidas, separar tienda/bodega en movimientos de merma y dejar auditoria.
- Dashboard debe alertar stock bajo, vencimientos y lotes estancados.
- Inventario debe exponer reporte de lotes por vencer por rango configurable.

## Puntos y descuentos

- Los puntos solo se ganan en compras de farmacia.
- Regla actual: por cada L 25.00 se otorgan 0.05 puntos.
- 1 punto equivale a L 1.00 como descuento.
- Minimo para redimir: L 50.00 en puntos disponibles.
- La parte pagada con puntos no genera puntos nuevos.
- Los descuentos de tercera/cuarta edad en farmacia se calculan desde precio de vineta/etiqueta, no desde precio rebajado al publico.
- Descuento tercera edad: 25% sobre precio de vineta.
- Descuento cuarta edad: 35% sobre precio de vineta y debe registrar evidencia de receta/DNI.
- Estado actual: se guarda nota de evidencia y se puede adjuntar PDF/imagen al expediente del paciente.

## Facturacion, recibos e impresion

- Recibo interno es el flujo principal para clinica y farmacia.
- Facturacion fiscal SAR debe ser opcional y habilitada por admin solo cuando el cliente decida emitir facturas reales desde el sistema.
- Configuracion fiscal debe guardar CAI, RTN, rango autorizado, punto de emision, establecimiento, correlativo y fecha limite.
- Si el cliente no tiene CAI, puede operar con recibos sin activar facturas.
- Si factura SAR esta activa, el sistema debe manejar autorizaciones versionadas, correlativo transaccional, documento fiscal persistido, reimpresion idempotente, anulacion con motivo, nota de credito y reporte fiscal.
- No se debe emitir factura si CAI, rango, correlativo, punto de emision o fecha limite estan incompletos, vencidos o agotados.
- Reimprimir una factura no debe consumir un nuevo correlativo.
- Anular una factura o crear nota de credito debe conservar el documento original y dejar auditoria.
- El alcance detallado vive en `sar-compliance-roadmap.md`.
- Papel termico soportado: 58mm y 80mm; recomendado 80mm.
- PDF/exportacion debe nombrarse con tipo, cliente/paciente y fecha cuando aplique.

## Cajas

- Clinica y farmacia deben tener cajas separadas.
- Una caja se abre por modulo y cajero con monto inicial.
- No debe haber dos cajas abiertas para el mismo modulo y cajero.
- El cierre debe registrar efectivo contado, tarjeta contado, transferencia contado y nota.
- El sistema calcula esperado desde recibos/ventas del dia por cajero y metodo de pago.
- El efectivo esperado suma monto inicial mas ventas/cobros en efectivo.
- Si hay diferencia entre contado y esperado, la nota es obligatoria.
- Apertura y cierre deben quedar auditados.

## Dashboard y reportes

- Dashboard debe adaptarse por permisos.
- Clinica: citas de hoy, pendientes, atendidos, consultas pagadas del dia/mes.
- Farmacia: ventas del dia/mes, productos por vencer, stock bajo, productos top.
- Admin: vista consolidada de clinica, farmacia, cajas, alertas, puntos y reportes.
- Reportes deben cubrir ventas, recibos, consultas, inventario, vencimientos, puntos y utilidad.
- La pantalla de Reportes debe mostrar resumen gerencial, alertas, graficos, puntos, movimientos de puntos, ventas por periodo/cajero/metodo, recibos clinicos por doctor/servicio, utilidad por producto/lote, productos top, productos estancados, stock bajo y vencimientos exportables por CSV y PDF/impresion.

## Auditoria

- El sistema debe registrar acciones sensibles en `audit_events`.
- Debe guardar usuario actor cuando exista token valido, modulo, accion, entidad, resumen, fecha y snapshots antes/despues cuando aplique.
- Primer corte auditado: login exitoso/fallido, pacientes, usuarios, configuracion, citas, consultas, recetas, recibos clinicos, ventas farmacia, productos, traslados y mermas.
- La auditoria no debe guardar passwords, hashes ni tokens en texto claro.
- La consulta de auditoria debe permitir filtrar por modulo, entidad e id.
- Admin debe tener una pantalla para consultar auditoria, ver cambios antes/despues y copiar CSV basico.

## Adjuntos y evidencias

- El expediente del paciente debe permitir adjuntar PDF, JPG, PNG y WEBP.
- Categorias iniciales: identidad/DNI, receta externa, estudio/resultado, evidencia descuento, consentimiento y otro.
- Cada adjunto debe guardar paciente, categoria, nombre original, tipo, tamano, descripcion, usuario y fecha.
- Los archivos deben guardarse fuera de Git en `ATTACHMENT_STORAGE_DIR`.
- Subir o eliminar adjunto debe crear auditoria.
- El borrado es logico para conservar rastro operativo.

## Licencia local

- El sistema puede bloquear operaciones nuevas si la licencia esta vencida o invalida.
- Consultar datos existentes debe seguir permitido.
- Manual privado: `manual_privado_licencias.md`.
