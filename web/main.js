let videoStreamDisplay = null;

let websocket;

function connect() {
    websocket = new WebSocket("ws://localhost:5678/");
}

function subscribe() {
    let message = {
        "channel": "video_stream",
        "type": "subscribe"
    }
    websocket.send(JSON.stringify(message));
    console.log('subscribed');
}

function receive(data) {
    console.log("received frame");
    videoStreamDisplay.src = `data:image/png;base64,${data.frame}`;
}

function send_control(x, y) {
    let message = {
        "channel": "control",
        "type": "publish",
        "x": x,
        "y": y,
    }
    websocket.send(JSON.stringify(message));
    console.log('sent control message');
}

function initWebsocket() {
    connect();
    websocket.onopen = () => {
        console.log('connected!');
        subscribe();
    }
    websocket.addEventListener("message", (message) => {
        // console.log(message);
        receive(JSON.parse(message.data));
    })
    // websocket.onmessage = ({message}) => receive(message);
}

window.addEventListener("DOMContentLoaded", () => {
    videoStreamDisplay = document.getElementById("videoStreamDisplay");
    initWebsocket();


    const upButton = document.getElementById('up-button');
    const downButton = document.getElementById('down-button');
    const leftButton = document.getElementById('left-button');
    const rightButton = document.getElementById('right-button');
    upButton.addEventListener('click', () => {
        send_control(0, 1);
    });
    downButton.addEventListener('click', () => {
        send_control(0, -1);
    });
    leftButton.addEventListener('click', () => {
        send_control(-1, 0);
    });
    rightButton.addEventListener('click', () => {
        console.log("press");
        send_control(1, 0);
    });
});

let activeKeys = new Set();

document.addEventListener("keydown", event => {
    activeKeys.add(event.key);
});

document.addEventListener("keyup", event => {
    activeKeys.delete(event.key);
});

document.addEventListener("keypress", function (e) {
    let x = 0;
    let y = 0;

    if (activeKeys.has('d')) {
        x += 1;
    }
    if (activeKeys.has('a')) {
        x -= 1;
    }
    if (activeKeys.has('w')) {
        y += 1;
    }
    if (activeKeys.has('s')) {
        y -= 1;
    }

    send_control(x, y);
});