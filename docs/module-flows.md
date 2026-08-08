# Clinicapharma - Flujos y funciones por modulo

Ultima revision: 2026-06-24

Este documento describe cada modulo funcional, su flujo operativo, datos minimos, reglas, salidas y criterios de aceptacion. Debe actualizarse en el mismo cambio cuando se modifique una pantalla, endpoint, tabla, validacion, permiso o regla de negocio.

## Guia rapida del flujo completo

Flujo principal de clinica:

1. Personal entra al sistema.
2. Recepcion busca o registra paciente.
3. Recepcion agenda o confirma cita.
4. Enfermero o doctor registra preconsulta/signos vitales.
5. Doctor registra consulta, diagnostico, tratamiento y seguimiento.
6. Doctor genera receta si aplica.
7. Caja clinica cobra consulta o servicio.
8. Expediente queda actualizado.

Flujo principal de farmacia:

1. Cajero/farmacia busca producto.
2. Selecciona presentacion y cantidad.
3. Asocia paciente/cliente o consumidor final.
4. Aplica descuento o puntos si corresponde.
5. Cobra con efectivo, tarjeta o transferencia.
6. Sistema descuenta inventario de tienda por FEFO/FIFO.
7. Genera recibo interno; factura SAR solo si el modulo fiscal completo esta activo.
8. Venta, puntos, lote y caja quedan trazados.

Flujo administrativo:

1. Admin configura negocio, usuarios, permisos y fiscal.
2. Admin revisa dashboard, cajas, reportes, inventario y licencia.
3. Admin ejecuta backup/restore segun rutina.
4. Admin valida auditoria cuando exista cambio sensible.

## Principios de usabilidad del sistema

Validacion basada en revision web 2026-06-22:

- Salesforce lista como funciones centrales de clinic management: agenda, EHR/registro clinico, billing y patient engagement: https://www.salesforce.com/healthcare/providers/clinic-management-software/
- DrChrono organiza el viaje del paciente desde intake hasta billing y pagos: https://www.drchrono.com/practice-management/
- Zoho describe el flujo coordinado de citas, registros, facturacion y reportes: https://www.zoho.com/healthcare/digest/clinic-management-software.html
- NN/g recomienda visibilidad de estado, lenguaje del usuario, consistencia, prevencion de errores, control del usuario, reconocimiento antes que memorizacion y ayuda/documentacion: https://www.nngroup.com/articles/ten-usability-heuristics/
- Para POS/inventario, Square y Shopify priorizan stock actualizado, barcode, alertas y ubicaciones; Odoo agrega lotes con vencimiento; sistemas de farmacia como GPOS destacan bloqueo de producto vencido en POS. Ver `pos-inventory-research.md`.

Aplicacion en Clinicapharma:

- El menu debe seguir el orden mental del negocio: Dashboard, Pacientes, Citas, Consulta, Personal, Farmacia, Inventario, Caja, Reportes, Configuracion.
- Cada pantalla debe mostrar estado claro: cargando, vacio, error, guardado, cobrado, cerrado, vencido, bajo stock o licencia bloqueada.
- Los formularios deben pedir primero lo que el usuario conoce: paciente, fecha, doctor, producto, cantidad, metodo de pago.
- Las acciones irreversibles o sensibles deben pedir confirmacion: merma, anulacion, cierre, descuento especial, cambio fiscal, desactivar usuario.
- El usuario debe poder volver al listado o cancelar sin perderse.

## Modulo 1 - Login y sesion

Proposito:

- Permitir entrada segura al sistema local.
- Identificar usuario para permisos, caja y auditoria.

Roles:

- Todos los usuarios activos.

Funciones:

- Iniciar sesion con usuario y contrasena.
- Guardar token local de sesion.
- Cerrar sesion.
- Leer configuracion publica del negocio para pintar login.
- Bloquear escrituras si licencia no permite operar.

Flujo:

1. Usuario abre Clinicapharma.
2. Sistema muestra logo/nombre del negocio si existe.
3. Usuario ingresa credenciales.
4. Backend valida usuario activo y password.
5. Sistema recibe token y datos de usuario.
6. UI muestra solo modulos permitidos.

Datos minimos:

- Usuario.
- Contrasena.
- Estado activo.
- Roles/permisos.

Reglas:

- Usuario inactivo no debe entrar.
- Token invalido debe regresar a login.
- Login no debe depender de internet.

Pendiente recomendado:

- Cambio obligatorio de password inicial.
- Bloqueo por intentos fallidos.
- Politica minima de contrasenas.
- Auditoria de login.

Criterios de aceptacion:

- Usuario valido entra.
- Usuario invalido recibe error claro.
- Modulos no autorizados no aparecen.

## Modulo 2 - Dashboard

Proposito:

- Dar vista rapida del dia segun rol.
- Mostrar alertas operativas.

Roles:

- Admin.
- Recepcion.
- Doctor.
- Farmacia.
- Cajero.

Funciones:

- Ver citas del dia y pendientes.
- Ver consultas/cobros del dia o mes.
- Ver ventas farmacia del dia o mes.
- Ver alertas de stock bajo.
- Ver alertas de vencimiento.
- Ver productos top o recientes cuando aplique.
- Actualizar datos manualmente.

Flujo:

1. Usuario entra despues del login.
2. Sistema carga metricas permitidas por rol.
3. Usuario revisa pendientes y alertas.
4. Usuario navega al modulo que necesita.

Datos minimos:

- Citas por estado.
- Totales de ventas/cobros.
- Stock bajo.
- Vencimientos.
- Alertas.

Reglas:

- Dashboard debe respetar permisos.
- Las alertas deben usar lenguaje claro.
- No debe mostrar datos de modulos no autorizados.

Criterios de aceptacion:

- Admin ve vista consolidada.
- Farmacia ve ventas, productos y stock.
- Recepcion ve citas/pacientes.
- Doctor ve citas/consultas cuando aplique.

## Modulo 3 - Personal, usuarios y permisos

Proposito:

- Administrar usuarios internos, roles, areas y permisos.

Roles:

- Admin.

Funciones:

- Crear usuario.
- Editar usuario.
- Activar/desactivar usuario.
- Cambiar contrasena.
- Asignar roles.
- Asignar permisos por modulo.
- Marcar usuario en turno.
- Definir area: recepcion, enfermeria, doctor, farmacia, caja, admin.

Flujo:

1. Admin abre Personal.
2. Busca o revisa usuario.
3. Crea/edita datos.
4. Asigna permisos.
5. Guarda cambios.
6. Usuario ve modulos segun permisos en siguiente sesion.

Datos minimos:

- Username.
- Nombre completo.
- Telefono opcional.
- Roles.
- Permisos por modulo.
- Area.
- Estado activo.
- Turno.

Reglas:

- No compartir usuarios entre empleados.
- Desactivar no debe borrar historico.
- Cambios de permisos deben auditarse.

Pendiente recomendado:

- Auditoria formal.
- Cambio obligatorio de password inicial.
- Evitar que admin se bloquee a si mismo accidentalmente.

Criterios de aceptacion:

- Admin puede crear usuario operativo.
- Usuario sin permiso no ve modulo.
- Usuario desactivado no inicia sesion.

## Modulo 4 - Configuracion del negocio

Proposito:

- Guardar datos del negocio, recibos, factura opcional, logo y papel.

Roles:

- Admin.

Funciones:

- Configurar nombre comercial/legal.
- Configurar RTN, direccion, telefono y correo.
- Configurar logo.
- Configurar pie de recibo.
- Activar/desactivar facturacion fiscal.
- Configurar CAI, rango, correlativo, punto de emision, establecimiento y fecha limite.
- Configurar papel termico 58mm/80mm.

Flujo:

1. Admin abre Configuracion.
2. Edita datos generales.
3. Define si operara con recibo o factura.
4. Si factura esta activa, completa datos fiscales.
5. Guarda.
6. Recibos/facturas usan nueva configuracion.

Datos minimos:

- Nombre comercial.
- Telefono/direccion.
- RTN si aplica.
- Factura habilitada o no.
- Datos CAI si aplica.
- Papel.

Reglas:

- Recibo interno es flujo principal.
- Factura fiscal solo si admin la habilita y el modulo SAR completo esta listo.
- Si no hay CAI o no se completo `sar-compliance-roadmap.md`, operar con recibos internos.
- Cambios fiscales, emision, reimpresion, anulacion y notas de credito deben auditarse.

Criterios de aceptacion:

- Login y recibos muestran branding.
- Factura no aparece si esta deshabilitada.
- Transferencia, recibo y factura muestran datos correctos.

## Modulo 5 - Pacientes y clientes

Proposito:

- Registrar personas atendidas en clinica o farmacia.
- Evitar duplicados.
- Servir como base del expediente y puntos.

Roles:

- Admin.
- Recepcion.
- Doctor.
- Enfermero.
- Farmacia/cajero si esta autorizado.

Funciones:

- Buscar por nombre, identidad o telefono.
- Crear paciente/cliente.
- Editar datos.
- Ver expediente.
- Ver puntos disponibles.

Flujo:

1. Usuario busca antes de crear.
2. Si no existe, crea paciente.
3. Completa datos generales.
4. Guarda.
5. Abre expediente o usa paciente en cita/venta.

Datos minimos:

- Nombre completo.
- Telefono.
- Identidad si existe.
- Fecha de nacimiento.
- Sexo.
- Direccion.
- Alergias.
- Antecedentes/condiciones conocidas.

Reglas:

- Identidad debe ayudar a evitar duplicados.
- Paciente puede tener muchas consultas.
- Paciente puede comprar en farmacia y acumular puntos.
- Cambios sensibles deben auditarse.

Criterios de aceptacion:

- Busqueda encuentra registros existentes.
- Nuevo paciente queda disponible para cita, consulta y venta.
- Expediente muestra historial global.

## Modulo 6 - Citas y agenda

Proposito:

- Organizar atencion clinica.
- Reducir olvidos con recordatorios operativos.

Roles:

- Admin.
- Recepcion.
- Doctor.
- Enfermero si autorizado.

Funciones:

- Crear cita.
- Editar cita.
- Cambiar estado: pendiente, atendida, cancelada.
- Ver citas por fecha/estado.
- Mostrar recordatorios desde 3 dias antes.
- Mantener recordatorio hasta atendida/cancelada.
- Abrir WhatsApp con mensaje prellenado.

Flujo:

1. Recepcion busca paciente.
2. Crea cita con fecha, hora, doctor y motivo.
3. Sistema la muestra en agenda.
4. Antes de fecha, recordatorio aparece.
5. Recepcion puede abrir WhatsApp.
6. Al atender, se marca como atendida.

Datos minimos:

- Paciente.
- Fecha/hora.
- Doctor.
- Motivo.
- Estado.
- Notas.

Reglas:

- No debe perderse una cita pendiente.
- WhatsApp usa mensaje claro para paciente.
- Estados deben ser visibles.

Pendiente recomendado:

- Prevencion de doble cita por doctor/hora.
- Reprogramacion con historial.

Criterios de aceptacion:

- Cita creada aparece en agenda.
- Recordatorio aparece desde 3 dias antes.
- Cita atendida/cancelada deja de alertar.

## Modulo 7 - Consulta medica y expediente

Proposito:

- Registrar atencion clinica completa.
- Mantener continuidad entre doctores.

Roles:

- Doctor.
- Enfermero para preconsulta.
- Admin si autorizado.

Funciones:

- Abrir expediente.
- Registrar signos vitales.
- Registrar motivo/historia clinica.
- Registrar diagnostico.
- Registrar tratamiento.
- Registrar notas internas.
- Registrar proxima cita.
- Registrar especialidad del doctor.
- Registrar referencia/interconsulta.
- Registrar seguimiento para proximo doctor.
- Ver consultas previas.

Flujo:

1. Doctor/enfermero selecciona paciente.
2. Enfermero o doctor captura signos vitales.
3. Doctor revisa historial previo.
4. Doctor registra historia, diagnostico y tratamiento.
5. Si refiere, registra especialidad destino y motivo.
6. Guarda consulta.
7. Puede generar receta o cobro.
8. Expediente queda actualizado.

Datos minimos:

- Paciente.
- Doctor.
- Especialidad.
- Signos vitales: presion, frecuencia cardiaca, SpO2, peso, temperatura.
- Historia/motivo.
- Diagnostico.
- Tratamiento.
- Seguimiento.
- Proxima cita si aplica.

Reglas:

- Expediente es global por paciente.
- Consultas de diferentes doctores quedan en el mismo expediente.
- Interconsulta debe conservar continuidad.
- Receta vinculada debe marcar consulta con receta.

Pendiente recomendado:

- Auditoria formal.
- Adjuntos clinicos desde panel de expediente.
- Plantillas por especialidad si el cliente las pide.

Criterios de aceptacion:

- Doctor ve historial antes de atender.
- Consulta nueva queda fechada.
- Receta puede vincularse a consulta.

## Modulo 8 - Recetas

Proposito:

- Emitir receta clara y reutilizable en expediente.

Roles:

- Doctor.
- Admin si autorizado.

Funciones:

- Crear receta desde consulta o paciente.
- Agregar medicamentos.
- Indicar dosis.
- Indicar via de administracion.
- Indicar frecuencia/intervalo.
- Indicar duracion.
- Agregar instrucciones.
- Imprimir/exportar.
- Ver historial de recetas.

Flujo:

1. Doctor termina consulta.
2. Abre receta.
3. Agrega items.
4. Revisa datos del paciente y doctor.
5. Guarda.
6. Sistema vincula receta al expediente y consulta si aplica.
7. Imprime/exporta.

Datos minimos:

- Paciente.
- Doctor.
- Especialidad.
- Medicamento.
- Dosis.
- Via.
- Frecuencia/intervalo.
- Duracion.
- Instrucciones.

Reglas:

- Receta debe ser legible.
- Si nace de consulta, debe quedar enlazada.
- Debe poder consultarse despues por paciente.

Pendiente recomendado:

- Plantilla de impresion configurable.
- Catalogo opcional de medicamentos frecuentes.
- Validaciones futuras de interacciones si se integra servicio externo.

Criterios de aceptacion:

- Receta se guarda con todos los items.
- Receta aparece en expediente.
- Receta se puede imprimir/copiar/exportar.

## Modulo 9 - Recibos clinicos

Proposito:

- Cobrar consultas o servicios de clinica.

Roles:

- Admin.
- Recepcion.
- Doctor si autorizado.
- Cajero.

Funciones:

- Crear recibo clinico.
- Asociar paciente.
- Asociar consulta si aplica.
- Registrar cajero.
- Registrar doctor.
- Registrar descripcion/servicio.
- Cobrar efectivo, tarjeta o transferencia.
- Guardar banco y referencia para transferencia.
- Copiar/imprimir recibo.

Flujo:

1. Usuario selecciona paciente/consulta.
2. Define descripcion del cobro.
3. Ingresa subtotal/descuento/total.
4. Selecciona metodo de pago.
5. Si transferencia, ingresa banco y referencia.
6. Guarda recibo.
7. Sistema permite copiar/imprimir.

Datos minimos:

- Paciente.
- Cajero.
- Descripcion.
- Metodo de pago.
- Total.
- Banco/referencia si transferencia.

Reglas:

- Recibo interno es principal.
- Factura fiscal es opcional.
- Caja clinica separada de farmacia.
- Cobro debe aparecer en caja/reporte.

Pendiente recomendado:

- Anulacion auditada.
- Reimpresion auditada.
- Cierre de caja completo.

Criterios de aceptacion:

- Cobro queda listado.
- Transferencia guarda referencia.
- Recibo se puede copiar/imprimir.

## Modulo 10 - Farmacia POS

Proposito:

- Vender productos de farmacia rapido y con control de inventario, pagos, puntos y descuentos.

Roles:

- Farmacia/cajero.
- Admin.

Funciones:

- Buscar producto por nombre.
- Buscar por SKU.
- Buscar por codigo de barras.
- Buscar por lote.
- Agregar producto al carrito.
- Seleccionar presentacion.
- Cambiar cantidad.
- Asociar paciente/cliente.
- Vender a consumidor final.
- Aplicar descuento tercera/cuarta edad.
- Registrar evidencia de descuento.
- Redimir puntos si cumple minimo.
- Cobrar efectivo, tarjeta o transferencia.
- Guardar banco y referencia.
- Generar recibo.
- Ver ventas recientes.

Flujo:

1. Cajero busca producto.
2. Selecciona presentacion y cantidad.
3. Sistema calcula precio y subtotal.
4. Cajero asocia cliente si aplica.
5. Aplica descuento/puntos si corresponde.
6. Selecciona metodo de pago.
7. Confirma venta.
8. Backend descuenta inventario vigente de tienda por FEFO/FIFO.
9. Sistema registra lotes usados, utilidad, puntos y recibo.

Datos minimos:

- Producto.
- Presentacion.
- Cantidad.
- Precio.
- Cliente o consumidor final.
- Metodo de pago.
- Banco/referencia si transferencia.
- Evidencia si cuarta edad.

Reglas:

- Venta descuenta de tienda, no de bodega.
- FEFO/FIFO debe escoger lotes elegibles y vigentes.
- Lote vencido no debe venderse ni por seleccion automatica ni por scanner.
- Si un lote se agota, descuenta en cascada.
- Parte pagada con puntos no genera puntos nuevos.
- Tercera edad: 25% sobre precio de vineta.
- Cuarta edad: 35% sobre precio de vineta y evidencia.
- Puntos solo nacen de compras de farmacia.

Pendiente recomendado:

- Anulacion/devolucion auditada.
- Lector de codigo de barras probado con hardware.

Criterios de aceptacion:

- Producto se agrega al carrito.
- Venta descuenta inventario.
- Recibo muestra pago y cliente.
- Puntos se calculan correctamente.

## Modulo 11 - Inventario

Proposito:

- Controlar productos, presentaciones, lotes, vencimientos, ubicaciones y costos.

Roles:

- Admin.
- Farmacia.
- Inventario si existe.

Funciones:

- Crear producto.
- Definir tipo de producto: individual/frasco/insumo, pastilla/blister/caja, guantes/par/caja u otro.
- Definir unidad base.
- Definir SKU/codigo de barras.
- Definir laboratorio/proveedor.
- Definir presentaciones de venta.
- Crear lote inicial.
- Registrar vencimiento.
- Registrar costo unitario.
- Registrar precio venta y precio vineta.
- Registrar stock bodega y tienda.
- Trasladar bodega a tienda.
- Registrar merma/perdida.
- Ver movimientos.
- Ver alertas de stock/vencimiento/estancado.
- Ver lotes por vencer por rango de dias desde panel 30/60/90.
- Retirar masivamente lotes vencidos con existencia desde el panel de vencimientos.

Flujo alta producto:

1. Usuario elige tipo de producto.
2. Ingresa datos generales.
3. Define presentaciones y precios.
4. Ingresa lote, costo, vencimiento, ubicacion, bodega y tienda.
5. Guarda.
6. Producto queda disponible en POS.

Flujo traslado:

1. Usuario abre lote.
2. Ingresa unidades a mover.
3. Sistema resta bodega y suma tienda.
4. Crea movimiento.

Flujo merma:

1. Usuario selecciona lote.
2. Ingresa cantidad perdida.
3. Indica razon/nota.
4. Sistema descuenta y crea movimiento.

Flujo retiro masivo de vencidos:

1. Usuario abre Inventario.
2. Revisa el panel de lotes por vencer.
3. Selecciona retirar vencidos.
4. Sistema pide confirmacion explicita.
5. Backend busca solo lotes con fecha vencida y existencia en tienda o bodega.
6. Sistema descuenta tienda y bodega a cero, creando movimientos de merma separados por ubicacion.
7. Sistema muestra cuantos lotes y unidades fueron retirados.
8. La accion queda auditada.

Datos minimos:

- Nombre.
- SKU/codigo de barras.
- Unidad base.
- Presentacion.
- Laboratorio/proveedor.
- Lote.
- Vencimiento.
- Costo.
- Precio venta.
- Precio vineta.
- Stock bodega.
- Stock tienda.

Reglas:

- Stock operativo de venta sale de tienda.
- Bodega no vende directamente.
- Todo traslado/merma debe crear movimiento.
- Retiro masivo de vencidos no debe afectar lotes vigentes ni lotes solo proximos a vencer.
- No vender producto vencido; si se escanea un lote vencido, la venta debe bloquearse con error claro.
- Reporte de vencimientos debe listar solo lotes vigentes con unidades disponibles.
- Inventario no debe depender solo de stock global.

Pendiente recomendado:

- Conteo ciclico/inventario ciego.
- Ajustes auditados.
- Compras/proveedores formal.

Criterios de aceptacion:

- Producto nuevo aparece en POS.
- Traslado actualiza bodega/tienda.
- Merma descuenta lote especifico.
- Retiro masivo descuenta solo lotes vencidos y deja movimientos de merma.
- Movimientos quedan visibles.

## Modulo 12 - Puntos y descuentos

Proposito:

- Fidelizar compras de farmacia y aplicar descuentos legales.

Roles:

- Farmacia/cajero.
- Admin.

Funciones:

- Acumular puntos por compra farmacia.
- Ver balance de puntos.
- Redimir puntos si cumple minimo.
- Registrar movimiento de puntos.
- Aplicar descuento tercera edad.
- Aplicar descuento cuarta edad.
- Registrar evidencia.

Flujo puntos:

1. Cajero asocia paciente/cliente en POS.
2. Sistema calcula puntos por monto elegible.
3. Si cliente tiene minimo L 50 en puntos, puede redimir.
4. Sistema descuenta puntos.
5. Movimiento queda registrado.

Datos minimos:

- Paciente.
- Venta.
- Puntos ganados/redimidos.
- Balance posterior.
- Nota.

Reglas:

- Por cada L 25.00 se otorgan 0.05 puntos.
- 1 punto equivale a L 1.00.
- Minimo para redimir: L 50.00.
- Lo pagado con puntos no genera puntos.
- Puntos solo farmacia, no clinica.
- Descuento tercera/cuarta edad se calcula desde precio de vineta.

Pendiente recomendado:

- Adjuntar archivo de evidencia.
- Reporte de puntos por fecha.

Criterios de aceptacion:

- Compra acumula puntos.
- Redencion respeta minimo.
- Balance queda correcto.

## Modulo 13 - Caja y cierres

Proposito:

- Controlar dinero por usuario y por area.

Roles:

- Admin.
- Cajero.
- Recepcion.
- Farmacia.

Funciones actuales:

- Ver resumen de caja farmacia.
- Ver resumen de caja clinica.
- Separar cobros clinicos y ventas farmacia.
- Ver pagos por efectivo, tarjeta y transferencia.
- Abrir caja por modulo y cajero.
- Registrar monto inicial.
- Cerrar caja con conteo por metodo de pago.
- Calcular esperado vs contado.
- Exigir nota si hay diferencia.
- Listar sesiones recientes.
- Auditar apertura y cierre.

Flujo actual:

1. Cajero selecciona modulo clinica/farmacia.
2. Cajero escribe su nombre y monto inicial.
3. Sistema abre caja si no hay otra abierta para ese modulo/cajero.
4. Durante el dia, ventas/recibos se registran con ese cajero.
5. Cajero ingresa efectivo, tarjeta y transferencia contados.
6. Sistema calcula esperado, contado y diferencia.
7. Si hay diferencia, pide nota.
8. Sistema cierra caja y crea evento de auditoria.

Funciones pendientes para entrega robusta:

- Anulaciones y reimpresiones auditadas.
- Reporte diario avanzado para admin.
- Cortes por rango horario si el cliente opera multiples turnos por dia con el mismo cajero.

Datos minimos:

- Usuario.
- Modulo: clinica o farmacia.
- Fecha/hora apertura.
- Fecha/hora cierre.
- Monto inicial.
- Esperado.
- Contado.
- Diferencia.
- Nota.

Reglas:

- Caja clinica y farmacia separadas.
- Cierre debe ser por usuario.
- Diferencias deben quedar explicadas.

Criterios de aceptacion:

- Admin sabe cuanto entro por metodo.
- Cierre no mezcla clinica con farmacia.
- Diferencias quedan registradas.
- No se permite cerrar con diferencia sin nota.

## SAR Honduras - flujo fiscal completo

Estado actual: documentado y pendiente de implementacion completa. Ver `sar-compliance-roadmap.md`.

### Objetivo

- Permitir facturacion fiscal solo cuando el cliente tenga autorizacion SAR vigente.
- Evitar correlativos duplicados, CAI vencido, rangos agotados y anulaciones sin evidencia.
- Mantener recibos internos separados de documentos fiscales.

### Flujo admin

1. Admin entra a Configuracion/SAR.
2. Registra RTN, razon social, CAI, establecimiento, punto de emision, rango autorizado, correlativo inicial y fecha limite.
3. Sistema valida formato basico y guarda autorizacion.
4. Sistema muestra estado: activa, por vencer, vencida, agotada o inactiva.
5. Toda modificacion queda auditada.

### Flujo de emision

1. Caja cobra consulta o venta farmacia.
2. Usuario elige recibo interno o factura SAR.
3. Si elige factura, backend valida autorizacion activa, fecha limite y rango.
4. Backend consume el siguiente correlativo en transaccion.
5. Backend crea documento fiscal persistido y lo vincula al recibo/venta.
6. UI imprime factura con CAI, rango, numero fiscal, fecha limite y datos del cliente.
7. Si se reimprime, el sistema usa el mismo documento fiscal y registra evento de reimpresion.

### Flujo de anulacion

1. Usuario autorizado abre documento fiscal.
2. Selecciona anular.
3. Ingresa motivo obligatorio.
4. Sistema marca documento como anulado, conserva original y registra auditoria.

### Flujo de nota de credito

1. Usuario autorizado abre factura original.
2. Selecciona nota de credito.
3. Ingresa monto, motivo y detalle.
4. Sistema crea documento complementario vinculado a la factura original.
5. Reporte fiscal refleja factura y nota asociada.

### Reglas

- No emitir factura si CAI esta vencido, incompleto o agotado.
- No reutilizar correlativos.
- Reimpresion no consume correlativo.
- Anulacion y nota de credito exigen motivo.
- Reporte fiscal debe cuadrar con recibos/ventas origen.

## Modulo 14 - Reportes

Proposito:

- Dar visibilidad administrativa y gerencial.

Roles:

- Admin.
- Usuarios con permiso de reportes.

Funciones actuales:

- Resumen gerencial inicial desde `/reports/summary`.
- Metricas operativas de clinica, farmacia, utilidad, puntos y caja.
- Alertas y graficos reutilizados del dashboard.
- Ventas/cobros por periodo, modulo, cajero, metodo de pago y documento desde `/reports/sales`.
- Recibos clinicos por doctor, servicio, cajero y metodo de pago desde `/reports/clinic-receipts`.
- Utilidad real por producto y lote desde `/reports/profit-by-lot`.
- Stock bajo por tienda/bodega desde `/reports/inventory/low-stock`.
- Vencimientos por rango desde `/reports/inventory/expiring-stock`.
- Consulta de puntos por paciente.
- Movimientos de puntos ganados/redimidos desde `/reports/points/movements`.
- Productos top desde `/reports/pharmacy/top-products`.
- Productos estancados desde `/reports/inventory/stagnant-lots`.
- Copia de CSV para metricas, alertas, ventas, utilidad, stock bajo, vencimientos, puntos, movimientos de puntos, productos top y estancados.
- Impresion/PDF por bloque de reporte para ventas, recibos clinicos, utilidad, stock bajo, vencimientos, puntos, productos top y estancados.

Reportes minimos recomendados:

- Ventas farmacia por fecha: implementado en reporte consolidado.
- Recibos clinicos por fecha: implementado en reporte consolidado.
- Recibos clinicos por doctor/servicio: implementado.
- Totales por metodo de pago: implementado.
- Ventas por usuario/cajero: implementado.
- Utilidad por producto/lote: implementado.
- Inventario bajo: implementado.
- Vencimientos: implementado.
- Productos top: implementado.
- Productos estancados: implementado.
- Puntos ganados/redimidos: implementado.
- Movimientos de inventario.
- Consultas por doctor.

Flujo:

1. Usuario abre Reportes.
2. Sistema carga resumen gerencial, ventas, recibos clinicos por doctor/servicio, utilidad por lote, stock bajo, vencimientos, puntos, movimientos de puntos, productos top y lotes estancados.
3. Usuario revisa metricas, alertas, graficos, cierres de venta, produccion clinica por medico/servicio, utilidad, ranking de productos e inventario critico.
4. Usuario copia CSV si necesita llevar datos a hoja de calculo.
5. Usuario abre PDF/impresion por bloque si necesita guardar o entregar el reporte.
6. Filtros visuales avanzados quedan como siguiente fase.

Datos minimos:

- Rango de fechas.
- Modulo.
- Usuario si aplica.
- Metodo de pago si aplica.

Reglas:

- Reportes deben cuadrar con recibos/ventas.
- Utilidad real debe venir de costo de lote asignado.
- Exportaciones deben tener nombre claro.

Criterios de aceptacion:

- Admin puede revisar cierre diario.
- Admin puede revisar recibos clinicos por doctor y servicio.
- Admin identifica productos por vencer.
- Admin identifica utilidad general, alertas, puntos y movimientos de puntos.
- Admin puede copiar CSV desde cada bloque principal de Reportes.
- Admin puede guardar PDF desde cada bloque principal de Reportes usando el dialogo de impresion del navegador.

## Modulo 15 - Auditoria

Proposito:

- Registrar acciones sensibles para control, soporte y reclamos.

Roles:

- Admin.
- Tecnico/dueno del sistema si aplica.

Funciones actuales:

- Registrar login exitoso.
- Registrar login fallido.
- Registrar creacion/edicion de pacientes.
- Registrar creacion/edicion de usuarios.
- Registrar cambios en configuracion del negocio.
- Registrar creacion/edicion de citas.
- Registrar creacion de consultas.
- Registrar creacion de recetas.
- Registrar recibos clinicos.
- Registrar ventas farmacia.
- Registrar productos de inventario.
- Registrar traslados bodega-tienda.
- Registrar mermas/perdidas.
- Consultar eventos con filtros por modulo, entidad e id.
- Ver eventos en UI admin.
- Filtrar por modulo, entidad, id y limite.
- Expandir cambios antes/despues cuando existan.
- Copiar CSV basico de los eventos listados.

Flujo:

1. Usuario realiza una accion sensible.
2. Backend completa la operacion principal.
3. Backend crea evento en `audit_events`.
4. Admin abre Auditoria.
5. Admin filtra por modulo, entidad o id.
6. Admin revisa resumen, usuario, fecha y cambios antes/despues.

Datos minimos:

- Usuario actor si existe.
- Modulo.
- Accion.
- Tipo de entidad.
- Id de entidad.
- Resumen.
- Fecha/hora.
- Datos antes/despues cuando aplique.
- Razon cuando aplique.

Reglas:

- No guardar passwords, hashes ni tokens en claro.
- Auditoria debe conservar datos suficientes para reconstruir quien hizo que.
- Anulaciones, cierres y reimpresiones deben auditarse cuando esos flujos existan.

Pendiente recomendado:

- Eventos finos de anulacion/reimpresion.
- Auditoria de anulacion, reimpresion y notas de credito cuando esos flujos se implementen.

Criterios de aceptacion:

- Crear paciente genera evento.
- Editar paciente guarda antes/despues.
- Venta farmacia genera evento.
- Traslado/merma generan evento.
- `GET /audit/` permite consultar eventos.
- La UI de Auditoria muestra eventos filtrables y permite copiar CSV basico.

## Modulo 16 - Licencia local

Proposito:

- Controlar uso local del sistema por instalacion/cliente.

Roles:

- Admin.
- Tecnico/dueno del sistema.

Funciones:

- Ver estado de licencia.
- Activar licencia.
- Validar vencimiento.
- Bloquear operaciones nuevas si licencia esta vencida o invalida.
- Permitir consulta de datos existentes.

Flujo:

1. Admin revisa estado.
2. Si requiere renovar, carga licencia.
3. Sistema valida firma/datos.
4. Estado queda actualizado.

Datos minimos:

- Cliente.
- Installation ID.
- License key.
- Estado.
- Fecha de expiracion.

Reglas:

- Licencia vencida bloquea escrituras.
- Consulta historica debe seguir disponible.
- Manual privado no se incluye en manual cliente.

Criterios de aceptacion:

- Licencia valida permite operar.
- Licencia invalida informa bloqueo.
- Datos existentes se pueden consultar.

## Modulo 17 - Impresion, PDF y comprobantes

Proposito:

- Entregar documentos claros para paciente, cliente y administracion.

Roles:

- Recepcion.
- Doctor.
- Farmacia.
- Admin.

Funciones:

- Copiar recibo.
- Imprimir/exportar recibo.
- Imprimir/exportar receta.
- Generar PDFs/manuales.
- Soportar papel 58mm y 80mm segun configuracion.

Flujo:

1. Usuario genera recibo o receta.
2. Sistema arma texto/formato.
3. Usuario copia, imprime o exporta.
4. Documento queda asociado al registro.

Datos minimos:

- Negocio.
- Paciente/cliente.
- Usuario/cajero/doctor.
- Fecha.
- Detalle.
- Total o instrucciones.

Reglas:

- Documento debe incluir datos del negocio.
- Factura solo si esta habilitada.
- Receta debe mostrar doctor, paciente e items.

Pendiente recomendado:

- Validar impresoras termicas reales.
- Plantillas configurables.
- Auditoria de reimpresiones si aplica.

Criterios de aceptacion:

- Receta se entiende al imprimir.
- Recibo muestra total y metodo de pago.
- Formato cabe en papel configurado.

## Modulo 18 - Backup y restauracion

Proposito:

- Proteger la base local ante dano, error humano o cambio de equipo.

Roles:

- Admin tecnico.
- Dueno del sistema.

Funciones actuales:

- Crear backup PostgreSQL con `scripts/backup-db.ps1`.
- Guardar backup en `C:\ClinicapharmaBackups`.
- Generar hash SHA256.
- Eliminar backups antiguos segun retencion.
- Restaurar backup con `scripts/restore-db.ps1`.
- Exigir `-ConfirmRestore` para restaurar.

Flujo backup:

1. Cerrar operaciones del dia.
2. Ejecutar `backup-db.ps1`.
3. Verificar mensaje de exito.
4. Confirmar archivo `.dump` y `.sha256`.
5. Copiar respaldo a unidad externa segun rutina.

Flujo restauracion:

1. Elegir archivo `.dump`.
2. Cerrar backend y conexiones activas.
3. Ejecutar `restore-db.ps1` con `-ConfirmRestore`.
4. Script valida SHA256 si existe.
5. Script recrea la base y restaura datos.
6. Tecnico inicia backend y valida login/datos.

Datos minimos:

- Nombre de base.
- Usuario PostgreSQL.
- Password PostgreSQL.
- Host/puerto.
- Archivo de backup.

Reglas:

- Restaurar reemplaza la base destino.
- No restaurar sin backup elegido y confirmado.
- Conservar backups minimo 30 dias.
- Probar restauracion antes de entrega.

Criterios de aceptacion:

- Backup genera archivo no vacio.
- Backup genera SHA256.
- Restauracion valida SHA256 cuando existe.
- Sistema inicia despues de restaurar.

## Modulo 19 - Adjuntos y evidencias

Proposito:

- Guardar documentos de soporte dentro del expediente del paciente.
- Respaldar descuentos especiales, recetas externas, estudios, identidad y consentimientos.

Roles:

- Admin.
- Recepcion.
- Doctor.
- Enfermeria.
- Farmacia/cajero si tiene permiso de pacientes.

Funciones actuales:

- Listar adjuntos por paciente.
- Subir PDF, JPG, PNG o WEBP.
- Clasificar por identidad/DNI, receta externa, estudio/resultado, evidencia descuento, consentimiento u otro.
- Guardar descripcion o nota.
- Descargar archivo autenticado.
- Eliminar adjunto de forma logica.
- Auditar subida y eliminacion.

Flujo:

1. Usuario abre expediente de paciente.
2. Entra al panel Adjuntos y evidencias.
3. Selecciona tipo de adjunto.
4. Agrega descripcion si aplica.
5. Selecciona archivo PDF o imagen.
6. Sistema valida tipo y tamano.
7. Backend guarda metadata en `patient_attachments` y archivo en `ATTACHMENT_STORAGE_DIR`.
8. Sistema registra auditoria.
9. Usuario puede descargar o eliminar el adjunto desde el expediente.

Datos minimos:

- Paciente.
- Categoria.
- Nombre original.
- Tipo MIME.
- Tamano.
- Descripcion.
- Usuario que subio.
- Fecha.

Reglas:

- Archivos permitidos: PDF, JPG, PNG y WEBP.
- Tamano maximo configurable con `ATTACHMENT_MAX_SIZE_BYTES`.
- Los binarios no deben versionarse en Git.
- El borrado debe ser logico para conservar rastro.
- Subir/eliminar debe auditarse.

Pendiente recomendado:

- Vincular un adjunto especifico a una venta con descuento.
- Versionado/expiracion si el cliente maneja documentos renovables.

Criterios de aceptacion:

- Expediente muestra adjuntos existentes.
- Usuario sube evidencia y queda visible sin recargar toda la app.
- Usuario descarga el archivo correcto.
- Eliminar quita el adjunto del listado y deja auditoria.

## Checklist por cambio funcional

Usar esta lista siempre que se toque una funcion:

- [ ] Se actualizo `requirements.md` si cambio una regla.
- [ ] Se actualizo este `module-flows.md` si cambio pantalla, paso, funcion, permiso o validacion.
- [ ] Se actualizo `api-contract.md` si cambio API.
- [ ] Se actualizo `database-schema.md` si cambio tabla/modelo/campo.
- [ ] Se actualizo `roadmap.md` si se completo o agrego trabajo.
- [ ] Se actualizo `changelog.md` si el cambio importa para usuario/entrega.
- [ ] Se valido rol/permisos.
- [ ] Se valido flujo feliz.
- [ ] Se valido error principal.
- [ ] Se valido que el usuario tenga mensajes claros.

## Minimos detalles para demo de entrega

- Tener usuario admin y usuarios demo por rol.
- Tener pacientes demo con historial.
- Tener citas de hoy, pendiente, atendida y cancelada.
- Tener una consulta con receta vinculada.
- Tener producto con lote vigente, bajo stock y proximo a vencer.
- Tener venta farmacia con efectivo.
- Tener venta farmacia con transferencia y banco.
- Tener cliente con puntos.
- Tener descuento tercera/cuarta edad probado.
- Tener recibo clinico.
- Tener dashboard con datos reales.
- Tener cierre/resumen de caja del dia.
- Tener backup reciente antes de demo.
- Tener plan de restauracion probado.
