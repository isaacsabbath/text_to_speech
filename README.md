# VoiceGen: Text to Speech with Azure Cognitive Services 🎤🗣️

VoiceGen is an application that utilizes **Azure Cognitive Services** to convert **text into natural-sounding speech**. The service is hosted on **Azure App Services**. I learned how to set up API keys, monitor logs, and integrate with **GitHub Actions** for continuous integration and deployment (CI/CD).

Visit the [VoiceGen Service](https://voicegen.azurewebsites.net/) to try it out!

---

## 🚀 Getting Started

### Prerequisites

Before you start, ensure you have the following:

1. **Azure Subscription**: You need an Azure account. If you don't have one, you can [sign up here](https://azure.microsoft.com/en-us/free/).
2. **Azure Cognitive Services - Speech API**: Create a Speech API resource in the Azure Portal to get your **API key** and **region**.

---

## 🖥️ Setting Up the Development Environment

### 1. Create a Virtual Environment

To set up a virtual environment for this project, follow these steps based on your operating system.

#### **Windows:**

1. Open your terminal or Command Prompt.
2. Create a virtual environment:
   ```bash
   python -m venv venv
  

3. Activate the virtual environment:
   ``` bash
    .\venv\Scripts\activate
  ## Install Requirements
    pip install -r requirements.txt
### **macOS/Linux:**
  ``` bash
     source venv/bin/activate
    pip install -r requirements.txt

     
