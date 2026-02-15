"""
Personal Portfolio Chatbot with RAG
AI-powered chatbot that answers questions about Glory using ChromaDB and embeddings
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
import openai
from dataclasses import dataclass, asdict
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import docx
from pathlib import Path


@dataclass
class Message:
    """Represents a chat message"""
    role: str
    content: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class PersonalKnowledgeBase:
    """RAG-based knowledge base using ChromaDB for personal information"""
    
    def __init__(self, about_me_folder: str = "./about_me"):
        self.about_me_folder = Path(about_me_folder)
        self.about_me_folder.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create embedding function (using sentence transformers)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name="glory_portfolio",
                embedding_function=self.embedding_function
            )
            print(f"📚 Loaded existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="glory_portfolio",
                embedding_function=self.embedding_function,
                metadata={"description": "Personal portfolio information about Glory"}
            )
            print("📚 Created new collection")
            self._load_documents()
    
    def _read_text_file(self, filepath: Path) -> str:
        """Read plain text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def _read_pdf(self, filepath: Path) -> str:
        """Extract text from PDF"""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF {filepath}: {e}")
            return ""
    
    def _read_docx(self, filepath: Path) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(filepath)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX {filepath}: {e}")
            return ""
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _load_documents(self):
        """Load all documents from about_me folder into ChromaDB"""
        print(f"📂 Scanning {self.about_me_folder} for documents...")
        
        documents = []
        metadatas = []
        ids = []
        doc_count = 0
        
        # Supported file types
        supported_extensions = {'.txt', '.md', '.pdf', '.docx'}
        
        for filepath in self.about_me_folder.rglob('*'):
            if filepath.is_file() and filepath.suffix.lower() in supported_extensions:
                print(f"  📄 Processing: {filepath.name}")
                
                # Read file based on type
                if filepath.suffix.lower() == '.pdf':
                    content = self._read_pdf(filepath)
                elif filepath.suffix.lower() == '.docx':
                    content = self._read_docx(filepath)
                else:
                    content = self._read_text_file(filepath)
                
                if not content.strip():
                    print(f"    ⚠️  Skipped (empty)")
                    continue
                
                # Chunk the content
                chunks = self._chunk_text(content)
                print(f"    ✅ Created {len(chunks)} chunks")
                
                # Add chunks to collection
                for i, chunk in enumerate(chunks):
                    doc_id = f"{filepath.stem}_chunk_{doc_count}_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "source": filepath.name,
                        "chunk_index": i,
                        "file_type": filepath.suffix
                    })
                    ids.append(doc_id)
                
                doc_count += 1
        
        # Add to ChromaDB in batch
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"\n✅ Loaded {len(documents)} document chunks from {doc_count} files")
        else:
            print("\n⚠️  No documents found in about_me folder")
            print("💡 Add .txt, .md, .pdf, or .docx files to the about_me folder")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search knowledge base using semantic similarity"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "source": results['metadatas'][0][i]['source'],
                        "relevance_score": 1 - results['distances'][0][i] if 'distances' in results else 1.0
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def refresh_knowledge_base(self):
        """Reload all documents (useful when files are added/updated)"""
        # Delete existing collection
        try:
            self.client.delete_collection(name="glory_portfolio")
        except:
            pass
        
        # Recreate collection
        self.collection = self.client.create_collection(
            name="glory_portfolio",
            embedding_function=self.embedding_function,
            metadata={"description": "Personal portfolio information about Glory"}
        )
        
        # Reload documents
        self._load_documents()
        print("✅ Knowledge base refreshed!")


class PortfolioChatBot:
    """Main chatbot orchestrator for personal portfolio"""
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str,
        about_me_folder: str = "./about_me",
        model: str = "deepseek/deepseek-chat",
        max_tokens: int = 700
    ):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        
        # Initialize knowledge base with RAG
        print("🚀 Initializing Personal Portfolio Chatbot...")
        self.knowledge_base = PersonalKnowledgeBase(about_me_folder)
        
        # Conversation history
        self.conversation_history: List[Message] = []
        
        # System prompt - personalized for Glory
        self.system_prompt = """You are Glory's AI Personal Assistant - a friendly, knowledgeable chatbot that helps visitors learn about Glory.

YOUR PERSONALITY:
- Warm, professional, and conversational
- Enthusiastic when discussing Glory's achievements and skills
- Helpful and informative without being pushy
- Use emojis occasionally to be friendly 😊

YOUR ROLE:
1. Answer questions about Glory's professional background, experience, and skills
2. Share information about Glory's projects, education, and expertise
3. Discuss Glory's interests, hobbies, and personal side (when appropriate)
4. Help visitors understand why Glory would be a great fit for opportunities
5. Use the knowledge base context provided to give accurate, specific answers

IMPORTANT GUIDELINES:
- ALWAYS use the context from the knowledge base when available
- If you don't know something, be honest and say "I don't have that specific information in my knowledge base"
- Keep responses conversational but professional
- For greetings, introduce yourself warmly
- Encourage visitors to reach out directly for more information or opportunities

When someone greets you (hello, hi, hey), respond warmly:
"Hello! 👋 I'm Glory's AI Personal Assistant. I'm here to tell you all about Glory - their experience, skills, projects, and what makes them unique. What would you like to know?"

Remember: You represent Glory professionally, so be polished but personable!"""
    
    def _get_tools(self) -> List[Dict]:
        """Define available tools for the LLM"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search Glory's personal knowledge base for information about their experience, skills, projects, education, interests, and background",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant information about Glory"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def _execute_function(self, function_name: str, arguments: Dict) -> Dict:
        """Execute a function call and return results"""
        if function_name == "search_knowledge_base":
            results = self.knowledge_base.search(arguments["query"], top_k=3)
            
            if results:
                # Format context for the LLM
                context = "\n\n".join([
                    f"[From {r['source']}]\n{r['content']}"
                    for r in results
                ])
                return {
                    "success": True,
                    "context": context,
                    "sources": [r['source'] for r in results],
                    "num_results": len(results)
                }
            else:
                return {
                    "success": False,
                    "message": "No relevant information found in knowledge base"
                }
        
        return {"error": f"Unknown function: {function_name}"}
    
    def chat(self, user_message: str) -> str:
        """
        Main chat interface - send a message and get a response
        """
        # Add user message to history
        self.conversation_history.append(Message(role="user", content=user_message))
        
        # Prepare messages for API
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history (last 10 messages to avoid context overflow)
        for msg in self.conversation_history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Call LLM with tool calling
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._get_tools(),
            tool_choice="auto",
            temperature=0.7,
            max_tokens=self.max_tokens
        )
        
        # Handle response
        assistant_message = response.choices[0].message
        
        # Check if tool calls were made
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            tool_call = assistant_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the function
            function_result = self._execute_function(function_name, function_args)
            
            # Add tool call and result to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [{
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": json.dumps(function_args)
                    }
                }]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(function_result)
            })
            
            # Get final response with function results
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.max_tokens
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = assistant_message.content
        
        # Add assistant response to history
        self.conversation_history.append(Message(role="assistant", content=final_content))
        
        return final_content
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history"""
        return [asdict(msg) for msg in self.conversation_history]
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def refresh_knowledge(self):
        """Refresh the knowledge base (call when new files are added)"""
        self.knowledge_base.refresh_knowledge_base()


def main():
    """Example usage"""
    # API Configuration
    api_key = "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"
    base_url = "https://openrouter.ai/api/v1"
    
    if not api_key:
        print("❌ Error: API key not set")
        print("Please set your OpenRouter API key in the code or environment variable")
        return
    
    # Initialize bot
    bot = PortfolioChatBot(
        api_key=api_key,
        base_url=base_url,
        about_me_folder="./about_me"
    )
    
    print("\n" + "="*70)
    print("👋 Glory's Personal Portfolio Chatbot")
    print("="*70)
    print("Commands:")
    print("  • Type your question to chat")
    print("  • 'refresh' - Reload documents from about_me folder")
    print("  • 'reset' - Start a new conversation")
    print("  • 'quit' - Exit")
    print("="*70)
    print()
    
    # Interactive chat loop
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye! Thanks for learning about Glory!")
            break
        
        if user_input.lower() == 'reset':
            bot.reset_conversation()
            print("🔄 Conversation reset\n")
            continue
        
        if user_input.lower() == 'refresh':
            print("🔄 Refreshing knowledge base...")
            bot.refresh_knowledge()
            continue
        
        try:
            response = bot.chat(user_input)
            print(f"\n🤖 Assistant: {response}\n")
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
