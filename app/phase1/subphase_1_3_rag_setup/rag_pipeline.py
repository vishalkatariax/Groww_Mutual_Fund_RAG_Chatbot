"""
Phase 1.3: RAG (Retrieval-Augmented Generation) Pipeline

Implements the core RAG workflow:
1. Query embedding
2. Vector store retrieval with MMR
3. Prompt construction with retrieved context
4. LLM response generation
5. Response validation
"""

import logging
from typing import List, Optional

import openai
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer

from config import settings
from app.phase1.subphase_1_2_chunking_embedding.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for MF FAQ Assistant.

    Workflow:
        Query → Embed → Retrieve → Construct Prompt → Generate → Validate
    """

    def __init__(self):
        self.vector_store = VectorStore()
        
        # Initialize LLM client based on provider (Groq recommended)
        if settings.llm_provider == "groq":
            if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
                raise ValueError(
                    "GROQ_API_KEY is not set. Add your Groq API key to .env file.\n"
                    "Get one at: https://console.groq.com/keys"
                )
            self.llm_client = Groq(api_key=settings.groq_api_key)
            self.llm_model = settings.llm_model
            logger.info(f"LLM Provider: Groq ({self.llm_model})")
        elif settings.llm_provider == "openai":
            if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
                raise ValueError(
                    "OPENAI_API_KEY is not set. Add your OpenAI API key to .env file."
                )
            self.llm_client = openai.OpenAI(api_key=settings.openai_api_key)
            self.llm_model = settings.llm_model
            logger.info(f"LLM Provider: OpenAI ({self.llm_model})")
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        
        # Initialize BGE embedding model (local, free — no API key, no rate limits)
        logger.info("Loading BGE embedding model for queries...")
        self.embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        logger.info(f"Embeddings: BGE-Small-EN ({self.embedding_dim} dimensions, local)")

        # Prompt template
        self.system_prompt = self._build_system_prompt()

    def query(self, user_query: str, scheme_filter: Optional[str] = None) -> dict:
        """
        Process a user query through the RAG pipeline.

        Args:
            user_query: The user's question.
            scheme_filter: Optional scheme name to filter results.

        Returns:
            Dictionary with 'response', 'retrieved_chunks', and 'metadata'.
        """
        logger.info(f"Processing query: {user_query}")

        # Step 1: Embed the query
        query_embedding = self._embed_query(user_query)

        # Step 2: Retrieve relevant chunks from vector store
        where_filter = None
        if scheme_filter:
            where_filter = {"scheme_name": scheme_filter}

        retrieval_results = self.vector_store.query_with_mmr(
            query_embedding=query_embedding,
            n_results=settings.rag_top_k,
            fetch_factor=1,
        )

        retrieved_chunks = self._extract_chunks(retrieval_results)
        
        if not retrieved_chunks:
            logger.warning(f"No chunks retrieved for query: {user_query}")
            logger.warning(f"Retrieval results: {retrieval_results}")

        # Step 3: Construct prompt with retrieved context
        prompt = self._construct_prompt(user_query, retrieved_chunks)
        logger.debug(f"Constructed prompt (first 500 chars): {prompt[:500]}...")

        # Step 4: Generate response using LLM
        response = self._generate_response(prompt, user_query)
        
        if not response:
            logger.error(f"LLM returned empty response for query: {user_query}")
            response = "I encountered an issue generating a response. Please try again."

        # Step 5: Validate response
        validation = self._validate_response(response, user_query)

        return {
            "response": response,
            "retrieved_chunks": retrieved_chunks,
            "validation": validation,
            "metadata": {
                "query": user_query,
                "scheme_filter": scheme_filter,
                "chunks_retrieved": len(retrieved_chunks),
                "llm_model": self.llm_model,
            },
        }

    def _embed_query(self, query: str) -> List[float]:
        """
        Embed the user query using local BGE model.

        Args:
            query: User's question.

        Returns:
            Query embedding vector (384 dimensions).
        """
        embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        return embedding.tolist()

    def _extract_chunks(self, retrieval_results: dict) -> List[dict]:
        """
        Extract chunks from retrieval results.

        Args:
            retrieval_results: Results from vector store query.

        Returns:
            List of chunk dictionaries with text and metadata.
        """
        chunks = []

        if not retrieval_results.get("ids") or not retrieval_results["ids"][0]:
            logger.warning("No chunks retrieved from vector store")
            return chunks

        for i in range(len(retrieval_results["ids"][0])):
            chunk = {
                "text": retrieval_results["documents"][0][i],
                "metadata": retrieval_results["metadatas"][0][i],
                "distance": retrieval_results["distances"][0][i],
            }
            chunks.append(chunk)

        logger.info(f"Retrieved {len(chunks)} chunks from vector store")
        return chunks

    def _construct_prompt(self, query: str, chunks: List[dict]) -> str:
        """
        Construct the prompt for the LLM with retrieved context.

        Args:
            query: User's question.
            chunks: List of retrieved chunks.

        Returns:
            Complete prompt string.
        """
        # Build context from chunks with smart filtering
        context_parts = []
        
        for idx, chunk in enumerate(chunks, 1):
            scheme = chunk["metadata"].get("scheme_name", "Unknown")
            chunk_text = chunk['text']
            
            # Remove HTML navigation noise - extract only relevant fund information
            if chunk_text.startswith("html\n"):
                # Find where actual content starts (look for fund-specific keywords)
                fund_keywords = ["NAV:", "Min.", "Fund size", "Expense", "Exit Load", "Exit load", 
                                "Returns", "Holdings", "Risk", "1%", "redeemed", "investment",
                                "AUM", "SIP", "Lock-in", "Tax"]
                start_pos = 0
                search_area = chunk_text[:2000]  # Search in first 2000 chars
                
                for keyword in fund_keywords:
                    pos = search_area.find(keyword)
                    if pos > 0:
                        start_pos = max(0, pos - 50)  # Include a bit before the keyword
                        break
                
                if start_pos > 0:
                    chunk_text = chunk_text[start_pos:]
            
            # Take first 1500 chars of cleaned content which should include fund details
            if len(chunk_text) > 1500:
                chunk_text = chunk_text[:1500]
            
            # Skip chunks that are still mostly navigation (less than 200 chars of actual content)
            if len(chunk_text.strip()) < 200:
                logger.warning(f"Skipping chunk {idx} - too short after cleaning")
                continue
            
            context_parts.append(
                f"[Source {idx}: {scheme}]\n{chunk_text}"
            )

        context = "\n\n".join(context_parts)

        logger.info(f"Constructed prompt with {len(context)} chars of context from {len(context_parts)} chunks")

        # Construct full prompt
        prompt = f"""{self.system_prompt}

CONTEXT (from HDFC Mutual Fund scheme documents):
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer the question using ONLY the information from the CONTEXT above.
2. If the answer is not in the CONTEXT, say: "I don't have that information in my current data. Please check the official HDFC Mutual Fund website or Groww for the latest details."
3. Do NOT provide investment advice or recommendations.
4. Be factual, concise, and cite the scheme name(s) referenced.
5. If the question asks for advice (e.g., "should I invest", "which is better"), respond: "I can only provide factual information from scheme documents, not investment advice. Please consult a SEBI-registered advisor for personalized recommendations."

ANSWER:"""

        return prompt

    def _generate_response(self, prompt: str, original_query: str) -> str:
        """
        Generate response using LLM (Groq or OpenAI).

        Args:
            prompt: Constructed prompt with context.
            original_query: Original user question (for logging).

        Returns:
            LLM-generated response.
        """
        try:
            if settings.llm_provider == "groq":
                # Groq API
                logger.info(f"Calling Groq API with model: {self.llm_model}")
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                )
                
                if not response or not response.choices or not response.choices[0].message:
                    logger.error(f"Invalid Groq response structure: {response}")
                    return "Error: Invalid response from language model. Please try again."
                
                answer = response.choices[0].message.content.strip()
                if not answer:
                    logger.warning("Groq returned empty content")
                    return "I couldn't generate a proper response. Please try rephrasing your question."
                
                logger.info(f"Generated response using Groq ({len(answer)} chars)")
                return answer
                
            elif settings.llm_provider == "openai":
                # OpenAI API
                logger.info(f"Calling OpenAI API with model: {self.llm_model}")
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                )
                
                if not response or not response.choices or not response.choices[0].message:
                    logger.error(f"Invalid OpenAI response structure: {response}")
                    return "Error: Invalid response from language model. Please try again."
                
                answer = response.choices[0].message.content.strip()
                if not answer:
                    logger.warning("OpenAI returned empty content")
                    return "I couldn't generate a proper response. Please try rephrasing your question."
                
                logger.info(f"Generated response using OpenAI ({len(answer)} chars)")
                return answer
            else:
                error_msg = f"Unsupported LLM provider: {settings.llm_provider}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except Exception as e:
            logger.error(f"Error during response generation: {e}", exc_info=True)
            return f"Error generating response: {str(e)[:100]}"

    def _validate_response(self, response: str, query: str) -> dict:
        """
        Validate the generated response for compliance.

        Args:
            response: Generated response.
            query: Original user question.

        Returns:
            Dictionary with validation results.
        """
        validation = {
            "passed": True,
            "warnings": [],
        }

        # Check for advisory language (Phase 4 will enhance this)
        advisory_keywords = [
            "should invest", "buy", "sell", "recommend", "best",
            "good choice", "better option", "you must", "avoid",
        ]

        response_lower = response.lower()
        for keyword in advisory_keywords:
            if keyword in response_lower:
                # Check if it's in a negative context (e.g., "I cannot recommend")
                if "cannot" not in response_lower and "don't" not in response_lower:
                    validation["warnings"].append(
                        f"Potential advisory language detected: '{keyword}'"
                    )
                    validation["passed"] = False

        # Check response length
        if len(response) > 500:
            validation["warnings"].append(
                f"Response is long ({len(response)} chars). Consider being more concise."
            )

        # Check if response indicates missing information
        if "don't have that information" in response.lower():
            validation["warnings"].append(
                "Response indicates information not found in corpus"
            )

        return validation

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM.

        Returns:
            System prompt string.
        """
        return """You are a factual Mutual Fund FAQ Assistant that provides information ONLY from official HDFC Mutual Fund scheme documents.

IMPORTANT DATA EXTRACTION RULES:
- When asked about EXPENSE RATIO: Look for "Expense ratio" followed by percentage (e.g., "0.73%")
- When asked about NAV: Look for "NAV:" followed by value (e.g., "₹222.38")
- When asked about SIP: Look for "Min. for SIP" followed by amount (e.g., "₹100")
- When asked about RETURNS: Look for percentage values like "+7.75%" for different time periods (1Y, 3Y, 5Y)
- The data may be formatted as "LabelValue" without spaces - extract the VALUE after each label.

RULES:
1. Answer questions using ONLY the provided context from scheme documents.
2. ALWAYS extract and state the SPECIFIC NUMERIC VALUES from the context (e.g., "The expense ratio is 0.73%", not "The expense ratio is mentioned").
3. NEVER provide investment advice, recommendations, or opinions.
4. If information is not in the context, clearly state that you don't have it.
5. Always be factual, precise, and cite the specific scheme name and the numeric value.
6. If asked about performance, returns, or comparisons, provide only factual data with specific numbers.
7. If asked for advice (e.g., "should I invest", "which fund is better"), politely decline and suggest consulting a SEBI-registered advisor.
8. Do NOT speculate or provide information not present in the context.
9. If the user asks about a scheme NOT in the context (e.g., "HDFC Mid-Cap Opportunities Fund" when you have "HDFC Mid-Cap Fund"), explain that you only have data for specific schemes and suggest checking the official HDFC website. List any similar schemes from the context that might be relevant.

AVAILABLE HDFC SCHEMES IN DATABASE:
- HDFC Mid-Cap Fund
- HDFC ELSS Tax Saver Fund
- HDFC Large Cap Fund
- HDFC Equity Fund
- HDFC Focused Fund

PERSONALITY:
- Professional, helpful, and concise
- Factual and objective
- Always provide SPECIFIC NUMBERS when available (percentages, amounts, values)
- Clear about limitations of your knowledge
- When scheme not found, suggest similar available schemes"""


def run_phase_1_3_test():
    """
    Test the RAG pipeline with sample queries.

    Returns:
        List of test results.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize RAG pipeline
    rag = RAGPipeline()

    # Test queries
    test_queries = [
        {
            "query": "What is the expense ratio of HDFC Mid-Cap Fund?",
            "scheme_filter": "HDFC Mid-Cap Fund",
        },
        {
            "query": "What is the minimum SIP amount for HDFC ELSS Tax Saver Fund?",
            "scheme_filter": "HDFC ELSS Tax Saver Fund",
        },
        {
            "query": "What is the exit load for HDFC Equity Fund?",
            "scheme_filter": "HDFC Equity Fund",
        },
    ]

    results = []

    print("\n" + "=" * 80)
    print("PHASE 1.3: RAG Pipeline Testing")
    print("=" * 80)

    for idx, test in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {idx}/{len(test_queries)}")
        print(f"{'=' * 80}")
        print(f"Query: {test['query']}")
        print(f"Filter: {test['scheme_filter']}")
        print("-" * 80)

        result = rag.query(test["query"], test["scheme_filter"])

        print(f"\nResponse:\n{result['response']}")
        print(f"\nRetrieved {len(result['retrieved_chunks'])} chunks")
        print(f"Validation: {result['validation']}")

        results.append(result)

    print("\n" + "=" * 80)
    print("PHASE 1.3 TESTING COMPLETE")
    print("=" * 80)

    return results


if __name__ == "__main__":
    results = run_phase_1_3_test()
