# 🎙️ Whisper Transcription API

This FastAPI application provides a simple API to transcribe audio files using OpenAI's [Whisper](https://github.com/openai/whisper) model (specifically, the `tiny` version). It supports asynchronous transcription tasks, where you can upload a file, check its status, and cancel if needed.

---

## 🔧 Requirements

- Python 3.8+

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App

Start the FastAPI server:

```bash
fastapi dev main.py
```

---

## 📚 API Endpoints

### 1. `POST /transcribe`

**Starts a new transcription task.**

#### Request:
- **Form-Data**: Upload an audio file (e.g., `.mp3`, `.wav`, `.m4a`).

#### Response:
```json
{
  "task_id": "de305d54-75b4-431b-adb2-eb6b9e546013",
  "status": "running",
  "result": null
}
```

The response includes a `task_id` which you will use to query the task status.

---

### 2. `GET /status/{task_id}`

**Checks the status of a transcription task.**

#### Path Parameters:
- `task_id` (string): The ID returned from `/transcribe`.

#### Response when running:
```json
{
  "task_id": "de305d54-75b4-431b-adb2-eb6b9e546013",
  "status": "running",
  "result": null
}
```

#### Response when completed:
```json
{
  "task_id": "de305d54-75b4-431b-adb2-eb6b9e546013",
  "status": "completed",
  "result": [
    {
      "id": 0,
      "seek": 0.0,
      "start": 0.0,
      "end": 5.0,
      "text": "Hello world!",
      "tokens": [50364, 2425, 3180, 13, 50464],
      "temperature": 0.0,
      "avg_logprob": -0.234,
      "compression_ratio": 1.23,
      "no_speech_prob": 0.01
    },
    ...
  ]
}
```

If the task failed, `status` will be `"failed"` and `result` will contain the error message as a string.

---

### 3. `DELETE /cancel/{task_id}`

**Cancels a running transcription task.**

#### Path Parameters:
- `task_id` (string): The ID of the running task to cancel.

#### Response:
```json
{
  "task_id": "de305d54-75b4-431b-adb2-eb6b9e546013",
  "status": "canceled",
  "result": null
}
```
## 📬 Example cURL Request

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_audio_file.mp3"
```

---

## 🧹 TODOs / Ideas

- Validate input file to make sure it's not malware, and it's a valid file for whisper to process.
- Add support for other Whisper tasks (e.g., `transcribe` without translation).
- Add optional language selection.
- Persist tasks in a database (Redis might be a good choice).
- Serve results as subtitle files (e.g., `.srt`, `.vtt`).
- Let the user choose between whisper models.
