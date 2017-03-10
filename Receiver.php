<?php

define('STATUS_OK', '200');
define('STATUS_ERROR', '400');

function response($code, $resp) {
	echo json_encode(array('code' => $code, 'response' => $resp));
}

if (isset($_POST['action'])) {
	$request = $_POST['action'];

	if ($request == "server_alive") {
		response(STATUS_OK, NULL);
	}

}

?>