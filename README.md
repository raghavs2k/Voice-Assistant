# AI Voice Assistant

A modern chatbot interface built with Streamlit that supports both text and voice interactions. The bot responds with both text and voice output.

## Features

- 🎤 Voice input with real-time transcription
- ⌨️ Text input support
- 🔊 Voice output for all bot responses
- 📝 Message history with transcriptions
- 🎨 Modern and clean UI
- 🔄 Clear chat functionality

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Text Input**: Type your message in the text input field and press Enter to send.

2. **Voice Input**: 
   - Click the "🎤 Voice" button
   - Speak your message when prompted
   - The message will be transcribed and sent automatically

3. **Clear Chat**: Click the "Clear Chat" button to reset the conversation.

## Requirements

- Python 3.7+
- Microphone access for voice input
- Internet connection for speech recognition

## Note

The current implementation includes a mock bot response. To integrate with an actual chatbot backend, modify the response logic in the text input and voice input handlers. 