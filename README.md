# intelligent-data-lake

pip install fastapi uvicorn transformers pandas scikit-learn torch

pip install streamlit requests
pip install dataprep

cd backend
uvicorn main:app --reload

NEW TERMINAL ----
cd frontend
streamlit run app.py
x

-----------Download 10 Gb model into local and use local path
huggingface-cli download tiiuae/falcon-7b-instruct --local-dir ~/models/falcon-7b-instruct

--------------------
OLLAMA

ollama serve &

