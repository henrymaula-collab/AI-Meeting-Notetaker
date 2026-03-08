import os
import sys
import queue
import threading
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Check for API key
if not os.environ.get("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY not found in environment.")
    print("Please set your API key in the .env file.")
    sys.exit(1)

# Audio recording parameters
SAMPLE_RATE = 16000  # 16kHz is optimal for speech recognition and saves file size
CHANNELS = 1         # Mono audio saves file size

audio_queue = queue.Queue()
recording = False

def audio_callback(indata, frames, time, status):
    """This is called by sounddevice for each audio block."""
    if status:
        print(status, file=sys.stderr)
    if recording:
        audio_queue.put(indata.copy())

def record_audio(filename="meeting_audio.wav"):
    """Records audio from the default microphone until the user presses Enter."""
    global recording
    print("\nStarting meeting recording...")
    print("Press Enter at any time to STOP recording and process the meeting.")

    recording = True
    audio_data = []

    # Start audio stream
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
        # Wait for user to press Enter to stop
        input() 
        recording = False
        print("Stopping recording... Please wait while we process the audio.")

    # Gather data from queue
    while not audio_queue.empty():
        audio_data.append(audio_queue.get())
    
    if not audio_data:
        print("No audio recorded.")
        return None

    # Concatenate all numpy arrays
    audio_np = np.concatenate(audio_data, axis=0)
    
    # Save as WAV file
    write(filename, SAMPLE_RATE, audio_np)
    print(f"Saved recording to {filename}")
    return filename

def process_meeting(audio_file):
    """Uploads the audio to Gemini and gets a transcription and summary."""
    print("\nUploading and processing audio with Gemini API...")
    
    try:
        client = genai.Client()
        
        # We use gemini-2.5-flash which is very fast and incredibly cheap, optimizing API credits
        # It natively handles multilingual inputs (like Finnish, Swedish, English) without extra cost
        model_id = "gemini-2.5-flash"
        
        # Upload the file to Gemini's File API for processing
        print("Uploading file to Google servers...")
        uploaded_file = client.files.upload(file=audio_file, config={'display_name': "Meeting Audio"})
        print("File uploaded successfully.")

        # Prepare the prompt instructions
        prompt = (
            "You are an expert AI meeting notetaker taking notes for a meeting."
            "The meeting language might be in Finnish, Swedish, or English, or a mix of them."
            "Please analyze the audio and provide the following:"
            "\n\n1. A full, clean transcription of the meeting (with speaker labels if possible, e.g., Speaker A, Speaker B)."
            "\n\n2. A concise summary of the most important points, decisions made, and action items."
            "\nRespond primarily in the main language that was used during the meeting."
        )

        print("Generating transcription and summary (this may take a minute based on the length)...")
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt, uploaded_file]
        )

        output_file = "meeting_notes.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("\n" + "="*50)
        print("MEETING NOTES GENERATED SUCCESSFULLY!")
        print("="*50)
        print(f"Notes have been saved to '{output_file}'")
        print("="*50 + "\n")
        print(response.text)

        # Cleanup the file from Gemini servers to stay tidy
        client.files.delete(name=uploaded_file.name)
        
    except Exception as e:
        print(f"An error occurred during processing: {e}")

def main():
    print("Welcome to AI Notetaker!")
    filename = "meeting_audio.wav"
    
    audio_file = record_audio(filename)
    if audio_file:
        process_meeting(audio_file)

if __name__ == "__main__":
    main()
