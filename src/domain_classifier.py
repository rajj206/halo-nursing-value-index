import json
import re
import difflib
from openai import OpenAI

endpoint = "https://demorkalepuopenai.openai.azure.com/openai/v1/"
model_name = "gpt-5-mini"
deployment_name = "nvi-domain-classifier"

api_key = ""

client = OpenAI(
    base_url=f"{endpoint}",
    api_key=api_key
)

# ---------- DOMAINS ----------
DOMAINS = [
    "Safe healing environments",
    "Caring relationships",
    "Symptom assessment/management",
    "Therapeutic/physical care",
    "Surveillance/intervention",
    "Patient/family teaching",
    "Interprofessional collaboration",
    "Advocacy",
    "Transitions in care",
    # --- Extra Caring Domains ---
    "Emotional healing & support",
    "Personalized/individual caring",
    "Spiritual & cultural support",
    "Companionship & presence",
    "Holistic well-being",
    "Dignity & respect"
]

# ---------- Keyword Map for fallback ----------
KEYWORD_MAP = [
    (re.compile(r"\b(hand( ?washing)?|clean|sanitize|quiet|safe|fall|call button)\b", re.I),
     "Safe healing environments"),
    (re.compile(r"\b(reassur|empathy|listen|relationship|courtesy|respect)\b", re.I),
     "Caring relationships"),
    (re.compile(r"\b(pain|hurts|dizzy|nausea|symptom|breath|shortness)\b", re.I),
     "Symptom assessment/management"),
    (re.compile(r"\b(ambulat|medicat|iv|dressing|injection|wound|spirometer|mobility)\b", re.I),
     "Therapeutic/physical care"),
    (re.compile(r"\b(oxygen|saturation|o2|monitor|escalate|rapid response|rescue|intervene)\b", re.I),
     "Surveillance/intervention"),
    (re.compile(r"\b(teach|educat|explain|show|demonstrate|instructions|discharge education)\b", re.I),
     "Patient/family teaching"),
    (re.compile(r"\b(huddle|team|surgeon|physio|dietitian|interdisciplinary|coordination)\b", re.I),
     "Interprofessional collaboration"),
    (re.compile(r"\b(advocat|not ready|preference|rights|speak up|request delay|appeal)\b", re.I),
     "Advocacy"),
    (re.compile(r"\b(discharge|transition|follow[- ]?up|home care|appointments|handoff)\b", re.I),
     "Transitions in care"),
    # --- New Caring Domains ---
    (re.compile(r"\b(anxious|worry|fear|sad|cry|comfort|encourag|emotional support|stress)\b", re.I),
     "Emotional healing & support"),
    (re.compile(r"\b(preference|choice|routine|custom|personal comfort|tailor)\b", re.I),
     "Personalized/individual caring"),
    (re.compile(r"\b(spiritual|prayer|belief|religion|ritual|faith|cultural)\b", re.I),
     "Spiritual & cultural support"),
    (re.compile(r"\b(companion|presence|sit with|talk with|lonely|not alone)\b", re.I),
     "Companionship & presence"),
    (re.compile(r"\b(holistic|mind[- ]?body|wellness|meditation|relaxation|breathing exercise)\b", re.I),
     "Holistic well-being"),
    (re.compile(r"\b(dignity|privacy|respect|self[- ]?esteem)\b", re.I),
     "Dignity & respect")
]

# ---------- Helpers ----------
def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()

def _fallback_keywords(text: str) -> str:
    for pattern, domain in KEYWORD_MAP:
        if pattern.search(text):
            return domain
    return "General nursing care"

def _closest_domain(label: str) -> str:
    matches = difflib.get_close_matches(label, DOMAINS, n=1, cutoff=0.5)
    return matches[0] if matches else ""

# ---------- AI Classifier ----------
def classify_record(text: str, action: str | None = None) -> dict:
    """Send transcript to Azure OpenAI and classify Domain + Intent + Emotion."""
    joined = text if not action else f"Action: {action}\nUtterance: {text}"

    messageslist = [
        {
            "role": "system",
            "content": (
                "You are an advanced AI classifier analyzing healthcare interactions. "
                "Input may contain:\n"
                " - AUDIO (spoken text: nurse, patient, doctor, family, staff)\n"
                " - VIDEO (observed actions: e.g., nurse adjusting IV, patient grimacing)\n\n"

                "Your task: Classify each record into exactly ONE domain, ONE intent, and ONE emotion.\n\n"

                "===========================\n"
                " DOMAINS\n"
                "===========================\n"
                + "\n".join([f"- {d}" for d in DOMAINS]) + "\n\n"

                "===========================\n"
                " INTENT RULES\n"
                "===========================\n"
                "- question → if the speaker is asking something\n"
                "- instruction → if it gives guidance, advice, or commands\n"
                "- statement → if it is descriptive, neutral, or informative\n\n"

                "===========================\n"
                " EMOTION RULES\n"
                "===========================\n"
                "- distress → if words/actions show pain, fear, anxiety, worry\n"
                "- positive → if words/actions show gratitude, smile, relief\n"
                "- neutral → if clinical or informational without strong emotion\n\n"

                "===========================\n"
                " OUTPUT FORMAT\n"
                "===========================\n"
                "Return STRICT JSON:\n"
                "{\n"
                "  \"domain\": \"<one domain>\",\n"
                "  \"intent\": \"<question|instruction|statement>\",\n"
                "  \"emotion\": \"<distress|positive|neutral>\"\n"
                "}\n\n"

                "===========================\n"
                " EXAMPLES\n"
                "===========================\n"
                "Utterance: 'Time for your painkiller, I’ll administer it via injection.'\n"
                "→ {\"domain\": \"Therapeutic/physical care\", \"intent\": \"statement\", \"emotion\": \"neutral\"}\n\n"

                "Utterance: 'Can you explain how I should use this inhaler?'\n"
                "→ {\"domain\": \"Patient/family teaching\", \"intent\": \"question\", \"emotion\": \"distress\"}\n\n"

                "Action: 'Nurse demonstrates wound dressing change while explaining steps.'\n"
                "→ {\"domain\": \"Patient/family teaching\", \"intent\": \"instruction\", \"emotion\": \"neutral\"}\n"
            )
        },
        {"role": "user", "content": joined}
    ]

    try:
        resp = client.chat.completions.create(
            model=deployment_name,
            messages=messageslist
        )
        raw = (resp.choices[0].message.content or "").strip()
        cleaned = _strip_code_fences(raw)

        parsed = json.loads(cleaned)
        domain = parsed.get("domain", "").strip()
        intent = parsed.get("intent", "").strip()
        emotion = parsed.get("emotion", "").strip()

        # Validate & fallback if needed
        if domain not in DOMAINS:
            domain = _closest_domain(domain)
        if not domain:
            domain = _fallback_keywords(joined)
        if not domain:
            domain = "Symptom assessment/management"

        if intent not in ["question", "instruction", "statement"]:
            intent = "statement"
        if emotion not in ["distress", "positive", "neutral"]:
            emotion = "neutral"

        return {"domain": domain, "intent": intent, "emotion": emotion}

    except Exception as e:
        # Hard fallback if API fails
        return {
            "domain": _fallback_keywords(joined),
            "intent": "statement",
            "emotion": "neutral",
            "error": str(e)
        }

# ---------- MAIN ----------
INPUT_AUDIO = "data/sample_transcripts.json"
INPUT_VIDEO = "data/sample_transcripts_video.json"
OUTPUT = "data/processed_all.json"

processed = []

# --- Process audio transcripts ---
with open(INPUT_AUDIO, "r", encoding="utf-8") as f:
    records_audio = json.load(f)

for rec in records_audio[:200]:  # subset for demo
    result = classify_record(rec.get("text", ""), rec.get("action"))
    rec.update(result)
    rec["source"] = "audio"
    processed.append(rec)

# --- Process video transcripts ---
with open(INPUT_VIDEO, "r", encoding="utf-8") as f:
    records_video = json.load(f)

for rec in records_video[:200]:
    result = classify_record(rec.get("text", ""), rec.get("action"))
    rec.update(result)
    rec["source"] = "video"
    processed.append(rec)

# --- Save combined file ---
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(processed, f, indent=2, ensure_ascii=False)

print(f"✅ Saved processed {len(processed)} transcripts → {OUTPUT}")