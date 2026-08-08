# MVP v1

## Objetivo

Crear una web app local para clinica y farmacia con recibos internos, inventario, agenda, consulta medica, farmacia POS, cajas separadas, puntos y reportes.

## Primera entrega funcional

1. Autenticacion basica y usuarios con permisos.
2. Dashboard modular por permisos.
3. Pacientes/clientes.
4. Agenda de citas.
5. Preconsulta flexible: enfermero o doctor.
6. Consulta medica: motivo, SOAP, diagnostico, tratamiento y receta.
7. Caja clinica con recibos.
8. Farmacia POS con recibos.
9. Inventario por producto, lote, vencimiento, ubicacion y presentacion.
10. Puntos de farmacia como descuento con minimo L 50.00.
11. Reportes diarios y mensuales.

## Reglas clave

- Clinica y farmacia tienen cajas separadas.
- Hay cierre de caja por usuario.
- Los puntos solo se ganan por compras en farmacia.
- La parte pagada con puntos no genera nuevos puntos.
- Tercera/cuarta edad se calcula desde fecha de nacimiento, con reglas configurables.
- Facturacion fiscal queda como modulo opcional separado.
