<?php

require_once 'funzioni_mysql.php';
require_once 'insta.php';

$data = new MysqlClass(); 
$data->connetti();


function op2register($from, $table, $blog, $op) {   // from: 0=php, 1=python    op: 0=add, 1=delete, 2=update
	global $data;
    $t = "sb_register";
    $v = array ($from, $table, $blog, $op);
    $r = "Who, `Table`, Blog, Operation";
    $regres = $data->inserisci($t,$v,$r);
    if($regres == 1)
        return True;
    else
        return False; 
}

function fetchSelectAndReturn($auth) {
    if (array_key_exists('Error', $auth)) {
        return $auth;
    }
    else {
        $rows = array();
        while($r = mysql_fetch_assoc($auth['Result'])) {
            $rows[] = $r;
        }
        return array('Result' => $rows);
    }
}

function fetchSelectOneAndReturn($auth) {
    if (array_key_exists('Error', $auth)) {
        return $auth;
    }
    else {
        return array('Result' => mysql_fetch_assoc($auth['Result']));
    }
}

function fetchUpDelAndReturn($auth) {
    if (array_key_exists('Error', $auth)) {
        return $auth;
    }
    else {
        return array('Result' => $auth['Result']);
    }
}

function fetchInstaResult($res) {
    if (array_key_exists('Error', $res)) {
        return $res;
    }
    else {
        return array('Result' => $res);
    }
}


if (isset($_POST['action'])) {
	$request = $_POST['action'];

	if ($request == "server_alive") {
		echo json_encode(array('Result' => ""));
	}

	if ($request == "get_app_accounts") {
		$q = 'SELECT * FROM sb_app_accounts ORDER BY ID';
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
	}

	if ($request == "get_my_accounts") {
		$q = 'SELECT * FROM sb_my_accounts ORDER BY ID';
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
	}

	if ($request == "get_tags") {
		$id = $_POST['ID'];
		$q = 'SELECT Name FROM sb_tags WHERE My_Account = '.intval($id).' ORDER BY Position';
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
	}

	if ($request == "get_blogs") {
		$id = $_POST['ID'];
		$q = 'SELECT Name FROM sb_other_accounts WHERE My_Account = '.intval($id);
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
	}

    if ($request == "get_status") {
        $id = $_POST['ID'];
        $q = 'SELECT State FROM sb_my_accounts WHERE ID = '.intval($id);
        $auth = $data->query($q);
        echo json_encode(fetchSelectOneAndReturn($auth));
    }

	if ($request == "update_blog_data") {
		$id = intval($_POST['ID']);
        $likes = intval($_POST['Likes']);
        $following = intval($_POST['Following']);
        $followers = intval($_POST['Followers']);
        $posts = intval($_POST['Posts']);
        $messages = intval($_POST['Messages']);
        $queue = intval($_POST['Queue']);
        $name = $_POST['Name'];
        $url = $_POST['Url'];

        $query = "";
        if(isset($_POST['Deadline_Post']))
            $query = "UPDATE sb_my_accounts SET Name='".$name."', Url='".$url."', Likes=".$likes.", Following=".$following.", Followers=".$followers.", Posts=".$posts.", Messages=".$messages.", Queue=".$queue.", Deadline_Post='".$_POST['Deadline_Post']."', Deadline_Like='".$_POST['Deadline_Like']."', Deadline_Follow='".$_POST['Deadline_Follow']."' WHERE ID=".$id;
        else    
            $query = "UPDATE sb_my_accounts SET Name='".$name."', Url='".$url."', Likes=".$likes.", Following=".$following.", Followers=".$followers.", Posts=".$posts.", Messages=".$messages.", Queue=".$queue." WHERE ID=".$id;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
        	if(op2register(1, "sb_my_accounts", $id, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
		}
        else
            echo json_encode($fetch_result);
	}

    if ($request == "update_blog_data_insta") {
        $id = intval($_POST['ID']);
        $following = intval($_POST['Following']);
        $followers = intval($_POST['Followers']);
        $posts = intval($_POST['Posts']);
        $messages = intval($_POST['Messages']);
        $name = $_POST['Name'];
        $private = $_POST['Private'];
        $usertags = $_POST['Usertags'];

        $query = "";
        if(isset($_POST['Deadline_Post']))
            $query = "UPDATE sb_my_accounts SET Name='".$name."', Following=".$following.", Followers=".$followers.", Posts=".$posts.", Messages=".$messages.", Private=".$private.", Usertags=".$usertags.", Deadline_Post='".$_POST['Deadline_Post']."', Deadline_Like='".$_POST['Deadline_Like']."', Deadline_Follow='".$_POST['Deadline_Follow']."' WHERE ID=".$id;
        else    
            $query = "UPDATE sb_my_accounts SET Name='".$name."', Following=".$following.", Followers=".$followers.", Posts=".$posts.", Messages=".$messages.", Private=".$private.", Usertags=".$usertags." WHERE ID=".$id;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(1, "sb_my_accounts", $id, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if ($request == "synch_operations") {
        $q = 'SELECT max(ID) as max FROM sb_register WHERE Who=0';
        $auth = $data->query($q);
        $max_id = mysql_fetch_assoc($auth['Result']);
        if ($max_id['max'] != null) {
            $q = 'SELECT * FROM sb_register WHERE ID<='.$max_id['max'].' AND Who=0 ORDER BY ID';
            $auth = $data->query($q);
            $rows = fetchSelectAndReturn($auth);
            $query = 'DELETE FROM sb_register WHERE ID<='.$max_id['max'].' AND Who=0';
            $result = $data->query($query);
            echo json_encode($rows);
        }
        else {
            echo json_encode(array('Result' => array()));
        }
    }

    if ($request == "synch_operations_webpage") {
        $q = 'SELECT max(ID) as max FROM sb_register WHERE Who=1';
        $auth = $data->query($q);
        $max_id = mysql_fetch_assoc($auth['Result']);
        if ($max_id['max'] != null) {
            $q = 'SELECT ID, `Table`, Blog, Operation FROM sb_register WHERE ID<='.$max_id['max'].' AND Who=1 ORDER BY ID';
            $auth2 = $data->query($q);
            $rows = fetchSelectAndReturn($auth2);
            console.log($rows);
            $query = 'DELETE FROM sb_register WHERE ID<='.$max_id['max'].' AND Who=1';
            $result = $data->query($query);
            if(array_key_exists('Error', $rows)) {
                echo json_encode($rows);
            }
            else {
                $update_data = array();
                $updated_blogs = array();
                $break = false;
                foreach ($rows['Result'] as $key => $row) {
                    if(($row['Table'] == 'sb_my_accounts') && (!in_array($row['Blog'], $updated_blogs))) {
                        $q = 'SELECT * FROM sb_my_accounts WHERE ID='.$row['Blog'];
                        $auth = $data->query($q);
                        $up = fetchSelectOneAndReturn($auth);
                        if(array_key_exists('Error', $up)) {
                            $break = true;
                            echo json_encode($up);
                        }
                        else {
                            $update_data[] = array('blog' => $up['Result']);
                            $updated_blogs[] = $row['Blog'];
                        }
                    }
                    else {
                        $q = 'SELECT * FROM sb_statistics';
                        $auth = $data->query($q);
                        $up = fetchSelectOneAndReturn($auth);
                        if(array_key_exists('Error', $up)) {
                            $break = true;
                            echo json_encode($up);
                        }
                        else {
                            $update_data[] = array('stats' => $up['Result']);
                        }
                    }
                }
                if(!$break) {
                    echo json_encode(array('Result' => $update_data));
                }
            }
        }
        else {
            echo json_encode(array('Result' => array()));
        }
    }

	if ($request == "update_statistics") {
		$session_start = $_POST['Session_Start'];
        $num_threads = intval($_POST['Num_Threads']);
        $num_post_like = intval($_POST['Num_Post_Like']);
        $num_follow = intval($_POST['Num_Follow']);
        
        $query = "";
        if(isset($_POST['Deadline_Update']))
            $query = "UPDATE sb_statistics SET Session_Start='".$session_start."', Num_Threads=".$num_threads.", Num_Post_Like=".$num_post_like.", Num_Follow=".$num_follow.", Deadline_Update='".$_POST['Deadline_Update']."'";
        else
            $query = "UPDATE sb_statistics SET Session_Start='".$session_start."', Num_Threads=".$num_threads.", Num_Post_Like=".$num_post_like.", Num_Follow=".$num_follow;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(1, "sb_statistics", 0, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
	}

    if ($request == "closing_operations") {
        $stop = $_POST['stop_session_time'];
        $query = "UPDATE sb_statistics SET Session_Stop='".$stop."'";
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(1, "sb_statistics", 0, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);

    }

    if ($request == "set_pw"){
        $pw = $_POST['pw'];
        $user = $_POST['user'];
        
        $hash = password_hash($pw, PASSWORD_DEFAULT);
        
        $query = 'UPDATE sb_users SET `Hash`="'.$hash.'" WHERE `Username`="'.$user.'"';
        $result = $data->query($query);
        
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result))
            echo json_encode($fetch_result);
        else
            echo json_encode($fetch_result);
    }

    if ($request == "get_program_status") {
        $q = 'SELECT * FROM sb_statistics';
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
    }

    if ($request == "get_app_accounts_ID") {
        $id = $_POST['id'];
        $q = 'SELECT * FROM sb_app_accounts WHERE ID = '.intval($id);
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
    }

    if ($request == "get_my_accounts_ID") {
        $id = $_POST['id'];
        $q = 'SELECT * FROM sb_my_accounts WHERE ID = '.intval($id);
        $auth = $data->query($q);
        echo json_encode(fetchSelectAndReturn($auth));
    }

    if ($request == "delete_app_accounts_ID") {
        $id = intval($_POST['id']);
        $query = 'DELETE FROM sb_app_accounts WHERE ID='.$id;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_app_accounts", $id, 1))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if ($request == "delete_my_accounts_ID") {
        $id = $_POST['id'];
        $query = 'DELETE FROM sb_my_accounts WHERE ID='.intval($id);
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_my_accounts", $id, 1))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if ($request == "add_app_accounts"){
        $type = intval($_POST['type']);
        $mail = $_POST['mail'];
        $token = $_POST['token'];
        $token_secret = $_POST['token_secret'];

        $t = "sb_app_accounts";
        $v = array ($type, $mail, $token, $token_secret);
        $r = "Type, Mail, Token, Token_Secret";

        $result = $data->inserisci($t,$v,$r);

        if ($result == 1){
            $q = 'SELECT max(ID) as ID FROM sb_app_accounts';
            $auth = $data->query($q);
            $r = mysql_fetch_assoc($auth['Result']);
            if(op2register(0, "sb_app_accounts", $r['ID'], 0))
                echo $r['ID'];
            else
                echo -1;
        }
        else
            echo 0;
    }

    if ($request == "add_my_accounts"){
        $type = intval($_POST['type']);
        $mail = $_POST['mail'];
        $name = $_POST['name'];
        $url = $_POST['url'];
        $postxd = intval($_POST['postxd']);
        $followxd = intval($_POST['followxd']);
        $likexd = intval($_POST['likexd']);
        $postxt = intval($_POST['postxt']);
        $followxt = intval($_POST['followxt']);
        $likext = intval($_POST['likext']);

        $t = "sb_my_accounts";

        if ($type == 1) {   // tumblr
            $token = $_POST['token'];
            $token_secret = $_POST['token_secret'];
            $app_account = intval($_POST['app_account']);
            $v = array ($type, $mail, $token, $token_secret, $app_account, $name, $url, $postxd, $followxd, $likexd, $postxt, $followxt, $likext);
            $r = "Type, Mail, Token, Token_Secret, App_Account, Name, Url, PostXD, FollowXD, LikeXD, PostXT, FollowXT, LikeXT";
        }
        else {
            $username = $_POST['username'];
            $password = $_POST['password'];
            $v = array ($type, $mail, $username, $password, $name, $url, $postxd, $followxd, $likexd, $postxt, $followxt, $likext);
            $r = "Type, Mail, Username, Password, Name, Url, PostXD, FollowXD, LikeXD, PostXT, FollowXT, LikeXT";
        }
        

        $result = $data->inserisci($t,$v,$r);

        if ($result == 1){
            $q = 'SELECT max(ID) as ID FROM sb_my_accounts';
            $auth = $data->query($q);
            $r = mysql_fetch_assoc($auth['Result']);
            if(op2register(0, "sb_my_accounts", $r['ID'], 0))
                echo $r['ID'];
            else
                echo -1;
        }
        else
            echo 0;
    }

    if ($request == "add_tag"){
        $id = intval($_POST['id']);
        $name = $_POST['name'];
        $pos = intval($_POST['position']);

        $t = "sb_tags";
        $v = array ($id, $name, $pos);
        $r = "My_Account, Name, Position";

        $result = $data->inserisci($t,$v,$r);

        if ($result == 1){
            if(op2register(0, "sb_tags", $id, 0))
                echo $result;
            else
                echo -1;
        }
        else
            echo $result;
    }

    if ($request == "add_blog"){
        $id = intval($_POST['id']);
        $name = $_POST['name'];

        $t = "sb_other_accounts";
        $v = array ($id, $name);
        $r = "My_Account, Name";

        $result = $data->inserisci($t,$v,$r);

        if ($result == 1){
            if(op2register(0, "sb_other_accounts", $id, 0))
                echo $result;
            else
                echo -1;
        }
        else
            echo $result;
    }

    if ($request == "delete_tag") {
        $id = $_POST['id'];
        $name = $_POST['name'];
        $query = 'DELETE FROM sb_tags WHERE My_Account='.intval($id).' AND Name="'.$name.'"';
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_tags", $id, 1))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);

    }

    if ($request == "delete_blog") {
        $id = $_POST['id'];
        $name = $_POST['name'];
        $query = 'DELETE FROM sb_other_accounts WHERE My_Account='.intval($id).' AND Name="'.$name.'"';
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_other_accounts", $id, 1))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if ($request == "update_app_accounts"){
        $id = intval($_POST['id']);
        $type = intval($_POST['type']);
        $mail = $_POST['mail'];
        $token = $_POST['token'];
        $token_secret = $_POST['token_secret'];

        $query = 'UPDATE sb_app_accounts SET Type='.$type.', Mail="'.$mail.'", Token="'.$token.'", Token_Secret="'.$token_secret.'" WHERE ID='.$id;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_app_accounts", $id, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if ($request == "update_my_accounts"){
        $id = intval($_POST['id']);
        $type = intval($_POST['type']);
        $mail = $_POST['mail'];
        $name = $_POST['name'];
        $url = $_POST['url'];
        $postxd = intval($_POST['postxd']);
        $followxd = intval($_POST['followxd']);
        $likexd = intval($_POST['likexd']);
        $postxt = intval($_POST['postxt']);
        $followxt = intval($_POST['followxt']);
        $likext = intval($_POST['likext']);

        if ($type == 1) {   // tumblr
            $token = $_POST['token'];
            $token_secret = $_POST['token_secret'];
            $app_account = intval($_POST['app_account']);
            $query = 'UPDATE sb_my_accounts SET Type='.$type.', Mail="'.$mail.'", Token="'.$token.'", Token_Secret="'.$token_secret.'", App_Account='.$app_account.', Name="'.$name.'", Url="'.$url.'", FollowXT='.$followxt.', PostXT='.$postxt.', LikeXT='.$likext.', FollowXD='.$followxd.', PostXD='.$postxd.', LikeXD='.$likexd.' WHERE ID='.$id;
        }
        else {  // instagram
            $username = $_POST['username'];
            $password = $_POST['password'];
            $query = 'UPDATE sb_my_accounts SET Type='.$type.', Mail="'.$mail.'", Username="'.$username.'", Password="'.$password.'", Name="'.$name.'", Url="'.$url.'", FollowXT='.$followxt.', PostXT='.$postxt.', LikeXT='.$likext.', FollowXD='.$followxd.', PostXD='.$postxd.', LikeXD='.$likexd.' WHERE ID='.$id;
        }

        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_my_accounts", $id, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if($request == "update_my_account_status") {
        $id = intval($_POST['id']);
        $query = 'UPDATE sb_my_accounts SET State=2 WHERE ID='.$id;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(0, "sb_my_accounts", $id, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if($request == "set_status") {
        $id = intval($_POST['id']);
        $status = intval($_POST['status']);
        $query = 'UPDATE sb_my_accounts SET State='.$status.' WHERE ID='.$id;
        $result = $data->query($query);
        $fetch_result = fetchUpDelAndReturn($result);
        if(!array_key_exists('Error', $fetch_result)) {
            if(op2register(1, "sb_my_accounts", $id, 2))
                echo json_encode($fetch_result);
            else
                echo json_encode(array('Error' => " Error on saving to register for blog ".$id."."));
        }
        else
            echo json_encode($fetch_result);
    }

    if($request == "get_insta_blog_info") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        echo json_encode(fetchInstaResult(get_user_info($username,$password)));
    }

    if($request == "get_id_by_username") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $user = $_POST['user'];
        echo json_encode(fetchInstaResult(get_id_by_username($username,$password,$user)));
    }

    if($request == "get_insta_media") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $user = $_POST['user'];
        $maxNum = $_POST['maxNum'];
        echo json_encode(fetchInstaResult(get_insta_media($username,$password,$user,$maxNum)));
    }

    if($request == "follow_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $user = $_POST['user'];
        echo json_encode(fetchInstaResult(follow_insta($username,$password,$user)));
    }

    if($request == "unfollow_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $user = $_POST['user'];
        echo json_encode(fetchInstaResult(unfollow_insta($username,$password,$user)));
    }

    if($request == "like_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $postID = $_POST['postID'];
        echo json_encode(fetchInstaResult(like_insta($username,$password,$user,$postID)));
    }

    if($request == "getHashtagFeed_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $tag = $_POST['tag'];
        $isPopular = $_POST['isPopular'];
        $maxNum = $_POST['maxNum'];
        echo json_encode(fetchInstaResult(getHashtagFeed($username,$password,$tag,$isPopular,$maxNum)));
    }

    if($request == "get_likers_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $postID = $_POST['postID'];
        $maxNum = $_POST['maxNum'];
        echo json_encode(fetchInstaResult(get_likers($username,$password,$postID,$maxNum)));
    }

    if($request == "get_comments_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $postID = $_POST['postID'];
        $maxNum = $_POST['maxNum'];
        echo json_encode(fetchInstaResult(get_comments($username,$password,$postID,$maxNum)));
    }

    if($request == "get_followers_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $userID = $_POST['userID'];
        $maxNum = $_POST['maxNum'];
        echo json_encode(fetchInstaResult(getFollowers($username,$password,$userID,$maxNum)));
    }

    if($request == "get_followings_insta") {
        $username = $_POST['username'];
        $password = $_POST['password'];
        $userID = $_POST['userID'];
        echo json_encode(fetchInstaResult(getFollowings($username,$password,$userID)));
    }


}

?>