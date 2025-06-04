import runpod
import time
import base64
from kokoro import KPipeline
import soundfile as sf
import torch
import io

# -----------------------------
# Load model ONCE at container startup
# -----------------------------

print("Initializing container...")

device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "hexgrad/Kokoro-82M"

print(f"Loading Kokoro model: {model_id} on {device}...")

# Use pre-trained Kokoro pipeline (this assumes KPipeline supports model_id)
start_time = time.time()

pipeline = KPipeline(model_id=model_id, device=device)
load_duration = time.time() - start_time

print(f"Kokoro pipeline loaded in {load_duration:.2f}s.")
print("Handler ready to accept requests.")

# -----------------------------
# Inference Handler
# -----------------------------

def handler(event):
    print("Worker Start")
    input = event.get('input', {})

    prompt = input.get('prompt', '')
    language_id = input.get('languageId', 'a')
    voice = input.get('voiceType', 'af_heart')

    print(f"Prompt: {prompt}, Language: {language_id}, Voice: {voice}")

    # Use the global pipeline
    try:
        generator = pipeline(prompt, lang_code=language_id, voice=voice)
        i, (gs, ps, audio) = next(enumerate(generator))
        print(f"Generated audio (step {i}): {gs}, {ps}")
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Encode audio
    buffer = io.BytesIO()
    sf.write(buffer, audio, 24000, format='WAV')
    buffer.seek(0)
    audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return {
        "status": "success",
        "audio_base64": audio_base64,
        "text": prompt,
        "sample_rate": 24000,
        "format": "wav"
    }

# -----------------------------
# RunPod Entry Point
# -----------------------------

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
