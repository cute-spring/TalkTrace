import os
import random
import uuid
import json
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables from .env files
load_dotenv("/Users/gavinzhang/TalkTrace/backend-python/.env")
load_dotenv("/Users/gavinzhang/TalkTrace/.env")

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("GCP_DATASET_ID")
TABLE_ID = os.getenv("GCP_TABLE_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

assert PROJECT_ID, "GCP_PROJECT_ID is not set"
assert DATASET_ID, "GCP_DATASET_ID is not set"
assert TABLE_ID, "GCP_TABLE_ID is not set"
assert CREDENTIALS_PATH and os.path.exists(CREDENTIALS_PATH), "GOOGLE_APPLICATION_CREDENTIALS is not set or file does not exist"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def random_tag():
    return {"name": random.choice(["FAQ", "Billing", "Tech", "General", "Urgent"]), "color": random.choice(["red", "blue", "green", "yellow", "purple"])}

def random_model():
    return {
        "name": random.choice(["gpt-4", "gpt-3.5-turbo", "llama-2", "gemini-pro"]),
        "version": random.choice(["v1", "v2", "2024.06"]),
        # JSON column: provide a JSON-encoded string to avoid streaming/type issues
        "params": json.dumps({"temperature": round(random.uniform(0.2, 1.0), 2), "top_p": round(random.uniform(0.7, 1.0), 2)})
    }

def random_prompts():
    return {
        "system": "You are a helpful assistant.",
        "user_instruction": random.choice([
            "Summarize the following document.",
            "Answer the user's question based on the provided context.",
            "Provide step-by-step reasoning.",
            "List the key points.",
        ])
    }

def random_retrieval():
    return {
        "top_k": random.randint(3, 10),
        "similarity_threshold": round(random.uniform(0.5, 0.95), 2),
        "reranker_enabled": random.choice([True, False])
    }

def random_chunk(idx):
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid.uuid4()),
        "title": f"Chunk {idx}",
        "source": random.choice(["doc", "faq", "kb", "email"]),
        "content": f"This is the content of chunk {idx}.",
        "metadata": {
            "publish_date": (now - timedelta(days=idx)).isoformat(),
            "effective_date": (now - timedelta(days=idx+1)).isoformat(),
            "expiration_date": (now + timedelta(days=30)).isoformat(),
            "chunk_type": random.choice(["paragraph", "table", "image"]),
            "confidence": round(random.uniform(0.7, 1.0), 2),
            "retrieval_rank": idx
        }
    }

def random_turn(turn):
    now = datetime.now(timezone.utc)
    return {
        "turn": turn,
        "role": random.choice(["user", "assistant"]),
        "query": f"Query {turn}",
        "response": f"Response {turn}",
        "retrieved_chunks": [random_chunk(c) for c in range(1, random.randint(1,3))],
        "timestamp": (now - timedelta(minutes=turn*2)).isoformat()
    }

def random_performance():
    return {
        "total_response_time": round(random.uniform(0.5, 2.5), 2),
        "retrieval_time": round(random.uniform(0.1, 0.5), 2),
        "generation_time": round(random.uniform(0.2, 1.0), 2),
        "tokens_used": random.randint(100, 500),
        "chunks_considered": random.randint(3, 10)
    }

def random_quality():
    return {
        "max_similarity": round(random.uniform(0.8, 1.0), 2),
        "avg_similarity": round(random.uniform(0.7, 0.99), 2),
        "diversity_score": round(random.uniform(0.5, 1.0), 2)
    }

def random_generation():
    return {
        "reasoning_chain": "Step 1: ... Step 2: ... Step 3: ...",
        "citation_usage": ["chunk-1", "chunk-2"]
    }

def random_feedback():
    now = datetime.now(timezone.utc)
    return {
        "rating": random.randint(1, 5),
        "category": random.choice(["accuracy", "completeness", "clarity", "citation"]),
        "comment": "Good answer.",
        "concern": "None",
        "suggested_improvement": "Add more details.",
        "feedback_date": now.isoformat(),
        "feedback_source": random.choice(["user", "admin"])
    }

def random_quality_scores():
    return {
        "context_understanding": random.randint(1, 5),
        "answer_accuracy": random.randint(1, 5),
        "answer_completeness": random.randint(1, 5),
        "clarity": random.randint(1, 5),
        "citation_quality": random.randint(1, 5)
    }

def random_analysis():
    now = datetime.now(timezone.utc)
    return {
        "issue_type": random.choice(["none", "hallucination", "incomplete", "irrelevant"]),
        "root_cause": "N/A",
        "expected_answer": "Expected answer text.",
        "acceptance_criteria": "Must cover all points.",
        "quality_scores": random_quality_scores(),
        "optimization_suggestions": ["Improve retrieval", "Tune model params"],
        "notes": "Analysis notes.",
        "analyzed_by": "QA Team",
        "analysis_date": now.isoformat()
    }

def make_test_case(idx):
    now = datetime.now(timezone.utc)
    return {
        "id": f"TC-{idx:04d}",
        "name": f"Test Case {idx}",
        "description": f"This is a sample test case {idx}.",
        "domain": random.choice(["finance", "healthcare", "education", "technology"]),
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "metadata": {
            "status": random.choice(["active", "inactive", "draft"]),
            "owner": random.choice(["alice", "bob", "carol", "dave"]),
            "priority": random.choice(["low", "medium", "high"]),
            "version": f"v{random.randint(1,3)}.0",
            "created_date": (now - timedelta(days=idx)).isoformat(),
            "updated_date": now.isoformat(),
            "source_session": f"session-{idx}",
            "tags": [random_tag() for _ in range(random.randint(1,3))]
        },
        "test_config": {
            "model": random_model(),
            "prompts": random_prompts(),
            "retrieval": random_retrieval()
        },
        "input": {
            "current_query": {
                "text": f"What is the answer to test case {idx}?",
                "timestamp": now.isoformat()
            },
            "conversation_history": [random_turn(t) for t in range(1, random.randint(2,5))],
            "current_retrieved_chunks": [random_chunk(c) for c in range(1, random.randint(1,3))]
        },
        "execution": {
            "actual": {
                "response": f"This is the actual response for test case {idx}.",
                "performance_metrics": random_performance(),
                "retrieval_quality": random_quality(),
                "generation_info": random_generation()
            },
            "user_feedback": random_feedback()
        },
        "analysis": random_analysis()
    }

# Generate 10 sample test cases
rows_to_insert = [make_test_case(i+1) for i in range(10)]

from google.cloud import bigquery

# Use a load job with explicit schema to ensure perfect alignment
table = client.get_table(table_ref)
job_config = bigquery.LoadJobConfig()
job_config.schema = table.schema
job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

job = client.load_table_from_json(rows_to_insert, table_ref, job_config=job_config)
job.result()  # Waits for the job to complete.
print(f"Successfully loaded {len(rows_to_insert)} sample test cases into {table_ref}.")