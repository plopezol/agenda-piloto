from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .api import router as api_router

app = FastAPI()
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Agenda Piloto</title>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen;
  margin: 0;
  padding: 1rem;
  background: #f9f9f9;
}

h1 {
  text-align: center;
  margin-bottom: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  position: relative;
}

/* Estados visuales */
.card.hueco {
  border-left: 6px solid #adb5bd;
  background: #f8f9fa;
}

.card.confirmada {
  border-left: 6px solid #28a745;
  background: #f4fff7;
}

.card.cancelada {
  border-left: 6px solid #dc3545;
  background: #fff5f5;
}

.estado-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  user-select: none;
}

.estado-hueco {
  background: #dee2e6;
  color: #495057;
}

.estado-confirmada {
  background: #28a745;
  color: white;
}

.estado-cancelada {
  background: #dc3545;
  color: white;
}

.btn {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  display: inline-block;
  text-align: center;
  user-select: none;
  transition: background-color 0.2s ease;
  margin: 0.15rem 0;
  width: 100%;
  padding: 0.4rem 0.6rem;
  font-size: 0.9rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-whatsapp {
  background-color: #25D366;
  color: white;
}
.btn-whatsapp:hover {
  background-color: #1ebe5a;
}

.btn-small {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  width: auto;
  margin: 0 0.15rem 0.15rem 0;
}

.flex-row {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.5rem;
}

.actions-row {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-top: 0.6rem;
  justify-content: flex-start;
}

.chip {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 16px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
  margin-left: 0.5rem;
  user-select:none;
  border: 1.5px solid transparent;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.chip.avisada-si {
  background: #28a745;
  color: white;
  border-color: #28a745;
}
.chip.avisada-si:hover {
  background: #218838;
  border-color: #1e7e34;
}

.chip.avisada-no {
  background: #adb5bd;
  color: #212529;
  border-color: #adb5bd;
}
.chip.avisada-no:hover {
  background: #909ba1;
  border-color: #868e96;
}

/* Menu contextual */
.menu {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  cursor: pointer;
  font-size: 1.4rem;
  background: #e9ecef;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu:hover {
  background-color: #e2e6ea;
}

.menu-content {
  display: none;
  position: absolute;
  top: 2.4rem;
  right: 1rem;
  background: white;
  box-shadow: 0 2px 7px rgba(0,0,0,0.15);
  border-radius: 6px;
  z-index: 10;
  min-width: 140px;
  font-size: 0.85rem;
  user-select: none;
}

.menu-content button {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  color: #333;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  transition: background-color 0.15s ease;
}

.menu-content button:last-child {
  border-bottom: none;
}

.menu-content button:hover {
  background-color: #f1f3f5;
}

/* Responsive & mobile-first adjustments */
#fechaSelector {
  width: 100%;
  font-size: 1rem;
  padding: 0.4rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

#fechaSelector, .btn-primary, .btn-secondary, .btn-whatsapp {
  width: 100%;
  margin-bottom: 0.5rem;
}

@media (min-width: 600px) {
  #fechaSelector {
    width: auto;
    margin-right: 0.5rem;
  }
  .btn-primary, .btn-secondary, .btn-whatsapp {
    width: auto;
    margin-bottom: 0;
  }
  .flex-row {
    justify-content: flex-start;
  }
  .actions-row {
    justify-content: flex-start;
  }
}

/* MODALES */
#crearCitaModal,
#moverCitaModal {
  display: none;
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.45);
}

.modal-content {
  background: white;
  max-width: 420px;
  width: 92%;
  margin: auto;
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.25);
}

.modal-content input,
.modal-content select {
  width: 100%;
  margin-bottom: 0.6rem;
  padding: 0.4rem;
}

#moverCitaModal select {
  width: 100%;
  padding: 0.4rem;
  font-size: 1rem;
}

.alert {
  border-radius: 6px;
  padding: 0.6rem;
  margin-top: 0.6rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.alert-retraso {
  background: #fff3cd;
  border-left: 6px solid #ffc107;
  color: #856404;
}

.alert-adelanto {
  background: #e2f0ff;
  border-left: 6px solid #0d6efd;
  color: #084298;
}
</style>
</head>

<body>

<h1>Agenda Piloto</h1>
<div style="text-align:center; margin-bottom:1rem;">
  <input type="date" id="fechaSelector" />
  <button class="btn btn-primary" onclick="cambiarFecha()">Ir al día</button>
  <button class="btn btn-secondary" onclick="toggleHuecos()">👁️ Huecos</button>
</div>

<div id="agenda"></div>

<div id="crearCitaModal">
  <div class="modal-content">
    <h3 id="modalTitulo">Crear / Editar cita</h3>
    <input type="hidden" id="row_sheet" />

    <label>Cliente</label>
    <input id="cliente" />

    <label>Teléfono</label>
    <input id="telefono" />

    <label>Servicio</label>
    <input id="servicio" />

    <label>Duración (min)</label>
    <input type="number" id="duracion" value="30" />

    <label>Flexibilidad</label>
    <select id="flexibilidad">
      <option>No</option>
      <option>Si</option>
    </select>

    <button class="btn btn-primary" onclick="guardarCita()">Guardar</button>
    <button class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
  </div>
</div>

<div id="moverCitaModal">
  <div class="modal-content">
    <h3>Mover cita</h3>
    <input type="hidden" id="row_origen" />

    <label>Hora destino</label>
    <select id="row_destino"></select>

    <button class="btn btn-primary" onclick="confirmarMover()">Mover</button>
    <button class="btn btn-secondary" onclick="cerrarMover()">Cancelar</button>
  </div>
</div>

<script>
/* ====== ACCESO PROTEGIDO (LOPD BÁSICO) ====== */
const AGENDA_PASSWORD = "010819"; // ⚠️ cambia esto por la contraseña que quieras
const AUTH_KEY = "agenda_auth_ok";

function checkAuth() {
  if (localStorage.getItem(AUTH_KEY) === "true") return true;

  const pass = prompt("🔒 Introduce la contraseña para acceder a la agenda:");
  if (pass === AGENDA_PASSWORD) {
    localStorage.setItem(AUTH_KEY, "true");
    return true;
  }
  alert("❌ Contraseña incorrecta");
  return false;
}
/* =========================================== */

let mostrarHuecos = true;

function toggleHuecos() {
  mostrarHuecos = !mostrarHuecos;
  cargarAgenda();
}

let fechaSeleccionada = null;

function parseHora(hora) {
  if (!hora) return 0;
  const [h, m] = hora.split(':').map(Number);
  return h * 60 + (m || 0);
}

function closeAllMenus() {
  document.querySelectorAll('.menu-content').forEach(menu => {
    menu.style.display = 'none';
  });
}

async function cargarAgenda() {
  if (!checkAuth()) return;
  const url = fechaSeleccionada ? `/agenda?fecha=${fechaSeleccionada}` : '/agenda';
  const res = await fetch(url);
  const data = await res.json();
  const avisosRes = await fetch(fechaSeleccionada ? `/agenda/avisos?fecha=${fechaSeleccionada}` : '/agenda/avisos');
  const avisos = await avisosRes.json();
  const cont = document.getElementById('agenda');
  cont.innerHTML = '';

  data.forEach(row => {
    if (!mostrarHuecos && row.Estado === 'hueco') return;
    const estado = row.Estado;
    const card = document.createElement('div');
    card.className = 'card ' + estado;

    let avisadaChip = '';
    if (estado !== 'hueco') {
      const avisada = row.Avisada === 'Si' ? 'Si' : 'No';
      const chipClass = avisada === 'Si' ? 'avisada-si' : 'avisada-no';

      avisadaChip = `<span class="chip ${chipClass}" onclick="toggleAvisada(${row.row_sheet}, '${avisada}', this)" title="Toggle Avisada">${avisada}</span>`;
    }

    // Buttons container
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'actions-row';

    // WhatsApp Button (prominent if telefono exists)
    let whatsappBtn = '';
    if (estado !== 'hueco' && row.Telefono) {
      const telefono = row.Telefono.replace(/\s+/g, '');
      const fechaTxt = fechaSeleccionada || 'hoy';
      let mensaje = '';

      if (estado === 'confirmada') {
        mensaje = `Hola ${row.Cliente || ''} 😊\nTe confirmamos tu cita el ${fechaTxt} a las ${row.Hora} para ${row.Servicio}.`;
      } else if (estado === 'cancelada') {
        mensaje = `Hola ${row.Cliente || ''} 😊\nConfirmamos la cancelación de tu cita el ${fechaTxt} a las ${row.Hora}.`;
      }

      const urlWA = `https://wa.me/${telefono}?text=${encodeURIComponent(mensaje)}`;
      whatsappBtn = document.createElement('a');
      whatsappBtn.href = urlWA;
      whatsappBtn.target = '_blank';
      whatsappBtn.rel = 'noopener noreferrer';
      whatsappBtn.innerHTML = '💬 WhatsApp';
      whatsappBtn.className = 'btn btn-whatsapp';
      actionsDiv.appendChild(whatsappBtn);
    }

// For hueco cards: only show Crear cita and Avisar clientas flexibles buttons
    if (estado === 'hueco') {
      // Crear cita button
      const crearBtn = document.createElement('button');
      crearBtn.className = 'btn btn-primary';
      crearBtn.textContent = '➕ Crear cita';
      crearBtn.onclick = () => abrirModal(row.row_sheet);
      actionsDiv.appendChild(crearBtn);

      // Nuevo botón: Avisar clientas flexibles
      const avisarBtn = document.createElement('button');
      avisarBtn.innerHTML = '💬 Avisar clientas flexibles';
      avisarBtn.className = 'btn btn-whatsapp';
      avisarBtn.onclick = () => avisarHuecoWhatsApp(row.row_sheet, row.Hora);
      actionsDiv.appendChild(avisarBtn);

      card.appendChild(actionsDiv);
      card.innerHTML = `
        <strong>Hora:</strong> ${row.Hora}<br/>
        <strong>Servicio:</strong> ${row.Servicio} – ${row.Duración} min<br/>
        <span class="estado-badge estado-${estado}">${estado}</span>
      `;
      card.appendChild(actionsDiv);
      cont.appendChild(card);
      return; // Skip rest for hueco
    }

    // Non-hueco cards

    // Editar button (secondary)
    const editarBtn = document.createElement('button');
    editarBtn.className = 'btn btn-secondary';
    editarBtn.textContent = '✏️ Editar';
    editarBtn.onclick = () => abrirModal(row.row_sheet, row);
    actionsDiv.appendChild(editarBtn);

    // Menu button ⋮
    const menuBtn = document.createElement('div');
    menuBtn.className = 'menu';
    menuBtn.textContent = '⋮';

    // Menu content
    const menuContent = document.createElement('div');
    menuContent.className = 'menu-content';

    // Helper to create menu buttons
    function createMenuButton(text, onClick) {
      const btn = document.createElement('button');
      btn.textContent = text;
      btn.onclick = () => {
        onClick();
        menuContent.style.display = 'none';
      };
      return btn;
    }

    // Confirmar
    menuContent.appendChild(createMenuButton('Confirmar', () => estado(row.row_sheet, 'confirmada')));
    // Cancelar
    menuContent.appendChild(createMenuButton('Cancelar', () => estado(row.row_sheet, 'cancelada')));
    // Pasar a hueco
    menuContent.appendChild(createMenuButton('Pasar a hueco', () => estado(row.row_sheet, 'hueco')));
    // Mover
    menuContent.appendChild(createMenuButton('Mover', () => {
      abrirMover(row.row_sheet);
      menuContent.style.display = 'none';
    }));

    menuBtn.appendChild(menuContent);

    // Toggle menu visibility
    menuBtn.onclick = (e) => {
      e.stopPropagation();
      closeAllMenus();
      if (menuContent.style.display === 'block') {
        menuContent.style.display = 'none';
      } else {
        menuContent.style.display = 'block';
      }
    };

    // Clicking outside closes menus
    document.body.addEventListener('click', () => {
      closeAllMenus();
    });

    actionsDiv.appendChild(menuBtn);

    // Info cliente with tel link if available
    let infoCliente = '';
    if (row.Telefono) {
      const telefono = row.Telefono;
      const telHtml = `<a href="tel:${telefono.replace(/\\s+/g, '')}" style="color:#007bff; text-decoration:none;">📞 ${telefono}</a>`;
      infoCliente = `
        <strong>Cliente:</strong> ${row.Cliente || '-'}<br/>
        <strong>Teléfono:</strong> ${telHtml}<br/>
      `;
    } else {
      infoCliente = `
        <strong>Cliente:</strong> ${row.Cliente || '-'}<br/>
        <strong>Teléfono:</strong> -<br/>
      `;
    }

    card.innerHTML = `
      <strong>Hora:</strong> ${row.Hora}<br/>
      ${infoCliente}
      <strong>Servicio:</strong> ${row.Servicio} – ${row.Duración} min<br/>
      <span class="estado-badge estado-${estado}">${estado}</span>
      ${avisadaChip}
    `;

    // Avisos de retraso / adelanto
    const avisosRow = avisos.filter(a =>
      (a.afecta_a && a.afecta_a.row_sheet === row.row_sheet) ||
      (a.posible_con && a.posible_con.row_sheet === row.row_sheet)
    );

    avisosRow.forEach(a => {
      const alert = document.createElement('div');
      alert.className = 'alert ' + (a.tipo === 'retraso' ? 'alert-retraso' : 'alert-adelanto');

      if (a.tipo === 'retraso') {
        alert.innerHTML = `
          ⚠️ Retraso estimado de <strong>${a.minutos} min</strong><br/>
          <div class="flex-row">
            <button class="btn btn-secondary btn-small" onclick="aplicarRetraso(${a.afecta_a.row_sheet}, 5)">+5</button>
            <button class="btn btn-secondary btn-small" onclick="aplicarRetraso(${a.afecta_a.row_sheet}, 10)">+10</button>
            <button class="btn btn-secondary btn-small" onclick="aplicarRetraso(${a.afecta_a.row_sheet}, 15)">+15</button>
            <button class="btn btn-whatsapp btn-small"
              onclick="avisarRetrasoWhatsApp(
                '${row.Cliente || ''}',
                '${row.Telefono || ''}',
                ${a.minutos}
              )">💬 Avisar</button>
          </div>
        `;
      } else {
        alert.innerHTML = `⏩ Adelanto posible de <strong>${a.minutos} min</strong>`;
      }

      card.appendChild(alert);
    });

    card.appendChild(actionsDiv);
    cont.appendChild(card);
  });
}

function cambiarFecha() {
  const f = document.getElementById('fechaSelector').value;
  fechaSeleccionada = f ? f : null;
  cargarAgenda();
}

async function estado(row, estado) {
  const url = fechaSeleccionada ? `/agenda/estado?fecha=${fechaSeleccionada}` : '/agenda/estado';
  await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({row_sheet: row, estado})
  });
  cargarAgenda();
}

async function toggleAvisada(row, valorActual, chipElem = null) {
  const nuevoValor = valorActual === 'Si' ? 'No' : 'Si';
  const baseUrl = fechaSeleccionada ? `/agenda/avisada?fecha=${fechaSeleccionada}` : '/agenda/avisada';
  const url = `${baseUrl}&row_sheet=${row}&avisada=${nuevoValor}`;

  await fetch(url, {
    method: 'POST'
  });

  // Update chip appearance immediately if element provided
  if (chipElem) {
    chipElem.textContent = nuevoValor;
    if (nuevoValor === 'Si') {
      chipElem.classList.remove('avisada-no');
      chipElem.classList.add('avisada-si');
      chipElem.setAttribute('onclick', `toggleAvisada(${row}, '${nuevoValor}', this)`);
    } else {
      chipElem.classList.remove('avisada-si');
      chipElem.classList.add('avisada-no');
      chipElem.setAttribute('onclick', `toggleAvisada(${row}, '${nuevoValor}', this)`);
    }
  } else {
    cargarAgenda();
  }
}

function abrirModal(row, datos = null) {
  document.getElementById('row_sheet').value = row;

  // Reset fields
  document.getElementById('cliente').value = '';
  document.getElementById('telefono').value = '';
  document.getElementById('servicio').value = '';
  document.getElementById('duracion').value = 30;
  document.getElementById('flexibilidad').value = 'No';

  // Si vienen datos (editar)
  if (datos) {
    document.getElementById('cliente').value = datos.Cliente || '';
    document.getElementById('telefono').value = datos.Telefono || '';
    document.getElementById('servicio').value = datos.Servicio || '';
    document.getElementById('duracion').value = datos.Duración || 30;
    document.getElementById('flexibilidad').value = datos.Flexibilidad || 'No';
  }

  document.getElementById('crearCitaModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function cerrarModal() {
  document.getElementById('crearCitaModal').style.display = 'none';
  document.body.style.overflow = 'auto';
}

async function guardarCita() {
  const url = fechaSeleccionada ? `/agenda/cita?fecha=${fechaSeleccionada}` : '/agenda/cita';
  await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      row_sheet: parseInt(document.getElementById('row_sheet').value),
      cliente: document.getElementById('cliente').value,
      telefono: document.getElementById('telefono').value,
      servicio: document.getElementById('servicio').value,
      duracion: parseInt(document.getElementById('duracion').value),
      flexibilidad: document.getElementById('flexibilidad').value
    })
  });
  cerrarModal();
  cargarAgenda();
}

async function abrirMover(rowOrigen) {
  document.getElementById('row_origen').value = rowOrigen;

  const url = fechaSeleccionada ? `/agenda?fecha=${fechaSeleccionada}` : '/agenda';
  const res = await fetch(url);
  const data = await res.json();

  const select = document.getElementById('row_destino');
  select.innerHTML = '';

  data.forEach(row => {
    if (row.Estado === 'hueco') {
      const opt = document.createElement('option');
      opt.value = row.row_sheet;
      opt.textContent = row.Hora;
      select.appendChild(opt);
    }
  });

  document.getElementById('moverCitaModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function cerrarMover() {
  document.getElementById('moverCitaModal').style.display = 'none';
  document.body.style.overflow = 'auto';
}

async function confirmarMover() {
  const rowOrigen = parseInt(document.getElementById('row_origen').value);
  const rowDestino = parseInt(document.getElementById('row_destino').value);

  const urlAgenda = fechaSeleccionada ? `/agenda?fecha=${fechaSeleccionada}` : '/agenda';
  const res = await fetch(urlAgenda);
  const data = await res.json();

  const citaOrigen = data.find(r => r.row_sheet === rowOrigen);
  const destino = data.find(r => r.row_sheet === rowDestino);

  if (!citaOrigen || !destino) {
    alert('Error al mover la cita');
    return;
  }

  const duracionCita = parseInt(citaOrigen.Duración || 0);

  // Calcular minutos libres hasta la siguiente cita
  const destinoHoraMin = parseHora(destino.Hora);
  let minutosLibres = Infinity;

  const siguientes = data
    .filter(r => r.row_sheet !== rowOrigen)
    .filter(r => parseHora(r.Hora) > destinoHoraMin)
    .sort((a, b) => parseHora(a.Hora) - parseHora(b.Hora));

  if (siguientes.length > 0) {
    minutosLibres = parseHora(siguientes[0].Hora) - destinoHoraMin;
  }

  // Si no cabe, pedir confirmación
  if (duracionCita > minutosLibres) {
    const ok = confirm(
      `⚠️ La cita dura ${duracionCita} min pero solo hay ${minutosLibres} min libres.\n\n¿Quieres moverla igualmente?`
    );
    if (!ok) return;
  }

  const baseUrl = fechaSeleccionada ? `/agenda/mover?fecha=${fechaSeleccionada}` : '/agenda/mover';
  const url = `${baseUrl}&row_origen=${rowOrigen}&row_destino=${rowDestino}`;

  await fetch(url, { method: 'POST' });
  cerrarMover();
  cargarAgenda();
}

// ======== WHATSAPP ASISTIDO PARA HUECOS ========
async function avisarHuecoWhatsApp(rowSheet, horaHueco) {
  const url = fechaSeleccionada
    ? `/agenda/hueco/sugeridas?fecha=${fechaSeleccionada}&row_sheet=${rowSheet}`
    : `/agenda/hueco/sugeridas?row_sheet=${rowSheet}`;

  const res = await fetch(url);
  const clientas = await res.json();

  if (!clientas.length) {
    alert("No hay clientas flexibles que encajen en este hueco.");
    return;
  }

  const ok = confirm(
    `Se va a avisar a ${clientas.length} clienta(s) por WhatsApp.\n\n¿Quieres continuar?`
  );
  if (!ok) return;

  for (const c of clientas) {
    if (!c.Telefono) continue;

    const telefono = c.Telefono.replace(/\s+/g, '');
    const mensaje =
      `Hola ${c.Cliente || ''} 😊\n` +
      `Se ha quedado un hueco libre el ${fechaSeleccionada || 'hoy'} a las ${horaHueco} ` +
      `para ${c.Servicio}.\n¿Te vendría bien?`;

    window.open(
      `https://wa.me/${telefono}?text=${encodeURIComponent(mensaje)}`,
      '_blank'
    );

    // Marcar como avisada
    const urlAvisada = fechaSeleccionada
      ? `/agenda/avisada?fecha=${fechaSeleccionada}&row_sheet=${c.row_sheet}&avisada=Si`
      : `/agenda/avisada?row_sheet=${c.row_sheet}&avisada=Si`;

    await fetch(urlAvisada, { method: 'POST' });
  }
}

// ======== WHATSAPP ASISTIDO PARA RETRASOS ========
function avisarRetrasoWhatsApp(cliente, telefono, minutos) {
  if (!telefono) {
    alert("No hay teléfono para esta clienta");
    return;
  }

  const ok = confirm(
    `Se va a avisar por WhatsApp de un retraso de ${minutos} minutos.\n\n¿Quieres continuar?`
  );
  if (!ok) return;

  const telefonoLimpio = telefono.replace(/\s+/g, '');
  const mensaje =
    `Hola ${cliente || ''} 😊\n` +
    `Vamos con un retraso aproximado de ${minutos} minutos.\n` +
    `Gracias por tu paciencia 💙`;

  const url = `https://wa.me/${telefonoLimpio}?text=${encodeURIComponent(mensaje)}`;
  window.open(url, '_blank');
}

// ======== APLICAR RETRASO MANUAL ========
async function aplicarRetraso(rowSheet, minutos) {
  const baseUrl = fechaSeleccionada ? `/agenda/retraso?fecha=${fechaSeleccionada}` : '/agenda/retraso';
  await fetch(baseUrl, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      row_sheet: rowSheet,
      minutos: minutos
    })
  });
  cargarAgenda();
}

window.onload = () => {
  if (!checkAuth()) {
    document.body.innerHTML = "<h2 style='text-align:center;margin-top:3rem;'>Acceso restringido</h2>";
    return;
  }

  const hoy = new Date().toISOString().slice(0,10);
  document.getElementById('fechaSelector').value = hoy;
  fechaSeleccionada = hoy;
  cargarAgenda();
};
</script>

</body>
</html>
"""
    return HTMLResponse(content=html_content)