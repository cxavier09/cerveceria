<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$empleadosFile = __DIR__ . '/empleados.json';
if(!file_exists($empleadosFile)) file_put_contents($empleadosFile, json_encode([]));

$empleados = json_decode(file_get_contents($empleadosFile), true);
if(!is_array($empleados)) $empleados = [];

$nombre = trim($_POST['nombre'] ?? '');
$dni    = trim($_POST['dni'] ?? '');
$rol    = trim($_POST['rol'] ?? 'Vendedor');
if($rol === '') $rol = 'Vendedor';

$empleados[] = ["nombre"=>$nombre, "dni"=>$dni, "rol"=>$rol];

file_put_contents($empleadosFile, json_encode($empleados, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE), LOCK_EX);
header('Location: index.php');
exit;
