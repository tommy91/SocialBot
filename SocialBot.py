import os
import sys
import time
import random
import datetime
import threading
import requests
from pprint import pprint
import socket
from httplib2 import ServerNotFoundError
from requests.exceptions import ConnectionError, Timeout, HTTPError

import dbManager
import pytumblr

#import Settings

# Per debugging locale
import local_settings as Settings


lock = threading.RLock()

sleepCharDefault = 0.02
sleepLineDefault = 0.3
sleepChar = 0.02
sleepLine = 0.3
lastline = ""

isTest = False
timers = {}
timersTime = {}
startSimble = "-> "
canWrite = True
startSessionTime = ""
appAccountList = {}
clients = {}
clientsInfo = {}
blogs = {}
matches = {}
followersList = {}
followingList = {}

# Specifics
TIMERHALFWINDOW = 10
LIMITFOLLOW = 4950
STATUS_RUN = 1
STATUS_STOP = 0

PATH_TO_SERVER = Settings.PATH_TO_SERVER
RECEIVER = Settings.RECEIVER 


def writeln(res, force = False):
    "Write a message with new line symble"
    global lock
    if (not force) and (not canWrite):
        return
    lock.acquire()
    now = datetime.datetime.now()
    nowstr = date2string(now)
    try:
        sys.stdout.write(nowstr + startSimble)
        sys.stdout.flush()
        write(res, force)
    finally:
        lock.release()


def write(res, force = False):
    "Write a message without new line symble"
    global lock, lastline
    if (not force) and (not canWrite):
        return
    lock.acquire()
    lastline = res
    try:
        time.sleep(sleepLine)
        for c in res:
            sys.stdout.write('%s' % c)
            sys.stdout.flush()
            time.sleep(sleepChar)

    finally:
        lock.release()


def clearline():
    "Clear the last line in output"
    global lock, lastline
    lock.acquire()
    try:
        cll = 0
        while cll < len(lastline):
            sys.stdout.write('\b \b')
            cll += 1
    finally:
        sys.stdout.flush()
        lock.release()


def date2string(d):
    day = date2str(d.day)
    month = date2str(d.month)
    year = date2str(d.year)
    hour = date2str(d.hour)
    minute = date2str(d.minute)
    second = date2str(d.second)
    return (str(hour) + ":" + str(minute) + ":" + str(second) + " " + str(day) + "/" + str(month))


def date2str(objDate):
    s = str(objDate)
    if len(s) == 1:
        s = "0" + s
    return s


def post_request(post_data):
    try:
        return send_and_check_request(post_data)
    except HTTPError as e:
        print e
        return None


def send_and_check_request(post_data):
    try:
        resp = requests.post(PATH_TO_SERVER + RECEIVER, data = post_data)
        if resp.status_code == 200:
            try:
                parsed = resp.json()
                if 'Error' in parsed:
                    print "Errore: " + str(parsed['Error'])
                    return None
                else:
                    return parsed['Result']
            except ValueError as e:
                print "Errore:"
                print resp.content
                return None
        else:
            resp.raise_for_status()
    except ConnectionError as e:
        print "Errore:"
        print e
        return None 
    except Timeout as e:
        print "Errore:"
        print e
        return None


def checkInputParams():
    global isTest, sleepChar, sleepLine
    lp = len(sys.argv)
    if lp > 2:
        print("\n\tError: " + str(lp-1) + " params, admitted only 1! Ignored all.\n")
    elif lp > 1:
        if(sys.argv[1]=='-f'):
            print("\n\tFast Mode On.\n\tNo sleep char/line.\n")
            sleepChar = 0.0
            sleepLine = 0.0
        elif(sys.argv[1]=='-t'):
            print("\n\tTest Mode On.\n")
            isTest = True
        elif(sys.argv[1] in ['-ft','-tf']):
            print("\n\tFast Mode On.\n\tNo sleep char/line.\n")
            sleepChar = 0.0
            sleepLine = 0.0
            print("\n\tTest Mode On.\n")
            isTest = True
        else:
            print("\n\tError: unknown command '" + sys.argv[1] + "', ignored.\n")


def printHello():
    write("""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$   WELCOME SOCIAL BOT   $$$$$$$$$$$$$$$$$$$$$$$$$$\n\
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n""")


def tryConnectToRemoteServer():
    "Look for the remote server"
    write("Trying connecting to server online.. ")
    resp = post_request({"action": "server_alive"})
    if resp != None:
        print "ok"
        return True
    else:
        return False


def tryConnectDB():
    "Look for database"
    write("Look for database (" + dbManager.dbName + ").. ")
    if (not os.path.exists(dbManager.dbName)):
        write("not in path\n")
        dbManager.initDB()
    else:
        write("already in path!\n")


def newEntry():
    global timers, canWrite
    while True:
        entry = raw_input("\n" + startSimble)
        if entry in ["quit","exit"]:
            canWrite = True
            closing_operations()
            break
        elif entry in ["log"]:
            canWrite = True
            logResults()
        elif entry in ["help","info"]:
            prevCanWrite = canWrite
            canWrite = True
            printHelpCmd()
            prevCanWrite = canWrite
    #     elif entry in ["dbmanager","dbm","dbManager","DBM"]:
    #         write_console(myConsole.console, "Opening DB Manager Console.. ")
    #         dBMConsole()
        elif (entry != "") and (entry.split()[0] in ["changeSpeed","speed","cs"]):
            changeSpeed(entry)
        elif (entry != "") and (entry.split()[0] in ["run","Run"]):
            try:
                if entry.split()[1] in ["all","All"]:
                    for key, blog in blogs.iteritems():
                        if blog['type'] == 1: 
                            if blog['data']['blogname'] != "not available":
                                runBlog(blog['ID'])
                            else:
                                write("Cannot run not available blog! (id: " + blog['strID'] + ")\n",True)
                        else:
                            if blog['data']['name'] != "not available":
                                runBlog(blog['ID'])
                            else:
                                write("Cannot run not available blog! (id: " + blog['strID'] + ")\n",True)
                else:
                    try:
                        runBlog(matches[entry.split()[1]])
                    except KeyError, msg:
                        write(entry.split()[1] + " is not an existing blogname!\n",True)
                if canWrite:
                    logResults()
            except IndexError, msg:
                write("   Syntax error: 'run all' or 'run _blogname_'\n",True)
        elif (entry != "") and (entry.split()[0] in ["stop","Stop"]):
            try:
                if entry.split()[1] in ["all","All"]:
                    for kb,blog in blogs.iteritems():
                        if blog['type'] == 1: 
                            if blog['data']['blogname'] != "not available":
                                stopBlog(blog['ID'])
                        else:
                            if blog['data']['name'] != "not available":
                                stopBlog(blog['ID'])
                    timers["update"].cancel()
                    timers = {}
                else: 
                    try:
                        stopBlog(matches[entry.split()[1]])
                    except KeyError, msg:
                        write(entry.split()[1] + " is not an existing blogname!\n",True)
            except IndexError, msg:
                write("   Syntax error: 'stop all' or 'stop _blogname_'\n",True)
        elif (entry != "") and (entry.split()[0] == "copy"):
            prevCanWrite = canWrite
            canWrite = True
            try:
                blog_to_copy = entry.split()[1]
                my_blog = entry.split()[2]
                limit = int(entry.split()[3])
                counter = int(entry.split()[4])
                write("Creating new thread for copy the blog.. ",True)
                t = threading.Thread(target=copyBlog, args=(blog_to_copy,my_blog,limit,counter)).start()
                updateStatistics()
                canWrite = prevCanWrite
            except IndexError, msg:
                write("   Syntax error: 'copy source myblog limit counter'\n",True)
                canWrite = prevCanWrite


def logResults():
    global canWrite
    write("Logging results..\n")
    while not raw_input() in ['q','Q']:
        pass
    canWrite = False


def printHelpCmd():
    "Print list of available commands"
    write("List of commands:\n",True)
    write("   - 'help': for list of instructions\n",True)
    write("   - 'changeSpeed': for changing printing text speed\n",True)
    write("   - 'copy blog_to_copy my_blog': for copy an entire blog\n",True)
    write("   - 'dbm': for open database manager console\n",True)
    write("   - 'run': for run a/all blog(s)\n",True)
    write("   - 'stop': for stop a/all blog(s)\n",True)
    write("   - 'quit': for quit\n",True)


def closing_operations():
    global timers, blogs
    write("Terminating program.\n")
    for key, blog in blogs.iteritems():
        if blog['status'] == STATUS_RUN:
            stopBlog(blog['ID'])
    try:
        timers["update"].cancel()
    except KeyError, msg:
        pass
    updateStatistics()
    resp = post_request({"action": "closing_operations", "stop_session_time": datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')})
    write("   Bye!\n\n")


def changeSpeed(entry):
    global sleepChar, sleepLine
    e = entry.split()
    l = len(entry.split())
    if (l > 1) and (l < 6):
        c = 1
        while c < l:
            if e[c] == "-c":
                c = c + 1
                if e[c] == "default":
                    sleepChar = sleepCharDefault
                else:
                    try:
                        sleepChar = float(e[c])
                    except ValueError, msg:
                        write("   Error: " + str(msg) + "\n",True)
                        break
                write("New speed char: " + str(sleepChar) + "\n",True)
                c = c + 1
            elif e[c] == "-l":
                c = c + 1
                if e[c] == "default":
                    sleepLine = sleepLineDefault
                else:
                    try:
                        sleepLine = float(e[c])
                    except ValueError, msg:
                        write("   Error: " + str(msg) + "\n",True)
                        break
                write("New speed line: " + str(sleepLine) + "\n",True)
                c = c + 1 
            else:
                write("Error: expecting '-c' or '-l' at " + str(c) + " position!\n",True)
                break
    elif l >= 6:
        write("Error: too many arguments!\n",True)
    else:
        write("Current speeds:\n   char: " + str(sleepChar) + "\n   line: " + str(sleepLine) + "\n",True)
        write("For modify this values enter:\n",True)
        write("   changeSpeed -c 'float_value/default' -l 'float_value/default'\n",True)


def runBlog(id_blog):
    global timers, blogs, lock, canWrite
    lock.acquire()
    prevCanWrite = canWrite
    canWrite = True
    blog = blogs[str(id_blog)]
    writeln("Run " + blog['data']['blogname'] + ":\n")
    calc_time_post_follow(id_blog)
    if blog['type'] == 1:
        check_num_post_follow(id_blog)
    else:
        check_num_like_follow_insta(id_blog)
    if timers == {}:
        set_update_timer()
    set_post_timer(id_blog)
    set_follow_timer(id_blog)
    set_like_timer(id_blog)
    if blog['type'] == 1:
        write("\t" + blog['data']['blogname'] + " is running.\n")
    else:
        write("\t" + blog['data']['name'] + " is running.\n")
    blogs[str(id_blog)]['status'] = STATUS_RUN
    updateBlogData(id_blog)
    updateStatistics()
    canWrite = prevCanWrite
    lock.release()


def stopBlog(id_blog):
    global timers, blogs, lock, canWrite
    lock.acquire()
    prevCanWrite = canWrite
    canWrite = True
    blog = blogs[str(id_blog)]
    if blog['type'] == 1:
        writeln("Stop " + blog['data']['blogname'] + ".. \n")
    else:
        writeln("Stop " + blog['data']['name'] + ".. \n")
    blogs[str(id_blog)]['status'] = STATUS_STOP
    updateBlogData(id_blog)
    timers[blog['strID'] + "-post"].cancel()
    del timers[blog['strID'] + "-post"]
    timers[blog['strID'] + "-follow"].cancel()
    del timers[blog['strID'] + "-follow"]
    timers[blog['strID'] + "-like"].cancel()
    del timers[blog['strID'] + "-like"]
    updateStatistics()
    if blog['type'] == 1:
        write("\t" + blog['data']['blogname'] + " stopped.\n")
    else:
        write("\t" + blog['data']['name'] + " stopped.\n")
    canWrite = prevCanWrite
    lock.release()


def calc_time_post_follow(id_blog):
    global timers, blogs
    blog = blogs[str(id_blog)]
    if blog['type'] == 1:
        write("\tCalcule timers for " + blog['data']['blogname'] + ":\n")
    else:
        write("\tCalcule timers for " + blog['data']['name'] + ":\n")
    blog['timer_post'] = int((24*60/(int(blog['num_post_xd'])/int(blog['num_post_xt'])))+0.5)
    write("\t\tpost every " + str(blog['timer_post']) + " minutes\n")
    blog['timer_follow'] = int((24*60/(int(blog['num_follow_xd'])/int(blog['num_follow_xt'])))+0.5)
    write("\t\tfollow every " + str(blog['timer_follow']) + " minutes\n")
    blog['timer_like'] = int((24*60/(int(blog['num_like_xd'])/int(blog['num_like_xt'])))+0.5)
    write("\t\tlike every " + str(blog['timer_like']) + " minutes\n")


def check_num_post_follow(id_blog):
    global timers, blogs
    blog = blogs[str(id_blog)]
    bn = blog['data']['blogname']
    if bn != "not available":
        write("\tCheck number posts in DB for " + bn + ":\n")
        posts = int(dbManager.countPost(bn))
        write("\t   #post: " + str(posts) + ".. ")
        if posts >= blog['num_post_xt']:
            write("ok\n")
        else:
            write("needed at least " + str(blog['num_post_xt']) + "\n")
            search_post(id_blog,bn,blog['blogs'],num_post=(blog['num_post_xt']-posts))
        follows = dbManager.countFollow(bn)
        write("\t   #follow: " + str(follows) + ".. ")
        if follows >= (blog['num_follow_xt']/2):
            write("ok\n")
        else:
            write("needed at least " + str(blog['num_follow_xt']/2) + "\n")
            search_by_tag(id_blog,bn,(blog['num_follow_xt']/2)-follows)
        f4f = dbManager.countFollow("f4f-tumblr")
        write("\t   #f4f-tumblr: " + str(f4f) + ".. ")
        if f4f >= (blog['num_follow_xt']/2):
            write("ok\n")
        else:
            write("needed at least " + str(blog['num_follow_xt']/2) + "\n")
            tag = random_f4f()
            searchTag(id_blog,"f4f-tumblr",(blog['num_follow_xt']/2)-f4f,tag)


def check_num_like_follow_insta(id_blog):
    global timers, blogs
    blog = blogs[str(id_blog)]
    bn = blog['data']['name']
    if bn != "not available":
        write("\tCheck number follow & likes in DB for " + bn + ":\n")
        follows = dbManager.countFollow(bn)
        write("\t   #follow: " + str(follows) + ".. ")
        if follows >= (blog['num_follow_xt']/2):
            write("ok\n")
        else:
            write("needed at least " + str(blog['num_follow_xt']/2) + "\n")
            search_by_tag_insta(id_blog,bn,(blog['num_follow_xt']/2)-follows)
        f4f = dbManager.countFollow("f4f-insta")
        write("\t   #f4f-insta: " + str(f4f) + ".. ")
        if f4f >= (blog['num_follow_xt']/2):
            write("ok\n")
        else:
            write("needed at least " + str(blog['num_follow_xt']/2) + "\n")
            tag = random_f4f()
            searchTagInsta(id_blog,"f4f-insta",(blog['num_follow_xt']/2)-f4f,tag)
        l4l = dbManager.countLike("l4l-insta")
        write("\t   #l4l-insta: " + str(like) + ".. ")
        if l4l >= blog['num_like_xt']:
            write("ok\n")
        else:
            write("needed at least " + str(blog['num_like_xt']) + "\n")
            tag = random_l4l()
            searchTagInsta(id_blog,"l4l-insta",blog['num_like_xt']-f4f,tag)

def search_post(id_blog,blogname,following_blogs,num_post=-1):
    global blogs
    blog = blogs[str(id_blog)]
    if num_post == -1:
        num_post = blog['num_post_xt']
    try:
        client = clientsInfo[blog['strID']]
        clientLike = clients[blog['strID']]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    num_following_blogs = len(following_blogs)
    postXblog = 0
    if num_following_blogs >= num_post:
        postXblog = 1
    else:
        postXblog = int(num_post/num_following_blogs)+1
    write("\t      Getting posts..\n")
    follows = dbManager.countFollow(blogname)
    need_follow = False
    if follows <= (blog['num_follow_xt']/2):
        need_follow = True
    for following_blog in following_blogs:
        # following_blog = following_blog['Name']
        counter = 0
        offset_posts = 0
        write("\t         post from " + following_blog + ".. ")
        new_follows = []
        id_posts = []
        while counter < postXblog:
            try:
                response = client.posts(following_blog, type = "photo", notes_info = need_follow, offset = offset_posts)  # , limit = postXblog*5
                if response['posts'] == []:
                    break
                for post in response['posts']:
                    try:
                        if (not post['liked']) and (not post['id'] in id_posts):
                            id = post['id']
                            id_posts.append(id)
                            reblog_key = post['reblog_key']
                            args = (id,reblog_key,following_blog,blogname,int(time.time()))
                            clientLike.like(id,reblog_key)
                            dbManager.add("PostsLikes",args)
                            counter_notes = 0
                            if need_follow:
                                for note in post['notes']:
                                    if not note['followed']:
                                        new_follows.append(note['blog_name'])
                                        counter_notes += 1
                                    if counter_notes >= (blog['num_follow_xt']/2):
                                        break
                            counter += 1
                    except KeyError,msg:
                        write("\n\t         Error (keyerror) on searchpost: " + str(msg) + "\n")
                        # pprint(post)
                        counter += 1
                    offset_posts += 1
                    clearline()
                    write("\t         post from " + following_blog + ".. " + str(counter) + "/" + str(postXblog) + "(scaled " + str(offset_posts) + "/" + str(response['blog']['posts']) + ")")
                    if counter >= postXblog:
                        break
            except Exception,msg:
                write("\n\t         Error Exception.. " + str(msg) + "\n") 
                break
        for new_follow in new_follows:
            args = (new_follow,blogname,int(time.time()))
            dbManager.add("Follow",args)
        write("\r\t         post from " + following_blog + ".. Done! (" + str(counter))
        if counter > 1:
            write(" posts")
        else:
            write(" post")
        if need_follow:
            write(" and " + str(len(new_follows)) + " follow)\n")
        else:
            write(")\n")
        updateStatistics()


def search_by_tag(id_blog,blogname,num_tags):
    global blogs
    blog = blogs[str(id_blog)]
    tag = random_tag(blog['tags'])
    searchTag(id_blog,blogname,num_tags,tag)


def search_by_tag_insta(id_blog,blogname,num_tags):
    global blogs
    blog = blogs[str(id_blog)]
    tag = random_tag(blog['blogs'])
    searchTagInsta(id_blog,blogname,num_tags,tag)


def searchTag(id_blog,blogname,num_tags,tag):
    try:
        client = clientsInfo[str(id_blog)]
        clientLike = clients[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    counter = 0
    write("\t      Getting follows..\n")
    new_follows = []
    write("\t         posts tagged " + tag + ".. ")
    timestamp = int(time.time())
    try:
        while counter < num_tags:
            response = client.tagged(tag,before=timestamp)
            for post in response:
                try:
                    if not post['followed']:
                        new_follows.append(post['blog_name'])
                        counter += 1
                        write("\r\t         posts tagged " + tag + ".. " + str(counter) + "/" + str(num_tags))
                    timestamp = post['timestamp']
                except KeyError,msg:
                    write("\n\t         Error (keyerror) on search_by_tag: " + str(msg) + "\n")
                    counter += 1
                if counter >= num_tags:
                    break
        for new_follow in new_follows:
            args = (new_follow,blogname,int(time.time()))
            dbManager.add("Follow",args)
        write("\r\t         posts tagged " + tag + ".. Done! (" + str(counter) + " follow)\n")
    except Exception,msg:
        write("\n\t         Error Exception\n")
    updateStatistics()


def searchTagInsta(id_blog,blogname,num_tags,tag):
    counter = 0
    write("\t      Searching by tags..\n")
    new_follows = []
    write("\t         posts tagged " + tag + ".. ")
    timestamp = int(time.time())
    try:
        while counter < num_tags:
            # response = client.tagged(tag,before=timestamp)
            # for post in response:
            #     try:
            #         if not post['followed']:
            #             new_follows.append(post['blog_name'])
            #             counter += 1
            #             write("\r\t         posts tagged " + tag + ".. " + str(counter) + "/" + str(num_tags))
            #         timestamp = post['timestamp']
            #     except KeyError,msg:
            #         write("\n\t         Error (keyerror) on search_by_tag: " + str(msg) + "\n")
            #         counter += 1
            #     if counter >= num_tags:
            #         break
            pass
        for new_follow in new_follows:
            args = (new_follow,blogname,int(time.time()))
            dbManager.add("Follow",args)
        write("\r\t         posts tagged " + tag + ".. Done! (" + str(counter) + " follow)\n")
    except Exception,msg:
        write("\n\t         Error Exception\n")
    updateStatistics()


def random_tag(tags):
    new_tags = []
    for tag in tags:
        if not tag in ["follow4follow","follow","f4f","followback","Follow4Follow","Follow","F4F","FollowBack","like4like","like","likeback","l4l","Like4Like","Like","LikeBack","L4L"]:
            new_tags.append(tag)
    tag_pos = random.randint(0, len(new_tags)-1)
    return new_tags[tag_pos]


def random_f4f():
    f4fs = ["follow4follow","follow","followback","f4f"]
    tag_pos = random.randint(0, len(f4fs)-1)
    return f4fs[tag_pos]


def random_l4l():
    l4ls = ["like4like","like","likeback","l4l"]
    tag_pos = random.randint(0, len(l4ls)-1)
    return l4ls[tag_pos]


def set_update_timer():
    global timers, timersTime
    fiveMin = 60*5
    tup = threading.Timer(fiveMin, updateBlogs)
    tup.start()
    timers["update"] = tup
    deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + fiveMin)).strftime('%H:%M:%S %d/%m')
    timersTime["update"] = deadline


def set_post_timer(id_blog):
    global timers, blogs
    blog = blogs[str(id_blog)]
    timer_post = random.randint((blog['timer_post']*60) - (TIMERHALFWINDOW*60), (blog['timer_post']*60) + (TIMERHALFWINDOW*60))
    tp = threading.Timer(timer_post, post, [id_blog, blog['data']['blogname']]) # in seconds
    tp.start() 
    timers[str(id_blog) + "-post"] = tp
    deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_post)).strftime('%H:%M:%S %d/%m')
    timersTime[str(id_blog) + "-post"] = deadline
    write("\tcreated new thread for post after " + str(timer_post) + "sec (~ " + str(int(timer_post/60)) + " min)\n")
    updateStatistics()


def set_like_timer(id_blog):
    global timers, blogs
    blog = blogs[str(id_blog)]
    timer_like = random.randint((blog['timer_like']*60) - (TIMERHALFWINDOW*60), (blog['timer_like']*60) + (TIMERHALFWINDOW*60))
    tl = threading.Timer(timer_like, like, [id_blog, blog['data']['blogname']]) # in seconds
    tl.start() 
    timers[str(id_blog) + "-like"] = tl
    deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_like)).strftime('%H:%M:%S %d/%m')
    timersTime[str(id_blog) + "-like"] = deadline
    write("\tcreated new thread for like after " + str(timer_like) + "sec (~ " + str(int(timer_like/60)) + " min)\n")
    updateStatistics()


def set_follow_timer(id_blog):
    global timers, blogs
    blog = blogs[str(id_blog)]
    timer_follow = random.randint((blog['timer_follow']*60) - (TIMERHALFWINDOW*60), (blog['timer_follow']*60) + (TIMERHALFWINDOW*60))
    tf = threading.Timer(timer_follow, follow, [id_blog, blog['data']['blogname']]) # in seconds
    tf.start() 
    timers[str(id_blog) + "-follow"] = tf
    deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + timer_follow)).strftime('%H:%M:%S %d/%m')
    timersTime[str(id_blog) + "-follow"] = deadline
    write("\tcreated new thread for follow after " + str(timer_follow) + "sec (~ " + str(int(timer_follow/60)) + " min)\n")
    updateStatistics()


def updateBlogs():
    global blogs,clients,timers,matches,lock
    lock.acquire()
    writeln("Update blogs info.\n")
    for kb,blog in blogs.iteritems():
        try:
            try:
                client = clientsInfo[blog['strID']]
            except KeyError, msg:
                write("Error: client for '" + blog['data']['blogname'] + "' not available! (" + str(msg) + ")\n")
                continue
            try:
                response = client.info()
                if not checkResponse(response):
                    continue
                blog['data']['likes'] = response["user"]["likes"]
                blog['data']['following'] = response["user"]["following"]
                blog['data']['followers'] = response["user"]["blogs"][0]["followers"]
                blog['data']['messages'] = response["user"]["blogs"][0]["messages"]
                blog['data']['posts'] = response["user"]["blogs"][0]["posts"]
                blog['data']['queue'] = response["user"]["blogs"][0]["queue"] 
                if blog['data']['username'] == "not available":
                    blog['data']['username'] = response["user"]["name"]
                    blog['data']['blogname'] = response["user"]["blogs"][0]["name"]
                    blog['data']['url'] = response["user"]["blogs"][0]["url"]
                    matches[response["user"]["blogs"][0]["name"]] = blog['ID']
            except Exception, msg:
                write("\tUpdate Error on client.info(): " + str(msg) + "\n")
        except ServerNotFoundError,msg:
            write("\tUpdate Error: " + str(msg) + "\n")
        except socket.error, msg:
            write("\tUpdate Error: " + str(msg) + "\n")
    fiveMin = 60*5
    deadline = datetime.datetime.fromtimestamp(float(int(time.time()) + fiveMin)).strftime('%H:%M:%S %d/%m')
    timersTime["update"] = deadline
    updateBlogsData()
    synchOperations()
    updateStatistics()
    if not isTest:
        set_update_timer()
    lock.release()


def post(id_blog, blogname, num_posts=-1, isDump = False):
    global blogs, clients, lock
    lock.acquire()
    writeln("Posting " + blogname + ":\n")
    blog = blogs[str(id_blog)]
    if num_posts == -1:
        num_posts = blog['num_post_xt']
    try:
        client = clients[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    posts = dbManager.getPosts(blogname,num_posts)
    if isDump:
        print posts 
    counter = 0
    for post in posts:
        try:
            if isDump:
                print post 
            client.reblog(blogname, id=post['id'], reblog_key=post['reblogKey'], tags = blog["tags"], type = "photo", caption="")
            args = (post['id'],blogname)
            dbManager.delete("PostsLikes",args)
            counter += 1
            write("\r\tposted " + str(counter) + "/" + str(num_posts))
        except Exception,msg:
            write("\n\tError: exception on " + blogname + " reblogging\n" + str(msg) + "\n")
    write("\r\tposted " + str(counter) + " posts!\n")
    if not isTest:
        set_post_timer(id_blog)
        count_posts = dbManager.countPost(blogname)
        if count_posts < num_posts:
            writeln(blogname + ": searching new posts!\n")
            search_post(id_blog,blogname,blog['blogs'],num_post=(num_posts-count_posts))
    updateBlogData(id_blog)
    lock.release()


def follow(id_blog, blogname, num_follows=-1, isDump = False):
    global blogs, clients, lock
    lock.acquire()
    writeln("Following " + blogname + ":\n")
    blog = blogs[str(id_blog)]
    if num_follows == -1:
        num_follows = blog['num_follow_xt']
    try:
        client = clients[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    if blog['data']['following'] >= LIMITFOLLOW:
        try:
            unfollow(id_blog,blogname)
        except Exception, msg:
            write("\n\tError: exception on " + blogname + " following\n")
    follows = dbManager.getFollows(blogname,num_follows/2)
    if isDump:
        print follows
    counter = 0
    for follow in follows:
        try:
            if isDump:
                print follow
            client.follow(follow['sourceBlog'])
            args = (follow['sourceBlog'],blogname)
            dbManager.delete("Follow",args)
            counter += 1
            write("\r\tfollowed " + str(counter) + "/" + str(num_follows))
        except Exception,msg:
            write("\n\tError: exception on " + blogname + " following\n")
    f4fs = dbManager.getFollows("f4f-tumblr",num_follows/2)
    if isDump:
        print f4fs
    for f4f in f4fs:
        try:
            if isDump:
                print f4f
            client.follow(f4f['sourceBlog'])
            args = (f4f['sourceBlog'],"f4f-tumblr")
            dbManager.delete("Follow",args)
            counter += 1
            write("\r\tfollowed " + str(counter) + "/" + str(num_follows))
        except Exception,msg:
            write("\n\tError: exception on f4f-tumblr following\n")
    write("\r\tfollowed " + str(counter) + " blogs!\n")
    if not isTest:
        set_follow_timer(id_blog)
        num_following_blogs = dbManager.countFollow(blogname)
        if num_following_blogs < num_follows/2:
            writeln(blogname + ": searching new follows!\n")
            search_by_tag(id_blog,blogname,(num_follows/2)-num_following_blogs)
        num_f4fs = dbManager.countFollow("f4f-tumblr")
        if num_f4fs < num_follows/2:
            writeln("f4f-tumblr: searching new follows!\n")
            tag = random_f4f()
            searchTag(id_blog,"f4f-tumblr",(num_follows/2)-num_f4fs,tag)
    updateBlogData(id_blog)
    lock.release()


def unfollow(id_blog,blogname):
    global followersList, followingList
    writeln("Unfollowing " + blogname + ":\n")
    blog = blogs[str(id_blog)]
    try:
        client = clients[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    updateFollowers(id_blog, blogname)
    counterUnfollow = 0
    alreadyGetFollowing = False
    firstTimeGetFollowing = True
    while (counterUnfollow <= blog['num_follow_xt']) and (not alreadyGetFollowing):
        try:
            blog_name_unfollow = followingList[id_blog].pop()
            if not (blog_name_unfollow in followersList[id_blog]):
                client.unfollow(blog_name_unfollow)
                counterUnfollow += 1
                write("\r\tUnfollowed " + str(counterUnfollow) + "/" + str(blog['num_follow_xt']))
        except IndexError, msg:
            if firstTimeGetFollowing:
                getFollowing(id_blog,blogname)
                firstTimeGetFollowing = False
            else:
                alreadyGetFollowing = True
                write("\n\tProblem: already get all following..\n")
    write("\r\tUnfollowed " + str(counterUnfollow) + " blogs.\n")


def like(id_blog, blogname, num_likes=-1):
    global blogs, clients, lock
    lock.acquire()
    writeln("Liking " + blogname + ":\n")
    blog = blogs[str(id_blog)]
    if num_likes == -1:
        num_likes = blog['num_like_xt']
    try:
        client = clientsInfo[str(id_blog)]
        clientLike = clients[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    tag = random_tag(blog['tags'])
    try:
        response = client.tagged(tag)
        counter = 0
        for post in response:
            try:
                if (not post['liked']) and (not post['followed']):
                    id = post['id']
                    reblog_key = post['reblog_key']
                    clientLike.like(id,reblog_key)
                    counter += 1
                    write("\r\tliked " + str(counter) + "/" + str(num_likes))
            except KeyError,msg:
                write("\n\tError (keyerror) on like: " + str(msg) + "\n")
                break
            if counter >= num_likes:
                break
        write("\r\tliked " + str(counter) + " posts!\n")
    except Exception,msg:
        write("Error Exception\n")
    if not isTest:
        set_like_timer(id_blog)
    updateBlogData(id_blog)
    lock.release()

def updateFollowers(id_blog, blogname):
    global followersList,blogs
    write("\tUpdate Followers List.. ")
    blog = blogs[str(id_blog)]
    try:
        client = clientsInfo[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    numFollowers = len(followersList[str(id_blog)])
    areNotEnough = (numFollowers < blog['data']['followers'])
    shouldGetNew = areNotEnough
    offsetFollowers = 0
    counterFollowers = 0
    numErrors = 0
    while shouldGetNew:
        try:
            followers = client.followers(blogname,offset=offsetFollowers)
            if followers['users'] == []:
                break
            for follower in followers['users']:
                offsetFollowers += 1
                if not (follower['name'] in followersList[str(id_blog)]):
                    followersList[str(id_blog)].append(follower['name'])
                    counterFollowers += 1
            if (numFollowers + offsetFollowers) >= followers['total_users']:
                shouldGetNew = False
            write("\r\tUpdate Followers List.. " + str(numFollowers + offsetFollowers) + "/" + str(followers['total_users']) + " ")
        except KeyError, msg:
            numErrors += 1
            if numErrors > 10:
                shouldGetNew = False
            else: 
                time.sleep(2)
    if not areNotEnough:
        write("no need!\n")
    else:
        write("Done! (" + str(counterFollowers) + " new blogs)\n")

def getFollowers(id_blog, blogname):
    global followersList
    write("\tGet Followers List.. ")
    try:
        client = clientsInfo[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    followersList[str(id_blog)] = []
    shouldGetNew = True
    counterFollowers = 0
    numErrors = 0
    while shouldGetNew:
        try:
            followers = client.followers(blogname,offset=counterFollowers)
            if followers['users'] == []:
                break
            for follower in followers['users']:
                counterFollowers += 1
                followersList[str(id_blog)].append(follower['name'])
            if counterFollowers >= followers['total_users']:
                shouldGetNew = False
            write("\r\tGet Followers List.. " + str(counterFollowers) + "/" + str(followers['total_users']) + " ")
        except KeyError, msg:
            numErrors += 1
            if numErrors > 10:
                shouldGetNew = False
            else: 
                time.sleep(2)
    if numErrors > 10:
        write("Error!\n")
    else:
        write("Done!\n")

def getFollowing(id_blog, blogname):
    global followingList
    write("\tGet Following List.. ")
    try:
        client = clientsInfo[str(id_blog)]
    except KeyError, msg:
        write("Error: client for '" + blogname + "' not available! (" + str(msg) + ")\n")
        return
    shouldGetNew = True
    counterFollowing = 0
    numErrors = 0
    while shouldGetNew:
        try:
            following = client.following(offset=counterFollowing)
            if following['blogs'] == []:
                break
            for follow in following['blogs']:
                counterFollowing += 1
                followingList[str(id_blog)].append(follow['name'])
            if counterFollowing >= following['total_blogs']:
                shouldGetNew = False
            write("\r\tGet Following List.. " + str(counterFollowing) + "/" + str(following['total_blogs']) + " ")
        except KeyError, msg:
            numErrors += 1
            if numErrors > 10:
                shouldGetNew = False
            else: 
                time.sleep(2)
    if numErrors > 10:
        write("Error!\n")
    else:
        write("Done!\n")


def mainBOT():
    write("Initializing the BOT:\n")
    initBOT()
    updateBlogsData(firstTime=True)
    synchOperations(firstTime=True)
    updateStatistics(firstTime=True)
    if isTest:
        testConnectedBlogs()
    write("Initialization finished! Run the blogs!\n")


def initBOT():
    "Start operations"
    global startSessionTime
    startSessionTime = datetime.datetime.fromtimestamp(float(int(time.time()))).strftime('%H:%M:%S %d/%m')
    write("Get data from online server:\n")
    write("Get App Accounts.. ")
    appAccounts = post_request({"action": "get_app_accounts"})
    if appAccounts == None:
        write("\tError: None response.\n")
        return
    write("ok\n")
    write("App Accounts:\n")
    counter = 0
    if len(appAccounts) == 0:
        write("\tNo app accounts fonud.\n")
    else:
        for appAccount in appAccounts:
            write("\t" + str(counter + 1) + ") " + appAccount["Mail"] + " (id: " + appAccount["ID"] + ")" + "\n")
            counter = counter + 1
            addAppAccount(appAccount)
    write("Get My Accounts.. ")
    myAccounts = post_request({"action": "get_my_accounts"})
    if myAccounts == None:
        write("\tError: None response.\n")
        return
    write("ok\n")
    write("My Accounts:\n")
    counter = 0
    if len(myAccounts) == 0:
        write("\tNo accounts fonud.\n")
    for myAccount in myAccounts:
        write("\t" + str(counter + 1) + ") " + myAccount["Mail"] + "\n")
        counter = counter + 1
    if len(myAccounts) != 0:
        write("Get Accounts Data:\n")
        counter = 0
        for myAccount in myAccounts:
            write("\t" + str(counter + 1) + ") " + myAccount["Mail"] + " -> ")
            tags = post_request({"action": "get_tags", "ID": myAccount['ID']})
            otherAccounts = post_request({"action": "get_blogs", "ID": myAccount['ID']})
            if (tags == None) or (otherAccounts == None):
                continue
            addMyAccount(myAccount,tags,otherAccounts)
            counter = counter + 1
            write("Done!\n")
    write("Get data from online server complete!\n")


def addAppAccount(account):
    global appAccountList
    appAccountList[str(account['ID'])] = {'ID': int(account['ID']), 'strID': str(account['ID']), 'mail': account["Mail"], 'token': account["Token"], 'tokenSecret': account["Token_Secret"], 'type': int(account['Type'])}


def addMyAccount(account,tags,otherAccounts):
    global followersList, followingList, blogs, matches
    if int(account['Type']) == 1:    # tumblr
        setup_clients(account)
        cData = get_tumblr_blog_info(str(account['ID']))
        blogs[str(account['ID'])] = {'ID': int(account['ID']), 'strID': str(account['ID']), 'mail': account['Mail'], 'type': int(account['Type']), 'app_account': int(account['App_Account']), 'token': account['Token'], 'tokenSecret': account['Token_Secret'], 'data': cData, 'tags': tags2list(tags), 'blogs': blogs2list(otherAccounts), 'num_post_xd': int(account['PostXD']), 'num_follow_xd': int(account['FollowXD']), 'num_like_xd': int(account['LikeXD']), 'num_post_xt': int(account['PostXT']), 'num_follow_xt': int(account['FollowXT']), 'num_like_xt': int(account['LikeXT']), 'status': STATUS_STOP}
        if cData['blogname'] != "not available":
            matches[cData['blogname']] = account['ID']
            followersList[str(account['ID'])] = []
            followingList[str(account['ID'])] = []
    else:   # instagram
        cData = get_insta_blog_info(account['Username'],account['Password'])
        blogs[str(account['ID'])] = {'ID': int(account['ID']), 'strID': str(account['ID']), 'mail': account['Mail'], 'type': int(account['Type']), 'username': account['Username'], 'password': account['Password'], 'data': cData, 'tags': tags2list(tags), 'blogs': blogs2list(otherAccounts), 'num_post_xd': int(account['PostXD']), 'num_follow_xd': int(account['FollowXD']), 'num_like_xd': int(account['LikeXD']), 'num_post_xt': int(account['PostXT']), 'num_follow_xt': int(account['FollowXT']), 'num_like_xt': int(account['LikeXT']), 'status': STATUS_STOP}
        if cData['name'] != "not available":
            matches[account['Username']] = account['ID']
            followersList[str(account['ID'])] = []
            followingList[str(account['ID'])] = []



def tags2list(tags):
    tagsList = []
    for tag in tags:
        tagsList.append(tag['Name'])
    return tagsList


def blogs2list(other_accounts):
    oaList = []
    for oa in other_accounts:
        oaList.append(oa['Name'])
    return oaList


def setup_clients(account):
    global appAccountList, clients, clientsInfo
    clnt = pytumblr.TumblrRestClient(
        appAccountList[str(account["App_Account"])]['token'],
        appAccountList[str(account["App_Account"])]['tokenSecret'],
        account["Token"],
        account["Token_Secret"],
    )
    clnt2 = pytumblr.TumblrRestClient(
        appAccountList[str(account["App_Account"])]['token'],
        appAccountList[str(account["App_Account"])]['tokenSecret'],
        account["Token"],
        account["Token_Secret"],
    )
    clientsInfo[str(account['ID'])] = clnt2
    clients[str(account['ID'])] = clnt


def get_tumblr_blog_info(account_id):
    global clients
    try:
        client = clients[account_id]
    except KeyError, msg:
        write("Error: client with ID '" + account_id + "' not available! (" + str(msg) + ")\n")
        return
    cData = {'username': "not available",
             'likes': "not available",
             'following': "not available",
             'followers': "not available",
             'messages': "not available",
             'blogname': "not available",
             'posts': "not available",
             'queue': "not available",
             'url': "not available"
             }
    try:
        response = client.info()
        if checkResponse(response):
            cData = {'username': response["user"]["name"],
                     'likes': response["user"]["likes"],
                     'following': response["user"]["following"],
                     'followers': response["user"]["blogs"][0]["followers"],
                     'messages': response["user"]["blogs"][0]["messages"],
                     'blogname': response["user"]["blogs"][0]["name"],
                     'posts': response["user"]["blogs"][0]["posts"],
                     'queue': response["user"]["blogs"][0]["queue"],
                     'url': response["user"]["blogs"][0]["url"]
                     }
    except ServerNotFoundError,msg:
        write(str(msg) + "\n")
    except socket.error, msg:
        write(str(msg) + "\n")
    return cData


def get_insta_blog_info(username,password):
    ibi = post_request({'action': 'get_insta_blog_info', 'username': username, 'password': password})
    if ibi != None:
        return {'private': ibi['private'],
                'following': ibi['following'],
                'followers': ibi['follower'],
                'messages': ibi['message'],
                'name': ibi['name'],
                'posts': ibi['post'],
                'usertags': ibi['usertags']
                }
    else:
        return {'private': "not available",
                'following': "not available",
                'followers': "not available",
                'messages': "not available",
                'name': "not available",
                'posts': "not available",
                'usertags': "not available"
                }


def checkResponse(res):
    "Check if there is an error in response"
    if "meta" in res:
        write("Error: " + res["meta"]["msg"] + " (status " + str(res["meta"]["status"]) + ")\n")
        return False
    else:
        return True


def updateBlogsData(firstTime=False):
    global blogs
    if firstTime:
        write("Update Blogs:\n")
    else: 
        writeln("Update Blogs:\n")
    for key, blog in blogs.iteritems():
        updateBlogData(blog['ID'])


def updateBlogData(id_blog):
    global blogs
    blog = blogs[str(id_blog)]
    if blog['type'] == 1:   # tumblr
        updateBlogDataTumblr(blog)
    else:   # instagram
        updateBlogDataInsta(blog)


def updateBlogDataTumblr(blog):
    write("\tUpdate " + blog['data']['blogname'] + ".. ")
    post_data_up = {"action": "update_blog_data", 
        "ID": blog['ID'],
        "Likes": blog['data']['likes'],
        "Following": blog['data']['following'],
        "Followers": blog['data']['followers'],
        "Posts": blog['data']['posts'],
        "Messages": blog['data']['messages'],
        "Queue": blog['data']['queue'],
        "Name": blog['data']['blogname'],
        "Url": blog['data']['url']
        }
    if (blog['strID'] + "-post") in timersTime:
        post_data_up["Deadline_Post"] = timersTime[blog['strID'] + "-post"]
    if (blog['strID'] + "-follow") in timersTime:
        post_data_up["Deadline_Follow"] = timersTime[blog['strID'] + "-follow"]
    if (blog['strID'] + "-like") in timersTime:
        post_data_up["Deadline_Like"] = timersTime[blog['strID'] + "-like"]
    up_res = post_request(post_data_up)
    if up_res != None:
        updateStatus(blog['ID'])
        write("end of update.\n")


def updateBlogDataInsta(blog):
    write("\tUpdate " + blog['data']['name'] + ".. ")
    post_data_up = {"action": "update_blog_data_insta", 
        "ID": blog['ID'],
        "Following": blog['data']['following'],
        "Followers": blog['data']['followers'],
        "Posts": blog['data']['posts'],
        "Messages": blog['data']['messages'],
        "Name": blog['data']['name'],
        "Private": blog['data']['private'],
        "Usertags": blog['data']['usertags']
        }
    if (blog['strID'] + "-post") in timersTime:
        post_data_up["Deadline_Post"] = timersTime[blog['strID'] + "-post"]
    if (blog['strID'] + "-follow") in timersTime:
        post_data_up["Deadline_Follow"] = timersTime[blog['strID'] + "-follow"]
    if (blog['strID'] + "-like") in timersTime:
        post_data_up["Deadline_Like"] = timersTime[blog['strID'] + "-like"]
    up_res = post_request(post_data_up)
    if up_res != None:
        updateStatus(blog['ID'])
        write("end of update.\n")


def updateStatus(id_blog):
    global blogs
    blog = blogs[str(id_blog)]
    post_data_up = {"action": "get_my_accounts_ID", "id": id_blog}
    status_res = post_request(post_data_up)
    if status_res != None:
        if (status_res[0]['State'] <= STATUS_RUN) and (blog['status'] != status_res[0]['State']):
            post_request({"action": "set_status", "id": id_blog, "status": blog['status']})


def synchOperations(firstTime=False):
    if firstTime:
        write("Synchronize with online register.. ")
    else:
        write("\tSynchronize with online register.. ")
    synch_req = post_request({'action': "synch_operations"})
    if len(synch_req) > 0:
        write("\n")
        for up_row in synch_req:
            updateData(up_row)
    else:
        write("already synch!\n")


def updateData(row):
    if row['Operation'] == '0':
        updateAddOp(row['Table'],row['Blog'])
    elif row['Operation'] == '1':
        updateDelOp(row['Table'],row['Blog'])
    elif row['Operation'] == '2':
        updateUpOp(row['Table'],row['Blog'])
    else:
        write("\t\tError: operation " + str(row['Operation']) + "unknown!\n")


def updateAddOp(table, id_blog):
    global blogs
    if table == "sb_app_accounts":
        newAppAccount = post_request({"action": "get_app_accounts_ID", "id": id_blog})
        addAppAccount(newAppAccount)
    elif table == "sb_my_accounts":
        newMyAccount = post_request({"action": "get_my_accounts_ID", "id": id_blog})
        newTags = post_request({"action": "get_tags", "id": id_blog})
        newBlogs = post_request({"action": "get_blogs", "id": id_blog})
        addAppAccount(newMyAccount, newTags, newBlogs)
        if newMyAccount['status'] == STATUS_RUN:
            runBlog(id_blog)
    elif table == "sb_other_accounts":
        newBlogs = post_request({"action": "get_blogs", "id": id_blog})
        blogs[str(id_blog)]['blogs'] = blogs2list(newBlogs)
    elif table == "sb_tags":
        newTags = post_request({"action": "get_tags", "id": id_blog})
        blogs[str(id_blog)]['tags'] = tags2list(newTags)
    else:
        write("\t\tError: '" + table + "' is no a valid table!")


def updateDelOp(table, id_blog):
    global blogs, clients, clientsInfo, matches
    if table == "sb_app_accounts":
        for key, blog in blogs:
            if blog['app_account'] == id_blog:
                blogs[key]['app_account'] = None
                del clients[blog['strID']]
                del clientsInfo[blog['strID']]
        del appAccountList[str(id_blog)]
    elif table == "sb_my_accounts":
        if blogs[str(id_blog)]['status'] == STATUS_RUN:
            stopBlog(id_blog)
        if blogs[str(id_blog)]['type'] == 1:    # tumblr
            del matches[blogs[str(id_blog)]['data']['blogname']]
            del blogs[str(id_blog)]
            del clients[str(id_blog)]
            del clientsInfo[str(id_blog)]
        else:   # instagram
            del matches[blogs[str(id_blog)]['data']['name']]
            del blogs[str(id_blog)]
        # todo cancellare tabelle db locale per account
    elif table == "sb_other_accounts":
        newBlogs = post_request({"action": "get_blogs", "id": id_blog})
        blogs[str(id_blog)]['blogs'] = blogs2list(newBlogs)
    elif table == "sb_tags":
        newTags = post_request({"action": "get_tags", "id": id_blog})
        blogs[str(id_blog)]['tags'] = tags2list(newTags)
    else:
        write("\t\tError: '" + table + "' is no a valid table!")


def updateUpOp(table, id_blog):
    global blogs
    if table == "sb_app_accounts":
        newAppAccount = post_request({"action": "get_app_accounts_ID", "id": id_blog})
        addAppAccount(newAppAccount)
    elif table == "sb_my_accounts":
        oldMyAccount = blogs[str(id_blog)]
        newMyAccount = post_request({"action": "get_my_accounts_ID", "id": id_blog})
        blogs[str(id_blog)]['mail'] = newMyAccount['Mail']
        if newMyAccount['Type'] == 1:   # tumblr
            blogs[str(id_blog)]['app_account'] = newMyAccount['App_Account']
            blogs[str(id_blog)]['token'] = newMyAccount['Token']
            blogs[str(id_blog)]['tokenSecret'] = newMyAccount['Token_Secret']
            if (oldMyAccount['app_account'] != newMyAccount['App_Account']) or (oldMyAccount['token'] != newMyAccount['Token']) or (oldMyAccount['tokenSecret'] != newMyAccount['Token_Secret']):
                setup_clients(newMyAccount)
        else:   # instagram
            blogs[str(id_blog)]['username'] = newMyAccount['Username']
            blogs[str(id_blog)]['password'] = newMyAccount['Password']
        blogs[str(id_blog)]['num_post_xd'] = int(newMyAccount['PostXD'])
        blogs[str(id_blog)]['num_follow_xd'] = int(newMyAccount['FollowXD'])
        blogs[str(id_blog)]['num_like_xd'] = int(newMyAccount['LikeXD'])
        blogs[str(id_blog)]['num_post_xt'] = int(newMyAccount['PostXT'])
        blogs[str(id_blog)]['num_follow_xt'] = int(newMyAccount['FollowXT'])
        blogs[str(id_blog)]['num_like_xt'] = int(newMyAccount['LikeXT'])
        calc_time_post_follow(id_blog)
        if (int(newMyAccount['Status']) > STATUS_RUN):
            if (oldMyAccount['status'] == STATUS_STOP):
                post_request({"action": "set_status", "id": id_blog, "status": STATUS_RUN})
                runBlog(id_blog)
            elif (oldMyAccount['status'] == STATUS_RUN):
                post_request({"action": "set_status", "id": id_blog, "status": STATUS_STOP})
                stopBlog(id_blog)
    elif (table == "sb_other_accounts") or (table == "sb_tags"):
        write("\t\tOperation not permitted!!! WTF is happening???")
    else:
        write("\t\tError: '" + table + "' is no a valid table!")



def updateStatistics(firstTime=False):
    global startSessionTime
    try:
        if firstTime:
            write("Update stats.. ")
        else:
            write("\tUpdate stats.. ")
        post_data_stats = {"action": "update_statistics",
            "Session_Start": startSessionTime,
            "Num_Threads": threading.activeCount(),
            "Num_Post_Like": dbManager.countAllPost(),
            "Num_Follow": dbManager.countAllFollow()}
        if "update" in timersTime:
            post_data_stats["Deadline_Update"] = timersTime["update"]
        up_stat = post_request(post_data_stats)
        if up_stat != None:
            write("ok\n")
    except KeyError, msg:
        print "KeyError:"
        print str(msg)


def copyBlog(blog_to_copy, my_blog, limitMax, counter):
    write("Done!\nLaunching procedure..\n",True)
    writeln("Start to copy " + blog_to_copy + " in " + my_blog + "..\n",True)
    my_account = matches[my_blog]
    try:
        client = clients[my_account]
    except KeyError, msg:
        write("Error: client for '" + my_blog + "' not available! (" + str(msg) + ")\n")
        return
    tags = blogs[str(my_account)]['tags']
    total_posts = (client.blog_info(blog_to_copy))['blog']['posts']
    if total_posts > limitMax:
        total_posts = limitMax
    # counter = 0
    howmany = 20
    while counter < total_posts:
        howmanythis = howmany
        if (counter + howmany) > total_posts:
            howmanythis = total_posts - counter
        posts = (client.posts(blog_to_copy, limit = howmanythis, offset = counter))['posts']
        for post in posts:
            write("\tReblogging post " + str(counter+1) + "/" + str(total_posts) + ".. ",True)
            if post['type'] != "photo":
                write("Not reblogged: it's a " + post['type'] + " post!\n",True)
                counter = counter + 1
                continue
            response = client.reblog(my_blog, id=post['id'], reblog_key=post['reblog_key'], tags = tags, type = "photo")
            if checkResponse(response):
                write("Done!\n",True)
            counter = counter + 1


def testConnectedBlogs():
    global blogs,clients, followersList, followingList
    writeln("Begin testing code:\n")
    # begin code to test

    # for key, blog in blogs.iteritems():
    #     check_num_post_follow(blog['ID'])
    #     post(blog['ID'], blog['data']['blogname'], 1)
    #     like(blog['ID'], blog['data']['blogname'], 1)
    #     follow(blog['ID'], blog['data']['blogname'], 2, isDump=True)

    posts = post_request({'action': 'search_tag', 'username': 'tommy__91', 'password': 'Thebest91', 'tag': 'picoftheday', 'num_posts': 10})
    for key, post in posts.iteritems():
        print key
    print posts['num_results']
    pprint(posts['items'][0])
    print "\n\n\n"
    pprint(posts['ranked_items'][0])
    # for post in posts:
    #     print post
    #     print str(post)
    #     likers = post_request({'action': 'get_likers', 'username': 'tommy__91', 'password': 'Thebest91', 'mediaID': str(post)})
    #     if likers != None:
    #         pprint(likers)
    #         break

    # end code to test
    writeln("End testing code!\n")


if __name__ == '__main__':
    try:
        os.system('clear')
        checkInputParams()
        printHello()
        if not tryConnectToRemoteServer():
            print "Closing.. bye."
        tryConnectDB()
        mainBOT()
        newEntry()
    except Exception, e:
        print "Global Error."
        print e


