-- Table PostsLikes (only for Tumblr)
create table PostsLikes (
    id              text, 
    reblogKey       text, 
    sourceBlog      text, 
    myBlog          text, 
    time            time
);


-- Table Follow
create table Follow (
    sourceBlog      text, 
    myBlog          text, 
    time            time,
    PRIMARY KEY (sourceBlog, myBlog)
);


-- Table Following
create table Following (
    myBlog          text, 
    followedBlog    text, 
    isFollowingBack boolean, 
    time            time,
    PRIMARY KEY (myBlog, followedBlog)
);


-- table Fstats
create table Fstats (
    myBlog          text, 
    followedBlog    text, 
    action          text,
    gotBy           text, 
    time            time
);


-- Table Unfollowed
create table Unfollowed (
    myBlog          text,
    unfollowedBlog  text,
    time            time,
    PRIMARY KEY (myBlog, unfollowedBlog)
);
