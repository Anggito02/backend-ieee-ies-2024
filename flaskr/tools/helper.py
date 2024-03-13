import os
import uuid
import datetime
import polars as pl

class SessionHelper:
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
        self.preds_res_npy_path = os.path.join(self.preds_dir_path, 'preds.npy')
        self.preds_fig_dir_path = os.path.join(self.preds_dir_path, 'fig')

ALLOWED_EXTENSIONS = ['csv', 'xlsx']

def allowed_files(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and extension in ALLOWED_EXTENSIONS, extension