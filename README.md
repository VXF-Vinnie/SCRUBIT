This is team scrubit, this is a local ai that can be installed into a personal device to go through and scrub all negative social media content to prepare for a professional career. 

IMPORTANT:
To run this, you need to install an Ollama AI model.
link here: https://ollama.com/

## Setup & Running

1. Clone or download this project folder to your machine.
2. Open your terminal inside this project folder and create a local virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. Install the local Python dependencies inside the environment:
   ```bash
   pip install -r requirements.txt
   ```
4. Start up the back-end server:
   '''bash
   uvicorn main:app --reload --port 8000
   '''
5. Start up the front-end server:
   '''bash
   python3 -m http.server 5500
   '''
6. open the local website on a browser, chrome works best for me
   ''' 
   http://0.0.0.0:5000/
   '''
7. Upload your social media archive .zip file and see posts get curated! 
