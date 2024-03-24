import time
import math
from flask import send_from_directory

from flaskr.tools.helper import InitSessionHelper, DatasetInfoHelper, DatasetPredHelper, InitPromptHelper, ClassificationHelper, allowed_files, get_session_fig_result_path, get_session_zip_result_path, get_all_fig_objects

from flaskr.tools.enums import ExceptionEnum

from models.iTransformer.main import ModelRunner as iTransformerRunner
from models.Mistral.main import ModelRunner as MistralRunner

from models.Classification.main import ModelRunner as ClassificationRunner

import os

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
            print("Predicting with iTransformer...")
            time_start_iTransformer = time.time()
            iTransformer_runner.run()
            print(f"Predicting done. Time spent {time.time() - time_start_iTransformer}s")

            # Create dataset pred helper
            dataset_pred_helper = DatasetPredHelper(init_session_helper.session_path)

            # Zip results
            init_session_helper.zip_session_files(dataset_info_helper.result_path)

            # Classification
            Classification_runner = ClassificationRunner(
                dataset_pred_helper.preds_res_csv_path
            )

            print("Classifying the results...")
            time_start_classifying = time.time()
            classification_result = Classification_runner.run()
            print(f"Classifying results done. Time spent {time.time() - time_start_classifying}")
            classification_helper = ClassificationHelper(classification_result)

            classification_feat_des = classification_helper.set_classification_feat_des(dataset_info_helper.features_des)          

            # Create init prompt helper
            print("Setting up the prompts...")
            time_start_set_prompt = time.time()
            init_prompt_helper = InitPromptHelper()         
            mistralRunner = MistralRunner()

            # Set mistral prompts
            summary_prompt = init_prompt_helper.set_prompt_summary(dataset_pred_helper.preds_res_csv_path, classification_feat_des)

            curr_state_prompts = init_prompt_helper.set_prompt_curr_states(classification_feat_des)
            pred_state_prompts = init_prompt_helper.set_prompt_pred_states(classification_feat_des)

            mistral_prompts_in = []

            mistral_prompts_in.append(summary_prompt)
            for feature in range(len(classification_feat_des)):
                mistral_prompts_in.append(curr_state_prompts[feature])
                mistral_prompts_in.append(pred_state_prompts[feature])
            print(f"Prompts set. Time spent {time.time() - time_start_set_prompt}")
            
            print("Running Mistral...")
            time_start_mistral = time.time()
            mistral_results, mistral_chat_session = mistralRunner.run(mistral_prompts_in)

            print(f"=== Mistral Results ===")
            print(mistral_results)
            print()
            print()
            
            print(f"=== Mistral Chat session ===")
            print(mistral_chat_session)
            print()
            print()

            print(f"Mistral done. Time spent {time.time() - time_start_mistral}")

            # Mistral results
            summary_result = mistral_results[0]
            init_prompt_helper.set_res_summary(summary_result)

            curr_state_results_temp = []
            pred_state_results_temp = []

            for feature_idx in range(math.ceil(len(classification_feat_des)/2)):
                curr_state_results_temp.append(mistral_results[feature_idx + 1])
                pred_state_results_temp.append(mistral_results[feature_idx + 1 + math.ceil(len(classification_feat_des)/2)])

            curr_state_results_dict = {}
            pred_state_results_dict = {}

            i = 0
            for feature in classification_feat_des:
                curr_state_results_dict[feature] = curr_state_results_temp[i]
                pred_state_results_dict[feature] = pred_state_results_temp[i]
                i += 1

            init_prompt_helper.set_res_curr_states(curr_state_results_dict)
            init_prompt_helper.set_res_pred_states(pred_state_results_dict)            

            # Return result
            result = {
                'session_id': init_session_helper.session_id,
                'document_path': dataset_info_helper.dataset_path,
                'prompts': {
                    'sumarry': init_prompt_helper.get_prompt_summary(),
                    'curr_states': init_prompt_helper.get_prompt_curr_states(),
                    'pred_states': init_prompt_helper.get_prompt_pred_states()
                },
                'results': {
                    'summary': init_prompt_helper.get_res_summary(),
                    'curr_states': init_prompt_helper.get_res_curr_states(),
                    'pred_states': init_prompt_helper.get_res_pred_states()
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