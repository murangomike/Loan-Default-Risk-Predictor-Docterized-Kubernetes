from flask import Flask, request, render_template
import joblib
import pandas as pd

app = Flask(__name__)

# Load your complete pipeline and expected features once on startup
try:
    complete_pipeline = joblib.load('complete_pipeline.joblib')
    expected_features = joblib.load('features.joblib')
    print(f"Model loaded successfully. Expected features: {expected_features}")
except Exception as e:
    print(f"Error loading model: {e}")
    complete_pipeline = None
    expected_features = []

# Define the main input fields for the form
form_fields = [
    'Income', 'Age', 'Experience', 'Married/Single', 'House_Ownership',
    'Car_Ownership', 'Profession', 'CITY', 'STATE', 'CURRENT_JOB_YRS', 'CURRENT_HOUSE_YRS'
]

# Define which fields are numerical
numerical_fields = ['Income', 'Age', 'Experience', 'CURRENT_JOB_YRS', 'CURRENT_HOUSE_YRS']
categorical_fields = ['Married/Single', 'House_Ownership', 'Car_Ownership', 'Profession', 'CITY', 'STATE']

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Check if model is loaded
            if complete_pipeline is None:
                return "Model not loaded properly. Please check server logs.", 500
            
            # Extract inputs from form
            input_data = {}
            for field in form_fields:
                value = request.form.get(field)
                if value is None or value.strip() == '':
                    return f"Missing input: {field}", 400
                
                # Convert numeric fields appropriately
                if field in numerical_fields:
                    try:
                        value = float(value)
                    except ValueError:
                        return f"Invalid numeric input for {field}: {value}", 400
                else:
                    # Keep categorical fields as strings, strip whitespace
                    value = value.strip()
                
                input_data[field] = value
            
            # Create DataFrame for prediction
            input_df = pd.DataFrame([input_data])
            
            # Add missing columns with appropriate default values
            for col in expected_features:
                if col not in input_df.columns:
                    # Add missing columns with default values based on column type
                    if col in categorical_fields:
                        input_df[col] = 'Unknown'  # Default for categorical
                    else:
                        input_df[col] = 0  # Default for numerical
            
            # Reorder columns to match training features
            input_df = input_df[expected_features]
            
            print(f"Input data shape: {input_df.shape}")
            print(f"Input data:\n{input_df}")
            
            # Predict using complete pipeline
            pred = complete_pipeline.predict(input_df)[0]
            prob = complete_pipeline.predict_proba(input_df)[0][1]  # Probability of default (class 1)
            
            # Create result dictionary
            result = {
                'prediction': int(pred),
                'probability': float(prob),
                'risk_level': 'HIGH RISK' if pred == 1 else 'LOW RISK',
                'confidence': float(max(prob, 1-prob)),
                'input_data': input_data
            }
            
            print(f"Prediction result: {result}")
            
            return render_template('result.html', **result)
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return f"Prediction failed: {str(e)}", 500
    
    # GET request - show the form
    return render_template('form.html', fields=form_fields, 
                         numerical_fields=numerical_fields,
                         categorical_fields=categorical_fields)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'model_loaded': complete_pipeline is not None,
        'expected_features_count': len(expected_features),
        'form_fields': form_fields
    }
    return status

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Extract inputs from form
        input_data = {}
        for field in fields:
            value = request.form.get(field)
            if value is None:
                return "Missing input: " + field, 400

            # Convert numeric fields appropriately
            if field in ['Income', 'Age', 'Experience', 'CURRENT_JOB_YRS', 'CURRENT_HOUSE_YRS']:
                try:
                    value = float(value)
                except ValueError:
                    return f"Invalid numeric input for {field}", 400
            input_data[field] = value
        
        # Create DataFrame for prediction
        input_df = pd.DataFrame([input_data])

        # Predict using pipeline
        pred = model.predict(input_df)[0]
        prob = model.predict_proba(input_df)[0][1]

        return render_template('result.html', prediction=pred, probability=prob)

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)