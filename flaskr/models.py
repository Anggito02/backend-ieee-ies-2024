from flask import Blueprint

from mongoengine import Document, StringField, DateTimeField, URLField, ReferenceField, BooleanField, IntField, ListField, EnumField, CASCADE

from datetime import datetime
from flaskr.tools.enums import FreqEnum

bp = Blueprint('models_bp', __name__)

class PromptInit(Document):
    prompt_warning = StringField(required=True)
    prompt_solution = StringField(required=True)
    prompt_insight = StringField(required=True)

    warning_created_at = DateTimeField(default=datetime.utcnow)
    solution_created_at = DateTimeField(default=datetime.utcnow)
    insight_created_at = DateTimeField(default=datetime.utcnow)

class PromptResInit(Document):
    res_warning = StringField(required=True)
    res_solution = StringField(required=True)
    res_insight = StringField(required=True)

    warning_created_at = DateTimeField(default=datetime.utcnow)
    solution_created_at = DateTimeField(default=datetime.utcnow)
    insight_created_at = DateTimeField(default=datetime.utcnow)

class DatasetInfo(Document):
    dataset_name = StringField(required=True)
    dataset_url = URLField(required=True)

    features_amount = IntField()
    features_des = ListField(StringField(max_length=20))
    freq = EnumField(FreqEnum, default=FreqEnum.HOURLY)

    created_at = DateTimeField(default=datetime.utcnow)

class DatasetPred(Document):
    pred_dir_url = URLField(required=True)
    pred_res_npy_url = URLField(required=True)
    pred_fig_dir_url = URLField(required=True)

class ChatSession(Document):
    session_id = StringField(required=True, unique=True)
    document_url = URLField(required=True)

    prompts = ReferenceField('PromptInit', reverse_delete_rule=CASCADE)
    results = ReferenceField('PromptResInit', reverse_delete_rule=CASCADE)
    dataset_info = ReferenceField('DatasetInfo', reverse_delete_rule=CASCADE)
    preds = ReferenceField('DatasetPred', reverse_delete_rule=CASCADE)

    is_deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField()
    deleted_at = DateTimeField()

    meta = {
        'indexes': [
            'session_id',
            {'fields': ['created_at'], 'expireAfterSeconds': 3600}
        ]
    }
    
class PromptCont(Document):
    session = ReferenceField(ChatSession, reverse_delete_rule=CASCADE)
    prompt = StringField(required=True)
    res = StringField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)
    res_created_at = DateTimeField(default=datetime.utcnow)
