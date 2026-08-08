const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');
const root = 'C:/dev/clinicapharma';
const outDir = path.join(root, 'docs', 'manual_screenshots');
const pdfPath = path.join(root, 'docs', 'manual_paso_a_paso_clinicapharma.pdf');
const htmlPath = path.join(outDir, 'manual_paso_a_paso_clinicapharma.html');
fs.mkdirSync(outDir, { recursive: true });

const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const devtoolsPort = 9334;
const userDataDir = path.join(os.tmpdir(), 'clinicapharma-module-manual-profile');
fs.rmSync(userDataDir, { recursive: true, force: true });
const chrome = spawn(chromePath, [
  '--headless=new',
  `--remote-debugging-port=${devtoolsPort}`,
  `--user-data-dir=${userDataDir}`,
  '--window-size=1440,950',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} ${res.status}`);
  return res.json();
}
async function waitChrome() {
  for (let i = 0; i < 60; i++) {
    try { return await getJson(`http://127.0.0.1:${devtoolsPort}/json/version`); } catch (_) { await sleep(500); }
  }
  throw new Error('Chrome DevTools did not start');
}
class Cdp {
  constructor(wsUrl) { this.wsUrl = wsUrl; this.id = 0; this.pending = new Map(); }
  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message)); else resolve(msg.result || {});
      }
    };
    await new Promise((resolve, reject) => { this.ws.onopen = resolve; this.ws.onerror = reject; });
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  close() { this.ws.close(); }
}
function imgData(file) {
  const b64 = fs.readFileSync(file).toString('base64');
  return `data:image/png;base64,${b64}`;
}
async function screenshot(cdp, name) {
  await sleep(1600);
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  const file = path.join(outDir, `${name}.png`);
  fs.writeFileSync(file, Buffer.from(result.data, 'base64'));
  return file;
}
async function evaluate(cdp, expression) {
  return cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
}
async function click(cdp, x, y) {
  await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
}
async function focusAndType(cdp, x, y, text) {
  await click(cdp, x, y);
  await sleep(250);
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Control', code: 'ControlLeft', windowsVirtualKeyCode: 17 });
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, modifiers: 2 });
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, modifiers: 2 });
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Control', code: 'ControlLeft', windowsVirtualKeyCode: 17 });
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8 });
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8 });
  await cdp.send('Input.insertText', { text });
}
async function navigateMenu(cdp, y) {
  await click(cdp, 94, y);
  await sleep(2200);
}
(async () => {
  try {
    await waitChrome();
    const tabInfo = await (await fetch(`http://127.0.0.1:${devtoolsPort}/json/new?http://127.0.0.1:8080`, { method: 'PUT' })).json();
    const cdp = new Cdp(tabInfo.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 950, deviceScaleFactor: 1, mobile: false });
    await sleep(3500);

    const shots = [];
    shots.push({ key: 'login', title: 'Acceso de personal', file: await screenshot(cdp, '01_login') });
    await focusAndType(cdp, 720, 485, 'admin');
    await focusAndType(cdp, 720, 552, 'admin123');
    await click(cdp, 720, 617);
    await sleep(4500);
    shots.push({ key: 'dashboard', title: 'Dashboard principal', file: await screenshot(cdp, '02_dashboard') });

    const routes = [
      ['patients', 'Pacientes y clientes', 142],
      ['appointments', 'Citas y agenda', 190],
      ['consultations', 'Consulta medica', 238],
      ['staff', 'Personal y permisos', 286],
      ['pharmacy', 'Farmacia POS', 334],
      ['inventory', 'Inventario y lotes', 382],
      ['cash', 'Cajas y cierres', 430],
      ['reports', 'Reportes', 478],
      ['settings', 'Configuracion del negocio/SAR', 526],
    ];
    for (const [key, title, y] of routes) {
      await navigateMenu(cdp, y);
      shots.push({ key, title, file: await screenshot(cdp, `${String(shots.length + 1).padStart(2, '0')}_${key}`) });
    }

    const css = `
      @page { size: Letter; margin: 14mm; }
      body { font-family: Arial, sans-serif; color: #182421; line-height: 1.45; }
      h1 { color: #00796b; font-size: 30px; margin-bottom: 4px; }
      h2 { color: #00796b; border-bottom: 1px solid #b9d7d1; padding-bottom: 5px; margin-top: 28px; }
      h3 { color: #24524b; margin-bottom: 4px; }
      .cover { min-height: 790px; display: flex; flex-direction: column; justify-content: center; }
      .muted { color: #5b6865; }
      .box { background: #eef7f5; border: 1px solid #b9d7d1; border-radius: 8px; padding: 12px 14px; margin: 14px 0; }
      .step { break-inside: avoid; page-break-inside: avoid; margin-bottom: 24px; }
      img { width: 100%; border: 1px solid #c7d8d4; border-radius: 8px; margin-top: 10px; }
      ul, ol { padding-left: 22px; }
      .pagebreak { break-before: page; page-break-before: always; }
      code { background: #eef1f0; padding: 1px 4px; border-radius: 4px; }
    `;
    const sections = [
      { shot: shots[0], text: ['Abrir el sistema en el navegador.', 'Ingresar con usuario y contrasena asignados por el administrador.', 'Presionar Entrar.'] },
      { shot: shots[1], text: ['Revisar citas, pacientes pendientes, ventas del dia, ventas del mes, bajo stock, lotes por vencer y notificaciones.', 'Usar el boton Actualizar cuando se hagan cambios desde otra computadora.'] },
      { shot: shots[2], text: ['Buscar pacientes por nombre, identidad o telefono.', 'Registrar nuevos pacientes/clientes con datos generales, alergias y antecedentes.', 'Abrir el expediente para ver historial, recetas y cobros.'] },
      { shot: shots[3], text: ['Crear citas para pacientes registrados.', 'Definir fecha, hora, doctor, motivo y estado.', 'Revisar alertas desde 3 dias antes y mantenerlas hasta atender o cancelar.', 'Usar WhatsApp para abrir el mensaje prellenado al numero +50492398074.'] },
      { shot: shots[4], text: ['Seleccionar paciente y registrar signos vitales, motivo, historia clinica, diagnostico y tratamiento.', 'El doctor o enfermera pueden llenar la informacion segun el flujo real de la clinica.', 'Luego se puede crear receta y cobrar consulta/servicio.'] },
      { shot: shots[5], text: ['Crear usuarios del negocio con nombre, telefono y area.', 'Asignar roles y permisos por modulo segun el trabajo real de cada persona.', 'Activar o desactivar usuarios y marcar personal de turno.'] },
      { shot: shots[6], text: ['Buscar producto por nombre, SKU, codigo de barra o codigo de lote.', 'Seleccionar presentacion: unidad, blister, caja, frasco u otra definida.', 'Seleccionar cliente para puntos/descuentos, metodo de pago y documento.', 'Cobrar con efectivo, tarjeta o transferencia; transferencia solicita banco y comprobante.'] },
      { shot: shots[7], text: ['Crear productos con laboratorio, proveedor, presentaciones, precio de venta, precio de vineta y stock minimo.', 'Para frascos o insumos, usar venta individual: cada frasco o pieza equivale a 1 unidad base.', 'Registrar lotes con vencimiento, costo de compra, bodega y tienda.', 'Trasladar producto de bodega a tienda sin contarlo como venta.', 'El POS descuenta por PEPS/FEFO y conserva trazabilidad por lote.'] },
      { shot: shots[8], text: ['Consultar cierre de farmacia y clinica por fecha y usuario.', 'Ver ventas/cobros por efectivo, tarjeta y transferencia.', 'Usar estos totales para cierre diario y control mensual.'] },
      { shot: shots[9], text: ['Revisar reportes operativos y listados relevantes.', 'Usar este modulo para evolucionar reportes de puntos, ventas, inventario y fiscal.'] },
      { shot: shots[10], text: ['Configurar datos del negocio: nombre comercial, razon social, RTN, direccion, telefono y correo.', 'Agregar logo por URL o data URL.', 'Activar o desactivar facturas; si el cliente no tiene CAI, se dejan solo recibos.', 'Configurar CAI, rango, punto de emision, fecha limite y pie legal cuando aplique.'] },
    ];
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
      <section class="cover">
        <h1>Clinicapharma</h1>
        <h2>Sistema para clinica y farmacia</h2>
        <p class="muted">Manual de uso y presentacion del MVP</p>
        <div class="box"><strong>Alcance:</strong> pacientes, citas, consulta medica, recetas, personal, farmacia POS, inventario por lotes, cajas, reportes, configuracion SAR y licenciamiento local.</div>
        <p>Este documento sirve para presentar el sistema y guiar al personal modulo por modulo en el uso diario.</p>
      </section>
      <section class="pagebreak"><h2>Resumen general</h2>
        <ul>
          <li><strong>Clinica:</strong> registro de pacientes, citas, expediente, consultas, recetas y cobros.</li>
          <li><strong>Farmacia:</strong> POS, busqueda de productos, descuentos, puntos, pagos y recibos/facturas.</li>
          <li><strong>Inventario:</strong> productos, presentaciones, proveedores, laboratorios, lotes, vencimientos, bodega y tienda.</li>
          <li><strong>Administracion:</strong> usuarios, roles, cajas, reportes, configuracion fiscal SAR y licencia offline.</li>
        </ul>
      </section>
      ${sections.map((s, i) => `<section class="step ${i === 0 ? 'pagebreak' : ''}"><h2>${i + 1}. ${s.shot.title}</h2><ol>${s.text.map(t => `<li>${t}</li>`).join('')}</ol><img src="${imgData(s.shot.file)}"></section>`).join('\n')}
      <section class="pagebreak"><h2>Recomendaciones de operacion local</h2>
        <ul>
          <li>Usar una computadora principal como servidor local con PostgreSQL, backend y frontend.</li>
          <li>Asignar IP fija al servidor para que recepcion, farmacia y doctor entren desde el navegador.</li>
          <li>Hacer respaldo diario de PostgreSQL.</li>
          <li>Configurar usuarios por rol y cerrar caja por usuario.</li>
          <li>Activar facturas solo cuando el negocio tenga CAI y rango autorizado.</li>
        </ul>
      </section>
    </body></html>`;
    fs.writeFileSync(htmlPath, html, 'utf8');

    await cdp.send('Page.navigate', { url: 'file:///' + htmlPath.replaceAll('\\', '/') });
    await sleep(1500);
    const pdf = await cdp.send('Page.printToPDF', { printBackground: true, preferCSSPageSize: true });
    fs.writeFileSync(pdfPath, Buffer.from(pdf.data, 'base64'));
    cdp.close();
    console.log(pdfPath);
  } finally {
    chrome.kill();
    fs.rmSync(userDataDir, { recursive: true, force: true });
  }
})().catch((err) => { console.error(err); try { chrome.kill(); } catch (_) {} process.exit(1); });


