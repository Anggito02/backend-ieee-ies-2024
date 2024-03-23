import os
import io
import uuid
import datetime
import polars as pl
import pandas as pd
import zipfile

from PIL import Image
from base64 import encodebytes

from flask import send_from_directory

ALLOWED_EXTENSIONS = ['csv', 'xlsx']

DEFAULT_INIT_PROMPT_SUMMARY = "You are a senior data analyst who specializes in getting data warning and solution insight to warn the user about some issues that might happen in the future. Below is a user's server logs data\n\n__DATASET__ \nThe first 48 rows of this data will be the current data and the next 48 rows of this data will be the prediction data. Please provide warning and solution insight for the following metrices, __FEATURES__. Your goal is to analyze the interrelation of metrics and highlight any concerning patterns or anomalies and the solution to the warning. Please give the answer in a list format. Please do not ask questions and just do the analysis of the data."

DEFAULT_CURRENT_STATE_PROMPT = "Now, your goal is to get the current state insight of the user's data (first 48 rows of the data) for __FEATURE__ metric. Insights should be given in one brief paragraph."

DEFAULT_PREDICTED_STATE_PROMPT = "Then, now your goal is to get the predicted state of the user's data (last 48 rows of the data) for __FEATURE__ metric. Insights should be given in one brief paragraph."

class InitSessionHelper:
    def __init__(self):
        self.session_id = self.create_session_id()
        self.session_path = self.create_session_dir()
        self.created_at = datetime.datetime.now()

    def get_session_id(self):
        return self.session_id
    
    def get_session_path(self):
        return self.session_path
    
    def create_session_id(self) -> str:
        try:
            self.session_id = str(uuid.uuid4())
            return self.session_id
        except:
            raise Exception('Failed to create session id')
    
    def create_session_dir(self) -> str:
        try:
            session_path = os.path.join('resources', 'public', self.session_id)

            if not os.path.exists(session_path):
                os.makedirs(session_path)
                os.makedirs(os.path.join(session_path, 'input'))
                os.makedirs(os.path.join(session_path, 'results'))

            self.session_path = session_path
            return session_path
        except:
            raise Exception('Failed to create session directory')
        
    def zip_session_files(self, result_dir_path):
        try:
            if not os.path.exists(os.path.join(result_dir_path, 'zipped')):
                os.makedirs(os.path.join(result_dir_path, 'zipped'))

            zip_dir_path = os.path.join(result_dir_path, 'zipped')

            # Zip documents
            with zipfile.ZipFile(os.path.join(zip_dir_path, 'doc.zip'), 'w') as zip:
                for root, dirs, files in os.walk(result_dir_path):
                    for file in files:
                        if file.split('.')[-1] in ALLOWED_EXTENSIONS:
                            zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), result_dir_path))
        except:
            raise Exception('Failed to zip session files')
            

class DatasetInfoHelper:
    def __init__(self, session_path):
        self.session_path = session_path
        self.dataset_name = None
        self.dataset_path = None
        self.result_path = None
        self.features_amount = None
        self.features_des = []
        self.freq = None

    def save_document(self, document, extension) -> bool:
        try:
            self.dataset_name = document.filename
            self.dataset_path = os.path.join(self.session_path, 'input')
            self.result_path = os.path.join(self.session_path, 'results')
            document.save(os.path.join(self.dataset_path, f'dataset.{extension}'))

            if extension == 'xlsx':
                df = pl.read_excel(os.path.join(self.dataset_path, f'dataset.xlsx'))
                df.write_csv(os.path.join(self.dataset_path, 'dataset.csv'))

            self.get_document_info()

        except Exception:
            raise Exception
        
    def get_document_info(self):
        try:
            df = pl.read_csv(os.path.join(self.dataset_path, 'dataset.csv'))
            self.features_des = list(df.columns[1:])
            self.features_amount = len(self.features_des)
            self.freq = 'h'
        except:
            raise Exception

    
class DatasetPredHelper:
    def __init__(self, session_path):
        self.session_path = session_path
        self.preds_dir_path = os.path.join(self.session_path, 'results')
        self.preds_res_doc_path = os.path.join(self.preds_dir_path, 'preds.xlsx')
        self.preds_res_csv_path = os.path.join(self.preds_dir_path, 'preds.csv')
        self.preds_res_npy_path = os.path.join(self.preds_dir_path, 'preds.npy')
        self.preds_fig_dir_path = os.path.join(self.preds_dir_path, 'fig')

class InitPromptHelper:
    def __init__(self):    
        self.prompt_summary = DEFAULT_INIT_PROMPT_SUMMARY

        self.prompt_curr_states = {}
        self.prompt_pred_states = {}

        self.result_summary = ""

        self.res_curr_states = {}
        self.res_pred_states = {}

    def set_prompt_summary(self, predicted_dataset_path, features_list):
        df = pd.read_csv(predicted_dataset_path)
        predicted_csv = df.to_csv(index=False, header=True, sep=',', line_terminator='\n')

        features = ", ".join(features_list)

        self.prompt_summary = self.prompt_summary.replace("__DATASET__", predicted_csv).replace("__FEATURES__", features)

        return self.prompt_summary

    def get_prompt_summary(self):
        return self.prompt_summary

    def set_res_summary(self, summary_res):
        self.result_summary = summary_res
        
    def get_res_summary(self):
        return self.result_summary
    
    def set_prompt_curr_states(self, features):
        for feature in range(len(features)):
            self.prompt_curr_states[feature] = DEFAULT_CURRENT_STATE_PROMPT.replace("__FEATURE__", features[feature])

        return self.prompt_curr_states
    
    def get_prompt_curr_states(self):
        return self.prompt_curr_states

    def set_prompt_pred_states(self, features):
        for feature in range(len(features)):
            self.prompt_pred_states[feature] = DEFAULT_PREDICTED_STATE_PROMPT.replace("__FEATURE__", features[feature])

        return self.prompt_pred_states
    
    def get_prompt_pred_states(self):
        return self.prompt_pred_states
    
    def set_res_curr_states(self, curr_states):
        for feature_result in curr_states:
            self.res_curr_states[feature_result] = curr_states[feature_result]

        return self.res_curr_states

    def get_res_curr_states(self):
        return self.res_curr_states
    
    def set_res_pred_states(self, pred_states):
        for feature_result in pred_states:
            self.res_pred_states[feature_result] = pred_states[feature_result]

        return self.res_pred_states

    def get_res_pred_states(self):
        return self.res_pred_states

class ClassificationHelper:
    def __init__(self, classification_result) -> None:
        self.classification_result = classification_result
        self.classification_amount = self.classification_result['amount']
        self.classification_index_features = self.classification_result['index_features']
        self.classification_label = self.classification_result['label']
        self.classification_feat_des = []

    def set_classification_feat_des(self, dataset_feature_des):
        for idx in self.classification_index_features:
            self.classification_feat_des.append(dataset_feature_des[self.classification_result[idx]])
        
        return self.classification_feat_des
    

def allowed_files(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and extension in ALLOWED_EXTENSIONS, extension

def get_session_zip_result_path(session_id):
    return os.path.join(os.getcwd(), 'resources', 'public', session_id, 'results', 'zipped')

def get_session_fig_result_path(session_id):
    return os.path.join(os.getcwd(), 'resources', 'public', session_id, 'results', 'fig')

def get_session_result_path(session_id):
    return os.path.join(os.getcwd(), 'resources', 'public', session_id, 'results')

def get_all_fig_objects(fig_result_path):
    imgs = []

    for img in os.listdir(fig_result_path):
        pil_img = Image.open(os.path.join(fig_result_path, img), 'r')
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        img_str = encodebytes(buffered.getvalue()).decode("utf-8")
        imgs.append(img_str)
    
    return imgs