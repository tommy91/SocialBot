<?php

$log_info_filename = 'log.log';
$log_error_filename = 'errors.log';


function logInfo($info) {
    $log = date("Y/m/d h:i:sa") . " -> " . $info . "\r\n";
    file_put_contents($log_info_filename, $log, FILE_APPEND | LOCK_EX);
}

function logError($msg) {
    $log = date("Y/m/d h:i:sa") . " -> " . $msg . "\r\n";
    error_log($log, 3, $log_error_filename); 
}

?>