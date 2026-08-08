const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const root = 'C:/dev/clinicapharma';
const docsDir = path.join(root, 'docs');
const shotsDir = path.join(docsDir, 'manual_screenshots');
const htmlPath = path.join(docsDir, 'manual_flujo_cliente_clinicapharma.html');
const pdfPath = path.join(docsDir, 'manual_flujo_cliente_clinicapharma.pdf');

function browserPath() {
  const candidates = [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  ];
  const found = candidates.find((candidate) => fs.existsSync(candidate));
  if (!found) throw new Error('No se encontro Chrome o Edge para generar el PDF.');
  return found;
}

function imgData(name) {
  const file = path.join(shotsDir, name);
  if (!fs.existsSync(file)) throw new Error(`Falta la captura: ${file}`);
  return `data:image/png;base64,${fs.readFileSync(file).toString('base64')}`;
}

function esc(text) {
  return text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

const screens = [
  {
    title: 'Entrar al sistema',
    image: '01_login.png',
    purpose: 'Aqui cada persona entra con su usuario. Esto ayuda a saber quien hizo cada movimiento.',
    steps: [
      'Abra Clinicapharma en el navegador.',
      'Escriba el usuario y la contrasena entregados por el administrador.',
      'Presione Entrar para ir a la pantalla principal.',
    ],
    tip: 'Cada empleado debe usar su propio usuario. No es recomendable compartir claves.',
  },
  {
    title: 'Revisar el dia en la pantalla principal',
    image: '02_dashboard.png',
    purpose: 'Esta pantalla funciona como el tablero del dia: muestra citas, ventas, cobros, alertas y pendientes.',
    steps: [
      'Revise las citas y pacientes pendientes.',
      'Mire las alertas de productos bajos o proximos a vencer.',
      'Use los resumenes de venta y caja para controlar el movimiento diario.',
    ],
    tip: 'Al iniciar el dia, esta es la primera pantalla que conviene revisar.',
  },
  {
    title: 'Registrar o buscar pacientes',
    image: '03_patients.png',
    purpose: 'Aqui se guardan los datos de las personas que llegan a consulta o compran en farmacia.',
    steps: [
      'Busque por nombre, identidad o telefono antes de crear un registro nuevo.',
      'Si no existe, agregue el paciente con sus datos principales.',
      'Abra su ficha para consultar historial, recetas o cobros anteriores.',
    ],
    tip: 'Evite duplicar pacientes. Primero busque, luego registre.',
  },
  {
    title: 'Organizar citas',
    image: '04_appointments.png',
    purpose: 'La agenda ayuda a ordenar las atenciones del dia y saber quien esta pendiente.',
    steps: [
      'Seleccione el paciente.',
      'Indique fecha, hora, doctor y motivo de visita.',
      'Actualice el estado de la cita segun avance la atencion.',
    ],
    tip: 'Una agenda actualizada evita confusiones entre recepcion, enfermeria y doctor.',
  },
  {
    title: 'Atender consulta y crear receta',
    image: '05_consultations.png',
    purpose: 'El personal autorizado registra signos, motivo de visita, diagnostico, tratamiento y receta.',
    steps: [
      'Seleccione el paciente que sera atendido.',
      'Registre la informacion de la consulta con lenguaje claro.',
      'Genere la receta cuando el doctor termine la atencion.',
      'Guarde el cobro o recibo de la consulta si corresponde.',
    ],
    tip: 'Si no hay enfermera, el doctor puede completar los datos necesarios de la preconsulta.',
  },
  {
    title: 'Vender en farmacia',
    image: '06_pharmacy.png',
    purpose: 'La farmacia permite buscar productos, elegir cantidades, aplicar descuentos o puntos y cobrar.',
    steps: [
      'Busque el producto por nombre, codigo o lote.',
      'Agregue los productos al carrito.',
      'Seleccione el cliente si desea acumular o usar puntos.',
      'Elija forma de pago: efectivo, tarjeta o transferencia.',
      'Emita recibo o factura segun la configuracion del negocio.',
    ],
    tip: 'El sistema descuenta del inventario para mantener el stock actualizado.',
  },
  {
    title: 'Controlar inventario y vencimientos',
    image: '07_inventory.png',
    purpose: 'El inventario muestra productos, lotes, existencias, precios, bodega, tienda y fechas de vencimiento.',
    steps: [
      'Registre productos y sus presentaciones.',
      'Agregue lotes con fecha de vencimiento y costo.',
      'Revise productos bajos o proximos a vencer.',
      'Traslade unidades de bodega a tienda cuando sea necesario.',
    ],
    tip: 'Revisar vencimientos con frecuencia ayuda a vender primero lo que esta mas cerca de vencer.',
  },
  {
    title: 'Cerrar caja',
    image: '08_cash.png',
    purpose: 'La caja ayuda a comparar lo vendido con el dinero recibido durante el dia.',
    steps: [
      'Revise los ingresos por efectivo, tarjeta y transferencia.',
      'Compare el total esperado con lo contado.',
      'Registre diferencias o notas si algo no coincide.',
      'Guarde el cierre para control diario y reportes.',
    ],
    tip: 'Hacer cierre por usuario mejora el control y reduce confusiones.',
  },
  {
    title: 'Configurar datos del negocio',
    image: '09_settings.png',
    purpose: 'Aqui se colocan datos del negocio, logo, telefono, direccion y opciones de documentos.',
    steps: [
      'Revise nombre comercial, RTN, direccion y telefono.',
      'Configure si el negocio usara recibos, facturas o ambos.',
      'Si aplica facturacion, agregue los datos autorizados por contabilidad.',
    ],
    tip: 'Si el cliente todavia no tiene datos fiscales listos, puede trabajar primero con recibos internos.',
  },
  {
    title: 'Consultar reportes',
    image: '10_reports.png',
    purpose: 'Los reportes sirven para revisar ventas, actividad, inventario, caja y resultados del negocio.',
    steps: [
      'Elija el reporte que desea revisar.',
      'Use fechas para consultar un dia, semana o mes.',
      'Revise la informacion antes de tomar decisiones de compra, cobro o control.',
    ],
    tip: 'Los reportes son mejores cuando el personal registra todo en el sistema el mismo dia.',
  },
];

const css = `
  @page { size: Letter; margin: 13mm; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    color: #1b2a2a;
    font-family: Arial, Helvetica, sans-serif;
    line-height: 1.48;
    background: #ffffff;
  }
  h1, h2, h3 { margin: 0; }
  p { margin: 0 0 10px; }
  .cover {
    min-height: 245mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 18px;
  }
  .brand {
    color: #00695c;
    font-size: 42px;
    letter-spacing: 0;
  }
  .subtitle {
    color: #334846;
    font-size: 23px;
    font-weight: 700;
  }
  .muted { color: #60706e; }
  .box {
    border: 1px solid #b7d8d2;
    background: #eef8f6;
    border-radius: 8px;
    padding: 14px 16px;
  }
  .toc {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 18px;
    margin-top: 12px;
  }
  .toc div {
    padding: 7px 9px;
    background: #f5faf9;
    border-left: 4px solid #009688;
  }
  .page {
    break-before: page;
    page-break-before: always;
    min-height: 245mm;
  }
  .section-title {
    color: #00695c;
    font-size: 24px;
    padding-bottom: 7px;
    border-bottom: 2px solid #b7d8d2;
    margin-bottom: 14px;
  }
  .flow {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 16px 0;
  }
  .flow div {
    border: 1px solid #cfe4e0;
    border-radius: 8px;
    padding: 10px;
    min-height: 62px;
    background: #f7fbfa;
    font-weight: 700;
    color: #2d4946;
  }
  .screen {
    break-before: page;
    page-break-before: always;
  }
  .screen h2 {
    color: #00695c;
    font-size: 22px;
    margin-bottom: 9px;
  }
  .purpose {
    font-size: 13px;
    color: #405654;
    margin-bottom: 10px;
  }
  ol {
    margin: 8px 0 12px 20px;
    padding: 0;
  }
  li { margin-bottom: 6px; }
  .tip {
    border-left: 5px solid #009688;
    background: #eef8f6;
    padding: 10px 12px;
    margin: 10px 0 12px;
    color: #2c4643;
  }
  img {
    width: 100%;
    border: 1px solid #bfd6d2;
    border-radius: 8px;
    display: block;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
  }
  th {
    background: #00695c;
    color: white;
    text-align: left;
    padding: 9px;
  }
  td {
    border: 1px solid #cfe0dd;
    padding: 9px;
    vertical-align: top;
  }
  footer {
    position: fixed;
    bottom: 5mm;
    left: 13mm;
    right: 13mm;
    color: #71817f;
    font-size: 9px;
    display: flex;
    justify-content: space-between;
  }
`;

const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Manual de flujo para cliente - Clinicapharma</title>
  <style>${css}</style>
</head>
<body>
  <footer><span>Clinicapharma - Manual para cliente</span><span>Uso diario del sistema</span></footer>
  <section class="cover">
    <div>
      <h1 class="brand">Clinicapharma</h1>
      <h2 class="subtitle">Manual sencillo del flujo del sistema</h2>
      <p class="muted">Guia pensada para duenos, recepcion, farmacia, caja y personal de clinica.</p>
    </div>
    <div class="box">
      <strong>Objetivo:</strong> explicar de forma clara como se usa el sistema en el dia a dia:
      desde que el paciente llega, hasta consulta, receta, venta en farmacia, caja y reportes.
    </div>
    <div>
      <h3>Contenido</h3>
      <div class="toc">
        ${screens.map((screen, index) => `<div>${index + 1}. ${esc(screen.title)}</div>`).join('')}
      </div>
    </div>
  </section>

  <section class="page">
    <h2 class="section-title">Flujo general del negocio</h2>
    <p>Clinicapharma organiza el trabajo de una clinica con farmacia en un solo lugar. La idea es que cada area registre lo que hace para que el negocio tenga control de pacientes, citas, productos, ventas, caja y reportes.</p>
    <div class="flow">
      <div>1. Recepcion registra o busca paciente</div>
      <div>2. Se agenda o confirma la cita</div>
      <div>3. Se atiende la consulta</div>
      <div>4. Se crea receta o cobro</div>
      <div>5. Farmacia vende productos</div>
      <div>6. Inventario se descuenta</div>
      <div>7. Caja revisa ingresos</div>
      <div>8. Administracion consulta reportes</div>
    </div>
    <div class="box">
      <strong>En palabras simples:</strong> el sistema ayuda a que nada quede "solo en papel" o "solo en la memoria".
      Cada venta, cita, consulta, receta y cierre queda registrado para revisarlo despues.
    </div>
    <table>
      <tr><th>Area</th><th>Que hace en el sistema</th></tr>
      <tr><td>Recepcion</td><td>Busca pacientes, registra nuevos datos y organiza citas.</td></tr>
      <tr><td>Doctor o enfermeria</td><td>Registra la atencion, signos importantes, diagnostico, tratamiento y receta.</td></tr>
      <tr><td>Farmacia</td><td>Vende productos, aplica descuentos o puntos y emite recibos.</td></tr>
      <tr><td>Caja</td><td>Revisa ingresos por efectivo, tarjeta y transferencia, y cierra el dia.</td></tr>
      <tr><td>Administracion</td><td>Configura datos del negocio, usuarios y revisa reportes.</td></tr>
    </table>
  </section>

  ${screens.map((screen, index) => `
    <section class="screen">
      <h2>${index + 1}. ${esc(screen.title)}</h2>
      <p class="purpose">${esc(screen.purpose)}</p>
      <h3>Pasos recomendados</h3>
      <ol>${screen.steps.map((step) => `<li>${esc(step)}</li>`).join('')}</ol>
      <div class="tip"><strong>Consejo:</strong> ${esc(screen.tip)}</div>
      <img src="${imgData(screen.image)}" alt="${esc(screen.title)}">
    </section>
  `).join('')}

  <section class="page">
    <h2 class="section-title">Rutina diaria recomendada</h2>
    <table>
      <tr><th>Momento</th><th>Que hacer</th></tr>
      <tr><td>Inicio del dia</td><td>Entrar al sistema, revisar citas, pacientes pendientes, caja anterior y alertas de inventario.</td></tr>
      <tr><td>Durante la atencion</td><td>Registrar cada paciente, cita, consulta, receta, venta y pago en el momento que ocurre.</td></tr>
      <tr><td>Durante ventas</td><td>Buscar bien el producto, seleccionar presentacion correcta y confirmar forma de pago.</td></tr>
      <tr><td>Antes de cerrar</td><td>Revisar ventas del dia, contar efectivo, comparar pagos y guardar cierre.</td></tr>
      <tr><td>Cada semana</td><td>Revisar productos bajos, productos por vencer, reportes de ventas y movimientos de caja.</td></tr>
    </table>
    <div class="box" style="margin-top: 16px;">
      <strong>Clave para el cliente:</strong> mientras mas constante sea el registro diario, mejores seran los reportes y el control del negocio.
    </div>
  </section>
</body>
</html>`;

fs.writeFileSync(htmlPath, html, 'utf8');

const port = 9333;
const userDataDir = path.join(os.tmpdir(), 'clinicapharma-pdf-client-profile');
fs.rmSync(userDataDir, { recursive: true, force: true });
const chrome = spawn(browserPath(), [
  '--headless=new',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${userDataDir}`,
  '--window-size=1440,950',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function getJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${url} ${res.status}`);
  return res.json();
}

async function waitBrowser() {
  for (let i = 0; i < 80; i += 1) {
    try {
      return await getJson(`http://127.0.0.1:${port}/json/version`);
    } catch (_) {
      await sleep(250);
    }
  }
  throw new Error('El navegador no inicio DevTools.');
}

class Cdp {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.id = 0;
    this.pending = new Map();
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result || {});
      }
    };
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
  }

  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  close() {
    this.ws.close();
  }
}

(async () => {
  let cdp;
  try {
    await waitBrowser();
    const fileUrl = `file:///${htmlPath.replaceAll('\\', '/')}`;
    const tabInfo = await getJson(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(fileUrl)}`, { method: 'PUT' });
    cdp = new Cdp(tabInfo.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await sleep(1200);
    const pdf = await cdp.send('Page.printToPDF', {
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: false,
    });
    fs.writeFileSync(pdfPath, Buffer.from(pdf.data, 'base64'));
    console.log(pdfPath);
  } finally {
    if (cdp) cdp.close();
    chrome.kill();
    fs.rmSync(userDataDir, { recursive: true, force: true });
  }
})().catch((error) => {
  try { chrome.kill(); } catch (_) {}
  console.error(error);
  process.exit(1);
});
