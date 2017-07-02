<?php

require 'vendor/autoload.php';
require 'logManager.php';

$ig = new \InstagramAPI\Instagram();


function connect($username, $password){
	global $ig;
	$ig->setUser($username, $password);
	$ig->login();
	return $ig->getUsernameId($username);
}

function get_user_info($username, $password) {
	global $ig;
	connect($username,$password);
	try {
		$info = $ig->getSelfUserInfo();
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password));
	}
	if ($info->status != 'ok')
		return array('Error' => $info);
	$userInfo = $info->user;
	return array(
					'follower' => $userInfo->follower_count,
					'following' => $userInfo->following_count,
					'name' => $userInfo->full_name,
					'private' => $userInfo->is_private,
					'post' => $userInfo->media_count,
					'message' => $userInfo->message,
					'usertags' => $userInfo->usertags_count
				);
}

function get_id_by_username($username, $password, $user) {
	global $ig;
	connect($username,$password);
	try {
		$info = $ig->getUserInfoByName($user);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'user' => $user));
	}
	if ($info->status != 'ok')
		return array('Error' => $info);
	return array($info->user->pk);
}

function get_insta_media($username, $password, $user, $max_num) {
	global $ig;
	connect($username,$password);
	try {
		$media = $ig->getUserFeed($user);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'user' => $user, 'max_num' => $max_num));
	}
	if ($media->status != 'ok')
		return array('Error' => $media);
	else {
		$response = array();
		$counter = 0;
		foreach ($media->items as $key => $value) {
			if (!($value->has_liked)) {
				array_push($response, $value->caption->media_id);
				$counter++;
				if ($counter >= $max_num)
					break;
			}
		}
		return $response;
	}
}

function follow_insta($username, $password, $user) {
	global $ig;
	connect($username,$password);
	try {
		$follow_response = $ig->follow($user);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'user' => $user));
	}
	if ($follow_response->status != 'ok')
		return array('Error' => $follow_response);
	else
		return array();
}

function unfollow_insta($username, $password, $user) {
	global $ig;
	connect($username,$password);
	try {
		$unfollow_response = $ig->unfollow($user);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'user' => $user));
	}
	if ($unfollow_response->status != 'ok')
		return array('Error' => $unfollow_response);
	else
		return array();
}

function like_insta($username, $password, $postID) {
	global $ig;
	connect($username,$password);
	try {
		$like_response = $ig->like($postID);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'postID' => $postID));
	}
	if ($like_response->status != 'ok')
		return array('Error' => $like_response);
	else
		return array();
}

function getHashtagFeed($username, $password, $tag, $is_popular, $max_num) {
	global $ig;
	connect($username,$password);
	try {
		$hashtagFeed = $ig->getHashtagFeed($tag);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'tag' => $tag, 'is_popular' => $is_popular, 'max_num' => $max_num));
	}
	if ($hashtagFeed->status != 'ok')
		return array('Error' => $hashtagFeed);
	else {
		$response = array();
		$counter = 0;
		if ($is_popular) {
			foreach ($hashtagFeed->ranked_items as $key => $value) {
				$is_private = $value->caption->user->is_private;
				$followed_by = $value->caption->user->friendship_status->followed_by;
				$following = $value->caption->user->friendship_status->following;
				$outgoing_request = $value->caption->user->friendship_status->outgoing_request;
				$has_liked = $value->has_liked;
				if ((!$is_private) && (!$followed_by) && (!$following) && (!$outgoing_request) && (!$has_liked)) {
					$post = array(	'mediaID' => $value->caption->media_id, 
						  			'userID' => $value->caption->user_id
						  			);
					array_push($response, $post);
					$counter++;
					if ($counter >= $max_num)
						break;
				}
			}
		}
		else {
			foreach ($hashtagFeed->items as $key => $value) {
				$is_private = $value->caption->user->is_private;
				$followed_by = $value->caption->user->friendship_status->followed_by;
				$following = $value->caption->user->friendship_status->following;
				$outgoing_request = $value->caption->user->friendship_status->outgoing_request;
				$has_liked = $value->has_liked;
				if ((!$is_private) && (!$followed_by) && (!$following) && (!$outgoing_request) && (!$has_liked)) {
					$post = array(	'mediaID' => $value->caption->media_id, 
						  			'userID' => $value->caption->user_id
						  			);
					array_push($response, $post);
					$counter++;
					if ($counter >= $max_num)
						break;
				}
			}
		}
		return $response;
	}
}

function get_likers($username, $password, $mediaID, $max_num = NULL) {
	global $ig;
	connect($username,$password);
	try {
		$likers = $ig->getMediaLikers($mediaID);
		$counter = 0;
		if ($likers->status != 'ok')
			return array('Error' => $likers);
		else {
			$response = array();
			if ($likers->user_count > 0) {
				foreach ($likers->users as $key => $value) {
					if ($value->is_private)
						continue;
					array_push($response, $value->pk);
					$counter++;
					if (($max_num != NULL) && ($counter >= $max_num))
						break;
				}
			}
			return $response;
		}
	} catch (Exception $e) {
		return array('Error' => $e->getMessage());
	}
}

function get_comments($username, $password, $mediaID, $max_num = NULL) {
	global $ig;
	connect($username,$password);
	try {
		$comments = $ig->getMediaComments($mediaID);
		$counter = 0;
		if ($comments->status != 'ok')
			return array('Error' => $comments);
		else {
			$response = array();
			if ($comments->comment_count > 0) {
				foreach ($comments->comments as $key => $value) {
					if ($value->user->is_private)
						continue;
					array_push($response, $value->user_id);
					$counter++;
					if (($max_num != NULL) && ($counter >= $max_num))
						break;
				}
			}
			return $response;
		}
	} catch (Exception $e) {
		return array('Error' => $e->getMessage());
	}
}

function getFollowers($username, $password, $userID = NULL, $max_num = NULL) {
	global $ig;
	$getting_my = true;
	if ($userID === NULL)
		$userID = connect($username,$password);
	else {
		$getting_my = false;
		connect($username,$password);
	}
	$maxId = null;
	$followers = array();
	$counter = 0;
	try {
		do {
			$response = $ig->getUserFollowers($userID, $maxId);
			if ($response->status != 'ok')
				return array('Error' => $response);
			foreach ($response->getUsers() as $key => $value) {
				if ((!$getting_my) && ($value->is_private))
					continue;
				array_push($followers, $value->pk);
				$counter++;
				if (($max_num != NULL) && ($counter >= $max_num))
						break;
			}
			$maxId = $response->getNextMaxId();
			if (($max_num != NULL) && ($counter >= $max_num))
					break;
		} while ($maxId !== null);
		return $followers;
	} catch (Exception $e) {
		return array('Error' => $e->getMessage());
	}
}

function getFollowings($username, $password, $userID = NULL) {
	global $ig;
	if ($userID === NULL)
		$userID = connect($username,$password);
	else
		connect($username,$password);
	$maxId = null;
	$followings = array();
	try {
		do {
			$response = $ig->getUserFollowings($userID, $maxId);
			if ($response->status != 'ok')
				return array('Error' => $response);
			foreach ($response->getUsers() as $key => $value) {
				array_push($followings, $value->pk);
			}
			$maxId = $response->getNextMaxId();
		} while ($maxId !== null);
		return $followings;
	} catch (Exception $e) {
		return array('Error' => $e->getMessage());
	}
}

function fetchInstaResult($res) {
    if (array_key_exists('Error', $res)) {
    	logError($res['Error']);
    	foreach ($res['Dump'] as $key => $value) {
    		logError($key.": ".$value);
    	}
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
        echo json_encode(fetchInstaResult(like_insta($username,$password,$postID)));
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