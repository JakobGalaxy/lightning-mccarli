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
});