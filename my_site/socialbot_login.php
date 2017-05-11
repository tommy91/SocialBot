<?php
    session_start();
    if(isset($_SESSION["username"])){
        header('Location: socialbot.php');
        exit;
    }
?>
<html>
    <head>
        <title>SOCIAL BOT LOGIN</title>
        <meta charset="utf-8">
	    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
        <link rel="stylesheet" type="text/css" href="css/login.css">
    </head>
    <body>
        <form action="socialbot.php" method="post">
            <h1>SOCIAL BOT</h1>
            <?php 
            if(isset($_COOKIE["error_msg"])){
                $error_msg = $_COOKIE["error_msg"];
                setcookie('error_msg', null, -1, '/');
                if($error_msg == "1")
                    echo '<div id="error-msg">Username wrong..</div><br>';
                if($error_msg == "2")
                    echo '<div id="error-msg">WTF R U DOING?!?!</div><br>';
                if($error_msg == "3")
                    echo '<div id="error-msg">Password wrong..</div><br>';
                if($error_msg == "4")
                    echo '<div id="error-msg">Missing post data..</div><br>';
                if($error_msg == "5")
                    echo '<div id="error-msg">Connection error..</div><br>';
            }
            ?>
            <input id="input-username" type="text" name="username" placeholder="Username" autocomplete="off" required/><br><br>
            <input id="input-password" type="password" name="password" placeholder="Password" autocomplete="off" required/><br><br>
            <input id="confirm-button" type="submit" value="Login">
        </form>
    </body>
</html>