<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$clientesFile = __DIR__ . '/clientes.json';
$clientes = json_decode(file_get_contents($clientesFile), true);
if(!is_array($clientes)) $clientes = [];

$i = isset($_GET['i']) ? (int)$_GET['i'] : -1;
if($i >= 0 && $i < count($clientes)){
  array_splice($clientes, $i, 1);
  file_put_contents($clientesFile, json_encode($clientes, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE), LOCK_EX);
}
header('Location: index.php');
exit;

