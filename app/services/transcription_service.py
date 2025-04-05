import multiprocessing
import whisper

tiny_whisper_model = whisper.load_model("tiny")

def transcribe_audio(task_id: str, audio_file: str, queue: multiprocessing.Queue):
    try:
        result = tiny_whisper_model.transcribe(audio_file, task="translate")
        queue.put((task_id, "completed", result["segments"]))
    except Exception as e:
        queue.put((task_id, "failed", str(e)))

def start_transcription_process(task_id: str, audio_file: str):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=transcribe_audio, args=(task_id, audio_file, queue))
    process.start()
    return process, queue

def cancel_transcription(process: multiprocessing.Process):
    if process.is_alive():
        process.terminate()
        process.join()
