import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import os
import io
import pdfplumber
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.llms.openai import OpenAI
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize ChromaDB client and collection
chroma_client = chromadb.Client()
chroma_collection = chroma_client.get_or_create_collection('qna_chromadb')

# Directory to save uploaded files
UPLOAD_DIRECTORY = os.getenv('UPLOAD_DIRECTORY', "./uploaded_files")

# Ensure the uploaded directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Function to clear the uploaded files directory
def clear_uploaded_files(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

# Function to save the uploaded file
def save_file(name, content):
    data = content.encode('utf8').split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), 'wb') as fp:
        fp.write(base64.decodebytes(data))
    
    # Convert PDF files to text and save as .txt
    if name.lower().endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_DIRECTORY, name)
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        text = extract_text_from_pdf(pdf_content)
        if text:
            text_filename = os.path.splitext(name)[0] + '.txt'
            text_path = os.path.join(UPLOAD_DIRECTORY, text_filename)
            with open(text_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_content):
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text.strip()  # Strip trailing whitespace and return
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {str(e)}")

# Global variable to hold the index
index = None

# Function to construct the index from uploaded directory
def construct_index(directory_path):
    global index, chroma_collection
    Settings.llm = OpenAI(
        temperature=0,
        model_name='gpt-3.5-turbo',
        streaming=True
    )
    
    # Delete and recreate the collection to clear old data
    chroma_client.delete_collection('qna_chromadb')
    chroma_collection = chroma_client.get_or_create_collection('qna_chromadb')
    
    documents = SimpleDirectoryReader(directory_path, filename_as_id=True).load_data()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    index.storage_context.persist()
    print(f"Index constructed with {len(documents)} documents.")  # Debugging output
    return index

# Function to query the index from ChromaDB
def query_index(query):
    global index
    if index is None:
        raise RuntimeError("Index has not been constructed yet.")
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response

# Define app layout
app.layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Div("Document Q&A",
                style={'font-family': 'Montserrat',
                    'font-size': 30, 
                    'textAlign': 'left', 
                    'color': '#007bff', 
                    'margin': '0px 0px 0px 0px', 
                    'margin-bottom': '0px'
                }), 
            html.H5('By Deyoz Rayamajhi', 
                style={'textAlign': 'left', 
                    'color': 'Purple',
                    'font-size': 12
                }
            )
        ], xs=7, sm=7, md=8, lg=8, xl=8, xxl=8),
        dbc.Col(html.H2(id='current-datetime',
            style={'font-family': 'Montserrat',
                    'font-size': 20, 
                    'textAlign': 'Right', 
                    'color': '#007bff', 
                    'margin': '10px 0px 0px 0px', 
                    'margin-bottom': '0px'
                }), xs=3, sm=3, md=3, lg=3, xl=3, xxl=3),
        dbc.Col(html.Img(src='assets/Logo.jpg',
            style={'height': '50px',
                    'width': '100%',  
                    'margin': '0px 0px 0px 0px', 
                    'margin-bottom': '0px'
                }), xs=2, sm=2, md=2, lg=1, xl=1, xxl=1)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop Here! or ', html.A('Upload Files from Folder!')],
                style={
                    'width': '100%', 'height': '250px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed',
                    'borderRadius': '50px', 'textAlign': 'center', 'margin': '50px 0px 0px 0px',
                    'fontSize': '20px', 'color': '#007bff', 'fontWeight': 'bold'
                }),
            multiple=True
        ), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='upload-status'), width=12)
    ]),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col(dbc.Input(id='query-input', placeholder="Ask a question about your document?...........", type='text',
            style={'margin': '0px 0px 0px 0px', 
                    'height': '100px', 
                    'overflowX': 'scroll',
                    'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)',  # Add shadow
                    'backgroundColor': 'lightBlack'  # Light grey background color
            }),
            xs=12, sm=12, md=10, lg=10, xl=11, xxl=11),
        dbc.Col(dbc.Button('Ask!', id='ask-button', color='primary', 
            style={'margin': '0px 0px 0px 0px', 'height': '100px', 'width': '90px'}), width=2,
            xs=12, sm=12, md=2, lg=2, xl=1, xxl=1)
    ], className='my-2'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.Div(id='output-answer', className='mt-4',
            style={'border': '1px solid #ddd', 'height': '400px', 'overflowY': 'scroll', 
                    'margin': '0px 0px 0px 0px' ,
                    'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)',  # Add shadow
                    'backgroundColor': 'lightBlack'  # Light grey background color
            }), width=12)
    ])
], style={'border': '2px solid #ccc', 'border-radius': '5px'})

# Callback to handle document upload and indexing
@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filenames):
    global UPLOAD_DIRECTORY, index  # Ensure we are referencing the global variables

    if contents is not None and filenames is not None:
        clear_uploaded_files(UPLOAD_DIRECTORY)  # Clear the uploaded files directory
        index = None  # Reset the index to None to clear the old references
        for content, name in zip(contents, filenames):
            save_file(name, content)
        
        construct_index(UPLOAD_DIRECTORY)
        return dbc.Alert(f"{filenames} file uploaded and indexed successfully!", color="success")
    
    return html.Div()

# Callback to handle query processing
@app.callback(
    Output('output-answer', 'children'),
    [Input('ask-button', 'n_clicks')],
    [State('query-input', 'value')]
)
def process_query(n_clicks, query):
    if n_clicks and query:
        try:
            response = query_index(query)
            if response:
                response_text = str(response)  # Convert the response to string format
                return html.Div([
                    html.H5("Query Results:"),
                    html.P(response_text)  # Display the response text in a paragraph
                ])
            else:
                return html.Div("No relevant documents found.")
        except Exception as e:
            return html.Div(f"Error processing query: {str(e)}")
    
    return html.Div()

# Callback to update current datetime
@app.callback(
    Output('current-datetime', 'children'),
    [Input('upload-data', 'contents')]  # Trigger the update on upload
)
def update_datetime(contents):
    return datetime.datetime.now().strftime("%B-%d-%y")

server = app.server  # Required for gunicorn

# Main entry point
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    # app.run_server(debug=True)

