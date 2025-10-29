from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

"""
Load environment variables (with sensible fallbacks) and validate configuration.
We try backend-python/.env first, then project root .env, and finally OS env.
Also ensure GOOGLE_APPLICATION_CREDENTIALS is set and file exists for ADC.
"""

script_dir = Path(__file__).resolve().parent

# Load env from backend-python/.env, then root .env (do not override already-set vars)
load_dotenv(dotenv_path=str(script_dir / "../backend-python/.env"), override=False)
load_dotenv(dotenv_path=str(script_dir / "../.env"), override=False)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("GCP_DATASET_ID")
TABLE_ID = os.getenv("GCP_TABLE_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

missing = [k for k, v in {
    "GCP_PROJECT_ID": PROJECT_ID,
    "GCP_DATASET_ID": DATASET_ID,
    "GCP_TABLE_ID": TABLE_ID,
}.items() if not v]

if missing:
    print("Missing required environment variables:", ", ".join(missing))
    print("Please set them in backend-python/.env or project .env, e.g.\n"
          "GCP_PROJECT_ID=dogggggg\nGCP_DATASET_ID=abc\nGCP_TABLE_ID=test-cases")
    sys.exit(1)

# Validate credentials if provided; strongly recommended for local runs
if not GOOGLE_APPLICATION_CREDENTIALS:
    print("Warning: GOOGLE_APPLICATION_CREDENTIALS is not set; relying on gcloud/ADC defaults.")
else:
    cred_path = Path(GOOGLE_APPLICATION_CREDENTIALS).expanduser().resolve()
    if not cred_path.exists():
        print(f"GOOGLE_APPLICATION_CREDENTIALS file not found: {cred_path}")
        print("Please update the path or export a valid credentials file path.")
        sys.exit(1)
    # Ensure the env var is set for google-auth to pick up
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)

# Instantiate BigQuery client (uses ADC via GOOGLE_APPLICATION_CREDENTIALS/gcloud)
client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# BigQuery schema covering Test Case Management sections:
# Overview, Conversation Context, Configuration, Execution Result, Analysis
schema = [
    # Overview
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("domain", "STRING"),
    bigquery.SchemaField("difficulty", "STRING"),

    bigquery.SchemaField(
        "metadata",
        "RECORD",
        mode="REQUIRED",
        fields=[
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("owner", "STRING"),
            bigquery.SchemaField("priority", "STRING"),
            bigquery.SchemaField("version", "STRING"),
            bigquery.SchemaField("created_date", "TIMESTAMP"),
            bigquery.SchemaField("updated_date", "TIMESTAMP"),
            bigquery.SchemaField("source_session", "STRING"),
            bigquery.SchemaField(
                "tags",
                "RECORD",
                mode="REPEATED",
                fields=[
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("color", "STRING"),
                ],
            ),
        ],
    ),

    # Configuration
    bigquery.SchemaField(
        "test_config",
        "RECORD",
        mode="REQUIRED",
        fields=[
            bigquery.SchemaField(
                "model",
                "RECORD",
                mode="REQUIRED",
                fields=[
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("version", "STRING"),
                    bigquery.SchemaField("params", "JSON"),
                ],
            ),
            bigquery.SchemaField(
                "prompts",
                "RECORD",
                mode="REQUIRED",
                fields=[
                    bigquery.SchemaField("system", "STRING"),
                    bigquery.SchemaField("user_instruction", "STRING"),
                ],
            ),
            bigquery.SchemaField(
                "retrieval",
                "RECORD",
                mode="NULLABLE",
                fields=[
                    bigquery.SchemaField("top_k", "INTEGER"),
                    bigquery.SchemaField("similarity_threshold", "FLOAT"),
                    bigquery.SchemaField("reranker_enabled", "BOOL"),
                ],
            ),
        ],
    ),

    # Conversation Context
    bigquery.SchemaField(
        "input",
        "RECORD",
        mode="REQUIRED",
        fields=[
            bigquery.SchemaField(
                "current_query",
                "RECORD",
                mode="REQUIRED",
                fields=[
                    bigquery.SchemaField("text", "STRING"),
                    bigquery.SchemaField("timestamp", "TIMESTAMP"),
                ],
            ),
            bigquery.SchemaField(
                "conversation_history",
                "RECORD",
                mode="REPEATED",
                fields=[
                    bigquery.SchemaField("turn", "INTEGER"),
                    bigquery.SchemaField("role", "STRING"),
                    bigquery.SchemaField("query", "STRING"),
                    bigquery.SchemaField("response", "STRING"),
                    bigquery.SchemaField(
                        "retrieved_chunks",
                        "RECORD",
                        mode="REPEATED",
                        fields=[
                            bigquery.SchemaField("id", "STRING"),
                            bigquery.SchemaField("title", "STRING"),
                            bigquery.SchemaField("source", "STRING"),
                            bigquery.SchemaField("content", "STRING"),
                            bigquery.SchemaField(
                                "metadata",
                                "RECORD",
                                mode="REQUIRED",
                                fields=[
                                    bigquery.SchemaField("publish_date", "TIMESTAMP"),
                                    bigquery.SchemaField("effective_date", "TIMESTAMP"),
                                    bigquery.SchemaField("expiration_date", "TIMESTAMP"),
                                    bigquery.SchemaField("chunk_type", "STRING"),
                                    bigquery.SchemaField("confidence", "FLOAT"),
                                    bigquery.SchemaField("retrieval_rank", "INTEGER"),
                                ],
                            ),
                        ],
                    ),
                    bigquery.SchemaField("timestamp", "TIMESTAMP"),
                ],
            ),
            bigquery.SchemaField(
                "current_retrieved_chunks",
                "RECORD",
                mode="REPEATED",
                fields=[
                    bigquery.SchemaField("id", "STRING"),
                    bigquery.SchemaField("title", "STRING"),
                    bigquery.SchemaField("source", "STRING"),
                    bigquery.SchemaField("content", "STRING"),
                    bigquery.SchemaField(
                        "metadata",
                        "RECORD",
                        mode="REQUIRED",
                        fields=[
                            bigquery.SchemaField("publish_date", "TIMESTAMP"),
                            bigquery.SchemaField("effective_date", "TIMESTAMP"),
                            bigquery.SchemaField("expiration_date", "TIMESTAMP"),
                            bigquery.SchemaField("chunk_type", "STRING"),
                            bigquery.SchemaField("confidence", "FLOAT"),
                            bigquery.SchemaField("retrieval_rank", "INTEGER"),
                        ],
                    ),
                ],
            ),
        ],
    ),

    # Execution Result
    bigquery.SchemaField(
        "execution",
        "RECORD",
        mode="REQUIRED",
        fields=[
            bigquery.SchemaField(
                "actual",
                "RECORD",
                mode="REQUIRED",
                fields=[
                    bigquery.SchemaField("response", "STRING"),
                    bigquery.SchemaField(
                        "performance_metrics",
                        "RECORD",
                        mode="REQUIRED",
                        fields=[
                            bigquery.SchemaField("total_response_time", "FLOAT"),
                            bigquery.SchemaField("retrieval_time", "FLOAT"),
                            bigquery.SchemaField("generation_time", "FLOAT"),
                            bigquery.SchemaField("tokens_used", "INTEGER"),
                            bigquery.SchemaField("chunks_considered", "INTEGER"),
                        ],
                    ),
                    bigquery.SchemaField(
                        "retrieval_quality",
                        "RECORD",
                        mode="NULLABLE",
                        fields=[
                            bigquery.SchemaField("max_similarity", "FLOAT"),
                            bigquery.SchemaField("avg_similarity", "FLOAT"),
                            bigquery.SchemaField("diversity_score", "FLOAT"),
                        ],
                    ),
                    bigquery.SchemaField(
                        "generation_info",
                        "RECORD",
                        mode="NULLABLE",
                        fields=[
                            bigquery.SchemaField("reasoning_chain", "STRING"),
                            bigquery.SchemaField("citation_usage", "STRING", mode="REPEATED"),
                        ],
                    ),
                ],
            ),
            bigquery.SchemaField(
                "user_feedback",
                "RECORD",
                mode="NULLABLE",
                fields=[
                    bigquery.SchemaField("rating", "INTEGER"),
                    bigquery.SchemaField("category", "STRING"),
                    bigquery.SchemaField("comment", "STRING"),
                    bigquery.SchemaField("concern", "STRING"),
                    bigquery.SchemaField("suggested_improvement", "STRING"),
                    bigquery.SchemaField("feedback_date", "TIMESTAMP"),
                    bigquery.SchemaField("feedback_source", "STRING"),
                ],
            ),
        ],
    ),

    # Analysis
    bigquery.SchemaField(
        "analysis",
        "RECORD",
        mode="NULLABLE",
        fields=[
            bigquery.SchemaField("issue_type", "STRING"),
            bigquery.SchemaField("root_cause", "STRING"),
            bigquery.SchemaField("expected_answer", "STRING"),
            bigquery.SchemaField("acceptance_criteria", "STRING"),
            bigquery.SchemaField(
                "quality_scores",
                "RECORD",
                mode="REQUIRED",
                fields=[
                    bigquery.SchemaField("context_understanding", "INTEGER"),
                    bigquery.SchemaField("answer_accuracy", "INTEGER"),
                    bigquery.SchemaField("answer_completeness", "INTEGER"),
                    bigquery.SchemaField("clarity", "INTEGER"),
                    bigquery.SchemaField("citation_quality", "INTEGER"),
                ],
            ),
            bigquery.SchemaField("optimization_suggestions", "STRING", mode="REPEATED"),
            bigquery.SchemaField("notes", "STRING"),
            bigquery.SchemaField("analyzed_by", "STRING"),
            bigquery.SchemaField("analysis_date", "TIMESTAMP"),
        ],
    ),
]

# If table exists but has no schema, recreate it with the defined schema
try:
    existing = client.get_table(table_ref)
    existing_schema_len = len(existing.schema or [])
    if existing_schema_len == 0:
        print(f"Table {table_ref} exists but has no schema. Recreating with full schema.")
        client.delete_table(table_ref, not_found_ok=True)
        table = bigquery.Table(table_ref, schema=schema)
        table.description = "Test Case Management schema covering Overview, Context, Configuration, Execution, Analysis"
        table.labels = {"env": "dev", "component": "test-case-management"}
        table = client.create_table(table, exists_ok=False)
        print(f"Recreated table {table.project}.{table.dataset_id}.{table.table_id}")
    else:
        # Create if missing, or ensure exists_ok for idempotency
        table = bigquery.Table(table_ref, schema=schema)
        table.description = "Test Case Management schema covering Overview, Context, Configuration, Execution, Analysis"
        table.labels = {"env": "dev", "component": "test-case-management"}
        table = client.create_table(table, exists_ok=True)
        print(f"Created/verified table {table.project}.{table.dataset_id}.{table.table_id}")
except NotFound:
    # Not found: create fresh with schema
    table = bigquery.Table(table_ref, schema=schema)
    table.description = "Test Case Management schema covering Overview, Context, Configuration, Execution, Analysis"
    table.labels = {"env": "dev", "component": "test-case-management"}
    table = client.create_table(table, exists_ok=False)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")