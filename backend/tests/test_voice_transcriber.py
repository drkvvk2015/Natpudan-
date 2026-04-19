from app.services.voice_transcriber import VoiceTranscriber


def test_extract_medical_entities_detects_terms():
    service = VoiceTranscriber()
    text = "Patient has fever and cough, taking aspirin for pain."

    entities = service.extract_medical_entities(text)

    symptom_names = {item["text"] for item in entities["symptoms"]}
    med_names = {item["text"] for item in entities["medications"]}

    assert "fever" in symptom_names
    assert "cough" in symptom_names
    assert "aspirin" in med_names


def test_analyze_sentiment_negative_bias_with_pain_language():
    service = VoiceTranscriber()
    sentiment = service.analyze_sentiment("Severe pain and feeling worse today")
    assert sentiment == "negative"
