import os
from src.data_loader import load_data
from src.model import train_model, evaluate_model

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'creditcard.csv')

X_train, X_test, y_train, y_test = load_data(DATA_PATH)

for model_type in ['rf', 'xgb', 'lr']:
    print(f"\n🔧 Training {model_type.upper()} model")
    model = train_model(X_train, y_train, model_type=model_type)
    report = evaluate_model(model, X_test, y_test)

    print(f"\n📊 Evaluation for {model_type.upper()}:")
    for label, metrics in report.items():
        if isinstance(metrics, dict):
            print(f"\nClass {label}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.4f}")
        else:
            print(f"  {label}: {metrics:.4f}")

print("\n🧠 Training Voting Ensemble")
train_model(X_train, y_train, model_type='voting')
