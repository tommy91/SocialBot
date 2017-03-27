<?php

class MysqlClass {

    // parametri per la connessione al database
    private $nomehost = "nome_host";
    private $nomeuser = "nome_user";
    private $password = "password";
    // nome del database da selezionare private 
    private $nomedb = "nome_db";

    //funzione per l'esecuzione delle query 
    public function query($sql) {
        if (isset($this->attiva)) {
            $sql = mysql_query($sql) or die(json_encode(array('Error' => mysql_error())));
            return array('Result' => $sql);
        } else {
            return false;
        }
    }

    // controllo sulle connessioni attive
    private $attiva = false;

    // funzione per la connessione a MySQL
    public function connetti() {
        if (!$this->attiva) {
            if ($connessione = mysql_connect($this->nomehost, $this->nomeuser, $this->password) or die(mysql_error())) {
                // selezione del database
                $selezione = mysql_select_db($this->nomedb, $connessione) or die(mysql_error());
            }
        } else {
            return true;
        }
    }

    // funzione per la chiusura della connessione
    public function disconnetti() {
        if ($this->attiva) {
            if (mysql_close()) {
                $this->attiva = false;
                return true;
            } else {
                return false;
            }
        }
    }

    //funzione per l'inserimento dei dati in tabella     
    public function inserisci($t, $v, $r = null) {
        if (isset($this->attiva)) {
            $istruzione = 'INSERT INTO ' . $t;
            if ($r != null) {
                $istruzione .= ' (' . $r . ')';
            }
            for ($i = 0; $i < count($v); $i++) {
                if (is_string($v[$i]))
                    $v[$i] = '"' . $v[$i] . '"';
            }
            $v = implode(',', $v);
            $istruzione .= ' VALUES (' . $v . ')';
            $query = mysql_query($istruzione) or die(mysql_error());
            if (!$query)
                return mysql_error();
            else
                return true;
        }else {
            return false;
        }
    }

    // funzione per l'estrazione dei record 
    public function estrai($risultato) {
        if (isset($this->attiva)) {
            $r = mysql_fetch_object($risultato);
            return $r;
        } else {
            return false;
        }
    }

}

?>

