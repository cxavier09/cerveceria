<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$empleadosFile = __DIR__ . '/empleados.json';
$empleados = json_decode(file_get_contents($empleadosFile), true);
if(!is_array($empleados)) $empleados = [];

$i = isset($_GET['i']) ? (int)$_GET['i'] : -1;
if($i >= 0 && $i < count($empleados)){
  array_splice($empleados, $i, 1);
  file_put_contents($empleadosFile, json_encode($empleados, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE), LOCK_EX);
}
header('Location: index.php');
exit;
