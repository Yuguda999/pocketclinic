# PocketClinic

A simple AI healthcare assistant designed to help healthcare workers in resource-constrained settings triage patients through SMS or voice messages.

## 🌟 Overview

PocketClinic is an AI-powered healthcare assistant that:
- Collects patient symptoms from voice recordings or text messages
- Analyzes symptoms using WHO IMCI (Integrated Management of Childhood Illness) protocols
- Triages patients based on symptom severity
- Dispatches referrals via SMS with teleconsultation links

## 🚀 Features

- **Multi-modal input**: Process both voice recordings and SMS text messages
- **Symptom collection**: Extract structured symptom data from unstructured inputs
- **Automated triage**: Classify cases as "Likely malaria", "Refer for pneumonia", or "All clear"
- **SMS notifications**: Send referral information to healthcare workers via Twilio
- **Agent-based architecture**: Uses CrewAI for a multi-agent workflow

## 🛠️ Technologies

- Python 3.10+
- [CrewAI](https://docs.crewai.com/) - Multi-agent orchestration
- [OpenAI](https://openai.com/) - GPT-4o for NLP and audio transcription
- [Twilio](https://www.twilio.com/) - SMS messaging
- [Vosk](https://alphacephei.com/vosk/) - Speech recognition
- [Pydub](https://github.com/jiaaro/pydub) - Audio processing

## 📋 Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- OpenAI API key
- Twilio account (SID, token, and phone number)

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pocketclinic.git
   cd pocketclinic
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Create a `.env` file based on `.env_example`:
   ```bash
   cp .env_example .env
   ```

4. Add your API keys to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_SID=your_twilio_sid
   TWILIO_TOKEN=your_twilio_token
   TWILIO_NUMBER=your_twilio_phone_number
   ```

## 🚀 Usage

### Command Line Interface

Run the main application:

```bash
python main.py
```

You can modify the input parameters in `main.py` to test different scenarios:
- `text_message`: SMS text describing patient symptoms
- `audio_file`: Path to an audio file containing symptom description
- `phone_number`: Recipient's phone number for SMS notifications

### REST API

PocketClinic also provides a REST API using FastAPI. To start the API server:

```bash
python server.py
```

This will start the API server at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

#### API Endpoints

The API provides the following endpoints:

- **POST /api/v1/process**: Process a request with text input
- **POST /api/v1/process/audio**: Process a request with audio input

Both endpoints handle the entire PocketClinic workflow:
1. Collect symptoms from the input (text or audio)
2. Triage the symptoms
3. Dispatch a referral via SMS

#### Testing the API

You can test the API using the provided test script:

```bash
python tests/test_api_single.py
```

## 🧪 Testing

The project includes test scripts for each component:

```bash
# Test symptom collection
python tests/test_symptom_collector.py

# Test symptom triage
python tests/test_triage_symptoms.py

# Test referral dispatch
python tests/test_referral_dispatch.py
```

## 📁 Project Structure

- `main.py` - Main application entry point
- `server.py` - FastAPI server entry point
- `agents.py` - CrewAI agent definitions
- `tasks.py` - CrewAI task definitions
- `api/` - API implementation
  - `main.py` - FastAPI application
  - `models.py` - Pydantic models for request/response validation
- `pocket_clinic_tools/` - Core functionality modules
  - `symptom_collector.py` - Extracts symptoms from text/audio
  - `triage_symptoms.py` - Evaluates symptom severity
  - `referral_dispatcher.py` - Sends SMS notifications
  - `audio_utils.py` - Audio preprocessing utilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- World Health Organization for IMCI protocols
- CrewAI for the agent framework
- OpenAI for NLP capabilities