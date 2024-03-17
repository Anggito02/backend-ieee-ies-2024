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

DEFAULT_WARNING_PROMPT = "You are a senior data analyst who specializes in getting data warning insight to warn the user about some issues that might happen in the future. Below is a user's server logs data\n\n__DATASET__ \nThe first 96 rows of this data will be the current data and the next 48 rows of this data will be the prediction data. Please provide warning insight for the following metrices, __FEATURES__. Your goal is to analyze the interrelation of metrics and highlight any concerning patterns or anomalies. Please give the answer in a list format. Please do not ask questions and just do the analysis of the data."

DEFAULT_SOLUTION_PROMPT = "Now, your goal is to get the solution from the warning insight that you gave. The solution should be give in a list format briefly and clearly. Below is the warning insight that you gave already gave before\n\n __WARNING_RES__"

DEFAULT_INSIGHT_PROMPT = "After this warning and solution you gave to the user,  your goal is to get a general insight of the user's data. The insight should be give in a list format briefly and clearly."

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
        self.default_warning_prompt = DEFAULT_WARNING_PROMPT
        self.default_solution_prompt = DEFAULT_SOLUTION_PROMPT
    
        self.prompt_warning = None
        self.prompt_solution = None
        self.prompt_insight = DEFAULT_INSIGHT_PROMPT

        self.res_warning = None
        self.res_solution = None
        self.res_insight = None

    def set_prompt_warning(self, predicted_dataset_path, features_list):
        df = pd.read_csv(predicted_dataset_path)
        predicted_csv = df.to_csv(index=False, header=True, sep=',', line_terminator='\n')

        features = ", ".join(features_list)

        self.prompt_warning = self.default_warning_prompt.replace("__DATASET__", predicted_csv).replace("__FEATURES__", features)

    def get_prompt_warning(self):
        return self.prompt_warning

    def set_prompt_solution(self, warning_res):
        self.prompt_solution = self.default_solution_prompt.replace("__WARNING_RES__", warning_res)

    def get_prompt_solution(self):
        return self.prompt_solution
    
    def get_prompt_insight(self):
        return self.prompt_insight
    
    def set_res_warning(self, warning_res):
        self.res_warning = warning_res

    def get_res_warning(self):
        return self.res_warning
    
    def set_res_solution(self, solution_res):
        self.res_solution = solution_res

    def get_res_solution(self):
        return self.res_solution
    
    def set_res_insight(self, insight_res):
        self.res_insight = insight_res
        
    def get_res_insight(self):
        return self.res_insight


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