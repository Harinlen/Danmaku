onmessage = (event) => {
    let inst = event.data
    let op = inst['op']
    if (op === 'add_to_queue') {
        postMessage({'op': 'add_to_queue', 'item': to_render_item(inst['item'])})
    }
}

let guard_level_info = {
    '1': ['总督', 'icon-guard1.png'],
    '2': ['提督', 'icon-guard2.png'],
    '3': ['舰长', 'icon-guard3.png'],
}

let image_cache_request = new XMLHttpRequest()

// Load the emoji info.
image_cache_request.open('GET', '/api/cache/emoji_map', false)
image_cache_request.send()
let emoji_map = JSON.parse(image_cache_request.responseText)

function create_danmaku(danmu_data) {
    let guard = danmu_data["guard_level"]
    let user_name = danmu_data["uname"]
    let content = danmu_data["msg"]
    let emoji_url = danmu_data["emoji_img_url"]
    let metal_name = danmu_data["fans_medal_name"],
        metal_level = danmu_data["fans_medal_level"],
        metal_wear = danmu_data["fans_medal_wearing_status"]
    // Fetch the avatar.
    image_cache_request.open('POST', '/api/cache/image/avatar', false)
    image_cache_request.send('{"url":"'+danmu_data['uface']+'"}')
    let avatar = JSON.parse(image_cache_request.responseText)['url']

    // Check emoji url.
    if(emoji_url.length > 0) {
        image_cache_request.open('POST','/api/cache/image/emoji', false)
        image_cache_request.send('{"url":"'+emoji_url+'"}')
        if (image_cache_request.status === 200) {
            let local_url = JSON.parse(image_cache_request.responseText)['url']
            content = '<img class="danmu-emoji" src="'+local_url+'" alt="'+content+'"/>'
        }
    }
    // Replace the emoji into image.
    for (const [emoji_str, emoji_url] of Object.entries(emoji_map)) {
        content = content.replaceAll(emoji_str, '<img class="danmaku-inline-emoji" src="'+emoji_url+'">')
    }
    // Generate the item object.
    return {'type': 'danmaku',
        'params': [avatar, guard, user_name, content, metal_name, metal_level, metal_wear]}
}

function create_gift(gift_data) {
    // Fetch the avatar.
    image_cache_request.open('POST', '/api/cache/image/avatar', false)
    image_cache_request.send('{"url":"'+gift_data['uface']+'"}')
    let avatar = JSON.parse(image_cache_request.responseText)['url']
    // Need to fetch the gift icon.
    image_cache_request.open('POST', '/api/cache/image/gift_icon', false)
    image_cache_request.send('{"url":"'+gift_data['gift_icon']+'"}')
    let gift_icon = JSON.parse(image_cache_request.responseText)['url']
    let content = '投喂 <span class="danmaku-gift">' + gift_data["gift_name"] + "</span> " +'<img class="danmaku-inline-emoji" src="'+gift_icon+'">' + " ×<span class=\"danmaku-gift\">" + gift_data["gift_num"] + "</span>"

    return {'type': 'gift',
        'params': [avatar, gift_data["guard_level"], gift_data["uname"], content, gift_data["fans_medal_name"], gift_data["fans_medal_level"], gift_data["fans_medal_wearing_status"]]}
}

function create_super_chat(sc_data) {
    // Need to fetch the user avatar.
    image_cache_request.open('POST', '/api/cache/image/avatar', false)
    image_cache_request.send('{"url":"'+sc_data['uface']+'"}')
    let avatar = JSON.parse(image_cache_request.responseText)['url']
    let content = "赠送 <span class=\"danmaku-gift\">醒目留言<img class=\"danmaku-inline-emoji\" src=\"/statics/skins/dialog/sc.png\"></span>×<span class=\"danmaku-gift\">1</span>说<br>" + sc_data["message"]
    return {'type': 'sc',
        'params': [avatar, sc_data["guard_level"], sc_data["uname"], content, sc_data["fans_medal_name"], sc_data["fans_medal_level"], sc_data["fans_medal_wearing_status"]]}
}

function create_guard(guard_data) {
    // Need to fetch the user avatar.
    image_cache_request.open('POST', '/api/cache/image/avatar', false)
    image_cache_request.send('{"url":"'+guard_data['user_info']["uface"]+'"}')
    let avatar = JSON.parse(image_cache_request.responseText)['url']
    let guard_info = guard_level_info[guard_data["guard_level"].toString()]
    let content = "开通 <span class=\"danmaku-gift\">" + guard_info[0] + "</span><img class=\"danmaku-inline-emoji\" src=\"/statics/skins/dialog/" + guard_info[1] + "\">×"+guard_data['guard_num'].toString()
    return {'type': 'guard',
        'params': [avatar, guard_data["guard_level"], guard_data['user_info']['uname'], content, guard_data["fans_medal_name"], guard_data["fans_medal_level"], guard_data["fans_medal_wearing_status"]]
    }
}

function to_render_item(item) {
    let packet_cmd = item['cmd']
    if(packet_cmd === 'LIVE_OPEN_PLATFORM_DM') {
        return create_danmaku(item['data'])
    } else if(packet_cmd === 'LIVE_OPEN_PLATFORM_SEND_GIFT') {
        return create_gift(item['data'])
    } else if(packet_cmd === 'LIVE_OPEN_PLATFORM_SUPER_CHAT') {
        return create_super_chat(item['data'])
    } else if(packet_cmd === 'LIVE_OPEN_PLATFORM_GUARD') {
        return create_guard(item['data'])
    } else {
        return null
    }
}

// Load the history request.
let fetch_history_request = new XMLHttpRequest()
fetch_history_request.open('GET',  '/api/cache/history_record', false)
fetch_history_request.send()
let history_record = JSON.parse(fetch_history_request.responseText)

history_record.forEach(function (item) {
    let rendered_item = to_render_item(item)
    if(rendered_item !== null) {
        postMessage({'op': 'add_history', 'item': rendered_item})
    }
})

postMessage({'op': 'start_websocket'})