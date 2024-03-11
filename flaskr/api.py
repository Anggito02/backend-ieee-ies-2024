from flask import Blueprint, current_app, jsonify

from .Controllers.SessionController import SessionController

bp = Blueprint('api_bp', __name__)
sessionController = SessionController()

# Session API
@bp.route('/api/session/create', methods=['POST'])
def create_session(request):
    """Method to create new session. Upload the source document to
    predict

    Args:
        request (json): json object containing uploaded document info

    Raises:
        Exception: Any error occured in the backend

    Returns:
        (json): {
            success: True
            status: 200
            message: "Session created successfully"
            data: {
                session_id: chat's session id
                document_url: document server url
                prompts: list of initial prompts [warning, solution, insight]
                results: list of initial results [warning, solution, insight]
                dataset_info: {
                    dataset_name: dataset name
                    dataset_url: dataset server url
                    features_amount: number of features
                    features_des: list of features description
                    freq: step/frequency of data point
                }
                preds: {
                    preds_dir_url: predictions server url
                    preds_res_npy_url: predictions result npy server url
                    preds_fig_dir_url: predictions figures server url
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
        return jsonify({'error': str(e)}), 500
        

# Promnpt API
@bp.route('/api/session/prompt/<session_id>', methods=['POST'])
def create_prompt(session_id, request):
    """Method to upload new prompt to the relevant session

    Args:
        session_id (str): session id
        request (json): json object containing user prompt

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
        response = sessionController.create_prompt(session_id, request)

        return jsonify({
            'success': True,
            'message': 'Prompt created successfully',
            'data': response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500