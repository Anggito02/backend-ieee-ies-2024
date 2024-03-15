from flask import send_from_directory

from flaskr.tools.helper import InitSessionHelper, DatasetInfoHelper, DatasetPredHelper, InitPromptHelper, allowed_files, get_session_zip_result_path

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
            init_session_helper = InitSessionHelper()

            # Create dataset info helper
            dataset_info_helper = DatasetInfoHelper(init_session_helper.session_path)

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
            iTransformer_runner.run()

            # Create dataset pred helper
            dataset_pred_helper = DatasetPredHelper(init_session_helper.session_path)

            # Zip results
            init_session_helper.zip_session_files(dataset_info_helper.result_path)

            # Create init prompt helper
            init_prompt_helper = InitPromptHelper()
            
            init_prompt_helper.set_prompt_warning(dataset_pred_helper.preds_res_csv_path, dataset_info_helper.features_des)

            # Run Mistral for warning

            # Run Mistral for solution
            init_prompt_helper.set_prompt_solution("__WARNING_RES__")

            # Run Mistral for insight

            # Return result
            result = {
                'session_id': init_session_helper.session_id,
                'document_path': dataset_info_helper.dataset_path,
                'prompts': {
                    'warning': init_prompt_helper.prompt_warning,
                    'solution': init_prompt_helper.prompt_solution,
                    'insight': init_prompt_helper.prompt_insight
                },
                'results': {
                    'warning': init_prompt_helper.res_warning,
                    'solution': init_prompt_helper.res_solution,
                    'insight': init_prompt_helper.res_insight
                },
                'dataset_info': {
                    'dataset_name': dataset_info_helper.dataset_name,
                    'dataset_path': dataset_info_helper.dataset_path,
                    'features_amount': dataset_info_helper.features_amount,
                    'features_des': dataset_info_helper.features_des,
                    'freq': dataset_info_helper.freq,
                },
                'preds': {
                    'preds_dir_path': dataset_pred_helper.preds_dir_path,
                    'preds_res_npy_path': dataset_pred_helper.preds_res_npy_path,
                    'preds_fig_dir_path': dataset_pred_helper.preds_fig_dir_path
                },
                'created_at': init_session_helper.created_at
            }

            return result

        except Exception as e:
            if (str(e) in [member.value for member in ExceptionEnum]):
                raise e
            else:
                raise Exception
    
    def create_prompt(self, session_id, request):
        return session_id, request
    
    def download_images(self, session_id):
        # Get session result path
        result_zip_path = get_session_zip_result_path(session_id)

        return send_from_directory(result_zip_path, 'fig.zip', as_attachment=True, mimetype='application/zip', download_name='result_images.zip')

    def download_docs(self, session_id):
        # Get session result path
        result_zip_path = get_session_zip_result_path(session_id)

        return send_from_directory(result_zip_path, 'doc.zip', as_attachment=True, mimetype='application/zip', download_name='result_documents.zip')