import traceback
from flask import Blueprint, jsonify, request

from flaskr.Controllers.SessionController import SessionController

bp = Blueprint('api_bp', __name__)
sessionController = SessionController()

# Session API
@bp.route('/api/session/create', methods=['POST'])
def create_session():
    """API to create new session. Upload the source document to
    predict

    Args:
        request: dataset document

    Raises:
        Exception: Any error occured in the backend

    Returns:
        (json): {
            success: True
            status: 200
            message: "Session created successfully"
            data: {
                session_id: chat's session id
                document_path: document server path
                prompts: {
                    summary: summary prompt
                    curr_states: {
                        {name of feature}: curr prompt, ...
                    }
                    pred_states: {
                        {name of feature}: pred prompt
                    }
                }
                results: {
                    summary: {
                        content: content of summary result
                        role: role of result summary (assistant)
                    }
                    curr_states: {
                        {name of feature}: {
                            content: content of curr state result
                            role: role of result curr state (assistant)
                        }
                    }
                    pred_states: {
                        {name of feature}: {
                            content: content of pred state result
                            role: role of result pred state (assistant)
                        }
                    }
                }
                classification_result: {
                    classified_amount: classified features amount
                    classified_features: classified features description
                    classfied_label: classifier result label
                }
                dataset_info: {
                    dataset_name: dataset name
                    dataset_path: dataset server path
                    features_amount: number of features
                    features_des: list of features description
                    freq: step/frequency of data point
                }
                preds: {
                    preds_dir_path: predictions server path
                    preds_res_npy_path: predictions result npy server path
                    preds_fig_dir_path: predictions figures server path
                }
                created_at: creation time
            }
        }
    """
    try:
        response = sessionController.create_session(request)

        return jsonify({
            'success': True,
            'message': 'Session created successfully',
            'data': response
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({
                'success': False,
                'message': 'An unexpected error occurred',
                'error': str(e)
            }), 500
        

# Promnpt API
@bp.route('/api/session/prompt/create/', methods=['POST'])
def create_cont_prompt():
    """API to upload new prompt to the relevant session

    Args:
        session_id (str): session id

    Raises:
        Exception: Any error occured in the backend

    Returns:
        (json): {
            success: True
            status: 200
            message: "Prompt created successfully"
            data: {
                prompt: prompt
                res: result
                created_at: creation time
            }
        }
    """
    try:
        session_id = request.args.get('session_id') 
        response = sessionController.create_cont_prompt(session_id, request)

        return jsonify({
            'success': True,
            'message': 'Prompt created successfully',
            'data': response
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# Download prediction images API
@bp.route('/api/session/download/images', methods=['GET'])
def download_images():
    """API to download prediction images

    Args:
        session_id (str): session id

    Raises:
        Exception: Any error occured in the backend

    Returns:
        (images): prediction images
    """
    try:
        session_id = request.args.get('session_id')
        response = sessionController.download_images(session_id)
        return jsonify({
                'success': True,
                'message': 'Images sent',
                'data': response
            })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# Download prediction docs API
@bp.route('/api/session/download/docs', methods=['GET'])
def download_docs():
    """API to download prediction docs

    Args:
        session_id (str): session id

    Raises:
        Exception: Any error occured in the backend

    Returns:
        (docs): prediction docs
    """
    try:
        session_id = request.args.get('session_id')
        return sessionController.download_docs(session_id)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
