onmessage = (event) => {
    let inst = event.data
    let op = inst['op']
    if (op === 'add_to_queue') {
        postMessage({'op': 'add_to_queue', 'item': to_render_item(inst['item'])})
    }
}

let image_cache_request = new XMLHttpRequest()

function create_danmaku(danmu_data) {
    let guard = danmu_data["guard_level"]
    let user_name = danmu_data["uname"]
    let content = danmu_data["msg"]
    let emoji_url = danmu_data["emoji_img_url"]

    // Check emoji url.
    if(emoji_url.length > 0) {
        // Need to fetch the image.
        image_cache_request.open('POST','/api/cache/image/emoji', false)
        image_cache_request.send('{"url":"'+emoji_url+'"}')
        if (image_cache_request.status === 200) {
            let local_url = JSON.parse(image_cache_request.responseText)['url']
            content = '<img class="danmu-emoji" src="'+local_url+'" alt="'+content+'"/>'
        }
    }
    //Generate the item object.
    return {'type': 'danmaku',
        'params': [guard, user_name, content]}
}

function create_gift(gift_data) {
    // Need to fetch the gift icon.
    image_cache_request.open('POST', '/api/cache/image/gift_icon', false)
    image_cache_request.send('{"url":"'+gift_data['gift_icon']+'"}')
    let gift_icon = JSON.parse(image_cache_request.responseText)['url']
    return {'type': 'gift',
        'params': [gift_icon, gift_data["uname"], "赠送 " + gift_data["gift_name"] + "x" + gift_data["gift_num"].toString(), gift_data["price"].toString() + " KB"]}
}

function create_super_chat(sc_data) {
    // Need to fetch the user avatar.
    image_cache_request.open('POST', '/api/cache/image/avatar', false)
    image_cache_request.send('{"url":"'+sc_data['uface']+'"}')
    let avatar = JSON.parse(image_cache_request.responseText)['url']
    return {'type': 'sc',
        'params': [avatar, sc_data["uname"], sc_data["message"], sc_data["rmb"].toString() + " MB"]}
}

function create_guard(guard_data) {
    // Need to fetch the user avatar.
    image_cache_request.open('POST', '/api/cache/image/avatar', false)
    image_cache_request.send('{"url":"'+guard_data['user_info']["uface"]+'"}')
    let avatar = JSON.parse(image_cache_request.responseText)['url']
    return {'type': 'guard',
        'params': [avatar, guard_data['user_info']['uname'], guard_data['guard_level']]
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
    }
}

// Load the history request.
let fetch_history_request = new XMLHttpRequest()
fetch_history_request.open('GET',  '/api/cache/history_record', false)
fetch_history_request.send()
let history_record = JSON.parse(fetch_history_request.responseText)

history_record.forEach(function (item) {
    postMessage({'op': 'add_history', 'item': to_render_item(item)})
})

postMessage({'op': 'start_websocket'})