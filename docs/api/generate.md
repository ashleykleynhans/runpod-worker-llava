## Request

```json
{
  "input": {
    "model_path": "liuhaotian/llava-v1.5-7b",
    "image": "base64 encoded image content",
    "prompt": "What is unusual about this image?",
    "temperature": 0.2,
    "max_new_tokens": 512,
    "stream": false
  }
}
```

## Response

## RUN

```json
{
  "id": "83bbc301-5dcd-4236-9293-a65cdd681858",
  "status": "IN_QUEUE"
}
```

## RUNSYNC

```json
{
  "delayTime": 7334,
  "executionTime": 20260,
  "id": "sync-acccda60-3017-41c8-bf93-d495ab1c0557-e1",
  "output": "The unusual aspect of this image is that a man is sitting on a folding chair in the back of a yellow taxi, which is driving down a busy city street. It is not common to see someone sitting in such a position in a taxi, as passengers typically sit inside the vehicle. The man's position on the folding chair and the presence of a laundry basket in the back of the taxi further contribute to the unconventional nature of the scene.",
  "status": "COMPLETED"
}
```
