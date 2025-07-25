import runpod
import time
import base64
from kokoro import KPipeline
import soundfile as sf
import torch
import io
import numpy as np

def handler(event):
    print("Worker Start")
    input = event['input']

    prompt = input.get('prompt')
    languageId = input.get('languageId', 'a')
    voice = input.get('voiceType', 'af_heart')

    print(f"Received prompt: {prompt}")
    print(f"Language is: {languageId}")

    pipeline = KPipeline(lang_code=languageId)
    text = prompt
    generator = pipeline(text, voice=voice)

    full_audio = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps)
        full_audio.append(audio)

    # Concatenate all audio chunks
    combined_audio = np.concatenate(full_audio)

    # Save to memory buffer instead of file
    buffer = io.BytesIO()
    sf.write(buffer, combined_audio, 24000, format='WAV')
    buffer.seek(0)

    # Encode as base64 for safe return
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
