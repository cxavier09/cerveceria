<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$ventasFile = __DIR__ . '/ventas.json';
$ventas = json_decode(file_get_contents($ventasFile), true);
if(!is_array($ventas)) $ventas = [];

$i = isset($_GET['i']) ? (int)$_GET['i'] : -1;
if($i >= 0 && $i < count($ventas)){
  array_splice($ventas, $i, 1);
  file_put_contents($ventasFile, json_encode($ventas, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE), LOCK_EX);
}
header('Location: index.php');
exit;
