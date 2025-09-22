import azure.cognitiveservices.speech as speechsdk
import json

# Azure Speech config
SPEECH_KEY = ""
SPEECH_REGION = "eastus"
AUDIO_FILE = "52e13b1a-657a-4e12-bd18-f9c85a090c06.wav"

# -------------------------
# Role Mapping Logic
# -------------------------
def identify_role(text: str) -> str:
    t = text.lower()

    # Nurse: instructions, vitals, procedures
    if any(x in t for x in ["let’s check", "time for your", "administer", "oxygen", "blood pressure", "monitor"]):
        return "Nurse"

    # Patient: symptoms, asking for help
    if any(x in t for x in ["i feel", "it hurts", "i’m worried", "please help", "i can’t breathe", "i’m scared"]):
        return "Patient"

    # Doctor: recommending, procedures
    if any(x in t for x in ["surgery", "doctor", "recommend", "mri", "scan", "prescribe"]):
        return "Doctor"

    # Family: relative mentions
    if any(x in t for x in ["my mom", "my dad", "for my brother", "worried about"]):
        return "Family"

    return "Unknown"

# -------------------------
# Transcription with diarization
# -------------------------
def transcribe_with_diarization():
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.AudioConfig(filename=AUDIO_FILE)

    # ConversationTranscriber automatically separates speakers
    transcriber = speechsdk.transcription.ConversationTranscriber(speech_config, audio_config)

    def handle_transcribed(evt):
        text = evt.result.text
        speaker_id = evt.result.speaker_id
        role = identify_role(text)
        print(f"Speaker {speaker_id} ({role}): {text}")

    transcriber.transcribed.connect(handle_transcribed)

    transcriber.start_transcribing_async().get()
    input("Press Enter to stop...\n")
    transcriber.stop_transcribing_async().get()

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    transcribe_with_diarization()



import subprocess
import os

def convert_to_azure_wav(input_path, output_path="converted.wav"):
    """
    Converts audio to 16kHz, 16-bit PCM mono WAV using ffmpeg.
    """
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1",        # mono
        "-ar", "16000",    # 16 kHz
        "-sample_fmt", "s16",  # 16-bit PCM
        output_path
    ]
    subprocess.run(command, check=True)
    return output_path

# Example
if __name__ == "__main__":
    infile = r"C:\Users\rkalepu\OneDrive - Microsoft\Desktop\AI Understanding\udemyKuljotOpenAi\chatCompletionsAPI\data\52e13b1a-657a-4e12-bd18-f9c85a090c06.wav"
    outfile = convert_to_azure_wav(infile)
    print("✅ Converted:", outfile)
