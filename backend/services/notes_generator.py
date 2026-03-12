class NotesGenerator:

    def generate_summary(self, topic: str, content: str) -> dict:
        summary = f"Key summary for {topic}: {content[:300]}..."

        key_points = [
            "Understand the core concept",
            "Memorize important formulas",
            "Practice numerical problems"
        ]

        return {
            "topic": topic,
            "summary": summary,
            "key_points": key_points
        }
