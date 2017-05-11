<?php

require 'vendor/autoload.php';

$ig = new \InstagramAPI\Instagram();


function connect($username, $password){
	global $ig;
	$ig->setUser($username, $password);
	$ig->login();
	//return $ig->getUsernameId($username);
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

function search_tag($username, $password, $tag, $num_posts) {
	global $ig;
	connect($username,$password);
	// $post = $ig->searchTags($tag);
	$post = $ig->getHashtagFeed($tag);
	if ($post->status != 'ok')
		return array('Error' => $post);
	else {
		// $media_ids = array();
		// foreach ($post->results as $key => $value) {
		// 	array_push($media_ids, $value->id);
		// 	if (($key + 1) == $num_posts)
		// 		break;
		// }
		// return $media_ids;
		return $post;
	}
}

function get_likers($username,$password,$mediaID) {
	global $ig;
	connect($username,$password);
	$likers = $ig->getMediaLikers($mediaID);
	try {
		if ($likers->status != 'ok')
			return array('Error' => $post);
		else {
			return $likers;
		}
	} catch (Exception $e) {
		return array('Error' => $e->getMessage());
	}
}

// $userID = connect($username,$password);
	
// $follower = $ig->getUserFollowers($userID);

// foreach ($follower->users as $key => $value) {
// 	echo $value->username, '<br>';
// }

?>