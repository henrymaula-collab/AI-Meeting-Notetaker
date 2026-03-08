# AI-Meeting-Notetaker
Fun hobby project to save costs and replace Notions meeting AI, tried and tested on meetings
# AI Notetaker

A minimal, highly cost-efficient Python application that records your meetings directly from your microphone and utilizes the Google Gemini API to transcribe and summarize the discussion. 

This app is optimized to:
- Be incredibly cheap using `gemini-2.5-flash` API (which excels at long context and audio).
- Automatically understand and process Finnish, Swedish, English, or any mix of the three seamlessly natively in the model avoiding multi-step API taxes.
- Output clean Markdown notes with a full transcription and a summary.

## Prerequisites

1. **Python 3.8+** installed.
2. A **Google Gemini API Key**. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Ensure you have the necessary system dependencies if `sounddevice` prompts for them (usually works out of the box on Mac/Windows).

## Setup Instructions

1. **Clone or open this folder.**
2. **Setup your API Key.**
   - Open the `.env` file.
   - Replace `your_api_key_here` with your actual Gemini API key.
3. **Install Dependencies.**
   Open your terminal in this directory and run:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application:**
   ```bash
   python notetaker.py
   ```
2. **Record:** 
   The app will start recording immediately from your default microphone. Just leave it running while your meeting takes place.
3. **Stop & Process:**
   When the meeting is over, press **Enter** in the terminal. The app will stop recording and immediately upload the audio to the Gemini API.
4. **Get Notes:**
   After a few moments, the application will print the transcription and summary to the screen and save them to a file called `meeting_notes.md`. The temporary audio is saved as `meeting_audio.wav`.

## How it's optimized

- **Model Choice:** By using `gemini-2.5-flash`, the audio processing is extremely fast and costs only fractions of a cent per minute. 
- **Single API Call:** Instead of passing the audio to a Speech-to-Text API and then sending the text to an LLM, this app sends the raw audio directly into Gemini. This single native multimodal call dramatically drastically lowers both cost and latency simultaneously. 
- **Audio Compression:** The script records at 16kHz mono, which is perfectly optimal for voice recognition while keeping the upload size small to save bandwidth.
