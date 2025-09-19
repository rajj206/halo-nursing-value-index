import json, random

with open("data/audio_transcripts.json") as f:
    data = json.load(f)

sample = random.sample(data, 1000)   # pick 1000 records

with open("data/sample_transcripts.json", "w", encoding="utf-8") as f:
    json.dump(sample, f, indent=2, ensure_ascii=False)

print("✅ Created sample_transcripts.json with 1000 records")

with open("data/video_transcripts.json") as f:
    data = json.load(f)

sample = random.sample(data, 1000)   # pick 1000 records

with open("data/sample_transcripts_video.json", "w", encoding="utf-8") as f:
    json.dump(sample, f, indent=2, ensure_ascii=False)

print("✅ Created sample_transcripts_video.json with 1000 records")
