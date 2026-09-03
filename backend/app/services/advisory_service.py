from __future__ import annotations

from typing import Dict, List, Optional

from app.core.exceptions import UnsupportedLanguageError
from app.core.logging_config import get_logger
from app.models.schemas import AdvisoryRequest, AdvisoryResponse, SeverityLevel
from app.utils.validation import severity_from_category, severity_from_wind_speed, validate_location

logger = get_logger("services.advisory")


ACTION_LIBRARY: Dict[str, Dict[str, List[str]]] = {
    "English": {
        "LOW": [
            "Monitor official updates from the India Meteorological Department (IMD).",
            "Ensure emergency supplies and important documents are easily accessible.",
            "Review your family disaster preparedness plan.",
        ],
        "MODERATE": [
            "Stay informed via IMD and NDRF advisories.",
            "Secure loose outdoor items and prepare for strong winds.",
            "Keep power backup, drinking water, and dry rations for at least 3 days.",
            "Identify the nearest shelter and evacuation route.",
        ],
        "HIGH": [
            "Follow evacuation orders issued by local authorities immediately.",
            "Move to higher ground if you live in low-lying or coastal areas.",
            "Disconnect electrical appliances and switch off main power before leaving.",
            "Keep mobile phones charged and share your location with family.",
        ],
        "EXTREME": [
            "EVACUATE IMMEDIATELY to the nearest designated cyclone shelter.",
            "Do NOT venture outside during the storm — flying debris can be fatal.",
            "After landfall, avoid fallen wires, damaged buildings, and flooded roads.",
            "Follow instructions from NDRF/State Disaster Management personnel.",
        ],
    },
    "Hindi": {
        "LOW": [
            "भारत मौसम विज्ञान विभाग (IMD) के आधिकारिक अपडेट पर नजर रखें।",
            "आपातकालीन सामान और महत्वपूर्ण दस्तावेज़ सुलभ स्थान पर रखें।",
            "पारिवारिक आपदा प्रबंधन योजना की समीक्षा करें।",
        ],
        "MODERATE": [
            "IMD और NDRF के सलाहकारों के माध्यम से जागरूक रहें।",
            "खुले में रखी सामानों को सुरक्षित करें और तेज़ हवाओं की तैयारी करें।",
            "कम से कम 3 दिनों के लिए बैकअप बिजली, पेयजल और सूखे राशन रखें।",
            "निकटतम आश्रय स्थल और निकासी मार्ग की पहचान करें।",
        ],
        "HIGH": [
            "स्थानीय अधिकारियों द्वारा जारी निकासी आदेशों का तुरंत पालन करें।",
            "यदि आप निचले या तटीय क्षेत्रों में रहते हैं, तो ऊँचे स्थान पर जाएँ।",
            "बिजली के उपकरणों को अनप्लग करें और जाने से पहले मुख्य बिजली बंद करें।",
            "मोबाइल फोन चार्ज रखें और परिवार के साथ अपना स्थान साझा करें।",
        ],
        "EXTREME": [
            "तुरंत निकटतम निर्दिष्ट चक्रवात आश्रय स्थल की ओर निकलें।",
            "तूफान के दौरान बाहर न जाएँ — उड़ते मलबे घातक हो सकते हैं।",
            "लैंडफॉल के बाद गिरे हुए बिजली के तार, क्षतिग्रस्त इमारतों और जलभराव वाली सड़कों से बचें।",
            "NDRF / राज्य आपदा प्रबंधन कर्मियों के निर्देशों का पालन करें।",
        ],
    },
}

MESSAGES: Dict[str, Dict[str, str]] = {
    "English": {
        "LOW": "Low-level cyclone activity detected. Remain alert and follow official weather updates.",
        "MODERATE": "Moderate cyclone conditions expected. Prepare an emergency kit and review your evacuation plan.",
        "HIGH": "Severe cyclone threat. Evacuate if instructed by authorities and follow all official advisories.",
        "EXTREME": "EXTREME CYCLONE THREAT — EVACUATE IMMEDIATELY to the nearest designated shelter.",
    },
    "Hindi": {
        "LOW": "निम्न-स्तर की चक्रवात गतिविधि सूचित हुई है। सतर्क रहें और आधिकारिक मौसम अपडेट का पालन करें।",
        "MODERATE": "मध्यम चक्रवात स्थितियों की संभावना है। आपातकालीन किट तैयार रखें और निकासी योजना की समीक्षा करें।",
        "HIGH": "गंभीर चक्रवात का खतरा। अधिकारियों के निर्देश पर निकासी करें और सभी आधिकारिक सलाहकारों का पालन करें।",
        "EXTREME": "अत्यधिक चक्रवात का खतरा — तुरंत निकटतम निर्दिष्ट आश्रय स्थल की ओर निकलें।",
    },
}

SUPPORTED_LANGUAGES = frozenset(ACTION_LIBRARY.keys())


class AdvisoryService:
    """Generates human-readable, safety-oriented cyclone advisories.

    Language architecture is extensible: add new language entries to
    ACTION_LIBRARY / MESSAGES and register them in SUPPORTED_LANGUAGES.

    Advisories always disclaim against replacing official NDRF/IMD guidance.
    """

    @staticmethod
    def supported_languages() -> List[str]:
        return sorted(SUPPORTED_LANGUAGES)

    @staticmethod
    def _disclaimer(language: str) -> str:
        if language == "Hindi":
            return "यह सलाह केवल सूचनात्मक उद्देश्य के लिए है। आधिकारिक IMD / NDRF / आपदा प्रबंधन दिशा-निर्देशों का पालन करें।"
        return "This advisory is for informational purposes only. Follow official IMD / NDRF / disaster-management instructions."

    def _resolve_severity(self, request: AdvisoryRequest, confidence: Optional[float] = None) -> SeverityLevel:
        conf = float(confidence if confidence is not None else 0.8)
        by_cat = severity_from_category(request.intensity_category, conf)
        by_ws = severity_from_wind_speed(request.wind_speed, conf)
        rank = ["LOW", "MODERATE", "HIGH", "EXTREME"]
        chosen = by_cat if rank.index(by_cat) >= rank.index(by_ws) else by_ws
        return chosen  # type: ignore[return-value]

    def generate(self, request: AdvisoryRequest) -> AdvisoryResponse:
        validate_location(request.location.latitude, request.location.longitude)

        language = (request.language or "English").strip().title()
        if language == "Hindi" or language.lower() in {"hindi", "hi"}:
            language = "Hindi"
        elif language == "English" or language.lower() in {"english", "en"}:
            language = "English"

        if language not in SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(language)

        severity = self._resolve_severity(request, confidence=0.8)
        actions = list(ACTION_LIBRARY[language][severity])
        actions.append(self._disclaimer(language))
        base_message = MESSAGES[language][severity]
        location_note = ""
        if language == "Hindi":
            location_note = (
                f" चक्रवात की स्थिति अक्षांश {request.location.latitude:.2f}, देशांतर {request.location.longitude:.2f} पर "
                f"लगभग {request.wind_speed:.1f} किमी/घंटा हवा की गति के साथ सूचित की गई है।"
            )
        else:
            location_note = (
                f" Cyclone located near lat {request.location.latitude:.2f}, lon {request.location.longitude:.2f} "
                f"with estimated sustained wind speed of {request.wind_speed:.1f} units."
            )
        message = f"{base_message}{location_note}"

        logger.info(
            "Advisory generated cyclone=%s severity=%s language=%s",
            request.cyclone_id,
            severity,
            language,
        )
        return AdvisoryResponse(
            cyclone_id=request.cyclone_id,
            severity=severity,
            language=language,
            message=message,
            recommended_actions=actions,
        )
