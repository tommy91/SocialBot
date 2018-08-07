<?php
ini_set('display_errors', 'On');
error_reporting(E_ALL | E_STRICT);

require 'vendor/autoload.php';
require 'logManager.php';

\InstagramAPI\Instagram::$allowDangerousWebUsageAtMyOwnRisk = true;
$ig = new \InstagramAPI\Instagram();


function connect($username, $password){
	global $ig;
	$ig->login($username, $password);
	$userID = $ig->people->getUserIdForName($username);
	return $userID;
}

function get_user_info($username, $password) {
	global $ig;
	connect($username,$password);
	try {
		$response = $ig->people->getSelfInfo();
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password));
	}
	if (!$response->isOk())
		return array('Error' => $response);
	$userInfo = $response->getUser();
	return array(
					'follower' => $userInfo->getFollowerCount(),
					'following' => $userInfo->getFollowingCount(),
					'name' => $userInfo->getFullName(),
					'private' => $userInfo->getIsPrivate(),
					'post' => $userInfo->getMediaCount(),
					'message' => $userInfo->getUnseenCount(),
					'usertags' => $userInfo->getUsertagsCount()
				);
}

function get_id_by_username($username, $password, $user) {
	global $ig;
	connect($username,$password);
	try {
		$id = $ig->people->getUserIdForName($user);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'user' => $user));
	}
	return array($id);
}

function get_insta_media($username, $password, $userID, $max_num) {
	global $ig;
	connect($username,$password);
	try {
		$response = $ig->timeline->getUserFeed($userID);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'userID' => $userID, 'max_num' => $max_num));
	}
	if (!$response->isOk())
		return array('Error' => $response);
	else {
		$itemsIds = array();
		$counter = 0;
		foreach ($response->getItems() as $key => $item) {
			if (!($item->getHasLiked())) {
				array_push($itemsIds, $item->getCaption()->getMediaId());
				$counter++;
				if ($counter >= $max_num)
					break;
			}
		}
		return $itemsIds;
	}
}

function follow_insta($username, $password, $userID) {
	global $ig;
	connect($username,$password);
	try {
		$follow_response = $ig->people->follow($userID);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'userID' => $userID));
	}
	if (!$follow_response->isOk())
		return array('Error' => $follow_response);
	else
		return array();
}

function unfollow_insta($username, $password, $userID) {
	global $ig;
	connect($username,$password);
	try {
		$unfollow_response = $ig->people->unfollow($userID);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'userID' => $userID));
	}
	if (!$unfollow_response->isOk())
		return array('Error' => $unfollow_response);
	else
		return array();
}

function like_insta($username, $password, $postID) {
	global $ig;
	connect($username,$password);
	try {
		$like_response = $ig->media->like($postID);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'postID' => $postID));
	}
	if (!$like_response->isOk())
		return array('Error' => $like_response);
	else
		return array();
}

function getHashtagFeed($username, $password, $tag, $is_popular, $max_num) {
	global $ig;
	connect($username,$password);
	$rankToken = \InstagramAPI\Signatures::generateUUID(); 
	try {
		$hashtagFeed = $ig->hashtag->getFeed($tag,$rankToken);
	} catch (Exception $e) {
		return array('Error' => $e->getMessage(), 'Dump' => array('username' => $username, 'password' => $password, 'tag' => $tag, 'is_popular' => $is_popular, 'max_num' => $max_num));
	}
	if ($hashtagFeed->isOk() != 'ok')
		return array('Error' => $hashtagFeed);
	$response = array();
	$counter = 0;
	if ($is_popular)
		$items = $hashtagFeed->getRankedItems();
	else
		$items = $hashtagFeed->getItems();
	foreach ($items as $key => $item) {
		$is_private = $item->getCaption()->getUser()->getIsPrivate();
		$followed_by = $item->getCaption()->getUser()->getFriendshipStatus()->getFollowedBy();
		$following = $item->getCaption()->getUser()->getFriendshipStatus()->getFollowing();
		$outgoing_request = $item->getCaption()->getUser()->getFriendshipStatus()->getOutgoingRequest();
		$has_liked = $item->getHasLiked();
		if ((!$is_private) && (!$followed_by) && (!$following) && (!$outgoing_request) && (!$has_liked)) {
			$post = array(	'mediaID' => $item->getCaption()->getMediaId(), 
				  			'userID' => $item->getCaption()->getUserId()
				  			);
			array_push($response, $post);
			$counter++;
			if ($counter >= $max_num)
				break;
		}
	}
	return $response;
}

function get_likers($username, $password, $mediaID, $max_num = NULL) {
	global $ig;
	connect($username,$password);
	try {
		$likers = $ig->media->getLikers($mediaID);
		$counter = 0;
		if (!$likers->isOk())
			return array('Error' => $likers);
		else {
			$response = array();
			if ($likers->getUserCount() > 0) {
				foreach ($likers->getUsers() as $key => $user) {
					if ($user->getIsPrivate())
						continue;
					array_push($response, $user->getPk());
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
		$comments = $ig->media->getComments($mediaID);
		$counter = 0;
		if (!$comments->isOk())
			return array('Error' => $comments);
		else {
			$response = array();
			if ($comments->getCommentCount() > 0) {
				foreach ($comments->getComments() as $key => $comment) {
					if ($comment->getUser()->getIsPrivate())
						continue;
					array_push($response, $comment->getUserId());
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
	connect($username,$password);
	$getting_my = ($userID === NULL);
	$followers = array();
	$counter = 0;
	// Generate a random rank token
	$rankToken = \InstagramAPI\Signatures::generateUUID(); 
	$maxId = NULL;
	try {
		do {
			if ($getting_my)
				$response = $ig->people->getSelfFollowers($rankToken, NULL, $maxId);
			else
				$response = $ig->people->getFollowers($userID, $rankToken, NULL, $maxId);
			if (!$response->isOk())
				return array('Error' => $response);
			foreach ($response->getUsers() as $key => $user) {
				if ((!$getting_my) && ($user->getIsPrivate()))
					continue;
				array_push($followers, $user->getPk());
				$counter++;
				if (($max_num != NULL) && ($counter >= $max_num))
						break;
			}
			if (($max_num != NULL) && ($counter >= $max_num))
					break;
			$maxId = $response->getNextMaxId();
			// sleeping for 5 seconds to avoid abuse API
			sleep(5);
		} while ($maxId !== NULL);
		return $followers;
	} catch (Exception $e) {
		return array('Error' => $e->getMessage());
	}
}

function getFollowings($username, $password, $userID = NULL, $max_num = NULL) {
	global $ig;
	connect($username,$password);
	$getting_my = ($userID === NULL);
	$following = array();
	$counter = 0;
	// Generate a random rank token
	$rankToken = \InstagramAPI\Signatures::generateUUID(); 
	$maxId = NULL;
	try {
		do {
			if ($getting_my)
				$response = $ig->people->getSelfFollowing($rankToken, NULL, $maxId);
			else
				$response = $ig->people->getFollowing($userID, $rankToken, NULL, $maxId);
			if (!$response->isOk())
				return array('Error' => $response);
			foreach ($response->getUsers() as $key => $user) {
				if ((!$getting_my) && ($user->getIsPrivate()))
					continue;
				array_push($following, $user->getPk());
				$counter++;
				if (($max_num != NULL) && ($counter >= $max_num))
						break;
			}
			if (($max_num != NULL) && ($counter >= $max_num))
					break;
			$maxId = $response->getNextMaxId();
			// sleeping for 5 seconds to avoid abuse API
			sleep(5);
		} while ($maxId !== NULL);
		return $following;
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

$username = "";
$password = "";

// echo "Test page:\r\n";

// echo "connect: ";
// $userID = connect($username, $password);
// print_r($userID);

// echo "get_user_info: ";
// $response = get_user_info($username, $password);
// print_r($response);

// echo "get_id_by_username: ";
// $user = "username";
// $userID = get_id_by_username($username, $password, $user);
// print_r($userID);

// echo "get_insta_media: ";
// $max_num = 1;
// $media = get_insta_media($username, $password, $userID, $max_num);
// print_r($media);

// echo "follow_insta: ";
// $response = follow_insta($username, $password, $userID);
// print_r($response);

// echo "unfollow_insta: ";
// $response = unfollow_insta($username, $password, $userID);
// print_r($response);

// echo "like_insta: ";
// $response = like_insta($username, $password, $media[0]);
// print_r($response);

// echo "getHashtagFeed: ";
// $is_popular = true;
// $tag = "hashtag";
// $max_num = 1;
// $response = getHashtagFeed($username, $password, $tag, $is_popular, $max_num);
// print_r($response);

// echo "get_likers: ";
// $max_num = 1;
// $response = get_likers($username, $password, $media[0], $max_num);
// print_r($response);

// echo "get_comments: ";
// $max_num = 1;
// $response = get_comments($username, $password, $media[0], $max_num);
// print_r($response);

// echo "getFollowers: ";
// $userID = NULL;
// $max_num = NULL;
// $response = getFollowers($username, $password, $userID, $max_num);
// print_r($response);

// echo "getFollowings: ";
// $userID = NULL;
// $max_num = NULL;
// $response = getFollowings($username, $password, $userID, $max_num);
// print_r($response);

?>