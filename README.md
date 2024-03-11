# Backend Project for IEEE-IES-2024

## Initialize Project
1. Use Python 3.8 above to run this project
2. Install requirements
```
bash pip install -r requirements.txt
```

3. Run the project
```
python run.py
```

## Add ML Models
1. Add ML models to a directory corresponds to the model
2. Save the `.pth` model to do ML operation
3. Add new runner class at the model directory

## API Endpoints
1. Create new session with `/api/session/create`
2. Create new prompt with related session id with `/api/session/prompt/create/<session_id>`

Read the full API documentation at [api.py](./flaskr/api.py)