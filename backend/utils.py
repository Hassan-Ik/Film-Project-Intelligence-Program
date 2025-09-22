import re
from typing import List, Tuple, Dict, Any
def extract_character_names(script: str) -> List[str]:
    """Extract character names from screenplay dialogue cues."""
    pattern = r'^\s*([A-Z][A-Z\s]*(?:\s*\(.*?)?\))\s*$'
    names = re.findall(pattern, script, re.MULTILINE)
    return list(dict.fromkeys([name.split('(')[0].strip() for name in names]))

def separate_dialogue_action(script: str) -> Tuple[str, str]:
    """Separate dialogue and action lines in a screenplay."""
    dialogue = []
    action = []
    lines = script.split('\n')
    is_dialogue = False
    for line in lines:
        if re.match(r'^\s*[A-Z][A-Z\s]*(?:\s*\(.*?)?\)\s*$', line):
            is_dialogue = True
            dialogue.append(line)
        elif is_dialogue and line.strip() and not re.match(r'^\s*(INT\.|EXT\.|FADE IN:|FADE OUT\.|CUT TO:)', line):
            dialogue.append(line)
        else:
            is_dialogue = False
            action.append(line)
    return '\n'.join(dialogue), '\n'.join(action)

def chunk_text(text: str, max_length: int = 20000) -> List[str]:
    """Split text into chunks of max_length characters."""
    if len(text) <= max_length:
        return [text]
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


VALENCE_MAP = {
    "joy": 0.9, "love": 0.8, "surprise": 0.3,
    "anger": -0.8, "fear": -0.6, "sadness": -0.9
}
AROUSAL_MAP = {
    "joy": 0.5, "love": 0.4, "surprise": 0.9,
    "anger": 0.8, "fear": 0.7, "sadness": -0.5
}

def valence_arousal(scores: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Calculate valence and arousal scores from emotion model output."""
    valence, arousal = 0.0, 0.0
    for s in scores:
        label = s["label"].lower()
        if label in VALENCE_MAP:
            valence += s["score"] * VALENCE_MAP[label]
            arousal += s["score"] * AROUSAL_MAP[label]
    return int(np.clip(valence * 10, -10, 10)), int(np.clip(arousal * 10, -10, 10))
