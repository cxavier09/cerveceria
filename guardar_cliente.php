<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$clientesFile = __DIR__ . '/clientes.json';
if(!file_exists($clientesFile)) file_put_contents($clientesFile, json_encode([]));

$clientes = json_decode(file_get_contents($clientesFile), true);
if(!is_array($clientes)) $clientes = [];

$nombre = trim($_POST['nombre'] ?? '');
$dni    = trim($_POST['dni'] ?? '');

$clientes[] = ["nombre"=>$nombre, "dni"=>$dni];

file_put_contents($clientesFile, json_encode($clientes, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE), LOCK_EX);
header('Location: index.php');
exit;

