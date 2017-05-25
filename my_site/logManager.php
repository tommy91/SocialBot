<?php

function logQuery($q) {
    $log = date("Y/m/d h:i:sa") . " -> " . $q . "\r\n";
    file_put_contents('log.log', $log, FILE_APPEND | LOCK_EX);
}

function readLog() {
	$content = file_get_contents('log.log');
	$lines =  explode(PHP_EOL,$content);
	foreach ($lines as $line) {
		printLine($line);
	}
}

function printLine($line) {
	$pieces = explode(" ", $line);
	foreach ($pieces as $v) {
		if (($v == 'FROM') || ($v == 'WHERE') || ($v == 'ORDER') || ($v == 'GROUP') || ($v == 'SET') || ($v == 'INTO') || ($v == 'VALUES'))  {
			echo "</br>";
			printSpaces(44);
		}
		echo $v . " ";
	}
	echo "</br>";
}

function printSpaces($num) {
	while ($num-- > 0) {
		echo "&nbsp;";
	}
}

?>