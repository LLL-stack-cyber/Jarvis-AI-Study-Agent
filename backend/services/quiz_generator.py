class QuizGenerator:
    def generate(self, topic: str, difficulty: str = "medium", count: int = 5) -> list[dict]:
        questions: list[dict] = []
        for index in range(1, count + 1):
            options = [
                f"Core concept of {topic}",
                f"Advanced concept of {topic}",
                f"Misconception about {topic}",
                f"Historical fact about {topic}",
            ]
            questions.append(
                {
                    "id": index,
                    "question": f"({difficulty}) Which statement best explains concept {index} in {topic}?",
                    "options": options,
                    "answer": options[0],
                }
            )
        return questions
