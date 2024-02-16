let max_danmaku_history_limit = window.screen.availHeight / 10
let danmaku_container = document.getElementById('danmaku-container')
let danmaku_history = document.getElementById('danmaku-history')
let danmaku_display_queue = []
let danmaku_pop_instance = null
let guard_map = {
    '1': 'icon-guard1.png',
    '2': 'icon-guard2.png',
    '3': 'icon-guard3.png',
}

let medal_color = {
    '1': 'linear-gradient(45deg, rgb(92, 150, 142), rgb(92, 150, 142))',
    '2': 'linear-gradient(45deg, rgb(92, 150, 142), rgb(92, 150, 142))',
    '3': 'linear-gradient(45deg, rgb(92, 150, 142), rgb(92, 150, 142))',
    '4': 'linear-gradient(45deg, rgb(92, 150, 142), rgb(92, 150, 142))',
    '5': 'linear-gradient(45deg, rgb(93, 123, 158), rgb(93, 123, 158))',
    '6': 'linear-gradient(45deg, rgb(93, 123, 158), rgb(93, 123, 158))',
    '7': 'linear-gradient(45deg, rgb(93, 123, 158), rgb(93, 123, 158))',
    '8': 'linear-gradient(45deg, rgb(93, 123, 158), rgb(93, 123, 158))',
    '9': 'linear-gradient(45deg, rgb(141, 124, 166), rgb(141, 124, 166))',
    '10': 'linear-gradient(45deg, rgb(141, 124, 166), rgb(141, 124, 166))',
    '11': 'linear-gradient(45deg, rgb(141, 124, 166), rgb(141, 124, 166))',
    '12': 'linear-gradient(45deg, rgb(141, 124, 166), rgb(141, 124, 166))',
    '13': 'linear-gradient(45deg, rgb(190, 100, 133), rgb(190, 100, 133))',
    '14': 'linear-gradient(45deg, rgb(190, 100, 133), rgb(190, 100, 133))',
    '15': 'linear-gradient(45deg, rgb(190, 100, 133), rgb(190, 100, 133))',
    '16': 'linear-gradient(45deg, rgb(190, 100, 133), rgb(190, 100, 133))',
    '17': 'linear-gradient(45deg, rgb(201, 156, 36), rgb(201, 156, 36))',
    '18': 'linear-gradient(45deg, rgb(201, 156, 36), rgb(201, 156, 36))',
    '19': 'linear-gradient(45deg, rgb(201, 156, 36), rgb(201, 156, 36))',
    '20': 'linear-gradient(45deg, rgb(201, 156, 36), rgb(201, 156, 36))',
    '21': 'linear-gradient(45deg, rgb(26, 84, 75), rgb(82, 157, 146))',
    '22': 'linear-gradient(45deg, rgb(26, 84, 75), rgb(82, 157, 146))',
    '23': 'linear-gradient(45deg, rgb(26, 84, 75), rgb(82, 157, 146))',
    '24': 'linear-gradient(45deg, rgb(26, 84, 75), rgb(82, 157, 146))',
    '25': 'linear-gradient(45deg, rgb(6, 21, 76), rgb(104, 136, 241))',
    '26': 'linear-gradient(45deg, rgb(6, 21, 76), rgb(104, 136, 241))',
    '27': 'linear-gradient(45deg, rgb(6, 21, 76), rgb(104, 136, 241))',
    '28': 'linear-gradient(45deg, rgb(6, 21, 76), rgb(104, 136, 241))',
    '29': 'linear-gradient(45deg, rgb(45, 8, 85), rgb(157, 155, 255))',
    '30': 'linear-gradient(45deg, rgb(45, 8, 85), rgb(157, 155, 255))',
    '31': 'linear-gradient(45deg, rgb(45, 8, 85), rgb(157, 155, 255))',
    '32': 'linear-gradient(45deg, rgb(45, 8, 85), rgb(157, 155, 255))',
    '33': 'linear-gradient(45deg, rgb(122, 4, 35), rgb(233, 134, 187))',
    '34': 'linear-gradient(45deg, rgb(122, 4, 35), rgb(233, 134, 187))',
    '35': 'linear-gradient(45deg, rgb(122, 4, 35), rgb(233, 134, 187))',
    '36': 'linear-gradient(45deg, rgb(122, 4, 35), rgb(233, 134, 187))',
    '37': 'linear-gradient(45deg, rgb(255, 97, 11), rgb(255, 208, 132))',
    '38': 'linear-gradient(45deg, rgb(255, 97, 11), rgb(255, 208, 132))',
    '39': 'linear-gradient(45deg, rgb(255, 97, 11), rgb(255, 208, 132))',
    '40': 'linear-gradient(45deg, rgb(255, 97, 11), rgb(255, 208, 132))'
}

let medal_border_color = {
    '1': 'rgb(92, 150, 142)',
    '2': 'rgb(92, 150, 142)',
    '3': 'rgb(92, 150, 142)',
    '4': 'rgb(92, 150, 142)',
    '5': 'rgb(93, 123, 158)',
    '6': 'rgb(93, 123, 158)',
    '7': 'rgb(93, 123, 158)',
    '8': 'rgb(93, 123, 158)',
    '9': 'rgb(141, 124, 166)',
    '10': 'rgb(141, 124, 166)',
    '11': 'rgb(141, 124, 166)',
    '12': 'rgb(141, 124, 166)',
    '13': 'rgb(190, 100, 133)',
    '14': 'rgb(190, 100, 133)',
    '15': 'rgb(190, 100, 133)',
    '16': 'rgb(190, 100, 133)',
    '17': 'rgb(201, 156, 36)',
    '18': 'rgb(201, 156, 36)',
    '19': 'rgb(201, 156, 36)',
    '20': 'rgb(201, 156, 36)',
    '21': 'rgb(103, 232, 255)',
    '22': 'rgb(103, 232, 255)',
    '23': 'rgb(103, 232, 255)',
    '24': 'rgb(103, 232, 255)',
    '25': 'rgb(103, 232, 255)',
    '26': 'rgb(103, 232, 255)',
    '27': 'rgb(103, 232, 255)',
    '28': 'rgb(103, 232, 255)',
    '29': 'rgb(103, 232, 255)',
    '30': 'rgb(103, 232, 255)',
    '31': 'rgb(103, 232, 255)',
    '32': 'rgb(103, 232, 255)',
    '33': 'rgb(255, 232, 84)',
    '34': 'rgb(255, 232, 84)',
    '35': 'rgb(255, 232, 84)',
    '36': 'rgb(255, 232, 84)',
    '37': 'rgb(255, 232, 84)',
    '38': 'rgb(255, 232, 84)',
    '39': 'rgb(255, 232, 84)',
    '40': 'rgb(255, 232, 84)'
}

let medal_text_color = {
    '1': 'rgb(92, 150, 142)',
    '2': 'rgb(92, 150, 142)',
    '3': 'rgb(92, 150, 142)',
    '4': 'rgb(92, 150, 142)',
    '5': 'rgb(93, 123, 158)',
    '6': 'rgb(93, 123, 158)',
    '7': 'rgb(93, 123, 158)',
    '8': 'rgb(93, 123, 158)',
    '9': 'rgb(141, 124, 166)',
    '10': 'rgb(141, 124, 166)',
    '11': 'rgb(141, 124, 166)',
    '12': 'rgb(141, 124, 166)',
    '13': 'rgb(190, 100, 133)',
    '14': 'rgb(190, 100, 133)',
    '15': 'rgb(190, 100, 133)',
    '16': 'rgb(190, 100, 133)',
    '17': 'rgb(201, 156, 36)',
    '18': 'rgb(201, 156, 36)',
    '19': 'rgb(201, 156, 36)',
    '20': 'rgb(201, 156, 36)',
    '21': 'rgb(26, 84, 75)',
    '22': 'rgb(26, 84, 75)',
    '23': 'rgb(26, 84, 75)',
    '24': 'rgb(26, 84, 75)',
    '25': 'rgb(6, 21, 76)',
    '26': 'rgb(6, 21, 76)',
    '27': 'rgb(6, 21, 76)',
    '28': 'rgb(6, 21, 76)',
    '29': 'rgb(45, 8, 85)',
    '30': 'rgb(45, 8, 85)',
    '31': 'rgb(45, 8, 85)',
    '32': 'rgb(45, 8, 85)',
    '33': 'rgb(122, 4, 35)',
    '34': 'rgb(122, 4, 35)',
    '35': 'rgb(122, 4, 35)',
    '36': 'rgb(122, 4, 35)',
    '37': 'rgb(255, 97, 11)',
    '38': 'rgb(255, 97, 11)',
    '39': 'rgb(255, 97, 11)',
    '40': 'rgb(255, 97, 11)'
}

function create_danmaku_box(avatar, guard, user_name, content, metal_name, metal_level, metal_wear) {
    let danmaku = document.createElement('div')
    danmaku.classList.add('danmaku-base')
    danmaku.classList.add('danmaku')

    let avatar_element = document.createElement('img')
    avatar_element.classList.add('avatar')
    avatar_element.src = avatar
    danmaku.appendChild(avatar_element)

    let dialog = document.createElement('div')
    dialog.classList.add('main')
    let name_element = document.createElement('div')
    name_element.classList.add('name-bar')
    let name_wrapper = document.createElement('div')
    name_wrapper.classList.add('name-bar-cell')
    let name_text = document.createElement('div')
    name_text.classList.add('user-name')
    name_text.innerText = user_name
    name_wrapper.appendChild(name_text)
    name_element.appendChild(name_wrapper)

    if (guard.toString() in guard_map) {
        let guard_wrapper = document.createElement('div')
        guard_wrapper.classList.add('name-bar-cell')
        let guard_icon = document.createElement('img')
        guard_icon.classList.add('name-guard')
        guard_icon.src = '/statics/skins/dialog/'+guard_map[guard.toString()]
        guard_wrapper.appendChild(guard_icon)
        name_element.appendChild(guard_wrapper)
    }

    if(metal_wear) {
        let metal_level_text = metal_level.toString()

        let metal_wrapper = document.createElement('div')
        metal_wrapper.classList.add('name-bar-cell')
        let metal = document.createElement('div')
        metal.classList.add('metal')
        metal.style.borderColor = medal_border_color[metal_level_text];
        name_element.appendChild(metal)
        let metal_label_element = document.createElement('div')
        metal_label_element.classList.add('metal-label')
        metal_label_element.style.backgroundImage = medal_color[metal_level_text]
        let metal_label_text = document.createElement('span')
        metal_label_text.innerText = metal_name
        metal_label_element.appendChild(metal_label_text)
        metal.appendChild(metal_label_element)
        let metal_level_element = document.createElement('div')
        metal_level_element.classList.add('metal-level')
        metal_level_element.style.color = medal_text_color[metal_level_text]
        metal_level_element.innerText = metal_level_text
        metal.appendChild(metal_level_element)
        metal_wrapper.appendChild(metal)
        name_element.appendChild(metal_wrapper)
    }

    dialog.appendChild(name_element)

    let content_border = document.createElement('div')
    content_border.classList.add('danmaku-border')
    let content_element = document.createElement('div')
    content_element.classList.add('danmaku-background')
    let content_wrapper = document.createElement('div')
    content_wrapper.classList.add('danmaku-body')
    content_wrapper.innerHTML = content
    content_element.appendChild(content_wrapper)
    content_border.appendChild(content_element)
    dialog.appendChild(content_border)

    danmaku.appendChild(dialog)

    return danmaku
}

function create_item(item_info) {
    let item_type = item_info['type']
    if(item_type === 'danmaku' || item_type === 'gift' || item_type === 'sc' || item_type === 'guard') {
        return create_danmaku_box(...item_info['params'])
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