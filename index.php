<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

function loadJson($path){
  if(!file_exists($path)) file_put_contents($path, json_encode([]));
  $raw = file_get_contents($path);
  $arr = json_decode($raw, true);
  return is_array($arr) ? $arr : [];
}

$empleadosFile = __DIR__ . '/empleados.json';
$clientesFile  = __DIR__ . '/clientes.json';
$ventasFile    = __DIR__ . '/ventas.json';

$empleados = loadJson($empleadosFile);
$clientes  = loadJson($clientesFile);
$ventas    = loadJson($ventasFile);
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Golden Drinks</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{
  --negro:#000; --blanco:#fff; --panel:#111; --borde:#fff;
}
*{box-sizing:border-box}
body{
  font-family: 'Segoe UI', Arial, sans-serif;
  margin:0; padding:0;
  background: url('fondo.png') no-repeat center center fixed;
  background-size: cover;
  color: var(--blanco);
}
.overlay{
  background: rgba(0,0,0,0.6);
  min-height: 100vh;
  padding: 24px;
}
header{
  display:flex; align-items:center; gap:16px; margin-bottom:10px;
}
header img{ width:140px; height:auto; }
h1{ margin:0; font-size: 40px; letter-spacing: .5px; }
h2{ margin:18px 0 8px; }
.panel{ background:#111; border:1px solid var(--borde); border-radius:10px; padding:18px; margin-top:16px; }
.barra{ display:flex; flex-wrap:wrap; gap:10px; margin:16px 0; }
.barra button, .btn, .tabla a.btn-link{
  background: var(--blanco); color: var(--negro); border:2px solid var(--blanco);
  padding:10px 16px; font-weight:700; border-radius:8px; cursor:pointer; text-decoration:none; display:inline-block;
}
.barra button.active{ background:transparent; color:var(--blanco); }
.tabla{ width:100%; border-collapse:collapse; margin-top:12px; }
.tabla th, .tabla td{ border:1px solid var(--borde); padding:10px; text-align:left; }
.tabla th{ background: var(--blanco); color: var(--negro); }
.seccion{ display:none; }
.grid-3{
  display:grid; grid-template-columns: repeat(3,1fr); gap:18px; align-items:start;
}
.card{
  background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.2);
  border-radius:12px; padding:12px; text-align:center;
}
.card img{ width:100%; max-width:320px; height:auto; border-radius:10px; display:block; margin:0 auto 10px; }
.caption{
  font-family:'Playfair Display', serif;
  font-size:18px; line-height:1.35; text-align:left; /* izquierda */
}
.caption .titulo{ font-weight:700; font-size:20px; }
.caption .precio{ margin-top:6px; opacity:.95; }
.form label{ display:block; margin-top:8px; }
.form input[type="text"], .form input[type="number"]{
  width:100%; padding:10px; border-radius:8px; border:1px solid #444; background:#222; color:#fff;
}
.form .btn{ margin-top:10px; }
a.btn-delete{
  background:#ff4d4d; color:#fff !important; border: none; padding:7px 12px; border-radius:6px;
}
a.btn-delete:hover{ background:#e60000; }
.notice{ font-size:14px; opacity:.9; }
.footer-space{ height:20px; }
</style>
</head>
<body>
<div class="overlay">

  <header>
    <img src="logo.png" alt="Logo">
    <h1>🍷 Golden Drinks</h1>
  </header>

  <!-- Registro de Empleados -->
  <div class="panel">
    <h2>Registro de Empleados</h2>
    <form class="form" action="guardar_empleado.php" method="POST">
      <label>Nombre:</label>
      <input type="text" name="nombre" required>
      <label>DNI:</label>
      <input type="number" name="dni" required>
      <label><strong>Selecciona el Rol:</strong></label>
      <div class="barra" id="rolesBar">
        <?php
          $roles = ["Administrador", "Vendedor", "Almacén", "Contador"];
          foreach ($roles as $rol) {
            echo "<button type='button' onclick=\"seleccionarRol('$rol', this)\">$rol</button>";
          }
        ?>
      </div>
      <!-- valor por defecto para evitar vacíos -->
      <input type="hidden" name="rol" id="rolSeleccionado" value="Vendedor">
      <button class="btn" type="submit">Registrar Empleado</button>
      <div class="notice">Si no eliges rol, se guardará como <b>Vendedor</b>.</div>
    </form>

    <h2 style="margin-top:16px;">Empleados Registrados</h2>
    <table class="tabla">
      <thead><tr><th>Nombre</th><th>DNI</th><th>Rol</th><th>Acciones</th></tr></thead>
      <tbody>
        <?php foreach ($empleados as $i => $emp): ?>
          <tr>
            <td><?= htmlspecialchars($emp['nombre']) ?></td>
            <td><?= htmlspecialchars($emp['dni']) ?></td>
            <td><?= htmlspecialchars($emp['rol']) ?></td>
            <td>
              <a class="btn-delete" href="eliminar_empleado.php?i=<?= $i ?>" onclick="return confirm('¿Eliminar empleado?');">Eliminar</a>
            </td>
          </tr>
        <?php endforeach; ?>
        <?php if(empty($empleados)): ?>
          <tr><td colspan="4">Sin empleados aún.</td></tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>

  <!-- Navegación de Secciones -->
  <div class="barra">
    <button onclick="mostrarSeccion('clientes')">Clientes</button>
    <button onclick="mostrarSeccion('productos')">Catálogo</button>
    <button onclick="mostrarSeccion('masvendidos')">Más Vendidos</button>
    <button onclick="mostrarSeccion('ventas')">Ventas</button>
    <button onclick="mostrarSeccion('sunat')">SUNAT</button>
  </div>

  <!-- Clientes -->
  <div id="clientes" class="panel seccion">
    <h2>Registro de Clientes</h2>
    <form class="form" action="guardar_cliente.php" method="POST">
      <label>Nombre:</label>
      <input type="text" name="nombre" required>
      <label>DNI:</label>
      <input type="number" name="dni" required>
      <button class="btn" type="submit">Registrar Cliente</button>
    </form>

    <h2>Clientes Registrados</h2>
    <table class="tabla">
      <thead><tr><th>Nombre</th><th>DNI</th><th>Acciones</th></tr></thead>
      <tbody>
        <?php foreach ($clientes as $i => $cli): ?>
          <tr>
            <td><?= htmlspecialchars($cli['nombre']) ?></td>
            <td><?= htmlspecialchars($cli['dni']) ?></td>
            <td>
              <a class="btn-delete" href="eliminar_cliente.php?i=<?= $i ?>" onclick="return confirm('¿Eliminar cliente?');">Eliminar</a>
            </td>
          </tr>
        <?php endforeach; ?>
        <?php if(empty($clientes)): ?>
          <tr><td colspan="3">Sin clientes aún.</td></tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>

  <!-- Catálogo -->
  <div id="productos" class="panel seccion">
    <h2>Catálogo de Licores</h2>
    <table class="tabla">
      <thead><tr><th>Producto</th><th>Stock</th><th>Precio</th></tr></thead>
      <tbody>
        <tr><td>Whisky Johnnie Walker Black</td><td>15</td><td>S/ 250</td></tr>
        <tr><td>Vodka Absolut</td><td>20</td><td>S/ 120</td></tr>
        <tr><td>Ron Zacapa</td><td>10</td><td>S/ 300</td></tr>
        <tr><td>Tequila Don Julio</td><td>8</td><td>S/ 350</td></tr>
        <tr><td>Gin Tanqueray</td><td>12</td><td>S/ 180</td></tr>
        <tr><td>Champagne Moët</td><td>6</td><td>S/ 600</td></tr>
        <tr><td>Pisco 4 Gallos</td><td>18</td><td>S/ 90</td></tr>
        <tr><td>Cerveza Corona (6 pack)</td><td>30</td><td>S/ 70</td></tr>
        <tr><td>Vino Casillero del Diablo</td><td>25</td><td>S/ 110</td></tr>
        <tr><td>Brandy Torres</td><td>14</td><td>S/ 150</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Más Vendidos (con imágenes y nombres elegantes debajo) -->
  <div id="masvendidos" class="panel seccion">
    <h2>Top 3 Licores Más Vendidos</h2>
    <div class="grid-3">
      <div class="card">
        <img src="bebida1.png" alt="Bebida 1">
        <div class="caption">
          <div class="titulo">WHISKY JOHNNIE WALKER BLUE LABEL GLENURY ROYAL BOTELLA DE 1L</div>
          <div class="precio">Precio: <b>S/. 2,100.00</b></div>
        </div>
      </div>
      <div class="card">
        <img src="bebida2.png" alt="Bebida 2">
        <div class="caption">
          <div class="titulo">WHISKY MACALLAN DOUBLE CASK 12 AÑOS BOTELLA 700ML</div>
          <div class="precio">Precio: <b>S/. 510.00</b></div>
        </div>
      </div>
      <div class="card">
        <img src="bebida3.png" alt="Bebida 3">
        <div class="caption">
          <div class="titulo">WHISKY JAPONÉS HIBIKI HARMONY MASTER'S SELECT LIMITED EDITION</div>
          <div class="precio">Precio: <b>S/. 1,750.00</b></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Ventas -->
  <div id="ventas" class="panel seccion">
    <h2>Registro de Ventas</h2>
    <form class="form" action="guardar_venta.php" method="POST">
      <label>Cliente (texto o elige de tu lista):</label>
      <input type="text" name="cliente" list="listaClientes" required>
      <datalist id="listaClientes">
        <?php foreach($clientes as $c){ echo '<option value="'.htmlspecialchars($c['nombre']).'">'; } ?>
      </datalist>

      <label>Producto (texto libre):</label>
      <input type="text" name="producto" required>

      <label>Monto (S/):</label>
      <input type="number" name="monto" step="0.01" required>

      <button class="btn" type="submit">Registrar Venta</button>
    </form>

    <h2>Historial de Ventas</h2>
    <table class="tabla">
      <thead><tr><th>Cliente</th><th>Producto</th><th>Monto</th><th>Acciones</th></tr></thead>
      <tbody>
        <?php foreach($ventas as $i => $v): ?>
          <tr>
            <td><?= htmlspecialchars($v['cliente']) ?></td>
            <td><?= htmlspecialchars($v['producto']) ?></td>
            <td>S/ <?= htmlspecialchars($v['monto']) ?></td>
            <td><a class="btn-delete" href="eliminar_venta.php?i=<?= $i ?>" onclick="return confirm('¿Eliminar venta?');">Eliminar</a></td>
          </tr>
        <?php endforeach; ?>
        <?php if(empty($ventas)): ?>
          <tr><td colspan="4">Sin ventas registradas aún.</td></tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>

  <!-- SUNAT -->
  <div id="sunat" class="panel seccion">
    <h2>Integración con SUNAT (Simulación)</h2>
    <p>Simulación de envío y validación de comprobantes electrónicos.</p>
    <div class="barra">
      <button class="btn" onclick="alert('Factura enviada a SUNAT.')">Enviar Factura</button>
      <button class="btn" onclick="alert('Boleta validada por SUNAT.')">Generar Boleta</button>
    </div>
  </div>

  <div class="footer-space"></div>
</div>

<script>
function seleccionarRol(rol, btn){
  document.getElementById('rolSeleccionado').value = rol;
  document.querySelectorAll('#rolesBar button').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
}
function mostrarSeccion(id){
  document.querySelectorAll('.seccion').forEach(s=>s.style.display='none');
  const el = document.getElementById(id);
  if(el) el.style.display='block';
}
// Mostrar por defecto "masvendidos"
mostrarSeccion('masvendidos');
</script>
</body>
</html>



