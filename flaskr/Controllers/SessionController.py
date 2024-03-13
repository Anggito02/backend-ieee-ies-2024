from flaskr.tools.helper import SessionHelper, DatasetInfoHelper,allowed_files
from flaskr.tools.enums import ExceptionEnum

from models.iTransformer.main import ModelRunner as iTransformerRunner

class SessionController:
    def __init__(self):
        pass

    def create_session(self, request):
        try:
            # Validate dataset document
            if 'dataset' not in request.files:
                raise Exception(ExceptionEnum.FAILED_UPLOAD.value)

            dataset = request.files['dataset']
            
            if dataset.filename == '':
                raise Exception(ExceptionEnum.FAILED_UPLOAD.value)
            
            is_file_allowed, extension = allowed_files(dataset.filename)
    
            if not is_file_allowed:
                raise Exception(ExceptionEnum.EXTENSION_NOT_ALLOWED.value)
            
            # Create session helper and id
            session_helper = SessionHelper()

            # Create dataset info helper
            dataset_info_helper = DatasetInfoHelper(session_helper.session_path)

            # Save dataset
            dataset_info_helper.save_document(dataset, extension)

            # Create iTransformer runner
            iTransformer_runner = iTransformerRunner(
                dataset_info_helper.dataset_path,
                dataset_info_helper.result_path,
                dataset_info_helper.freq,
                dataset_info_helper.features_amount
            )

            # Run iTransformer
            return iTransformer_runner.run()

        except Exception as e:
            if (str(e) in [member.value for member in ExceptionEnum]):
                raise e
            else:
                raise Exception
    
    def create_prompt(self, session_id, request):
        return session_id, request