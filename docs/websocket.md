# WebSocket Communication

## Message Format

```json
{
  "channel": "<CHANNEL>",
  "type": "<MESSAGE-TYPE>",
  ...
}
```

#### Video Stream

##### Publish-Frame Message

- this message is sent from the client to the server

```json
{
  "channel": "video_stream",
  "type": "publish_frame",
  // time of recording
  "timestamp": "2022-12-19 22:15:30.408000",
  "frame": "<BASE64-PNG>"
}
```

#### Frame-Data Message

- this message is sent from the server to all subscribed clients

```json
{
  "channel": "video_stream",
  "type": "frame_data",
  // time of recording
  "timestamp": "2022-12-19 22:15:30.408000",
  "frame": "<BASE64-PNG>"
}
```

##### Subscribe Message

- this message is sent from the client to the server

```json
{
  "channel": "video_stream",
  "type": "subscribe"
}
```