let max_danmaku_history_limit = window.screen.availHeight / 10
let danmaku_container = document.getElementById('danmaku-container')
let danmaku_history = document.getElementById('danmaku-history')
let render_rules = {
    "guard": {
        '0': "当前",
        '1': "总督",
        '2': "提督",
        '3': "舰长",
    }
}
let danmaku_display_queue = []
let danmaku_pop_instance = null

function create_danmaku(guard, user_name, content) {
    let danmaku = document.createElement('div')
    danmaku.classList.add('danmaku-base')
    danmaku.classList.add('danmaku')
    danmaku.innerHTML = '<span class="guard-'+guard+'">【'+render_rules['guard'][guard]+'】</span>' + `${user_name}：` + content
    return danmaku
}

function create_gift_box(icon_url, user_name, description, gift_size) {
    let gift = document.createElement('div')
    gift.classList.add('danmaku-base')
    gift.classList.add('danmaku-gift')

    let attach1 = document.createElement('div')
    attach1.style.background = "rgba(255, 255, 255, 0.1)"
    attach1.style.margin = "32px 0px 12px 24px"
    attach1.style.width = "calc(100% - 50px)"
    attach1.style.height = "calc(var(--font-size) + 34px)"
    attach1.style.borderRadius = "calc(var(--font-size) * 2)";
    attach1.style.border = "2px solid black"
    gift.appendChild(attach1)

    let gift_icon_div = document.createElement('div')
    gift_icon_div.style.position = "relative"
    gift_icon_div.style.float = "left"
    gift_icon_div.style.width = "calc(var(--font-size) + 18px)"
    gift_icon_div.style.top = "8px"
    gift_icon_div.style.left = "calc(var(--font-size) * 0.5 + 6px)"
    let gift_icon_element = document.createElement('img')
    gift_icon_element.src = icon_url
    gift_icon_element.style.width = "calc(var(--font-size) + 18px)"
    gift_icon_div.appendChild(gift_icon_element)
    attach1.appendChild(gift_icon_div)

    let user_name_element = document.createElement('div')
    user_name_element.style.position = "relative"
    gift_icon_div.style.float = "left"
    user_name_element.style.left = "calc(var(--font-size) + 6px)"
    user_name_element.style.top = "50%"
    user_name_element.style.transform = "translate(0, -50%)"
    user_name_element.classList.add('gift-text')
    user_name_element.innerText = user_name
    attach1.appendChild(user_name_element)

    let attach2 = document.createElement('div')
    attach2.innerText = "传输文件 (0/1)"
    attach2.style.float = "right"
    attach2.style.fontFamily = "SimHei"
    attach2.style.position = "relative"
    attach2.style.right = "50px"
    attach2.style.top = "calc(var(--font-size) * -2 + 3px)"
    attach2.classList.add('gift-text')
    attach1.appendChild(attach2)

    let attach3 = document.createElement('div')
    attach3.style.position = "relative"
    attach3.style.padding = "10px 15px"
    attach3.style.display = "table"
    attach3.style.top = "-20px"
    attach3.style.left = "65px"
    attach3.style.border = "2px solid rgba(0, 0, 0, 1.0)"
    attach3.style.backgroundColor = "rgba(255, 255, 255, 1.0)"
    attach3.style.width = "calc(100% - 160px)"
    attach3.style.color = "rgba(0, 0, 0, 1.0)"
    gift.appendChild(attach3)

    let attach6 = document.createElement('div')
    attach3.appendChild(attach6)

    let attach4 = document.createElement('div')
    attach4.style.float = "left"
    attach4.innerText = "项目类型："
    attach4.style.fontFamily = "SimHei"
    attach6.appendChild(attach4)

    let gift_info = document.createElement('div')
    gift_info.style.float = "left"
    gift_info.innerText = description
    attach6.appendChild(gift_info)

    let attach7 = document.createElement('div')
    attach3.appendChild(attach7)

    let attach5 = document.createElement('div')
    attach5.style.clear = "left"
    attach5.style.float = "left"
    attach5.style.fontFamily = "SimHei"
    attach5.innerText = "附件大小："
    attach7.appendChild(attach5)

    let gift_price_element = document.createElement('div')
    gift_price_element.style.float = "left"
    gift_price_element.innerText = gift_size
    attach7.appendChild(gift_price_element)

    return gift
}

function create_guard(user_face, user_name, guard_level) {
    let guard_div = document.createElement('div')
    guard_div.classList.add('danmaku-base')
    guard_div.classList.add('danmaku-guard')

    let guard_background = document.createElement('div')
    guard_background.style.display = "flex"
    guard_background.style.backgroundColor = "rgba(var(--sc-background), 1.0)"
    guard_background.style.backgroundImage = 'url("/statics/skins/ptn-base/guard_background.png")'
    guard_background.style.backgroundRepeat = "no-repeat"
    guard_background.style.backgroundPosition = "right"
    guard_background.style.backgroundSize = "auto 100%"
    guard_div.appendChild(guard_background)

    let guard_face = document.createElement('img')
    guard_face.src = user_face
    guard_face.classList.add('guard-face')
    guard_face.style.float = "left"
    guard_face.style.height = "5em"
    guard_background.appendChild(guard_face)

    let guard_info = document.createElement('div')
    guard_info.style.float = 'left'
    guard_info.style.margin = '1em 1em'
    guard_background.appendChild(guard_info)

    let guard_title = document.createElement('div')
    guard_title.innerText = `【${render_rules['guard'][guard_level.toString()]}上任】`
    guard_info.appendChild(guard_title)

    let guard_text = document.createElement('div')
    guard_text.innerText = `${user_name}：加入了大航海`
    guard_info.appendChild(guard_text)

    return guard_div
}

function create_item(item_info) {
    let item_type = item_info['type']
    if(item_type === 'danmaku') {
        let last_element = danmaku_history.lastElementChild
        if(last_element !== null) {
            // Check the class list.
            if(last_element.classList.contains("danmaku")) {
                last_element.classList.add('danmaku-splitter')
            }
        }
        return create_danmaku(...item_info['params'])
    }
    if(item_type === 'gift' || item_type === 'sc') {
        return create_gift_box(...item_info['params'])
    }
    if(item_type === 'guard') {
        return create_guard(...item_info['params'])
    }
}

function add_history(item_info) {
    danmaku_history.appendChild(create_item(item_info))
}

function show_next_danmaku() {
    // Pick the last danmaku from the queue.
    let candidate = danmaku_display_queue.pop()
    // Add the candidate to the container.
    candidate.classList.add("danmaku-enter")
    candidate.classList.add("outside")
    danmaku_container.appendChild(candidate)
    // Enable the history danmaku animation.
    danmaku_history.style.transform = "translateY(" + (-candidate.offsetHeight).toString() + "px)"
    danmaku_history.classList.add("anime")
    //Show the splitter.
    let last_danmaku = danmaku_history.lastElementChild
    if(last_danmaku) {
        if(last_danmaku.classList.contains('danmaku') && candidate.classList.contains('danmaku')) {
            last_danmaku.classList.add('danmaku-splitter')
        }
    }
    // Start the outside animation.
    candidate.classList.remove("outside")
    candidate.ontransitionend = () => {
        // Clear the function binding.
        candidate.ontransitionend = null
        // Reset the danmaku history style.
        danmaku_history.classList.remove("anime")
        danmaku_history.style.transform = "none"
        // Remove all the animation tag.
        candidate.classList.remove("danmaku-enter")
        // Move the candidate item to history.
        danmaku_history.appendChild(candidate)
        // Limit the max history records.
        if(danmaku_history.childElementCount > max_danmaku_history_limit) {
            danmaku_history.removeChild(danmaku_history.firstElementChild)
        }
        // Flush the history record.
        fetch('/api/cache/history_record/flush', {method: 'POST'}).then()
        // Check the display queue.
        if(danmaku_display_queue.length > 0) {
            // Set the splitter to the last item in the history.
            danmaku_pop_instance = setTimeout(show_next_danmaku, 1000);
        } else {
            danmaku_pop_instance = null
        }
    }
}

function add_to_queue(item_info) {
    //Append the element to display queue.
    danmaku_display_queue.push(create_item(item_info))
    //Start the display function.
    if(!danmaku_pop_instance) {
        show_next_danmaku();
    }
}