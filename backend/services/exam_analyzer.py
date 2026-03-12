class ExamAnalyzer:
    def analyze(self, topic: str, score: float, weak_areas: list[str]) -> dict:
        if score >= 85:
            readiness = "high"
        elif score >= 65:
            readiness = "medium"
        else:
            readiness = "low"

        recommendations = [f"Review your {topic} summary notes daily for 20 minutes."]
        recommendations.extend([f"Solve 10 extra questions in: {area}." for area in weak_areas])
        if score < 65:
            recommendations.append("Use spaced repetition flashcards for weak concepts.")

        return {
            "topic": topic,
            "score": score,
            "readiness": readiness,
            "weak_areas": weak_areas,
            "recommendations": recommendations,
        }
