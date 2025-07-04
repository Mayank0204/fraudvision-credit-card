import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def load_data(path):
    df = pd.read_csv(path)
    X = df.drop(columns=['Class', 'Time'], errors='ignore')
    y = df['Class']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
    joblib.dump(scaler, scaler_path)

    X_resampled, y_resampled = SMOTE(random_state=42).fit_resample(X_scaled, y)
    return train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
