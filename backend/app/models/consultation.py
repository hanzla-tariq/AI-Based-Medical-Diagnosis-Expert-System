import json
from datetime import datetime
from ..extensions import db


class Consultation(db.Model):
    """Consultation model for storing diagnosis records."""
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Patient details
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    medical_history = db.Column(db.Text, nullable=True, default='')

    # Symptom details
    symptoms = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)

    # Diagnosis mode
    mode = db.Column(db.String(20), nullable=False)  # 'form' or 'chatbot'
    chat_log = db.Column(db.Text, nullable=True)  # JSON string for chatbot conversations

    # AI Analysis results
    ai_analysis = db.Column(db.Text, nullable=True)
    medication_recs = db.Column(db.Text, nullable=True)
    food_recs = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def set_chat_log(self, chat_messages):
        """Store chat log as JSON string."""
        self.chat_log = json.dumps(chat_messages)

    def get_chat_log(self):
        """Retrieve chat log as list."""
        if self.chat_log:
            return json.loads(self.chat_log)
        return []

    def to_dict(self):
        """Serialize consultation to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'age': self.age,
            'gender': self.gender,
            'medical_history': self.medical_history,
            'symptoms': self.symptoms,
            'duration': self.duration,
            'severity': self.severity,
            'mode': self.mode,
            'ai_analysis': self.ai_analysis,
            'medication_recs': self.medication_recs,
            'food_recs': self.food_recs,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Consultation {self.id} - User {self.user_id}>'
