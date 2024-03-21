from flask import send_from_directory

from flaskr.tools.helper import InitSessionHelper, DatasetInfoHelper, DatasetPredHelper, InitPromptHelper, allowed_files, get_session_fig_result_path, get_session_zip_result_path, get_all_fig_objects

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

            # Classification
            ## Run prediction classification
            ## Get warning dan danger features
            ## temp
            ## classification_result = Classification()
            classification_result = {'amount': 0, 'index_features': [], 'label': ""}
            
            classification_feat_des = []
            for i in range(len(classification_result['index_features'])):
                classification_feat_des.append(dataset_info_helper.features_des[classification_result['index_features'][i]])

            # Create init prompt helper
            init_prompt_helper = InitPromptHelper()
            
            # Run Mistral for warning
            warning_prompt = init_prompt_helper.set_prompt_warning(dataset_pred_helper.preds_res_csv_path, classification_feat_des)
            # warning_result = Mistral(warning_prompt)
            warning_result = ""
            init_prompt_helper.set_res_warning(warning_result)

            # Run Mistral for solution
            solution_prompt = init_prompt_helper.set_prompt_solution(warning_result)
            # solution_result = Mistral(solution_prompt)
            solution_result = ""
            init_prompt_helper.set_res_solution(solution_result)

            # Run Mistral for insight
            insight_prompt = init_prompt_helper.get_prompt_insight()
            # insight_result = Mistral(insight_prompt)
            insight_result = ""
            init_prompt_helper.set_res_insight(insight_result)

            # Run Mistral for current and predicted state per feature
            for i in range(len(classification_feat_des)):
                curr_state_prompt = init_prompt_helper.set_prompt_curr_state(classification_feat_des)
                # curr_state_result = Mistral(curr_state_prompt)
                curr_state_result = ""
                init_prompt_helper.set_prompt_curr_state(curr_state_result)

                pred_state_prompt = init_prompt_helper.set_prompt_pred_state(classification_feat_des)
                # pred_state_result = Mistral(pred_state_prompt)
                pred_state_result = ""
                init_prompt_helper.set_prompt_pred_state(pred_state_result)


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
                'classification_result': {
                    'classified_amount': classification_result['amount'],
                    'classified_features': classification_feat_des,
                    'classified_label': classification_result['label']
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
    
    def create_cont_prompt(self, session_id, request):
        try:
            prompt = request.json['prompt']
            # Get Mistral Session Object
            # mistral = Mistral(session_id)

            # Run Mistral
            # result = mistral.run(r)
            result = "This is result from API"
            return result
        except:
            pass
    
    def download_images(self, session_id):
        # Get fig result path
        fig_result_path = get_session_fig_result_path(session_id)

        return get_all_fig_objects(fig_result_path)
    
    def download_docs(self, session_id):
        # Get session result path
        result_zip_path = get_session_zip_result_path(session_id)

        return send_from_directory(result_zip_path, 'doc.zip', as_attachment=True, mimetype='application/zip', download_name='result_documents.zip')