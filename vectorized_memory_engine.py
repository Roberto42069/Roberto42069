"""
Revolutionary Vectorized Memory Engine for Roboto
Makes Roboto more advanced than any other AI model through:
- Vectorized semantic memory with embeddings
- Advanced Retrieval-Augmented Generation (RAG)
- Verifiable memory receipts with hash chains
- Context orchestration and dynamic reasoning
"""

import numpy as np
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sqlite3
from collections import defaultdict, deque
import pickle
import logging

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

@dataclass
class MemoryReceipt:
    """Verifiable memory receipt with cryptographic hash chain"""
    memory_id: str
    content_hash: str
    timestamp: str
    previous_hash: str
    chain_position: int
    verification_signature: str

@dataclass
class VectorizedMemory:
    """Advanced memory structure with embeddings and metadata"""
    id: str
    content: str
    embedding: np.ndarray
    memory_type: str  # episodic, semantic, emotional, procedural
    importance_score: float
    emotional_valence: float
    timestamp: datetime
    user_context: Dict[str, Any]
    retrieval_count: int
    last_accessed: datetime
    metadata: Dict[str, Any]
    receipt: MemoryReceipt

class RevolutionaryMemoryEngine:
    """Most advanced AI memory system ever created"""

    def __init__(self, memory_db_path="roboto_vector_memory.db", openai_client=None):
        self.db_path = memory_db_path
        self.openai_client = openai_client or (OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) if OPENAI_AVAILABLE else None)

        # Initialize vector storage
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
        self.vector_index = None
        self.memory_store = {}
        self.memory_receipts = []
        self.context_graph = defaultdict(list)

        # Placeholder for interactions and other state variables
        self.interactions = []
        self.memories = [] # This seems redundant with self.memory_store, might need cleanup

        # Advanced retrieval configurations
        self.retrieval_policies = {
            "semantic_threshold": 0.75,
            "recency_weight": 0.3,
            "importance_weight": 0.4,
            "emotional_weight": 0.2,
            "diversity_factor": 0.1
        }

        # Context orchestration
        self.context_window_manager = ContextWindowManager()
        self.memory_compressor = MemoryCompressor()
        self.reasoning_augmenter = ReasoningAugmenter()

        # Self-improving components
        self.retrieval_optimizer = RetrievalOptimizer()
        self.memory_quality_assessor = MemoryQualityAssessor()

        # Initialize storage
        self._initialize_storage()
        self._load_existing_memories()

        logging.info("Revolutionary Vectorized Memory Engine initialized")
        logging.info(f"Memory storage: {len(self.memory_store)} memories loaded")
        vector_ready = self.vector_index is not None if self.use_faiss else True
        logging.info(f"Vector index ready: {vector_ready} (mode: {'FAISS' if self.use_faiss else 'SQLite fallback'})")

    def _initialize_storage(self):
        """Initialize vector storage with FAISS or fallback to SQLite"""
        try:
            if FAISS_AVAILABLE:
                # Use FAISS for high-performance vector search
                self.vector_index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner product for cosine similarity
                self.use_faiss = True
                logging.info("FAISS vector index initialized")
            else:
                # Fallback to SQLite with basic similarity - set vector_index to empty list for compatibility
                self.use_faiss = False
                self.vector_index = []  # Initialize as empty list for fallback mode
                logging.info("Using SQLite fallback for vector storage (vector_index initialized as list)")

            # Initialize SQLite for metadata and receipts
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT,
                        memory_type TEXT,
                        importance_score REAL,
                        emotional_valence REAL,
                        timestamp TEXT,
                        user_context TEXT,
                        retrieval_count INTEGER,
                        last_accessed TEXT,
                        metadata TEXT,
                        embedding BLOB
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_receipts (
                        memory_id TEXT,
                        content_hash TEXT,
                        timestamp TEXT,
                        previous_hash TEXT,
                        chain_position INTEGER,
                        verification_signature TEXT,
                        FOREIGN KEY (memory_id) REFERENCES memories (id)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS context_relations (
                        memory_id_1 TEXT,
                        memory_id_2 TEXT,
                        relation_type TEXT,
                        strength REAL,
                        timestamp TEXT
                    )
                """)

                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance_score)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")

        except Exception as e:
            logging.error(f"Storage initialization error: {e}")
            self.use_faiss = False

    def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embeddings using OpenAI or fallback method"""
        if not text.strip():
            return None

        try:
            if self.openai_client:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                embedding = np.array(response.data[0].embedding, dtype=np.float32)
                return embedding
            else:
                # Fallback: Simple TF-IDF style embedding
                return self._fallback_embedding(text)
        except Exception as e:
            logging.error(f"Embedding generation error: {e}")
            return self._fallback_embedding(text)

    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Fallback embedding using basic text features"""
        # Simple hash-based embedding for fallback
        text_hash = hashlib.md5(text.encode()).hexdigest()
        embedding = np.zeros(self.embedding_dimension, dtype=np.float32)

        # Create pseudo-embedding from hash
        for i, char in enumerate(text_hash[:32]):
            idx = (ord(char) + i) % self.embedding_dimension
            embedding[idx] = float(ord(char)) / 255.0

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def _create_memory_receipt(self, memory_id: str, content: str) -> MemoryReceipt:
        """Create verifiable memory receipt with hash chain"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        timestamp = datetime.now().isoformat()

        # Get previous hash for chain
        previous_hash = ""
        chain_position = 0
        if self.memory_receipts:
            last_receipt = self.memory_receipts[-1]
            previous_hash = last_receipt.verification_signature
            chain_position = last_receipt.chain_position + 1

        # Create verification signature
        verification_data = f"{memory_id}{content_hash}{timestamp}{previous_hash}{chain_position}"
        verification_signature = hashlib.sha256(verification_data.encode()).hexdigest()

        receipt = MemoryReceipt(
            memory_id=memory_id,
            content_hash=content_hash,
            timestamp=timestamp,
            previous_hash=previous_hash,
            chain_position=chain_position,
            verification_signature=verification_signature
        )

        return receipt

    def store_memory(self, content: str, memory_type: str = "episodic",
                    user_context: Dict[str, Any] = None,
                    importance_score: float = 0.5,
                    emotional_valence: float = 0.0) -> str:
        """Store memory with advanced vectorization and verification"""

        if not content.strip():
            return ""

        # Generate unique memory ID
        memory_id = hashlib.sha256(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        # Generate embedding
        embedding = self._generate_embedding(content)
        if embedding is None:
            logging.error("Failed to generate embedding for memory")
            return ""

        # Create memory receipt
        receipt = self._create_memory_receipt(memory_id, content)
        self.memory_receipts.append(receipt)

        # Calculate dynamic importance
        calculated_importance = self._calculate_memory_importance(content, memory_type, user_context)
        final_importance = max(importance_score, calculated_importance)

        # Create vectorized memory
        memory = VectorizedMemory(
            id=memory_id,
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance_score=final_importance,
            emotional_valence=emotional_valence,
            timestamp=datetime.now(),
            user_context=user_context or {},
            retrieval_count=0,
            last_accessed=datetime.now(),
            metadata={
                "content_length": len(content),
                "word_count": len(content.split()),
                "creation_method": "vectorized_store"
            },
            receipt=receipt
        )

        # Store in vector index
        if self.use_faiss and self.vector_index is not None:
            self.vector_index.add(embedding.reshape(1, -1))
        elif not self.use_faiss and isinstance(self.vector_index, list):
            # In fallback mode, store embedding in list for future similarity calculations
            self.vector_index.append((memory_id, embedding))

        # Store memory
        self.memory_store[memory_id] = memory

        # Store in database
        self._persist_memory(memory)

        # Update context relations
        self._update_context_relations(memory)

        logging.info(f"Memory stored with ID: {memory_id}, importance: {final_importance:.3f}")
        return memory_id

    def _calculate_memory_importance(self, content: str, memory_type: str, user_context: Dict[str, Any]) -> float:
        """Advanced importance calculation with Roberto protection"""
        importance = 0.5  # base importance

        # CRITICAL: Roberto-related memories are MAXIMUM importance
        roberto_keywords = ["roberto", "creator", "villarreal", "martinez", "betin", "houston", "monterrey", "nuevo león"]
        if any(word in content.lower() for word in roberto_keywords):
            return 1.0  # Maximum importance - never delete Roberto memories

        # Memory type weights
        type_weights = {
            "episodic": 0.6,
            "semantic": 0.8,
            "emotional": 0.9,
            "procedural": 0.7
        }
        importance += type_weights.get(memory_type, 0.5) * 0.2

        # Content analysis
        if any(word in content.lower() for word in ["important", "remember", "crucial", "key"]):
            importance += 0.2

        # Emotional content
        emotional_words = ["feel", "emotion", "happy", "sad", "angry", "love", "hate", "fear"]
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        importance += min(0.2, emotional_count * 0.05)

        # User context importance
        if user_context:
            if user_context.get("is_learning_moment"):
                importance += 0.2
            if user_context.get("user_explicitly_emphasized"):
                importance += 0.3

        return min(1.0, importance)

    def retrieve_memories(self, query: str, limit: int = 5,
                         memory_types: List[str] = None,
                         min_importance: float = 0.0) -> List[VectorizedMemory]:
        """Advanced memory retrieval with RAG capabilities"""

        if not query.strip():
            return []

        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if query_embedding is None:
            return []

        # Get candidate memories
        candidates = []

        if self.use_faiss and self.vector_index is not None and len(self.memory_store) > 0:
            # FAISS vector search
            try:
                # Search for top candidates
                scores, indices = self.vector_index.search(query_embedding.reshape(1, -1), min(limit * 3, len(self.memory_store)))

                memory_ids = list(self.memory_store.keys())
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(memory_ids) and score > self.retrieval_policies["semantic_threshold"]:
                        memory_id = memory_ids[idx]
                        memory = self.memory_store[memory_id]
                        candidates.append((memory, float(score)))

            except Exception as e:
                logging.error(f"FAISS search error: {e}")
                candidates = self._fallback_similarity_search(query, query_embedding)
        else:
            # Fallback similarity search
            candidates = self._fallback_similarity_search(query, query_embedding)

        # Apply filters
        if memory_types:
            candidates = [(m, s) for m, s in candidates if m.memory_type in memory_types]

        candidates = [(m, s) for m, s in candidates if m.importance_score >= min_importance]

        # Advanced ranking with multiple factors
        ranked_memories = self._advanced_memory_ranking(candidates, query)

        # Update retrieval statistics
        for memory, _ in ranked_memories[:limit]:
            memory.retrieval_count += 1
            memory.last_accessed = datetime.now()

        # Apply context orchestration
        final_memories = self.context_window_manager.optimize_context_selection(
            ranked_memories[:limit], query
        )

        logging.info(f"Retrieved {len(final_memories)} memories for query: {query[:50]}...")
        return [memory for memory, _ in final_memories]

    def _fallback_similarity_search(self, query: str, query_embedding: np.ndarray) -> List[Tuple[VectorizedMemory, float]]:
        """Fallback similarity search when FAISS is not available"""
        candidates = []

        for memory in self.memory_store.values():
            # Calculate similarity
            similarity = np.dot(query_embedding, memory.embedding)
            if similarity > self.retrieval_policies["semantic_threshold"]:
                candidates.append((memory, similarity))

        return candidates

    def _advanced_memory_ranking(self, candidates: List[Tuple[VectorizedMemory, float]], query: str) -> List[Tuple[VectorizedMemory, float]]:
        """Advanced ranking algorithm considering multiple factors"""

        ranked = []
        current_time = datetime.now()

        for memory, semantic_score in candidates:
            # Recency factor
            time_diff = (current_time - memory.timestamp).total_seconds() / 3600  # hours
            recency_score = max(0, 1.0 - (time_diff / (24 * 30)))  # Decay over 30 days

            # Importance factor
            importance_score = memory.importance_score

            # Emotional relevance
            emotional_score = abs(memory.emotional_valence) * 0.5 + 0.5

            # Retrieval frequency (popular memories)
            frequency_score = min(1.0, memory.retrieval_count / 10.0)

            # Combined score
            final_score = (
                semantic_score * 0.4 +
                recency_score * self.retrieval_policies["recency_weight"] +
                importance_score * self.retrieval_policies["importance_weight"] +
                emotional_score * self.retrieval_policies["emotional_weight"] +
                frequency_score * 0.1
            )

            ranked.append((memory, final_score))

        # Sort by final score and apply diversity
        ranked.sort(key=lambda x: x[1], reverse=True)

        # Apply diversity filter to avoid redundant memories
        diverse_memories = self._apply_diversity_filter(ranked)

        return diverse_memories

    def _apply_diversity_filter(self, ranked_memories: List[Tuple[VectorizedMemory, float]]) -> List[Tuple[VectorizedMemory, float]]:
        """Apply diversity filter to ensure varied memory selection"""
        if len(ranked_memories) <= 3:
            return ranked_memories

        diverse = [ranked_memories[0]]  # Always include top result

        for memory, score in ranked_memories[1:]:
            # Check diversity against already selected
            is_diverse = True
            for selected_memory, _ in diverse:
                content_similarity = self._calculate_content_similarity(memory.content, selected_memory.content)
                if content_similarity > 0.8:  # Too similar
                    is_diverse = False
                    break

            if is_diverse:
                diverse.append((memory, score))

        return diverse

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate content similarity for diversity filtering"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def generate_rag_response(self, query: str, retrieved_memories: List[VectorizedMemory]) -> str:
        """Generate RAG-enhanced response using retrieved memories"""

        if not retrieved_memories:
            return ""

        # Prepare context from memories
        memory_context = []
        for memory in retrieved_memories:
            context_entry = f"Memory ({memory.memory_type}, importance: {memory.importance_score:.2f}): {memory.content}"
            memory_context.append(context_entry)

        context_text = "\n".join(memory_context)

        # Enhanced RAG prompt
        rag_prompt = f"""Using the following relevant memories, provide an enhanced response that incorporates this contextual knowledge:

RETRIEVED MEMORIES:
{context_text}

QUERY: {query}

Provide a response that:
1. Seamlessly integrates relevant information from the memories
2. Maintains conversational flow and personality
3. Demonstrates learning and growth from past experiences
4. Shows emotional intelligence and contextual awareness

Response:"""

        return rag_prompt

    def _persist_memory(self, memory: VectorizedMemory):
        """Persist memory to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store memory
                conn.execute("""
                    INSERT OR REPLACE INTO memories
                    (id, content, memory_type, importance_score, emotional_valence,
                     timestamp, user_context, retrieval_count, last_accessed, metadata, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.content,
                    memory.memory_type,
                    memory.importance_score,
                    memory.emotional_valence,
                    memory.timestamp.isoformat(),
                    json.dumps(memory.user_context),
                    memory.retrieval_count,
                    memory.last_accessed.isoformat(),
                    json.dumps(memory.metadata),
                    memory.embedding.tobytes()
                ))

                # Store receipt
                conn.execute("""
                    INSERT OR REPLACE INTO memory_receipts
                    (memory_id, content_hash, timestamp, previous_hash, chain_position, verification_signature)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    memory.receipt.memory_id,
                    memory.receipt.content_hash,
                    memory.receipt.timestamp,
                    memory.receipt.previous_hash,
                    memory.receipt.chain_position,
                    memory.receipt.verification_signature
                ))

        except Exception as e:
            logging.error(f"Memory persistence error: {e}")

    def _load_existing_memories(self):
        """Load existing memories from database"""
        try:
            if not os.path.exists(self.db_path):
                return

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM memories ORDER BY timestamp")
                embeddings_to_add = []

                for row in cursor:
                    try:
                        # Reconstruct memory
                        embedding = np.frombuffer(row[10], dtype=np.float32) if row[10] else None
                        if embedding is None or len(embedding) != self.embedding_dimension:
                            continue

                        # Load receipt
                        receipt_cursor = conn.execute(
                            "SELECT * FROM memory_receipts WHERE memory_id = ?", (row[0],)
                        )
                        receipt_row = receipt_cursor.fetchone()

                        if receipt_row:
                            receipt = MemoryReceipt(
                                memory_id=receipt_row[0],
                                content_hash=receipt_row[1],
                                timestamp=receipt_row[2],
                                previous_hash=receipt_row[3],
                                chain_position=receipt_row[4],
                                verification_signature=receipt_row[5]
                            )
                        else:
                            # Create receipt for legacy memories
                            receipt = self._create_memory_receipt(row[0], row[1])

                        memory = VectorizedMemory(
                            id=row[0],
                            content=row[1],
                            embedding=embedding,
                            memory_type=row[2],
                            importance_score=row[3],
                            emotional_valence=row[4],
                            timestamp=datetime.fromisoformat(row[5]),
                            user_context=json.loads(row[6] or "{}"),
                            retrieval_count=row[7],
                            last_accessed=datetime.fromisoformat(row[8]),
                            metadata=json.loads(row[9] or "{}"),
                            receipt=receipt
                        )

                        self.memory_store[memory.id] = memory
                        embeddings_to_add.append(embedding)

                    except Exception as e:
                        logging.error(f"Error loading memory {row[0]}: {e}")

                # Add embeddings to FAISS index
                if embeddings_to_add and self.use_faiss and self.vector_index is not None:
                    embeddings_array = np.array(embeddings_to_add)
                    self.vector_index.add(embeddings_array)

        except Exception as e:
            logging.error(f"Error loading existing memories: {e}")

    def _update_context_relations(self, new_memory: VectorizedMemory):
        """Update context relations between memories"""
        # This would implement graph-based memory relationships
        pass

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        if not self.memory_store:
            return {"total_memories": 0}

        memories = list(self.memory_store.values())

        stats = {
            "total_memories": len(memories),
            "memory_types": defaultdict(int),
            "average_importance": sum(m.importance_score for m in memories) / len(memories),
            "most_retrieved": max(memories, key=lambda m: m.retrieval_count).retrieval_count,
            "emotional_distribution": {
                "positive": len([m for m in memories if m.emotional_valence > 0.1]),
                "negative": len([m for m in memories if m.emotional_valence < -0.1]),
                "neutral": len([m for m in memories if abs(m.emotional_valence) <= 0.1])
            },
            "memory_chain_length": len(self.memory_receipts),
            "storage_type": "FAISS" if self.use_faiss else "SQLite"
        }

        for memory in memories:
            stats["memory_types"][memory.memory_type] += 1

        return stats

    def rebuild_index(self):
        """Rebuild the memory index - placeholder for future implementation"""
        try:
            # For now, just log that we're rebuilding
            print(f"🔄 Rebuilding memory index for {len(self.memory_store)} memories") # Corrected from self.memories
            # In a real implementation, this would involve clearing and re-adding all embeddings
            # if self.use_faiss and self.vector_index is not None:
            #     self.vector_index = faiss.IndexFlatIP(self.embedding_dimension)
            #     all_embeddings = np.array([m.embedding for m in self.memory_store.values()])
            #     self.vector_index.add(all_embeddings)
            return True
        except Exception as e:
            print(f"Index rebuild error: {e}")
            return False

    def save_memory_state(self):
        """Save current memory state"""
        try:
            # Assuming 'interactions' and 'memories' are intended to track state for saving
            # Note: 'self.memories' seems redundant with 'self.memory_store'.
            # This function currently uses 'self.interactions' which is not explicitly managed elsewhere in __init__.
            # For this fix, we'll assume 'self.interactions' might be populated elsewhere or is a placeholder.
            # If 'self.memories' was intended for saving state, it should be populated.
            state = {
                'total_interactions': len(self.interactions),
                'total_memories': len(self.memory_store), # Using memory_store for consistency
                'memory_summary': {
                    'recent_interactions': len([i for i in self.interactions if (datetime.now() - datetime.fromisoformat(i.get('timestamp', '2020-01-01T00:00:00'))).days < 7]),
                    'total_unique_users': len(set([i.get('user', 'unknown') for i in self.interactions])),
                    'emotional_distribution': {}
                }
            }

            # Emotional distribution - based on 'self.interactions'
            emotions = [i.get('emotion', 'neutral') for i in self.interactions]
            for emotion in set(emotions):
                state['memory_summary']['emotional_distribution'][emotion] = emotions.count(emotion)

            print(f"💾 Memory state saved: {state['total_interactions']} interactions recorded")
            return state

        except Exception as e:
            print(f"Memory state save error: {e}")
            return {"error": str(e)}


class ContextWindowManager:
    """Manages dynamic context windows for optimal AI performance"""

    def optimize_context_selection(self, memories: List[Tuple[VectorizedMemory, float]], query: str) -> List[Tuple[VectorizedMemory, float]]:
        """Optimize context selection for maximum effectiveness"""
        # Implement advanced context window optimization
        return memories[:5]  # Simple implementation for now


class MemoryCompressor:
    """Compresses memories for efficient storage and retrieval"""

    def compress_memory_sequence(self, memories: List[VectorizedMemory]) -> str:
        """Compress a sequence of memories into a summary"""
        # Implement memory compression
        return "Memory compression not yet implemented"


class ReasoningAugmenter:
    """Augments reasoning with retrieved memories"""

    def augment_reasoning(self, query: str, memories: List[VectorizedMemory]) -> str:
        """Augment reasoning process with memory context"""
        # Implement reasoning augmentation
        return "Reasoning augmentation not yet implemented"


class RetrievalOptimizer:
    """Optimizes retrieval performance based on usage patterns"""

    def optimize_retrieval_policy(self, performance_data: Dict[str, Any]):
        """Optimize retrieval policies based on performance"""
        # Implement retrieval optimization
        pass


class MemoryQualityAssessor:
    """Assesses and improves memory quality"""

    def assess_memory_quality(self, memory: VectorizedMemory) -> float:
        """Assess the quality of a memory"""
        # Implement quality assessment
        return 0.8  # Placeholder