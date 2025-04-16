# utils/azure_tts.py

import os
import azure.cognitiveservices.speech as speechsdk

def synthesize_speech(text, filename, voice="en-KE-AsiliaNeural"):
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")

    if not speech_key or not speech_region:
        raise Exception("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION must be set.")

    # Create speech config
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_synthesis_voice_name = voice

    # Create output config to save to file
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    # Create synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Synthesize text
    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"✅ Speech synthesized and saved to: {filename}")
        return filename
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error_msg = f"❌ Canceled: {cancellation_details.reason} - {cancellation_details.error_details}"
        print(error_msg)
        raise Exception(error_msg)
