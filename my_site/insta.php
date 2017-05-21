<?php

require 'vendor/autoload.php';

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
	$info = $ig->getSelfUserInfo();
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
	$info = $ig->getUserInfoByName($user);
	if ($info->status != 'ok')
		return array('Error' => $info);
	return array($info->user->pk);
}

function get_insta_media($username, $password, $user, $max_num) {
	global $ig;
	connect($username,$password);
	$media = $ig->getUserFeed($user);
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
	$follow_response = $ig->follow($user);
	if ($follow_response->status != 'ok')
		return array('Error' => $follow_response);
	else
		return array();
}

function unfollow_insta($username, $password, $user) {
	global $ig;
	connect($username,$password);
	$unfollow_response = $ig->unfollow($user);
	if ($unfollow_response->status != 'ok')
		return array('Error' => $unfollow_response);
	else
		return array();
}

function like_insta($username, $password, $postID) {
	global $ig;
	connect($username,$password);
	$like_response = $ig->like($postID);
	if ($like_response->status != 'ok')
		return array('Error' => $like_response);
	else
		return array();
}

function getHashtagFeed($username, $password, $tag, $is_popular, $max_num) {
	global $ig;
	connect($username,$password);
	$hashtagFeed = $ig->getHashtagFeed($tag);
	if ($hashtagFeed->status != 'ok')
		return array('Error' => $hashtagFeed);
	else {
		$response = array();
		$counter = 0;
		if ($is_popular) {
			foreach ($hashtagFeed->ranked_items as $key => $value) {
				$followed_by = $value->caption->user->friendship_status->followed_by;
				$following = $value->caption->user->friendship_status->following;
				$outgoing_request = $value->caption->user->friendship_status->outgoing_request;
				$has_liked = $value->has_liked;
				if ((!$followed_by) && (!$following) && (!$outgoing_request) && (!$has_liked)) {
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
				$followed_by = $value->caption->user->friendship_status->followed_by;
				$following = $value->caption->user->friendship_status->following;
				$outgoing_request = $value->caption->user->friendship_status->outgoing_request;
				$has_liked = $value->has_liked;
				if ((!$followed_by) && (!$following) && (!$outgoing_request) && (!$has_liked)) {
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
	$likers = $ig->getMediaLikers($mediaID);
	$counter = 0;
	try {
		if ($likers->status != 'ok')
			return array('Error' => $likers);
		else {
			$response = array();
			if ($likers->user_count > 0) {
				foreach ($likers->users as $key => $value) {
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
	$comments = $ig->getMediaComments($mediaID);
	$counter = 0;
	try {
		if ($comments->status != 'ok')
			return array('Error' => $comments);
		else {
			$response = array();
			if ($comments->comment_count > 0) {
				foreach ($comments->comments as $key => $value) {
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
	if ($userID === NULL)
		$userID = connect($username,$password);
	else
		connect($username,$password);
	$maxId = null;
	$followers = array();
	$counter = 0;
	try {
		do {
			$response = $ig->getUserFollowers($userID, $maxId);
			if ($response->status != 'ok')
				return array('Error' => $response);
			foreach ($response->getUsers() as $key => $value) {
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


?>