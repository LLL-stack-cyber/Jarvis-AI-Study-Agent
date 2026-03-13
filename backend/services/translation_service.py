from deep_translator import GoogleTranslator


class TranslationService:

    def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate any text into the target language.
        Example languages: 'hi', 'kn', 'fr'
        """

        if target_language == "en":
            return text

        try:
            translated = GoogleTranslator(
                source="auto",
                target=target_language
            ).translate(text)

            return translated

        except Exception:
            return text


    def translate_questions(self, questions: list[dict], target_language: str):

        translated_questions = []

        for q in questions:
            translated = self.translate_text(q["question"], target_language)

            translated_questions.append({
                "number": q["number"],
                "question": translated
            })

        return translated_questions
