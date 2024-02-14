onmessage = (event) => {
    let inst = event.data
    let op = inst['op']
    if(op === 'start') {
        start_websocket(inst['host'])
    }
}

function start_websocket(host_addr) {
    let ws = new WebSocket('ws://'+host_addr+'/danmaku')
    ws.onmessage = function (e) {
        let packet = JSON.parse(e.data)
        if ('cmd' in packet) {
            let cmd = packet['cmd']
            if(cmd === 'MTC_REFRESH') {
                postMessage({'op': 'refresh'})
                return
            }
        }
        // Bypass the packet to UI.
        postMessage({'op': 'new_item', 'item': packet})
    }
    ws.onclose = function (e) {
        console.log('Connection closed, retry 1 second later...')
        setTimeout(function () {
            start_websocket()
        }, 1000)
    }
    ws.onerror = function (e) {
        console.log(e)
    }
}
