# Backend Project for IEEE-IES-2024

## Initialize Project

### Install MongoDB
1. Download MongoDB at [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Install MongoDB and MongoDB Compass to easily manage database
3. Add New connection to the MongoDB and click connect

![Tux, the Linux mascot](/resources/assets/new_connection.png)

### Install CUDA
1. Downlaod **CUDA 11.8** at [https://developer.nvidia.com/cuda-11-8-0-download-archive](https://developer.nvidia.com/cuda-11-8-0-download-archive)
2. Download version that suitable with the OS

### Initialize .env
1. Create a `.env` file in the root project
2. Initialize `MONGO_URI` environment variables for example
```
MONGO_URI='mongodb://localhost:27017/db_name'
```
3. Initialize `USE_GPU` environment to use **GPU** or **CPU**
```
USE_GPU=True || USE_GPU=False
```

***(Remember to always restart the server if `.env` is changed)***

### Run Project
1. Use Python 3.8 above to run this project
2. Install requirements
```
pip install -r requirements.txt
```

3. Install PyTorch CUDA for CUDA 11.8
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

4. Download TA-Lib Wheel
Download (<b>TA_Lib‑0.4.24‑cp38‑cp38‑win_amd64.whl</b> for 64 bit OR <b>TA_Lib‑0.4.24‑cp38‑cp38‑win32.whl</b> for 32 bit) from <a href=[here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)>here</a> and save it in the project

5. Install TA-Lib
```
pip install TA_Lib‑0.4.24‑cp38‑cp38‑win_amd64.whl
```
6. Run the project
```
python run.py
```

### Hit the API using Postman and Search Engine
1. Download API Postman Collection in this link [(Download API Collection)](https://itsacid-my.sharepoint.com/:u:/g/personal/5025201216_student_its_ac_id/EfNK0F2K16RNqrUknuRfVo8Bo_bygNvbcwuSrUVG_A35ig?e=0oVf3h)
2. Import collection in Postman

![Import Postman Collection](/resources/assets/import_collection.png)

3. Create a new environment
4. Set the `root_url` postman environment variable to where the app is running

![Postman Environment](/resources/assets/postman_env.png)

5. Connect the collection to the new environment

![Postman Collection Environment Connection](/resources/assets/collection_env_connection.png)


- To hit the `/api/session/create`. Use the `create-new-session` request.
- To hit the `/api/session/prompt/create/?session_id={{session_id}}`. Use the `create-cont-prompt` request.
- To hit the `/api/session/download/images?session_id={{session_id}}`. Simply copy the url in a search engine to donwload the image zip file.
- To hit the `/api/session/download/docs?session_id={{session_id}}`. Simply copy the url in a search engine to donwload the document zip file.

## How to Add ML Models
1. Add ML models to a directory corresponds to the model
2. Save the `.pth` model to do ML operation
3. Add new runner class at the model directory

## API Endpoints
1. Create new session with `/api/session/create`
2. Create new prompt with related session id with `/api/session/prompt/create/`
3. Download session result images with `/api/session/download/images`
4. Download session document images with `/api/session/download/docs`

Read the full API documentation at [api.py](/flaskr/api.py)
