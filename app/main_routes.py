from flask import request, render_template, send_file
from flask_login import login_required, current_user
import pandas as pd
import io
import json
from src.predict import load_model, load_scaler, make_prediction
from app.db_models import db, PredictionLog

def register_main_routes(app):
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    @app.route("/", methods=["GET", "POST"], endpoint="home")
    @login_required
    def home():
        result = None
        filename = None
        model_type = 'rf'
        mode = 'single'

        if request.method == "POST":
            try:
                model_type = request.form.get('model', 'rf')
                mode = request.form.get('mode', 'single')
                file = request.files.get('file')
                if not file:
                    raise ValueError("No file uploaded.")

                filename = file.filename
                df = pd.read_csv(file)
                df.drop(columns=[col for col in ['Class', 'Time'] if col in df.columns], inplace=True)

                thresholds = {'rf': 45, 'xgb': 42, 'lr': 60, 'voting': 50}
                threshold = thresholds.get(model_type, 50)

                if mode == 'single':
                    if df.shape[0] != 1:
                        raise ValueError("Single mode expects exactly one row.")

                    original_df = df.copy()
                    if model_type == 'lr':
                        df = load_scaler().transform(df)

                    row_data = original_df.iloc[0].tolist()
                    prediction, proba = make_prediction(load_model(model_type), row_data, model_type)
                    fraud_proba = round(proba[1] * 100, 2)

                    status = (
                        "Fraud" if fraud_proba >= threshold else
                        "Uncertain" if fraud_proba >= 40 else
                        "Legit"
                    )

                    result = {
                        'prediction': status,
                        'confidence': round(max(proba) * 100, 2),
                        'fraud_proba': fraud_proba,
                        'model_used': model_type.upper(),
                        'threshold': threshold,
                        'error': None
                    }

                    log = PredictionLog(
                        user_id=current_user.id,
                        input_data=json.dumps(row_data),
                        prediction=status,
                        model_used=model_type.upper()
                    )
                    db.session.add(log)
                    db.session.commit()

                    return render_template(
                        'home.html',
                        result=result,
                        filename=filename,
                        selected_model=model_type,
                        mode=mode
                    )

                elif mode == 'batch':
                    if model_type in ['lr', 'voting']:
                        features = load_scaler().transform(df)
                    else:
                        features = df.values

                    predictions, fraud_probs = [], []

                    for row in features:
                        _, proba = make_prediction(load_model(model_type), row, model_type)
                        prob = round(proba[1] * 100, 2)
                        label = "Fraud" if prob >= threshold else "Uncertain" if prob >= 40 else "Legit"
                        predictions.append(label)
                        fraud_probs.append(prob)

                    df['Prediction'] = predictions
                    df['Fraud_Probability'] = fraud_probs

                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)

                    return send_file(
                        io.BytesIO(csv_buffer.getvalue().encode()),
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name='batch_predictions.csv'
                    )

            except Exception as e:
                result = {
                    'prediction': None,
                    'confidence': None,
                    'fraud_proba': None,
                    'model_used': model_type.upper(),
                    'error': str(e)
                }

        return render_template('home.html', result=result, filename=filename, selected_model=model_type, mode=mode)

    @app.route("/docs")
    def docs():
        return render_template("docs.html")

    @app.route("/tech")
    def tech():
        return render_template("tech.html")

    @app.route("/glossary")
    def glossary():
        return render_template("glossary.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")
