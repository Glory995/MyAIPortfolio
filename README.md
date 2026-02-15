# 🤖 Glory's Personal Portfolio Chatbot

An intelligent AI chatbot that answers questions about Glory using **RAG (Retrieval Augmented Generation)**, **ChromaDB**, and **OpenAI-compatible APIs**. The chatbot reads documents from the `about_me` folder, creates embeddings, and uses semantic search to provide accurate, context-aware responses.

## ✨ Features

- 🧠 **RAG Implementation**: Uses ChromaDB for vector storage and semantic search
- 📚 **Document Processing**: Automatically reads .txt, .md, .pdf, and .docx files
- 🎯 **Smart Embeddings**: Uses sentence-transformers for semantic understanding
- 💬 **Conversational Memory**: Maintains conversation context
- 🌐 **Web Interface**: Beautiful, responsive chat widget
- 🔌 **REST API**: FastAPI backend with full documentation
- 🔄 **Auto-Refresh**: Can reload knowledge base when documents are updated

## 🏗️ Architecture

```
portfolio_chatbot/
├── about_me/                 # 📂 Add your documents here!
│   └── about_glory.md       # Sample document
├── chroma_db/               # 🗄️ Vector database (auto-created)
├── portfolio_bot.py         # 🤖 Main chatbot logic with RAG
├── api_server.py            # 🌐 FastAPI backend server
├── index.html               # 💻 Web interface
└── requirements.txt         # 📦 Dependencies
```

## 📋 Prerequisites

- Python 3.8+
- OpenRouter API key (or compatible OpenAI API)

## 🚀 Installation

### 1. Clone or Download

```bash
# If you have the files, navigate to the directory
cd portfolio_chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai` - For LLM API calls
- `chromadb` - Vector database for embeddings
- `sentence-transformers` - For creating embeddings
- `PyPDF2` & `python-docx` - For document processing
- `fastapi` & `uvicorn` - For web API
- `pydantic` - For data validation

### 3. Add Your Content

**This is the most important step!** Add documents about yourself to the `about_me` folder:

```bash
# Add text files
about_me/bio.txt
about_me/experience.md
about_me/cv.pdf
about_me/projects.docx
```

Supported formats:
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents
- `.docx` - Word documents

**What to include:**
- Your professional experience
- Technical skills
- Education and certifications
- Projects and achievements
- Personal interests and hobbies
- Contact information
- Anything you want the chatbot to know about you!

### 4. Configure API Key

Edit `portfolio_bot.py` and `api_server.py` to add your API key:

```python
api_key = "your-openrouter-api-key-here"
base_url = "https://openrouter.ai/api/v1"
```

Or use environment variables:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

## 💻 Usage

### Option 1: Command Line Interface

Run the chatbot directly in your terminal:

```bash
python portfolio_bot.py
```

Commands:
- Type your questions naturally
- `refresh` - Reload documents from about_me folder
- `reset` - Start a new conversation
- `quit` - Exit

### Option 2: Web Interface (Recommended)

1. **Start the API server:**

```bash
python api_server.py
```

The server will start at `http://localhost:8000`

2. **Open the web interface:**

Open `index.html` in your browser or serve it:

```bash
# Simple HTTP server
python -m http.server 3000
# Then open: http://localhost:3000
```

3. **Start chatting!** Click the chat button in the bottom-right corner.

## 🎨 Web Interface Features

- **Beautiful Design**: Modern gradient UI with smooth animations
- **Chat Widget**: Fixed chat button that opens/closes smoothly
- **Sample Questions**: Pre-defined questions to get started
- **Typing Indicators**: Shows when the bot is thinking
- **Responsive**: Works on desktop and mobile
- **Keyboard Shortcuts**: 
  - `Ctrl+/` - Open chat
  - `Esc` - Close chat

## 📊 How It Works

### RAG Pipeline

1. **Document Loading**:
   - Scans `about_me` folder for documents
   - Extracts text from PDFs, Word docs, Markdown, and text files

2. **Chunking**:
   - Splits documents into 500-word chunks with 50-word overlap
   - Preserves context while keeping chunks manageable

3. **Embedding**:
   - Uses `sentence-transformers` (all-MiniLM-L6-v2) to create embeddings
   - Stores vectors in ChromaDB for fast similarity search

4. **Query**:
   - User asks a question
   - Question is embedded using same model
   - Semantic search finds top 3 most relevant chunks

5. **Response**:
   - Retrieved context is provided to the LLM
   - LLM generates a natural response based on the context
   - Response is returned to the user

### Example Flow

```
User: "What programming languages does Glory know?"
  ↓
[Embedding] → Query vector
  ↓
[ChromaDB] → Semantic search
  ↓
[Context] → "Python (Expert), JavaScript (Advanced)..."
  ↓
[LLM] → "Glory is proficient in several languages. Their primary..."
  ↓
User: [Response displayed]
```

## 🔧 Customization

### Change the Model

Edit `portfolio_bot.py`:

```python
bot = PortfolioChatBot(
    api_key=api_key,
    base_url=base_url,
    model="gpt-4",  # Change model here
    max_tokens=700   # Adjust response length
)
```

### Modify System Prompt

Edit the `system_prompt` in `PortfolioChatBot.__init__()` to change the bot's personality and behavior.

### Adjust Chunking

Edit `_chunk_text()` method:

```python
def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
    # Adjust chunk_size and overlap values
```

### Change Embedding Model

Edit `PersonalKnowledgeBase.__init__()`:

```python
self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"  # Different model
)
```

Popular options:
- `all-MiniLM-L6-v2` - Fast, good quality (default)
- `all-mpnet-base-v2` - Better quality, slower
- `multi-qa-mpnet-base-dot-v1` - Optimized for Q&A

## 📡 API Endpoints

### POST `/chat`
Send a message and get a response

**Request:**
```json
{
  "message": "What does Glory do?",
  "session_id": "session_123"
}
```

**Response:**
```json
{
  "response": "Glory is a software engineer...",
  "session_id": "session_123",
  "timestamp": "2026-02-15T10:30:00"
}
```

### GET `/health`
Check API status

### POST `/refresh_knowledge`
Reload all documents from about_me folder

### Full API docs at: `http://localhost:8000/docs`

## 🎯 Sample Questions

Try asking:
- "What is Glory's professional experience?"
- "What technologies does Glory work with?"
- "Tell me about Glory's projects"
- "What are Glory's interests?"
- "Is Glory available for opportunities?"
- "What makes Glory unique?"
- "How can I contact Glory?"

## 🐛 Troubleshooting

### No documents loaded
- Check that files are in the `about_me` folder
- Ensure files have supported extensions (.txt, .md, .pdf, .docx)
- Check file permissions

### ChromaDB errors
- Delete `chroma_db` folder and restart
- Ensure sentence-transformers is installed correctly

### API connection errors
- Verify API key is correct
- Check internet connection
- Ensure API server is running on port 8000

### Web interface not connecting
- Update `API_BASE` in `index.html` to match your server URL
- Check CORS settings in `api_server.py`
- Verify server is running: `http://localhost:8000/health`

## 🔄 Updating Content

When you add or modify documents in `about_me`:

**Command Line:**
```bash
# In the CLI, type:
refresh
```

**Web Interface:**
```bash
# Call the API:
curl -X POST http://localhost:8000/refresh_knowledge
```

## 🚀 Deployment

### Deploy API to Cloud

```bash
# Using Docker
docker build -t portfolio-chatbot .
docker run -p 8000:8000 portfolio-chatbot

# Or deploy to Heroku, AWS, etc.
```

### Host Web Interface

- Upload `index.html` to GitHub Pages, Netlify, or Vercel
- Update `API_BASE` to your deployed API URL

## 📝 Tips for Best Results

1. **Quality Content**: Add detailed, well-written documents
2. **Organization**: Use clear headings and structure
3. **Coverage**: Include all aspects you want the bot to discuss
4. **Regular Updates**: Keep content fresh and accurate
5. **Test Queries**: Try different questions to verify responses

## 🤝 Contributing

Feel free to enhance this project:
- Add new document formats
- Improve embedding strategies
- Enhance the UI
- Add more features

## 📄 License

Free to use and modify for your personal portfolio!

## 🙏 Acknowledgments

Built with:
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- FastAPI for the backend
- OpenRouter for LLM access

---

**Created for Glory's Portfolio - Powered by AI** 🚀
