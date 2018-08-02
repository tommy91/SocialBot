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
    myblog          text, 
    time            time
);


-- table Following
create table Following (
    myBlog          text, 
    followedBlog    text, 
    isFollowingBack boolean, 
    time            time
);


-- table Fstats
create table Fstats (
    myBlog          text, 
    followedBlog    text, 
    action          text,
    gotBy           text, 
    time            time
);
