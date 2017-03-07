<?php

if (isset($_POST['action'])) {
	$request = $_POST['action'];

	if ($request == "server_alive") {
		echo "ok"
	}

}

?>