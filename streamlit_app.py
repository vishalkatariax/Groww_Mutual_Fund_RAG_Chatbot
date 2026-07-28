"""
Streamlit Application for MF FAQ Assistant
Combines frontend UI and backend RAG pipeline in a single Streamlit app
"""

import streamlit as st
import time
from datetime import datetime
from app.phase1.subphase_1_3_rag_setup.rag_pipeline import RAGPipeline
from app.phase1.subphase_1_4_compliance.compliance_pipeline import CompliancePipeline
from app.core.intent_classifier import intent_classifier
from app.core.refusal_handler import refusal_handler
from app.core.response_validator import response_validator
from config import settings

# Page configuration
st.set_page_config(
    page_title="Groww MF FAQ Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: white;
    }
    .disclaimer-banner {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #666;
    }
    .source-link {
        color: #667eea;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'compliance_pipeline' not in st.session_state:
    st.session_state.compliance_pipeline = None

# Header
st.markdown("""
    <div class="main-header">
        <h1>📊 Groww MF FAQ Assistant</h1>
        <p>Facts-only Mutual Fund FAQ Assistant for HDFC schemes</p>
    </div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
    <div class="disclaimer-banner">
        <strong>⚠️ Disclaimer:</strong> This assistant provides factual information only. 
        It does not provide investment advice or recommendations. 
        All data is sourced from Groww. Investments are subject to market risks.
    </div>
""", unsafe_allow_html=True)

# Sidebar with scheme information
with st.sidebar:
    st.header("Available Schemes")
    schemes = [
        "HDFC Mid-Cap Fund",
        "HDFC Equity Fund", 
        "HDFC Focused Fund",
        "HDFC ELSS Tax Saver Fund",
        "HDFC Large Cap Fund"
    ]
    selected_scheme = st.selectbox("Select a scheme", schemes)
    
    st.header("About")
    st.info("""
    This assistant answers factual questions about HDFC Mutual Fund schemes using data sourced from Groww.
    
    **Features:**
    - Real-time data from Groww
    - Facts-only responses
    - No investment advice
    - Source attribution
    """)
    
    st.header("Example Questions")
    example_questions = [
        "What is the expense ratio of HDFC Mid-Cap Fund?",
        "What is the exit load for HDFC ELSS Tax Saver?",
        "Minimum SIP amount for HDFC Large Cap Fund?",
        "What is the lock-in period for ELSS funds?"
    ]
    for question in example_questions:
        if st.button(question, key=question):
            st.session_state.messages.append({"role": "user", "content": question})

# Main chat interface
st.header("Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Assistant:** {message['content']}")
            if "source_url" in message:
                st.markdown(f"📎 [Source]({message['source_url']})")
            if "last_updated" in message:
                st.caption(f"Last updated: {message['last_updated']}")

# Chat input
if prompt := st.chat_input("Ask a question about HDFC Mutual Funds..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(f"**You:** {prompt}")
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("Processing your query..."):
            try:
                # Initialize pipelines if needed
                if st.session_state.compliance_pipeline is None:
                    st.session_state.compliance_pipeline = CompliancePipeline()
                
                if st.session_state.rag_pipeline is None:
                    st.session_state.rag_pipeline = RAGPipeline()
                
                # Step 1: Input guardrails validation
                compliance_pipeline = st.session_state.compliance_pipeline
                is_valid, message, sanitized_query = compliance_pipeline.process_query(prompt)
                
                if not is_valid:
                    if message == "ADVISORY_DETECTED":
                        # Route to refusal handler
                        refusal_response = refusal_handler.handle_advisory(
                            query=sanitized_query or prompt,
                            source_url="https://groww.in/mutual-funds",
                        )
                        response = refusal_response["answer"]
                        source_url = refusal_response["source_url"]
                        last_updated = refusal_response["last_updated"]
                        is_refusal = True
                    else:
                        response = f"I cannot process this query: {message}"
                        source_url = None
                        last_updated = datetime.now().strftime("%Y-%m-%d")
                        is_refusal = True
                else:
                    # Step 2: Intent classification
                    intent_result = intent_classifier.classify(sanitized_query)
                    intent_type = intent_result["intent"]
                    
                    # Step 3: Route based on intent
                    if intent_type == "advisory":
                        refusal_response = refusal_handler.handle_advisory(
                            query=sanitized_query,
                            source_url="https://groww.in/mutual-funds",
                        )
                        response = refusal_response["answer"]
                        source_url = refusal_response["source_url"]
                        last_updated = refusal_response["last_updated"]
                        is_refusal = True
                    
                    elif intent_type == "ambiguous":
                        refusal_response = refusal_handler.handle_ambiguous(
                            query=sanitized_query,
                            source_url="https://groww.in/mutual-funds",
                        )
                        response = refusal_response["answer"]
                        source_url = refusal_response["source_url"]
                        last_updated = refusal_response["last_updated"]
                        is_refusal = True
                    
                    else:
                        # Factual query - route to RAG pipeline
                        rag_pipeline = st.session_state.rag_pipeline
                        rag_result = rag_pipeline.query(sanitized_query)
                        response = rag_result.get("response", "")
                        
                        if not response:
                            response = "I couldn't generate a response to your question. Please try rewording it."
                            source_url = "https://groww.in/mutual-funds"
                        else:
                            # Extract source URL from metadata
                            if rag_result.get("retrieved_chunks"):
                                source_url = rag_result["retrieved_chunks"][0].get("metadata", {}).get("source_url")
                            else:
                                source_url = "https://groww.in/mutual-funds"
                        
                        last_updated = datetime.now().strftime("%Y-%m-%d")
                        is_refusal = False
                        
                        # Step 4: Output guardrails validation
                        is_valid, val_message, validated_response = compliance_pipeline.process_response(
                            response=response,
                            source_url=source_url,
                            is_refusal=False,
                        )
                        
                        if not is_valid:
                            fallback_response = refusal_handler.handle_not_found(
                                query=sanitized_query,
                                source_url=source_url,
                            )
                            response = fallback_response["answer"]
                            source_url = fallback_response["source_url"]
                        else:
                            response = validated_response or response
                
                # Display response
                st.markdown(f"**Assistant:** {response}")
                if source_url:
                    st.markdown(f"📎 [Source]({source_url})")
                st.caption(f"Last updated: {last_updated}")
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "source_url": source_url,
                    "last_updated": last_updated
                })
                
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Footer
st.markdown("---")
st.caption("Data sourced from Groww | Last updated: " + datetime.now().strftime("%Y-%m-%d"))
