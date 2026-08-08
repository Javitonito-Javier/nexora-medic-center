# 📘 Manual de Usuario - Nexora Labs Medic Center

Bienvenido al sistema de gestión clínica más intuitivo del mercado. Este manual está diseñado para que todo el personal (desde recepcionistas hasta doctores) pueda usar el sistema sin necesidad de conocimientos técnicos avanzados.

---

## 🏁 1. Primeros Pasos

### Iniciar Sesión
1. Abra el sistema en su navegador o aplicación.
2. Ingrese su **Usuario** y **Contraseña**.
3. Presione "Ingresar".

> **Nota de Seguridad:** Si usted se aleja de su puesto por más de 2 minutos, el sistema se bloqueará automáticamente. Para volver a entrar, solo escriba su contraseña nuevamente.

### Roles del Sistema
El sistema detecta automáticamente su rol y muestra solo lo que necesita:
- **Recepcionista:** Agenda, Registro de Pacientes, Caja.
- **Doctor:** Consultas, Recetas, Historias Clínicas.
- **Enfermera:** Triaje, Signos Vitales, Vacunación.
- **Administrador:** Reportes, Configuración, Usuarios.

---

## 🏥 2. Módulo de Recepción

### Registrar un Paciente Nuevo
1. Haga clic en **"Nuevo Paciente"**.
2. Llene los datos básicos (Nombre, Teléfono, Identidad).
   - *Tip:* Solo los campos marcados con (*) son obligatorios. Puede completar el resto después.
3. Guarde. El sistema creará la ficha automáticamente.

### Agendar una Cita
1. Seleccione el paciente (puede buscar escribiendo parte de su nombre, incluso con errores).
2. Elija el doctor y la fecha/hora en el calendario.
3. Confirme la cita. El paciente recibirá un recordatorio (si está configurado).

### Cobro en Caja (POS)
1. Seleccione la venta del día o escanee el código de la receta.
2. El sistema mostrará los productos a cobrar.
3. Elija el método de pago (Efectivo, Tarjeta, Seguro).
4. Imprima o envíe el recibo.

---

## 👨‍⚕️ 3. Módulo Médico (Doctores y Enfermeras)

### Realizar una Consulta
1. En su lista de "Pacientes del Día", haga clic en el paciente.
2. **Importante:** Revise la **Barra Roja Superior** si el paciente tiene alergias o condiciones crónicas.
3. Escriba la nota de evolución, diagnóstico y tratamiento.
   - *Tranquilidad:* Si se va la luz mientras escribe, el sistema guarda borradores automáticos cada 30 segundos. No perderá nada.
4. Al finalizar, presione "Guardar Consulta".

### Recetar Medicamentos
1. Dentro de la consulta, vaya a la pestaña "Recetas".
2. Busque el medicamento por nombre.
3. Indique la dosis y frecuencia.
4. **Opción Avanzada:** Si hay varios doctores, puede aparecer el botón "Derivar a Especialista". Úselo para enviar el paciente a otro colega con un informe adjunto.
5. Guarde la receta. Puede imprimirla o enviarla digitalmente.

### Derivar Pacientes (Solo si hay múltiples doctores)
1. Al guardar la consulta, seleccione "Derivar".
2. Elija el especialista destino y la prioridad.
3. El especialista recibirá una notificación y podrá ver su historia completa.
4. Cuando el especialista termine, el paciente regresará a su lista con el informe de vuelta.

---

## 💊 4. Módulo de Farmacia e Inventario

### Despachar una Receta
1. Busque la receta pendiente por nombre del paciente o número de ticket.
2. El sistema le mostrará los medicamentos exactos y sus lotes (fechas de vencimiento).
3. **Regla de Oro:** El sistema sugiere automáticamente el lote que vence primero (FEFO).
   - *Excepción:* Si el cliente prefiere otro lote o hay daño físico, puede cambiarlo manualmente haciendo clic en "Cambiar Lote".
4. Confirme la entrega y marque como "Despachado".

### Control de Inventario
- Las alertas de stock bajo aparecen en amarillo.
- Los productos próximos a vencer (<30 días) aparecen en rojo.
- Nunca elimine productos; si se equivoca, use "Anular Movimiento" para mantener el registro auditado.

---

## 🆘 5. Preguntas Frecuentes y Solución de Problemas

| Problema | Solución |
|----------|----------|
| **"Se fue la luz/internet mientras guardaba"** | No haga nada. El sistema recuperó su trabajo automáticamente. Verifique que el ícono de "Nube" esté verde. |
| **"La pantalla se puso negra"** | Es el bloqueo de seguridad. Escriba su contraseña para desbloquear. |
| **"No encuentro al paciente en la lista"** | Use la barra de búsqueda y escriba solo una parte del nombre (ej. "Juan" en lugar de "Juan Pérez"). El sistema es inteligente y lo encontrará. |
| **"Quiero borrar un error"** | No use "Borrar". Use "Anular" o "Corregir" para que quede registrado en la auditoría. |

---

## 📞 Soporte
Si tiene dudas que no están en este manual, contacte al administrador del sistema o al soporte técnico.

*¡Gracias por usar Nexora Labs Medic Center!*
