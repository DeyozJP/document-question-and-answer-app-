# document-question-and-answer-app-

### Document Question and Answering System
This project is a Document Question and Answering System built using LlamaIndex, ChromaDB, and GPT-3.5 Turbo The system allows users to upload documents in various formats (Word, PDF, text) and then query these documents to extract useful information. Users can ask questions, request summaries, and inquire about specific details within the documents. This system leverages advanced natural language processing (NLP) techniques to provide accurate and meaningful responses.

#### Features
Document Upload: Users can upload documents in Word, PDF, or text format.
Question and Answering: Users can ask questions related to the content of the uploaded documents.
Summarization: Users can request summaries of the documents to get a quick overview of the content.
Natural Language Processing: Utilizes GPT-3.5 Turbo and ChatGPT for understanding and responding to user queries.
Persistent Storage: Uses ChromaDB to store and manage vector indices for efficient querying.

#### Technology Stack
LlamaIndex: For indexing and querying documents.
GPT-3.5 Turbo & ChatGPT: For natural language understanding and generating responses.
Dash: For building the web application interface.
ChromaDB: For storing and managing vector indices.

#### How It Works
Upload Document: The user uploads a document through the web interface.
Indexing: The document is indexed using LlamaIndex to facilitate efficient querying.
Querying: The user submits a question or a request for summarization.
Processing: The system uses GPT-3.5 Turbo to process the query and generate a response.
Response: The response is displayed to the user through the web interface.


#### Getting Started
To get started with this project, follow these steps:
Clone the repository.
Install the required dependencies using the provided requirements.txt.
Set up your environment variables, including your OpenAI API key.
Run the application using Docker or your preferred method.
Access the web interface and start uploading documents and querying them.

#### Prerequisites
Python 3.8+
Docker (optional, for containerized deployment)
OpenAI API key
