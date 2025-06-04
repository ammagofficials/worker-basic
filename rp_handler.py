import runpod
import time
import base64
import soundfile as sf
import torch
import io
from kokoro import KPipeline  # Assumes kokoro is properly installed

# Preload the model (optional, helps avoid cold-start delay)
pipeline_cache = {}

def handler(event):
    print("Worker Start")
    input = event['input']

    prompt = input.get('prompt')
    languageId = input.get('languageId', 'a')       # e.g., 'en' for English
    voice = input.get('voiceType', 'af_heart')      # Default voice

    print(f"Received prompt: {prompt}")
    print(f"Language is: {languageId}")

    # Load pipeline from Hugging Face model
    cache_key = f"{languageId}-{voice}"
    if cache_key not in pipeline_cache:
        print("Loading model...")
        pipeline_cache[cache_key] = KPipeline(
            lang_code=languageId,
            model_id="hexgrad/Kokoro-82M",  # Explicitly use this Hugging Face model
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

    pipeline = pipeline_cache[cache_key]

    # Generate audio
    generator = pipeline(prompt, voice=voice)

    i, (gs, ps, audio) = next(enumerate(generator))
    print(f"Generated audio index: {i}")

    # Save audio to buffer
    buffer = io.BytesIO()
    sf.write(buffer, audio, 24000, format='WAV')
    buffer.seek(0)

    # Encode to base64
    audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return {
        "status": "success",
        "audio_base64": audio_base64,
        "text": prompt,
        "sample_rate": 24000,
        "format": "wav"
    }

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
