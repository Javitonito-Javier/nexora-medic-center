# Clinicapharma - UI Guidelines

Ultima revision: 2026-07-12

## Personalidad visual

La interfaz debe sentirse medica, limpia, profesional y rapida para trabajo diario. No debe parecer landing page ni sistema decorativo; debe priorizar lectura, velocidad y confianza.

## Tema

- Usar Material 3.
- Tema claro y oscuro global con Riverpod.
- Color principal: verde celadon/grisaceo (`0xFF77BFA3`).
- Color secundario medico: azul (`0xFF2F80C0` en claro, azul suave en oscuro).
- Fondo claro: verdes muy suaves y superficies limpias.
- Fondo oscuro: tonos verde-negro sin perder contraste.
- Color terciario/acento ambar (`0xFFE0A23A` claro, `0xFFE6B765` oscuro) para resaltados puntuales.
- Tipografia: Manrope empaquetada localmente en `assets/fonts` (regular 400, semibold 600, bold 700); no usar fuentes descargadas en runtime porque el sistema debe operar sin internet.
- Bordes: tokens de radio definidos en `app_theme.dart`: 12px para cards (`_cardRadius`), 10px para campos, botones, chips y tiles de navegacion (`_fieldRadius`); maximo 14px solo para marcos decorativos como el logo del sidebar.
- Evitar paletas de un solo tono; usar azul medico para acciones clinicas y datos.

## Layout

- Navegacion lateral fija en desktop, agrupada por secciones: General, Clinica, Farmacia y Administracion.
- El item activo del menu se resalta con barra lateral izquierda, fondo suave y texto/icono en color primario.
- Top bar con titulo, notificaciones, tema, usuario y logout.
- Cada modulo debe abrir directo a la herramienta real, no a explicaciones.
- Usar paneles y tarjetas solo para agrupar informacion operativa.
- Evitar cards dentro de cards.
- Mantener densidad de informacion apta para recepcion, farmacia y doctor.

## Formularios

- Campos con labels claros y tamanos consistentes.
- Botones principales abajo o al final de cada flujo, sin overflow.
- Formularios largos deben permitir scroll y no quedar tapados por botones.
- Validaciones deben explicar que falta, no solo fallar.
- En busquedas grandes usar filtro por texto/autocomplete.

## Inventario

- El alta de producto debe iniciar por como se vende: producto individual/frasco/insumo, pastilla/blister/caja o guantes/par/caja.
- El alta de producto debe presentarse como asistente de 3 pasos maximo: producto, venta/precios y lote/stock con resumen antes de guardar.
- El stock siempre debe explicarse en unidad base para evitar confundir frascos, tabletas, pares o cajas.
- Para productos individuales, mostrar precio de venta individual y dejar caja como opcion secundaria, no como requisito.
- Para productos individuales, incluir una guia visible con ejemplos: frasco/pieza como unidad base, venta individual como 1 unidad y caja solo si se vende cerrada.
- En lote/stock, mostrar un resumen calculado de bodega + tienda en unidad base antes de guardar.
- Evitar crear presentaciones visuales o payloads con precio 0 si el usuario no pretende vender esa presentacion.

## Citas

- La agenda debe priorizar citas pendientes y proximas por atender sobre citas ya cerradas.
- Las alertas de cita deben activarse 3 dias antes y permanecer visibles hasta que la cita quede atendida o cancelada.
- Cada cita debe ofrecer accion de WhatsApp al numero `+50492398074` con mensaje prellenado de fecha, hora y doctor.
- La agenda debe mostrar contadores compactos para hoy, vencidas y proximas 72 horas.

## POS farmacia

- Flujo ideal: buscar producto -> agregar -> seleccionar cliente/descuento -> elegir pago -> cobrar.
- La cabecera del POS debe mostrar el estado del flujo con pasos compactos: escaneo, carrito y cobro.
- El carrito debe mostrar cantidades, presentacion, subtotal y total siempre visibles.
- Cuando haya productos en carrito, el panel de carrito debe repetir subtotal, descuento y total para que el cajero no dependa solo del panel de cobro.
- Cliente seleccionado debe mostrar puntos, descuento legal disponible y acciones rapidas.
- Productos recientes/top deben mostrarse como tarjetas clicables.
- Cobro debe destacar metodo de pago, documento, descuento, referencia y banco.

## Clinica

- Expediente del paciente debe mostrar historial global por fechas, especialidad del doctor, referencias/interconsultas, diagnostico, tratamiento, seguimiento y recetas vinculadas a cada consulta.
- Las recetas creadas desde una consulta deben quedar visibles dentro del evento clinico correspondiente, ademas del listado general de recetas.
- Consulta debe separar signos vitales, historia clinica, diagnostico, tratamiento, notas y receta.
- Receta impresa debe mostrar titulo, doctor, paciente, medicamento, dosis, via, intervalo/frecuencia, duracion e instrucciones.

## Accesibilidad y responsividad

- Todos los iconos no obvios deben tener tooltip.
- Texto no debe salirse de botones ni tarjetas.
- Usar contrastes validos en claro/oscuro.
- En resoluciones pequenas, paneles deben apilarse y mantener acciones visibles.
- Estados de carga, error y vacio deben tener accion de reintento cuando aplique.

## Graficos

- Dashboard puede usar barras, lineas y circulares si ayudan a decidir.
- Graficos deben mostrar valores, etiquetas y rangos entendibles.
- No usar graficos como decoracion; cada grafico debe responder una pregunta de negocio.
