import os
import time
import logging
import uuid
import random
from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import azure.cognitiveservices.speech as speechsdk
import io
from utils.text_processing import clean_text, chunk_text
from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Create a temp directory for audio files
os.makedirs("temp", exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    try:
        text = request.form.get("text", "")
        language = request.form.get("language", "en")
        voice_speed = request.form.get("voice_speed", False)
        voice_speed = True if voice_speed == "true" else False
        use_azure = request.form.get("use_azure", "false") == "true"
        voice_name = request.form.get("voice_name", "")
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        logger.debug(f"Received text input of length: {len(text)}")
        
        # Clean and process the text
        cleaned_text = clean_text(text)
        
        if len(cleaned_text) > 100000:  # Set a reasonable limit
            return jsonify({"error": "Text is too long. Maximum is 100,000 characters."}), 400
            
        # Generate a unique ID for this conversion
        file_id = str(uuid.uuid4())
        file_path = f"temp/{file_id}.mp3"
        
        # Use Azure Cognitive Services if requested
        if use_azure:
            # Get Azure credentials from environment variables
            speech_key = os.environ.get("AZURE_SPEECH_KEY")
            service_region = os.environ.get("AZURE_SPEECH_REGION")
            
            if not speech_key:
                return jsonify({"error": "Azure Speech API key not configured. Please set the AZURE_SPEECH_KEY environment variable."}), 500
            
            # Map language code to appropriate voice name if not specified
            if not voice_name:
                voice_map = {
                    "en": "en-US-JennyNeural",
                    "es": "es-ES-ElviraNeural",
                    "fr": "fr-FR-DeniseNeural",
                    "de": "de-DE-KatjaNeural",
                    "it": "it-IT-ElsaNeural",
                    "pt": "pt-BR-FranciscaNeural",
                    "ru": "ru-RU-SvetlanaNeural",
                    "ja": "ja-JP-NanamiNeural",
                    "ko": "ko-KR-SunHiNeural",
                    "zh-CN": "zh-CN-XiaoxiaoNeural"
                }
                voice_name = voice_map.get(language, "en-US-JennyNeural")
            
            # Setup speech configuration
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Set the output format to MP3
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )
            
            logger.debug(f"Using Azure TTS with voice: {voice_name}")
            
            # For long texts, chunk and process
            if len(cleaned_text) > 5000:
                logger.debug(f"Long text detected ({len(cleaned_text)} chars). Chunking text.")
                chunks = chunk_text(cleaned_text, 4000)  # Slightly smaller chunks for Azure
                
                # Process each chunk and combine
                with open(file_path, 'wb') as outfile:
                    for i, chunk in enumerate(chunks):
                        logger.debug(f"Processing chunk {i+1}/{len(chunks)} with Azure")
                        
                        # Create a temporary file for this chunk
                        temp_chunk_path = f"temp/temp_chunk_{file_id}_{i}.mp3"
                        
                        # Create a speech synthesizer with the temporary file as output
                        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_chunk_path)
                        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                        
                        # Synthesize the text
                        result = synthesizer.speak_text_async(chunk).get()
                        
                        # Check result
                        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                            # Read the temporary file and append to the output
                            with open(temp_chunk_path, 'rb') as chunk_file:
                                outfile.write(chunk_file.read())
                            # Remove the temporary file
                            os.remove(temp_chunk_path)
                        else:
                            raise Exception(f"Speech synthesis failed: {result.reason}")
            else:
                # For shorter texts
                audio_config = speechsdk.audio.AudioOutputConfig(filename=file_path)
                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                
                result = synthesizer.speak_text_async(cleaned_text).get()
                if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                    raise Exception(f"Speech synthesis failed: {result.reason}")
                
            message = "Text converted successfully with premium Azure voice!"
        else:
            # Use gTTS as fallback
            # For long texts, chunk and process
            if len(cleaned_text) > 5000:
                logger.debug(f"Long text detected ({len(cleaned_text)} chars). Chunking text.")
                chunks = chunk_text(cleaned_text, 5000)  # 5000 chars per chunk
                
                # Initialize a combined audio file
                combined = io.BytesIO()
                
                for i, chunk in enumerate(chunks):
                    logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
                    # Convert text chunk to speech
                    tts = gTTS(text=chunk, lang=language, slow=voice_speed)
                    chunk_audio = io.BytesIO()
                    tts.write_to_fp(chunk_audio)
                    chunk_audio.seek(0)
                    combined.write(chunk_audio.read())
                    
                combined.seek(0)
                with open(file_path, 'wb') as f:
                    f.write(combined.read())
            else:
                # For shorter texts, process directly
                tts = gTTS(text=cleaned_text, lang=language, slow=voice_speed)
                tts.save(file_path)
                
            message = "Text converted successfully!"
            
        return jsonify({
            "success": True,
            "file_id": file_id,
            "message": message,
            "file_path": f"/download/{file_id}"
        })
            
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return jsonify({"error": f"Failed to convert text: {str(e)}"}), 500

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file:
            # Read the file content
            content = file.read().decode('utf-8')
            
            # Check the file size
            if len(content) > 100000:
                return jsonify({"error": "File is too large. Maximum is 100,000 characters."}), 400
                
            return jsonify({"success": True, "text": content})
            
    except UnicodeDecodeError:
        return jsonify({"error": "Could not decode file. Please upload a valid text file."}), 400
    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500

@app.route("/download/<file_id>")
def download_file(file_id):
    try:
        # Sanitize file_id to prevent directory traversal
        file_id = file_id.replace('/', '').replace('\\', '')
        file_path = f"temp/{file_id}.mp3"
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
            
        return send_file(file_path, as_attachment=True, download_name="speech.mp3")
        
    except Exception as e:
        logger.error(f"Error during file download: {str(e)}")
        return jsonify({"error": f"Failed to download file: {str(e)}"}), 500

# Cleanup function to remove old temporary files
@app.before_request
def cleanup_temp_files():
    try:
        now = time.time()
        temp_dir = "temp"
        
        # Only run cleanup occasionally to reduce overhead
        if os.path.exists(temp_dir) and random.random() < 0.1:  # 10% chance of running
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # Remove files older than 1 hour
                    if now - os.path.getmtime(file_path) > 3600:
                        os.remove(file_path)
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {str(e)}")
