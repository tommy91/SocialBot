function highlightUpdate(elem) {
    elem.addClass('highlight');
    setTimeout(function() {
        elem.removeClass('highlight')
    }, 10000);
}


function checkResponse(resp) {
    if ('Error' in resp)
        return false;
    else 
        return true;
}


function poll() {
    console.log(Date() + " -> poll");
    $.post("Receiver.php",
    {
        action: "synch_operations_webpage"
    },
    function(response, status) {
        var resp = JSON.parse(response);
        if (checkResponse(resp)) {
            resp = resp['Result'];
            for (var k in resp) {
                if('blog' in resp[k]) {
                    var id_blog = resp[k]['blog']['ID'];
                    if($('#' + id_blog + '_likes').text() != resp[k]['blog']['Likes']) {
                        $('#' + id_blog + '_likes').html(resp[k]['blog']['Likes']);
                        highlightUpdate($('#' + id_blog + '_likes'));
                    }
                    if($('#' + id_blog + '_following').text() != resp[k]['blog']['Following']) {
                        $('#' + id_blog + '_following').html(resp[k]['blog']['Following']);
                        highlightUpdate($('#' + id_blog + '_following'));
                    }
                    if($('#' + id_blog + '_followers').text() != resp[k]['blog']['Followers']) {
                        $('#' + id_blog + '_followers').html(resp[k]['blog']['Followers']);
                        highlightUpdate($('#' + id_blog + '_followers'));
                    }
                    if($('#' + id_blog + '_posts').text() != resp[k]['blog']['Posts']) {
                        $('#' + id_blog + '_posts').html(resp[k]['blog']['Posts']);
                        highlightUpdate($('#' + id_blog + '_posts'));
                    }
                    if($('#' + id_blog + '_msg').text() != resp[k]['blog']['Messages']) {
                        $('#' + id_blog + '_msg').html(resp[k]['blog']['Messages']);
                        highlightUpdate($('#' + id_blog + '_msg'));
                    }
                    if($('#' + id_blog + '_queue').text() != resp[k]['blog']['Queue']) {
                        $('#' + id_blog + '_queue').html(resp[k]['blog']['Queue']);
                        highlightUpdate($('#' + id_blog + '_queue'));
                    }
                    if($('#' + id_blog + '_dp').text() != resp[k]['blog']['Deadline_Post']) {
                        $('#' + id_blog + '_dp').html(resp[k]['blog']['Deadline_Post']);
                        highlightUpdate($('#' + id_blog + '_dp'));
                    }
                    if($('#' + id_blog + '_df').text() != resp[k]['blog']['Deadline_Follow']) {
                        $('#' + id_blog + '_df').html(resp[k]['blog']['Deadline_Follow']);
                        highlightUpdate($('#' + id_blog + '_df'));
                    }
                    if($('#' + id_blog + '_dl').text() != resp[k]['blog']['Deadline_Like']) {
                        $('#' + id_blog + '_dl').html(resp[k]['blog']['Deadline_Like']);
                        highlightUpdate($('#' + id_blog + '_dl'));
                    }
                    if(status2int($('#' + id_blog + '_status').attr('status')) != resp[k]['blog']['Status']) {
                        setNewStatus($('#' + id_blog + '_status'),resp[k]['blog']['Status']);
                        highlightUpdate($('#' + id_blog + '_status'));
                    }
                }
                else {
                    if($('#session_start').text() != resp[k]['stats']['Session_Start']) {
                        $('#session_start').html(resp[k]['stats']['Session_Start']);
                        checkSession($('#session_start').text(), $('#session_stop').text());
                        if ($('#session_start').is(":visible"))
                            highlightUpdate($('#session_start'));
                        else
                            highlightUpdate($('#session_stop'));
                    }
                    if($('#session_stop').text() != resp[k]['stats']['Session_Stop']) {
                        $('#session_stop').html(resp[k]['stats']['Session_Stop']);
                        checkSession($('#session_start').text(), $('#session_stop').text());
                        if ($('#session_stop').is(":visible"))
                            highlightUpdate($('#session_stop'));
                        else
                            highlightUpdate($('#session_start'));
                    }
                    if($('#num_threads').text() != resp[k]['stats']['Num_Threads']) {
                        $('#num_threads').html(resp[k]['stats']['Num_Threads']);
                        highlightUpdate($('#num_threads'));
                    }
                    if($('#num_post_like').text() != resp[k]['stats']['Num_Post_Like']) {
                        $('#num_post_like').html(resp[k]['stats']['Num_Post_Like']);
                        highlightUpdate($('#num_post_like'));
                    }
                    if($('#num_follow').text() != resp[k]['stats']['Num_Follow']) {
                        $('#num_follow').html(resp[k]['stats']['Num_Follow']);
                        highlightUpdate($('#num_follow'));
                    }
                    if($('#deadline_update').text() != resp[k]['stats']['Deadline_Update']) {
                        $('#deadline_update').html(resp[k]['stats']['Deadline_Update']);
                        highlightUpdate($('#deadline_update'));
                    }
                }
            }
            timer = setPollTimeout();
        }
        else {
            console.log(resp['Error']);
            timer = setPollTimeout();
        }
    });
}


function status2int(status) {
    if (status == "red")
        return 0;
    if (status == "green")
        return 1;
    if (status == "yellow")
        return 2;
}


function setNewStatus(elem, status) {
    if (status == 0) {
        elem.attr('src','img/red_status.png');
        elem.attr('status','red');
        elem.attr('alt', 'Red Status');
    }
    else if (status == 1) {
        elem.attr('src','img/green_status.png');
        elem.attr('status','green');
        elem.attr('alt', 'Green Status');
    }
    else if (status == 2) {
        elem.attr('src','img/yellow_status.png');
        elem.attr('status','yellow');
        elem.attr('alt', 'Yellow Status');
    }
}


function setPollTimeout() {
   return setTimeout(poll, 30000);
}


function setAccountStatus() {
	$.post("Receiver.php",
    {
        action: "get_my_accounts"
    },
    function(accounts_data, status) {
        var ad = JSON.parse(accounts_data);
        if (checkResponse(ad)) {
            ad = ad['Result'];
            for (var k in ad) {
            	var text = '<ul id="ul_' + ad[k]['ID'] + '" class="ul_account">'
            		+ '<li class="li_account"><div id="' + ad[k]['ID'] + '_name" class="div_account name_account">'
            		+ '<a href="' + ad[k]['Url'] + '" target="_blank" id="' + ad[k]['ID'] + '_url" class="href_account"> + ' + ad[k]['Name'] + '</a></div>';
            	if (parseInt(ad[k]['Status']) == 0)
            		text = text + '<img src="img/red_status.png" id="' + ad[k]['ID'] + '_status" class="status_account" idb="' + ad[k]['ID'] + '" status="red" alt="Red Status"/>';
            	if (parseInt(ad[k]['Status']) == 1)
            		text = text + '<img src="img/green_status.png" id="' + ad[k]['ID'] + '_status" class="status_account" idb="' + ad[k]['ID'] + '" status="green" alt="Green Status"/>';
            	if (parseInt(ad[k]['Status']) > 1)
            		text = text + '<img src="img/yellow_status.png" id="' + ad[k]['ID'] + '_status" class="status_account" idb="' + ad[k]['ID'] + '" status="yellow" alt="Yellow Status"/>';
                if (parseInt(ad[k]['Type']) == 1)
                    text = text + '<img src="img/tumblr.png" class="social_account" alt="Tumblr Account"/>';
                if (parseInt(ad[k]['Type']) == 2)
                    text = text + '<img src="img/insta.png" class="social_account" alt="Insta Account"/>';
            	text = text	+ '</li>'
            		+ '<li class="li_account"><div class="tag_account">Likes:</div><div id="' + ad[k]['ID'] + '_likes" class="div_account">' + ad[k]['Likes'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Following:</div><div id="' + ad[k]['ID'] + '_following" class="div_account">' + ad[k]['Following'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Followers:</div><div id="' + ad[k]['ID'] + '_followers" class="div_account">' + ad[k]['Followers'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Posts:</div><div id="' + ad[k]['ID'] + '_posts" class="div_account">' + ad[k]['Posts'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Messages:</div><div id="' + ad[k]['ID'] + '_msg" class="div_account">' + ad[k]['Messages'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Queue:</div><div id="' + ad[k]['ID'] + '_queue" class="div_account">' + ad[k]['Queue'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Deadline Post:</div><div id="' + ad[k]['ID'] + '_dp" class="div_account">' + ad[k]['Deadline_Post'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Deadline Follow:</div><div id="' + ad[k]['ID'] + '_df" class="div_account">' + ad[k]['Deadline_Follow'] + '</div></li>'
            		+ '<li class="li_account"><div class="tag_account">Deadline Like:</div><div id="' + ad[k]['ID'] + '_dl" class="div_account">' + ad[k]['Deadline_Like'] + '</div></li>'
            		+ '</ul>';
            	$('#account-container').append(text);
            }
        }
        else
            console.log(ad['Error']);
    });
}


function setBotStatus() {
	$.post("Receiver.php",
    {
        action: "get_program_status"
    },
    function(program_status, status) {
        var ps = JSON.parse(program_status);
        if (checkResponse(ps)) {
            ps = ps['Result'];
            var text = '<div class="program_container"><div class="tag_program"><img src="img/green_status.png" class="status_program" alt="Green Status"/>Session Start:</div><div id="session_start" class="div_program">' + ps[0]['Session_Start'] + '</div></div>'
                + '<div class="program_container"><div class="tag_program"><img src="img/red_status.png" class="status_program" alt="Red Status"/>Session Stop:</div><div id="session_stop" class="div_program">' + ps[0]['Session_Stop'] + '</div></div>'
        		+ '<div class="program_container"><div class="tag_program"># Threads:</div><div id="num_threads" class="div_program">' + ps[0]['Num_Threads'] + '</div></div>'
        		+ '<div class="program_container"><div class="tag_program"># Post Like:</div><div id="num_post_like" class="div_program">' + ps[0]['Num_Post_Like'] + '</div></div>'
        		+ '<div class="program_container"><div class="tag_program"># Follow:</div><div id="num_follow" class="div_program">' + ps[0]['Num_Follow'] + '</div></div>'
        		+ '<div class="program_container"><div class="tag_program">Deadline Update:</div><div id="deadline_update" class="div_program">' + ps[0]['Deadline_Update'] + '</div></div>';
        	$('#program-stats-container').append(text);
            checkSession(ps[0]['Session_Start'], ps[0]['Session_Stop']);
        }
        else
            console.log(ps['Error']);
    });
}


function checkSession(start, stop) {
    if (stop == null) {
        $('#session_stop').parent().hide();
        $('#session_start').parent().show();
    }
    else {
        if (str2date(stop) > str2date(start)) {
            $('#session_start').parent().hide();
            $('#session_stop').parent().show();
        }
        else {
            $('#session_stop').parent().hide();
            $('#session_start').parent().show();
        }
    }
}


function str2date(s) {
    var d = new Date();
    var year = d.getFullYear();
    var reggie = /(\d{2}):(\d{2}):(\d{2}) (\d{2})\/(\d{2})/;
    var dateArray = reggie.exec(s); 
    var dateObject = new Date(
        (+year),
        (+dateArray[5])-1, // Careful, month starts at 0!
        (+dateArray[4]),
        (+dateArray[1]),
        (+dateArray[2]),
        (+dateArray[3])
    );
    return dateObject;
}


function showCorrectTableFields(table) {
    if (table == "app_accounts") {
        $('.just-my').hide();
        $('.both').show();
    }
    else {
        $('.both').show();
        $('.just-my').show();
    }
}


function fill_account_names(table) {
    $.post("Receiver.php",
    {
        action: "get_" + table.toLowerCase()
    },
    function(accounts_data, status) {
        var ad = JSON.parse(accounts_data);
        if (checkResponse(ad)) {
            ad = ad['Result'];
            $('#select-third-option').append('<option value="0">Select Account</option>');
            for (var kad in ad) {
                $('#select-third-option').append('<option value="' + ad[kad]['ID'] + '">' + ad[kad]['Mail'] + '</option>');
            }
        }
        else 
            console.log(ad['Error']);
    });
}


function fill_account_data(table, blog) {
    $.post("Receiver.php",
    {
        action: "get_" + table.toLowerCase() + "_ID",
        id: blog
    },
    function(account_data, status) {
        var ad = JSON.parse(account_data);
        if (checkResponse(ad)) {
            ad = ad['Result'];
            $('#select-type-modify').val(ad[0]['Type']);
            $('#select-type-modify').attr('old_value',ad[0]['Type']);
            $('#input-mail-modify').val(ad[0]['Mail']);
            $('#input-mail-modify').attr('old_value',ad[0]['Mail']);
            $('#input-token-modify').val(ad[0]['Token']);
            $('#input-token-modify').attr('old_value',ad[0]['Token']);
            $('#input-token-secret-modify').val(ad[0]['Token_Secret']);
            $('#input-token-secret-modify').attr('old_value',ad[0]['Token_Secret']);
            if (table.toLowerCase() == 'my_accounts') {
                $('#input-name-modify').val(ad[0]['Name']);
                $('#input-name-modify').attr('old_value',ad[0]['Name']);
                $('#input-url-modify').val(ad[0]['Url']);
                $('#input-url-modify').attr('old_value',ad[0]['Url']);
                $('#input-postxd-modify').val(ad[0]['PostXD']);
                $('#input-postxd-modify').attr('old_value',ad[0]['PostXD']);
                $('#input-likexd-modify').val(ad[0]['LikeXD']);
                $('#input-likexd-modify').attr('old_value',ad[0]['LikeXD']);
                $('#input-followxd-modify').val(ad[0]['FollowXD']);
                $('#input-followxd-modify').attr('old_value',ad[0]['FollowXD']);
                $('#input-postxt-modify').val(ad[0]['PostXT']);
                $('#input-postxt-modify').attr('old_value',ad[0]['PostXT']);
                $('#input-likext-modify').val(ad[0]['LikeXT']);
                $('#input-likext-modify').attr('old_value',ad[0]['LikeXT']);
                $('#input-followxt-modify').val(ad[0]['FollowXT']);
                $('#input-followxt-modify').attr('old_value',ad[0]['FollowXT']);
                $.post("Receiver.php",
                {
                    action: "get_app_accounts"
                },
                function(app_accounts, status) {
                    var aa = JSON.parse(app_accounts);
                    if (checkResponse(aa)) {
                        aa = aa['Result'];
                        for (var ka in aa) {
                            $('#select-app-account-modify').append('<option value="' + aa[ka]['ID'] + '">' + aa[ka]['Mail'] + '</option>');
                        }
                        $('#select-app-account-modify').val(ad[0]['App_Account']);
                        $('#select-app-account-modify').attr('old_value',ad[0]['App_Account']);
                        $.post("Receiver.php",
                        {
                            action: "get_tags",
                            ID: ad[0]['ID']
                        },
                        function(json_tags, status) {
                            var tags = JSON.parse(json_tags);
                            if (checkResponse(tags)) {
                                tags = tags['Result'];
                                for (var kt in tags) {
                                    $('#div-tags-modify').append('<li class="li-modify"><input class="li-input-tags-modify" value="' + tags[kt]['Name'] + '" old_value="' + tags[kt]['Name'] + '" new_tag="false"></input></li>');
                                }
                                $('#div-tags-modify').prepend('<li class="li-modify"><input class="li-input-tags-modify" value="..." old_value="..." new_tag="true"></input></li>');
                                deleted_tags = [];
                                $.post("Receiver.php",
                                {
                                    action: "get_blogs",
                                    ID: ad[0]['ID']
                                },
                                function(json_blogs, status) {
                                    var blogs = JSON.parse(json_blogs);
                                    if (checkResponse(blogs)) {
                                        blogs = blogs['Result'];
                                        for (var kb in blogs) {
                                            $('#div-blogs-modify').append('<li class="li-modify"><input class="li-input-blogs-modify" value="' + blogs[kb]['Name'] + '" old_value="' + blogs[kb]['Name'] + '" new_blog="false"></inpu></li>');
                                        }
                                        $('#div-blogs-modify').prepend('<li class="li-modify"><input class="li-input-blogs-modify" value="..." old_value="..." new_blog="true"></input></li>');
                                        deleted_blogs = [];
                                    }
                                    else
                                        console.log(blogs['Error']);
                                });
                            }
                            else
                                console.log(tags['Error']);
                        });
                    }
                    else
                        console.log(aa['Error']);
                });
            }
        }
        else
            console.log(ad['Error']);
    });
}


function addEmptyEntryList() {
    $('#div-tags-modify').append('<li class="li-modify"><input class="li-input-tags-modify" value="..." old_value="..." new_tag="true"></input></li>');
    $('#div-blogs-modify').append('<li class="li-modify"><input class="li-input-blogs-modify" value="..." old_value="..." new_blog="true"></input></li>');
}


function addAppAccount2Selector() {
    $.post("Receiver.php",
    {
        action: "get_app_accounts"
    },
    function(app_accounts, status) {
        var aa = JSON.parse(app_accounts);
        if (checkResponse(aa)) {
            aa = aa['Result'];
            for (var ka in aa) {
                $('#select-app-account-modify').append('<option value="' + aa[ka]['ID'] + '">' + aa[ka]['Mail'] + '</option>');
            }
        }
        else
            console.log(aa['Error']);
    });
}


function deleteAccount(table, blog) {
    $.post("Receiver.php",
    {
        action: "delete_" + table.toLowerCase() + "_ID",
        id: blog
    },
    function(result, status) {
        var resp = JSON.parse(result);
        if (checkResponse(resp)) {
            if (resp['Result'] == 1){
                alert("Account deleted from " + table);
            }
            else
                alert("Error: " + resp['Result']);
        }
        else
            console.log(resp['Error']);
    });
}


function addAccount(table) {
    var data_to_pass = { action: "add_" + table.toLowerCase(),
                         type: $('#select-type-modify').val(),
                         mail: $('#input-mail-modify').val(),
                         token: $('#input-token-modify').val(),
                         token_secret: $('#input-token-secret-modify').val() 
                        };
    if (table.toLowerCase() == 'my_accounts') {
        data_to_pass['app_account'] = $('#select-app-account-modify').val();
        data_to_pass['name'] = $('#input-name-modify').val();
        data_to_pass['url'] = $('#input-url-modify').val();
        data_to_pass['postxd'] = $('#input-postxd-modify').val();
        data_to_pass['likexd'] = $('#input-likexd-modify').val();
        data_to_pass['followxd'] = $('#input-followxd-modify').val();
        data_to_pass['postxt'] = $('#input-postxt-modify').val();
        data_to_pass['likext'] = $('#input-likext-modify').val();
        data_to_pass['followxt'] = $('#input-followxt-modify').val();
    }
    $.post("Receiver.php", data_to_pass,
    function(id_blog, status) {
        console.log(id_blog);
        if (id_blog > 0){
            if (table.toLowerCase() == 'app_accounts') {
                alert("New App Account inserted.");
            }
            else {
                var tags2add = [];
                $('.li-input-tags-modify').each(function(){
                    if($(this).val()!="...")
                        tags2add.push($(this).val());
                });
                var num_tags = tags2add.length;
                var inserted_tags = 0;
                for(var kta in tags2add) {
                    $.post("Receiver.php",
                    {
                        action: "add_tag",
                        id: id_blog,
                        name: tags2add[kta],
                        position: kta
                    },
                    function(result, status) {
                        if (result == 1){
                            inserted_tags = inserted_tags + 1;
                            if (inserted_tags == num_tags) {
                                var blogs2add = [];
                                $('.li-input-blogs-modify').each(function(){
                                    if($(this).val()!="...")
                                        blogs2add.push($(this).val());
                                });
                                var num_blogs = blogs2add.length;
                                var inserted_blogs = 0;
                                for(var kba in blogs2add) {
                                    $.post("Receiver.php",
                                    {
                                        action: "add_blog",
                                        id: id_blog,
                                        name: blogs2add[kba]
                                    },
                                    function(result, status) {
                                        if (result == 1){
                                            inserted_blogs = inserted_blogs + 1;
                                            if (inserted_blogs == num_blogs) {
                                                alert("New My Account inserted.");
                                            }
                                        }
                                        else
                                            alert("Error: " + result);
                                    });
                                }
                            }
                        }
                        else
                            alert("Error: " + result);
                    });
                }
            }
        }
        else
            alert("Error: account NOT inserted!");
    });

}


function updateAccount(table, id_blog) {
    var data_to_pass = { action: "update_" + table.toLowerCase(),
                         id: $('#select-third-option').val(),
                         type: $('#select-type-modify').val(),
                         mail: $('#input-mail-modify').val(),
                         token: $('#input-token-modify').val(),
                         token_secret: $('#input-token-secret-modify').val() 
                        };
    if (table.toLowerCase() == 'my_accounts') {
        data_to_pass['app_account'] = $('#select-app-account-modify').val();
        data_to_pass['name'] = $('#input-name-modify').val();
        data_to_pass['url'] = $('#input-url-modify').val();
        data_to_pass['postxd'] = $('#input-postxd-modify').val();
        data_to_pass['likexd'] = $('#input-likexd-modify').val();
        data_to_pass['followxd'] = $('#input-followxd-modify').val();
        data_to_pass['postxt'] = $('#input-postxt-modify').val();
        data_to_pass['likext'] = $('#input-likext-modify').val();
        data_to_pass['followxt'] = $('#input-followxt-modify').val();
    }
    $.post("Receiver.php", data_to_pass,
    function(resp, status) {
        var res = JSON.parse(resp);
        if (checkResponse(res)) {
            if (res['Result'] == 1){
                if (table.toLowerCase() == 'app_accounts') {
                    alert("App Account updated.");
                }
                else {
                    alert("My Account data updated, now updating tags and blogs...");
                    updateTags(id_blog);
                    updateBlogs(id_blog);
                }
            }
            else
                alert("Error: account NOT updated!");
        }
        else
            console.log(res['Error']);
    });

}


function updateTags(id_blog) {
    if (deleted_tags.length == 0) {
        insertTags(id_blog);
    }
    else {
        deleteTags(id_blog);
    }
}


function deleteTags(id_blog) {
    var num_del_tags = deleted_tags.length;
    var del_tags = 0;
    for(var ktd in deleted_tags) {
        $.post("Receiver.php",
        {
            action: "delete_tag",
            id: id_blog,
            name: deleted_tags[ktd]
        },
        function(result, status) {
            var res = JSON.parse(result);
            if (checkResponse(res)) {
                if (res['Result'] == 1){
                    del_tags = del_tags + 1;
                    if (del_tags == num_del_tags) {
                        insertTags(id_blog);
                    }
                }
                else
                    alert("Error: " + res['Result']);
            }
            else
                console.log(res['Error']);
        });
    } 
}


function insertTags(id_blog) {
    var tags2update = [];
    $('.li-input-tags-modify').each(function(){
        if(($(this).attr('new_tag') == "true")&&($(this).val()!="..."))
            tags2update.push($(this).val());
    });
    var num_tags = tags2update.length;
    if (num_tags == 0) {
        alert("Tags for account updated.");
    }
    var inserted_tags = 0;
    for(var ktu in tags2update) {
        $.post("Receiver.php",
        {
            action: "add_tag",
            id: id_blog,
            name: tags2update[ktu],
            position: ktu
        },
        function(result, status) {
            if (result == 1){
                inserted_tags = inserted_tags + 1;
                if (inserted_tags == num_tags) {
                    alert("Tags for account updated.");
                }
            }
            else
                alert("Error: " + result);
        });
    }
}


function updateBlogs(id_blog) {
    if (deleted_blogs.length == 0) {
        insertBlogs(id_blog);
    }
    else {
        deleteBlogs(id_blog);
    }
}


function deleteBlogs(id_blog) {
    var num_del_blogs = deleted_blogs.length;
    var del_blogs = 0;
    for(var kbd in deleted_blogs) {
        $.post("Receiver.php",
        {
            action: "delete_blog",
            id: id_blog,
            name: deleted_blogs[kbd]
        },
        function(result, status) {
            var res = JSON.parse(result);
            if (checkResponse(res)) {
                if (res['Result'] == 1){
                    del_blogs = del_blogs + 1;
                    if (del_blogs == num_del_blogs) {
                        insertBlogs(id_blog);
                    }
                }
                else
                    alert("Error: " + res['Result']);
            }
            else
                console.log(res['Error']);
        });
    }       
}


function insertBlogs() {
    var blogs2update = [];
    $('.li-input-blogs-modify').each(function(){
        if(($(this).attr('new_blog') == "true")&&($(this).val()!="..."))
            blogs2update.push($(this).val());
    });
    var num_blogs = blogs2update.length;
    if (num_blogs == 0) {
        alert("Blogs for account updated.");
    }
    var inserted_blogs = 0;
    for(var kbu in blogs2update) {
        $.post("Receiver.php",
        {
            action: "add_blog",
            id: id_blog,
            name: blogs2update[kbu]
        },
        function(result, status) {
            if (result == 1){
                inserted_blogs = inserted_blogs + 1;
                if (inserted_blogs == num_blogs) {
                    alert("Blogs for account updated.");
                }
            }
            else
                alert("Error: " + result);
        });
    }
}


var deleted_blogs = [];
var deleted_tags = [];
var timer = null;
var focus = true;

$(document).ready(function() {

    $( "#div-tags-modify" ).sortable({items: 'li:not(:first)'});
    $( "#div-blogs-modify" ).sortable({items: 'li:not(:first)'});

	setAccountStatus();
	setBotStatus();
    timer = setPollTimeout();
    
    $("#change-pw-btn").click(function() {
        $("#change-pw").fadeToggle("slow");
    });
    
    $("#change-pw-confirm").click(function() {
        var new_pw = $("#input-new-pw").val();
        var new_pw2 = $("#input-new-pw2").val();
        var user = ($("#username").text()).toLowerCase()
        if (new_pw !== new_pw2){
            window.alert("Error: the passwords don't match! Retry");
            $("#input-new-pw").val("");
            $("#input-new-pw2").val("");
        }
        else {
            $.post("Receiver.php",
            {
                action: "set_pw",
                user: user,
                pw: new_pw
            },
            function(data, status) {
                if (data.length<=2) { 
                    window.alert("Password modified with success!");
                    $("#input-new-pw").val("");
                    $("#input-new-pw2").val("");
                }
                if (data.length > 2) {
                    window.alert("Password NOT modified, some error occur!");
                    $("#input-new-pw").val("");
                    $("#input-new-pw2").val("");
                }
            });
        }
    });

    $("#modify-data-btn").click(function() {
        $("#modify-data-container").fadeToggle("slow");
    });

    $('#select-table').on('change', function(){
        $('.input').val('');
        $('.small-input').val('');
        $('.list').empty();
        $('#select-third-option').empty();
        $('#select-app-account-modify').empty();
        var table = $('#select-table').val();
        if (table == "0") {
            $('.both').hide();
            $('.just-my').hide();
        }
        else {
            var action = $('#select-action').val();
            if (action == "1") {
                addEmptyEntryList();
                showCorrectTableFields(table);
                addAppAccount2Selector();
            }
            if ((action == '3') || (action == '2')) {
                $('.both').hide();
                $('.just-my').hide();
                fill_account_names(table);
            }
        }         
    });

    $('#select-action').on('change', function(){
        $('.input').val('');
        $('.small-input').val('');
        $('.list').empty();
        $('#select-third-option').empty();
        $('#select-app-account-modify').empty();
        var action = $('#select-action').val();
        var table = $('#select-table').val();
        if (table != '0') {
            if (action == '0') {
                $('.both').hide();
                $('.just-my').hide();
            }
            if (action == '1') {
                addEmptyEntryList();
                showCorrectTableFields(table);
                addAppAccount2Selector();
            }
            if ((action == '3') || (action == '2')) {
                $('.both').hide();
                $('.just-my').hide();
                fill_account_names(table); 
            }
        }
    });

    $('#select-third-option').on('change', function() {
        var action = $('#select-action').val();
        var table = $('#select-table').val();
        var blog = $('#select-third-option').val();
        if (action != '2') {
            $('.input').val('');
            $('.small-input').val('');
            $('.list').empty();
            $('#select-app-account-modify').empty();
            showCorrectTableFields(table);
            fill_account_data(table,blog);
        }
        else {
            $('#confirm-buttons').show();
        }
    });

    $('#reset-modify').click(function() {
        if(confirm("Wanna reset?")) {
            $('.input').val('');
            $('.small-input').val('');
            $('.list').empty();
            $('#select-third-option').empty();
            $('#select-app-account-modify').empty();
            $('#select-action').val("0");
            $('#select-table').val("0");
            $('.both').hide();
            $('.just-my').hide();
        }
    });

    $('#confirm-modify').click(function() {
        if(confirm("Confirm the changes?")) {
            var action = $('#select-action').val();
            var table = $('#select-table').val();
            if (action == 2) {  // delete
                var blog = $('#select-third-option').val();
                deleteAccount(table,blog);
            }
            if (action == 1) {  // add
                addAccount(table);
            }
            if (action == 3) {  // update
                var blog = $('#select-third-option').val();
                updateAccount(table, blog);
            }
        }
    }); 

    $(document.body).on('change', '.li-input-tags-modify', function() {
        if($(this).val() == "") {
            if($(this).attr('old_value') != "...") {
                if($(this).attr('new_tag') == "false")
                    deleted_tags.push($(this).attr('old_value'));
                $(this).parent().remove(); 
            }
            else {
                $(this).val("...");
            }
        }
        else {
            if($(this).attr('old_value') == "...") {
                $(this).attr('old_value',$(this).val());
                $(this).parent().parent().prepend('<li class="li-modify"><input class="li-input-tags-modify" value="..." old_value="..." new_tag="true"></input></li>');
            }
            else {
                if($(this).attr('new_tag') == "false") {
                    $(this).attr('new_tag', "true");
                    deleted_tags.push($(this).attr('old_value'));
                }
            }
        }
    });  

    $(document.body).on('change', '.li-input-blogs-modify', function() {
        if($(this).val() == "") {
            if($(this).attr('old_value') != "...") {
                if($(this).attr('new_blog') == "false")
                    deleted_blogs.push($(this).attr('old_value'));
                $(this).parent().remove(); 
            }
            else {
                $(this).val('...');
            }
        }
        else {
            if($(this).attr('old_value') == "...") {
                $(this).attr('old_value',$(this).val());
                $(this).parent().parent().prepend('<li class="li-modify"><input class="li-input-blogs-modify" value="..." old_value="..." new_blog="true"></input></li>');
            }
            else {
                if($(this).attr('new_blog') == "false") {
                    $(this).attr('new_blog', "true");
                    deleted_blogs.push($(this).attr('old_value'));
                }
            }
        }
    });   

    $(document.body).on('focus', '.li-input-tags-modify', function() {
        if($(this).val() == "...") {
            $(this).val('');
        }
    });

    $(document.body).on('focusout', '.li-input-tags-modify', function() {
        if($(this).attr('old_value') == "...") {
            $(this).val('...');
        }
    });

    $(document.body).on('focus', '.li-input-blogs-modify', function() {
        if($(this).val() == "...") {
            $(this).val('');
        }
    });

    $(document.body).on('focusout', '.li-input-blogs-modify', function() {
        if($(this).attr('old_value') == "...") {
            $(this).val('...');
        }
    });

    $(window).on('blur', function() {
        clearTimeout(timer);
        timer = null;
        focus = false;
    });

    $(window).on('focus', function() {
        if (!focus) {
            focus = true;
            poll();
        }
    });

    $(document.body).on('click', '.status_account', function(){
        var status = $(this).attr('status');
        var id_blog = $(this).attr('idb');
        if(status != 'yellow') {
            $.post("Receiver.php",
            {
                action: "update_my_account_status",
                id: id_blog
            },
            function(result, status) {
                var res = JSON.parse(result);
                if (checkResponse(res)) {
                    if (res['Result'] == 1){
                        $('#' + id_blog + '_status').attr('src','img/yellow_status.png');
                        $('#' + id_blog + '_status').attr('status','yellow');
                        $('#' + id_blog + '_status').attr('alt', 'Yellow Status');
                    }
                    else
                        console.log(res['Result']);
                }
                else
                    console.log(res['Error']);
            });
        }
        else
            alert("Cannot change this status!!");
    });

});

