import os
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, roc_auc_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def save_model(model, name):
    joblib.dump(model, os.path.join(MODELS_DIR, f'{name}.pkl'))

def load_model(name):
    return joblib.load(os.path.join(MODELS_DIR, f'{name}.pkl'))

def train_model(X_train, y_train, model_type='rf'):
    if model_type == 'rf':
        rf = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced',
            min_samples_leaf=5
        )
        calibrated = CalibratedClassifierCV(rf, method='isotonic', cv=5)
        calibrated.fit(X_train, y_train)
        save_model(calibrated, 'rf')
        return calibrated

    elif model_type == 'xgb':
        xgb = XGBClassifier(
            n_estimators=100,
            use_label_encoder=False,
            eval_metric='logloss',
            scale_pos_weight=10,
            max_depth=5,
            learning_rate=0.1
        )
        calibrated = CalibratedClassifierCV(xgb, method='isotonic', cv=5)
        calibrated.fit(X_train, y_train)
        save_model(calibrated, 'xgb')
        return calibrated

    elif model_type == 'lr':
        lr = LogisticRegression(max_iter=1000, class_weight='balanced')
        lr.fit(X_train, y_train)
        save_model(lr, 'lr')
        return lr

    elif model_type == 'voting':
        rf = load_model('rf')
        xgb = load_model('xgb')
        lr = load_model('lr')
        voting = VotingClassifier(
            estimators=[('rf', rf), ('xgb', xgb), ('lr', lr)],
            voting='soft',
            weights=[1, 1, 3]
        )
        voting.fit(X_train, y_train)
        save_model(voting, 'voting')
        return voting

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    report['AUC'] = auc
    return report
