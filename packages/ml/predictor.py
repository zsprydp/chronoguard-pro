import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb
import logging

logger = logging.getLogger(__name__)


class NoShowPredictor:
    """
    Advanced ML predictor for appointment no-shows using ensemble methods
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.model_path = model_path or "ml/models/no_show_model.pkl"
        
    def extract_features(self, appointment_data: Dict) -> pd.DataFrame:
        """
        Extract features from appointment and patient data
        """
        features = {}
        
        # Patient historical features
        features['patient_no_show_rate'] = appointment_data.get('patient_no_show_rate', 0)
        features['patient_total_appointments'] = appointment_data.get('patient_total_appointments', 0)
        features['patient_cancellation_rate'] = appointment_data.get('patient_cancellation_rate', 0)
        features['days_since_last_appointment'] = appointment_data.get('days_since_last_appointment', 0)
        
        # Appointment timing features
        scheduled_time = pd.to_datetime(appointment_data['scheduled_time'])
        features['hour_of_day'] = scheduled_time.hour
        features['day_of_week'] = scheduled_time.dayofweek
        features['is_monday'] = int(scheduled_time.dayofweek == 0)
        features['is_friday'] = int(scheduled_time.dayofweek == 4)
        features['is_morning'] = int(6 <= scheduled_time.hour < 12)
        features['is_afternoon'] = int(12 <= scheduled_time.hour < 17)
        features['is_evening'] = int(scheduled_time.hour >= 17)
        
        # Booking pattern features
        booked_at = pd.to_datetime(appointment_data.get('booked_at', scheduled_time))
        features['booking_lead_time'] = (scheduled_time - booked_at).days
        features['is_same_day_booking'] = int(features['booking_lead_time'] == 0)
        features['is_advance_booking'] = int(features['booking_lead_time'] > 7)
        
        # Appointment type features
        appointment_type = appointment_data.get('appointment_type', 'consultation')
        features['is_consultation'] = int(appointment_type == 'consultation')
        features['is_follow_up'] = int(appointment_type == 'follow_up')
        features['is_procedure'] = int(appointment_type == 'procedure')
        features['appointment_duration'] = appointment_data.get('duration_minutes', 30)
        
        # Provider features
        features['provider_no_show_rate'] = appointment_data.get('provider_no_show_rate', 0.1)
        features['provider_avg_satisfaction'] = appointment_data.get('provider_avg_satisfaction', 4.0)
        
        # Insurance and demographic features
        features['has_insurance'] = int(bool(appointment_data.get('insurance_provider')))
        features['age'] = appointment_data.get('patient_age', 40)
        features['is_senior'] = int(features['age'] >= 65)
        features['is_young_adult'] = int(18 <= features['age'] <= 30)
        
        # Communication features
        features['prefers_sms'] = int(appointment_data.get('preferred_contact') == 'sms')
        features['prefers_email'] = int(appointment_data.get('preferred_contact') == 'email')
        features['reminder_sent'] = int(appointment_data.get('reminder_sent', False))
        
        # External factors
        features['is_holiday_week'] = int(appointment_data.get('is_holiday_week', False))
        features['weather_severity'] = appointment_data.get('weather_severity', 0)  # 0-5 scale
        
        # Practice-level features
        features['practice_no_show_rate'] = appointment_data.get('practice_no_show_rate', 0.15)
        features['practice_size'] = appointment_data.get('practice_size', 5)  # Number of providers
        
        return pd.DataFrame([features])
    
    def train_model(self, training_data: pd.DataFrame, labels: pd.Series):
        """
        Train the ensemble model with XGBoost as the primary classifier
        """
        logger.info(f"Training model with {len(training_data)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            training_data, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            scale_pos_weight=3  # Handle class imbalance
        )
        
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Store feature columns
        self.feature_columns = training_data.columns.tolist()
        
        # Calculate accuracy
        accuracy = self.model.score(X_test_scaled, y_test)
        logger.info(f"Model accuracy: {accuracy:.3f}")
        
        # Save model
        self.save_model()
        
        return accuracy
    
    def predict(self, appointment_data: Dict) -> Tuple[float, Dict]:
        """
        Predict no-show probability for a single appointment
        """
        if self.model is None:
            self.load_model()
        
        # Extract features
        features = self.extract_features(appointment_data)
        
        # Ensure columns match training
        features = features[self.feature_columns]
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get prediction probability
        no_show_prob = self.model.predict_proba(features_scaled)[0][1]
        
        # Get feature importance for explanation
        feature_importance = self.get_feature_importance(features)
        
        # Determine risk level
        risk_level = self._calculate_risk_level(no_show_prob)
        
        return no_show_prob, {
            'risk_level': risk_level,
            'top_factors': feature_importance[:5],
            'probability': float(no_show_prob)
        }
    
    def batch_predict(self, appointments: List[Dict]) -> List[Tuple[float, Dict]]:
        """
        Predict no-show probabilities for multiple appointments
        """
        predictions = []
        for appointment in appointments:
            pred = self.predict(appointment)
            predictions.append(pred)
        return predictions
    
    def get_feature_importance(self, features: pd.DataFrame) -> List[Tuple[str, float]]:
        """
        Get feature importance for explainability
        """
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_imp = list(zip(self.feature_columns, importances))
            feature_imp.sort(key=lambda x: x[1], reverse=True)
            
            # Calculate actual impact on this prediction
            scaled_features = self.scaler.transform(features).flatten()
            impact_scores = []
            
            for feat_name, importance in feature_imp:
                idx = self.feature_columns.index(feat_name)
                actual_value = scaled_features[idx]
                impact = importance * abs(actual_value)
                impact_scores.append((feat_name, impact))
            
            impact_scores.sort(key=lambda x: x[1], reverse=True)
            return impact_scores
        
        return []
    
    def _calculate_risk_level(self, probability: float) -> str:
        """
        Convert probability to risk level
        """
        if probability < 0.15:
            return "low"
        elif probability < 0.35:
            return "medium"
        else:
            return "high"
    
    def save_model(self):
        """
        Save model and scaler to disk
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """
        Load model from disk
        """
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            logger.info("Model loaded successfully")
        except FileNotFoundError:
            logger.warning("No saved model found, initializing new model")
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """
        Initialize a default model with synthetic data
        """
        # Create synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        synthetic_data = []
        labels = []
        
        for _ in range(n_samples):
            # Generate random appointment data
            appointment = {
                'scheduled_time': datetime.now() + timedelta(days=np.random.randint(1, 30)),
                'patient_no_show_rate': np.random.random() * 0.5,
                'patient_total_appointments': np.random.randint(1, 50),
                'patient_cancellation_rate': np.random.random() * 0.3,
                'days_since_last_appointment': np.random.randint(0, 180),
                'appointment_type': np.random.choice(['consultation', 'follow_up', 'procedure']),
                'duration_minutes': np.random.choice([15, 30, 45, 60]),
                'provider_no_show_rate': np.random.random() * 0.2,
                'provider_avg_satisfaction': 3 + np.random.random() * 2,
                'patient_age': np.random.randint(18, 80),
                'insurance_provider': np.random.choice(['', 'BlueCross', 'Aetna', 'United']),
                'preferred_contact': np.random.choice(['phone', 'sms', 'email']),
                'practice_no_show_rate': 0.1 + np.random.random() * 0.2,
                'practice_size': np.random.randint(2, 10)
            }
            
            features = self.extract_features(appointment)
            synthetic_data.append(features.iloc[0])
            
            # Generate label based on features (with some noise)
            no_show_prob = appointment['patient_no_show_rate'] * 0.5 + np.random.random() * 0.3
            labels.append(int(no_show_prob > 0.3))
        
        # Train on synthetic data
        training_df = pd.DataFrame(synthetic_data)
        self.train_model(training_df, pd.Series(labels))