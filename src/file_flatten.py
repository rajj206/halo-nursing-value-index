import json
import pandas as pd

# ---------- Load the JSON ----------
with open("data/processed_transcripts.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ---------- Convert to DataFrame ----------
df = pd.json_normalize(data)

# ---------- Show as table ----------
print(df.head())

# ---------- Save to CSV (optional) ----------
df.to_csv("data/processed_transcripts_flat.csv", index=False, encoding="utf-8")

print("✅ Flattened JSON saved as processed_transcripts_flat.csv")
