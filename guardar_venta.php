<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$ventasFile = __DIR__ . '/ventas.json';
if(!file_exists($ventasFile)) file_put_contents($ventasFile, json_encode([]));

$ventas = json_decode(file_get_contents($ventasFile), true);
if(!is_array($ventas)) $ventas = [];

$cliente  = trim($_POST['cliente'] ?? '');
$producto = trim($_POST['producto'] ?? '');
$monto    = trim($_POST['monto'] ?? '0');

$ventas[] = ["cliente"=>$cliente, "producto"=>$producto, "monto"=>$monto];

file_put_contents($ventasFile, json_encode($ventas, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE), LOCK_EX);
header('Location: index.php');
exit;
