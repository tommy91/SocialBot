<?php
session_start();

// per debug locale
require_once 'example_funzioni_mysql.php';

//require_once 'funzioni_mysql.php';

if(isset($_GET['logout'])) {
    if(isset($_SESSION['username'])){
        unset($_SESSION['username']);
    }
    if(isset($_POST['username'])){
        unset($_POST['username']);
    }
    if(isset($_POST['password'])){
        unset($_POST['password']);
    }
    header('Location: socialbot_login.php');
    exit;
}

$data = new MysqlClass(); 
$data->connetti();

function setError($error_msg){
    setcookie('error_msg', $error_msg + $_POST["username"], time() + (60), "/");
    header('Location: socialbot_login.php');
    exit;
}

if(!isset($_SESSION["username"])){
    if((!isset($_POST["username"]))||(!isset($_POST["password"]))){
        setError("4");
    }
    $username = strtolower($_POST["username"]);
    $password = $_POST["password"];

    $q = 'SELECT Hash FROM sb_users WHERE Username="'.$username.'"';
    $auth = $data->query($q);
    if($auth == False) {
        setError("5");
    }
    $auth_length = mysql_num_rows($auth['Result']);
    if($auth_length == 0){
        setError("1");
    }
    if($auth_length > 1){
        setError("2");
    }
    $response = mysql_fetch_row($auth['Result']);
    $hash = $response[0];

    if (!password_verify($password, $hash)){
        setError("3");
    } 
    $_SESSION['username'] = $username;
}
else{
    $username = $_SESSION["username"];
}

?>

<html>
    <head>
        <title>SOCIAL BOT</title>
        <meta charset="utf-8">
	    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
	    <script type="text/javascript" src="script/socialbot.js"></script>
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        <link rel="stylesheet" type="text/css" href="css/socialbot.css">
    </head>
    <body>
        <div id="header">
            <h3 class="hello">Hi&nbsp;</h3>
            <h3 id="username" class="hello"><?php echo ucwords(htmlspecialchars($username)); ?></h3>
            <h3 class="hello">!</h3>
            <a href="?logout" id="logout"><button class="btn">Logout</button></a>
        </div>
        <div><button id="change-pw-btn" class="btn">CHANGE PASSWORD</button></div>
        <div id="change-pw">
            Insert here new password: <input id="input-new-pw" type="password" name="new-pw" placeholder="..." autocomplete="off" required/></br></br>
            Confirm the new password: <input id="input-new-pw2" type="password" name="new-pw2" placeholder="..." autocomplete="off" required/></br></br>
            <button id="change-pw-confirm" class="btn-confirm">CONFIRM</button>
        </div>
        <div><button id="modify-data-btn" class="btn">MODIFY</button></div>
        <div id="modify-data-container">
            <div id="header-modify">
                <select id="select-table" class="select">
                    <option value="0">Select Account Type</option>
                    <option value="app_accounts">App Accounts</option>
                    <option value="my_accounts">My Accounts</option>
                </select>
                <select id="select-action" class="select">
                    <option value="0">Select Action</option>
                    <option value="1">Add</option>
                    <option value="2">Delete</option>
                    <option value="3">Modify</option>
                </select>
                <select id="select-third-option" class="select"></select>
            </div>
            <div id="modify-data-content">
                <div id="modify-account" class="modify">
                    <div id="div-type-modify" class="modify maa mmat mmai">
                        <div id="tag-type-modify" class="inline">Type: </div>
                        <select id="select-type-modify" class="inline select">
                            <option value="1">Tumblr</option>
                            <option value="2">Instagram</option>
                        </select>
                    </div>
                    <div id="div-mail-modify" class="modify maa mmat mmai">
                        <div id="tag-mail-modify" class="inline">Mail: </div>
                        <input id="input-mail-modify" class="inline input"></input>
                    </div>
                    <div id="div-token-modify" class="modify maa mmat">
                        <div id="tag-token-modify" class="inline">Token: </div>
                        <input id="input-token-modify" class="inline input"></input>
                    </div>
                    <div id="div-token-secret-modify" class="modify maa mmat">
                        <div id="tag-token-secret-modify" class="inline">Token Secret: </div>
                        <input id="input-token-secret-modify" class="inline input"></input>
                    </div>
                    <div id="div-username-modify" class="modify mmai">
                        <div id="tag-username-modify" class="inline">Username: </div>
                        <input id="input-username-modify" class="inline input"></input>
                    </div>
                    <div id="div-password-modify" class="modify mmai">
                        <div id="tag-password-modify" class="inline">Password: </div>
                        <input id="input-password-modify" class="inline input"></input>
                    </div>
                    <div id="div-app-account-modify" class="modify mmat">
                        <div id="tag-app-account-modify" class="inline">App Account: </div>
                        <select id="select-app-account-modify" class="inline select"></select>
                    </div>
                    <div id="div-name-modify" class="modify mmat mmai">
                        <div id="tag-name-modify" class="inline">Name: </div>
                        <input id="input-name-modify" class="inline input"></input>
                    </div>
                    <div id="div-url-modify" class="modify mmat mmai">
                        <div id="tag-url-modify" class="inline">Url: </div>
                        <input id="input-url-modify" class="inline input"></input>
                    </div>
                    <div id="div-xxd-modify" class="modify mmat mmai">
                        <div id="tag-postxd-modify" class="inline">PostXD: </div>
                        <input id="input-postxd-modify" class="inline small-input space"></input>
                        <div id="tag-likexd-modify" class="inline">LikeXD: </div>
                        <input id="input-likexd-modify" class="inline small-input space"></input>
                        <div id="tag-followxd-modify" class="inline">FollowXD: </div>
                        <input id="input-followxd-modify" class="inline small-input"></input>
                    </div>
                    <div id="div-xxt-modify" class="modify mmat mmai">
                        <div id="tag-postxt-modify" class="inline">PostXT: </div>
                        <input id="input-postxt-modify" class="inline small-input space"></input>
                        <div id="tag-likext-modify" class="inline">LikeXT: </div>
                        <input id="input-likext-modify" class="inline small-input space"></input>
                        <div id="tag-followxt-modify" class="inline">FollowXT: </div>
                        <input id="input-followxt-modify" class="inline small-input"></input>
                    </div>
                    <div id="div-tags-blogs-modify" class="modify mmat mmai">
                        <div id="div-tags-container-modify">
                            <div id="tag-tags-modify">Tags:</div>
                            <ul id="div-tags-modify" class="list"></ul>
                        </div>
                        <div id="div-blogs-container-modify">
                            <div id="tag-blogs-modify">Search:</div>
                            <ul id="div-blogs-modify" class="list"></ul> 
                        </div>
                    </div>
                </div>
                <div id="confirm-buttons" class="modify">
                    <button id="reset-modify" class="btn-confirm inline">RESET</button>
                    <button id="confirm-modify" class="btn-confirm inline">CONFIRM</button>
                </div>
            </div>
        </div>
        <div id="program-stats-container"></div> 
        <div id="account-container"></div>
    </body>
</html>

