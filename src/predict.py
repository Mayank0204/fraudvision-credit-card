import joblib
import numpy as np
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_model_path(name):
    return os.path.join(BASE_DIR, 'models', f'{name}.pkl')

def load_model(model_type):
    path = get_model_path(model_type)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)

def load_scaler():
    path = get_model_path('scaler')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Scaler file not found: {path}")
    return joblib.load(path)

def make_prediction(model, features, model_type):
    features = np.array(features).reshape(1, -1)
    scaler = load_scaler()
    features_scaled = scaler.transform(features)

    if model_type == 'voting':
        models = {
            'rf': load_model('rf'),
            'xgb': load_model('xgb'),
            'lr': load_model('lr')
        }

        weights = {'rf': 0.2, 'xgb': 0.2, 'lr': 0.6}
        final_proba = sum(
            weights[m] * models[m].predict_proba(features_scaled)[0][1]
            for m in models
        )

        prediction = int(final_proba >= 0.5)
        return prediction, [1 - final_proba, final_proba]

    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0]
    return prediction, probability
