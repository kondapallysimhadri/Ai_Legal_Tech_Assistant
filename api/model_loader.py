from src.predict import LegalPredictor

class MLModelLoader:
    def __init__(self):
        self._predictor = None

    @property
    def is_loaded(self):
        return True

    def get_predictor(self):
        if self._predictor is None:
            print("📦 [LAZY LOAD] Loading ML Predictor on first request...")
            from src.predict import LegalPredictor
            self._predictor = LegalPredictor()
        return self._predictor

    def predict_case(self, data_dict: dict):
        predictor = self.get_predictor()
        if not predictor.is_loaded:
            raise RuntimeError("Model is not loaded.")
        return predictor.predict_case(data_dict)

    def predict(self, data_dict: dict):
        predictor = self.get_predictor()
        if not predictor.is_loaded:
            raise RuntimeError("Model is not loaded.")

        res = predictor.predict_case(data_dict)
        return (
            res["prediction"],
            res["confidence"],
            res["explanation"],
            res["success_probability"],
            res,
        )

ml_service = MLModelLoader()
