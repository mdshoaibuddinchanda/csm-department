# treatments.py
# ─────────────────────────────────────────────────────────────────
# Single source of truth for all dental treatment types and durations.
#
# Slot tiers:
#   SHORT  → 20 min  (Checkup, Tooth pain, Braces/alignment)
#   MEDIUM → 30 min  (Cosmetic, Gum treatment, Missing tooth,
#                     Extraction, Cavity filling)
#   LONG   → 45 min  (Root canal)
#
# Adding a new treatment: just add an entry to TREATMENT_CATALOGUE.
# Everything else (extractor, agent, booking) picks it up automatically.
# ─────────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Treatment:
    key: str            # internal identifier   e.g. "root_canal"
    display_name: str   # shown to patient       e.g. "Root Canal Treatment"
    duration_minutes: int
    slot_tier: str      # SHORT | MEDIUM | LONG  (for display/docs)


# ── Master catalogue ─────────────────────────────────────────────

TREATMENT_CATALOGUE: list[Treatment] = [

    # QUICK – 15 min
    Treatment("dental_checkup",     "Dental Checkup",              15, "QUICK"),

    # SHORT – 20 min
    Treatment("tooth_pain",         "Tooth Pain Consultation",     20, "SHORT"),
    Treatment("braces_alignment",   "Braces / Alignment",          20, "SHORT"),
    Treatment("cavity_filling",     "Cavity Filling",              20, "SHORT"),
    Treatment("tooth_extraction",   "Tooth Extraction / Removal",  30, "SHORT"),

    # MEDIUM – 45 min
    Treatment("cosmetic_dental",    "Cosmetic Dental",             45, "MEDIUM"),
    Treatment("gum_treatment",      "Gum Treatment",               45, "MEDIUM"),

    # LONG – 60 min
    Treatment("missing_tooth",      "Missing Tooth Replacement",   60, "LONG"),
    Treatment("root_canal",         "Root Canal Treatment",        60, "LONG"),
]


# ── Lookup helpers ───────────────────────────────────────────────

_BY_KEY: dict[str, Treatment] = {t.key: t for t in TREATMENT_CATALOGUE}

# Flat alias map → treatment key
# Used by the extractor to map raw patient phrases to a canonical key.
_ALIAS_MAP: dict[str, str] = {
    # dental_checkup
    "checkup":           "dental_checkup",
    "check up":          "dental_checkup",
    "check-up":          "dental_checkup",
    "dental checkup":    "dental_checkup",
    "routine checkup":   "dental_checkup",
    "general checkup":   "dental_checkup",
    "dental exam":       "dental_checkup",

    # tooth_pain
    "tooth pain":        "tooth_pain",
    "toothache":         "tooth_pain",
    "tooth ache":        "tooth_pain",
    "dental pain":       "tooth_pain",
    "pain in tooth":     "tooth_pain",
    "pain in teeth":     "tooth_pain",

    # braces_alignment
    "braces":            "braces_alignment",
    "alignment":         "braces_alignment",
    "braces alignment":  "braces_alignment",
    "orthodontic":       "braces_alignment",
    "teeth alignment":   "braces_alignment",
    "teeth straightening": "braces_alignment",

    # cosmetic_dental
    "cosmetic":          "cosmetic_dental",
    "cosmetic dental":   "cosmetic_dental",
    "teeth whitening":   "cosmetic_dental",
    "whitening":         "cosmetic_dental",
    "veneers":           "cosmetic_dental",
    "smile makeover":    "cosmetic_dental",

    # gum_treatment
    "gum treatment":     "gum_treatment",
    "gum disease":       "gum_treatment",
    "gum infection":     "gum_treatment",
    "periodontitis":     "gum_treatment",
    "gingivitis":        "gum_treatment",
    "gum":               "gum_treatment",

    # missing_tooth
    "missing tooth":     "missing_tooth",
    "missing teeth":     "missing_tooth",
    "implant":           "missing_tooth",
    "dental implant":    "missing_tooth",
    "denture":           "missing_tooth",
    "bridge":            "missing_tooth",
    "tooth replacement": "missing_tooth",

    # tooth_extraction
    "extraction":        "tooth_extraction",
    "tooth extraction":  "tooth_extraction",
    "tooth removal":     "tooth_extraction",
    "remove tooth":      "tooth_extraction",
    "pulled tooth":      "tooth_extraction",
    "wisdom tooth":      "tooth_extraction",
    "wisdom teeth":      "tooth_extraction",

    # cavity_filling
    "filling":           "cavity_filling",
    "cavity":            "cavity_filling",
    "cavity filling":    "cavity_filling",
    "tooth filling":     "cavity_filling",
    "dental filling":    "cavity_filling",
    "composite filling": "cavity_filling",

    # root_canal
    "root canal":        "root_canal",
    "rct":               "root_canal",
    "root canal treatment": "root_canal",
    "endodontic":        "root_canal",
}


def get_treatment_by_key(key: str) -> Optional[Treatment]:
    """Return a Treatment by its canonical key, or None."""
    return _BY_KEY.get(key)


def get_treatment_by_alias(raw_phrase: str) -> Optional[Treatment]:
    """
    Match a raw patient phrase (case-insensitive) to a Treatment.
    Returns None if no match found.
    """
    normalised = raw_phrase.lower().strip()
    key = _ALIAS_MAP.get(normalised)
    if key:
        return _BY_KEY.get(key)

    # Partial match fallback: check if any alias is a substring
    for alias, treatment_key in _ALIAS_MAP.items():
        if alias in normalised:
            return _BY_KEY.get(treatment_key)

    return None


def get_duration_for_treatment(key: str, default_minutes: int = 30) -> int:
    """
    Return duration in minutes for a given treatment key.
    Falls back to default_minutes if key is unknown.
    """
    t = _BY_KEY.get(key)
    return t.duration_minutes if t else default_minutes


def list_treatments_for_display() -> str:
    """
    Returns a clean numbered list of all treatments for chatbot display.
    Each treatment on its own line with duration.
    """
    lines = []
    current_tier = None
    tier_labels = {
        "QUICK":  "⚡ Express",
        "SHORT":  "🕐 Quick Visit",
        "MEDIUM": "🕑 Standard",
        "LONG":   "🕒 Extended",
    }

    for i, t in enumerate(TREATMENT_CATALOGUE, 1):
        if t.slot_tier != current_tier:
            current_tier = t.slot_tier
            lines.append(f"\n{tier_labels[current_tier]} ({t.duration_minutes} min)")
        lines.append(f"  {i}. {t.display_name}")

    return "\n".join(lines)