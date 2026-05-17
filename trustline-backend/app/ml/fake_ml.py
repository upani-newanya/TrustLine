"""Thin ML wrapper that delegates to injected predictor callables.

Used by the agent pipeline to unify real ML models and test stubs
behind a single interface.
"""


class FakeML:
    """Wraps distress and emotion predictor functions into a unified ML API."""

    def __init__(self, distress_predictor, emotion_predictor):
        self._distress = distress_predictor
        self._emotion = emotion_predictor

    def predict_distress(self, text: str):
        return self._distress(text)

    def predict_emotion(self, text: str):
        return self._emotion(text)
