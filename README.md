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
4. Run the analysis pipeline:
   ```bash
   python3 app.py
   ```
