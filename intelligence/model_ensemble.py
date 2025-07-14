import numpy as np
from typing import List, Dict, Any

class ModelEnsemble:
    """Generic stacking/ensemble framework for Ghost AI 3.0."""
    def __init__(self, base_models: List[Any], meta_model: Any):
        self.base_models = base_models  # List of sklearn-like models
        self.meta_model = meta_model    # Meta-model (e.g., logistic regression)
        self.is_trained = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Train base models and meta-model."""
        # Train base models
        base_preds = []
        for model in self.base_models:
            model.fit(X, y)
            base_preds.append(model.predict_proba(X)[:, 1])  # Use probability for stacking
        base_preds = np.array(base_preds).T  # shape: (n_samples, n_models)
        # Train meta-model on base model predictions
        self.meta_model.fit(base_preds, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble predictions."""
        if not self.is_trained:
            raise RuntimeError("Ensemble not trained yet.")
        base_preds = []
        for model in self.base_models:
            base_preds.append(model.predict_proba(X)[:, 1])
        base_preds = np.array(base_preds).T
        return self.meta_model.predict(base_preds)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble prediction probabilities."""
        if not self.is_trained:
            raise RuntimeError("Ensemble not trained yet.")
        base_preds = []
        for model in self.base_models:
            base_preds.append(model.predict_proba(X)[:, 1])
        base_preds = np.array(base_preds).T
        return self.meta_model.predict_proba(base_preds)[:, 1]

    def explain(self, X: np.ndarray) -> Dict[str, Any]:
        """Compute SHAP values for the meta-model and return feature importances."""
        try:
            import shap
            # Get base model predictions as features
            base_preds = []
            for model in self.base_models:
                base_preds.append(model.predict_proba(X)[:, 1])
            base_preds = np.array(base_preds).T
            explainer = shap.Explainer(self.meta_model, base_preds)
            shap_values = explainer(base_preds)
            # Return mean absolute SHAP values for each base model
            feature_importances = np.abs(shap_values.values).mean(axis=0)
            return {
                'shap_values': shap_values.values,
                'feature_importances': feature_importances,
                'base_model_names': [type(m).__name__ for m in self.base_models]
            }
        except ImportError:
            print("SHAP is not installed. Run 'pip install shap' to use explainability features.")
            return {}
        except Exception as e:
            print(f"Error computing SHAP values: {e}")
            return {}

# Example usage (to be replaced with actual model objects):
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.linear_model import LogisticRegression
# base_models = [RandomForestClassifier(), ...]
# meta_model = LogisticRegression()
# ensemble = ModelEnsemble(base_models, meta_model)
# ensemble.fit(X_train, y_train)
# preds = ensemble.predict(X_test)
# explanation = ensemble.explain(X_test)
# print(explanation['feature_importances']) 