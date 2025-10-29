"""BigQuery Test Case Service"""
from google.cloud import bigquery
from app.config import settings
from app.services.base_service import BaseTestCaseService
from app.models.test_case import TestCase, TestCaseCreate, TestCaseStatus, TestCaseMetadata
from datetime import datetime
import uuid

class BigQueryTestCaseService(BaseTestCaseService):
    def __init__(self):
        self.client = bigquery.Client(project=settings.gcp_project_id)
        self.table_id = f"{settings.gcp_project_id}.{settings.gcp_dataset_id}.{settings.gcp_table_id}"

    async def get_test_cases(self, page: int, page_size: int, status: str, domain: str, priority: str, search: str):
        # Build a flattened projection so the frontend receives top-level fields
        select_clause = (
            "SELECT "
            "id, name, description, domain, difficulty, "
            "metadata.status AS status, "
            "metadata.owner AS owner, "
            "metadata.priority AS priority, "
            "CAST(metadata.created_date AS STRING) AS created_date, "
            "CAST(metadata.updated_date AS STRING) AS updated_date, "
            "metadata.tags AS tags "
            f"FROM `{self.table_id}`"
        )

        where_clauses = []
        query_params = []

        if status:
            where_clauses.append("metadata.status = @status")
            query_params.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        if domain:
            where_clauses.append("domain = @domain")
            query_params.append(bigquery.ScalarQueryParameter("domain", "STRING", domain))

        if priority:
            where_clauses.append("metadata.priority = @priority")
            query_params.append(bigquery.ScalarQueryParameter("priority", "STRING", priority))

        if search:
            # Use wildcard inside the parameter for LIKE
            where_clauses.append("(LOWER(name) LIKE @search OR LOWER(description) LIKE @search)")
            query_params.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{search.lower()}%"))

        where_clause_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Count query for pagination
        count_query = f"SELECT COUNT(*) AS total FROM `{self.table_id}`{where_clause_sql}"
        count_job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        count_query_job = self.client.query(count_query, job_config=count_job_config)
        count_rows = list(count_query_job.result())
        total = int(count_rows[0].get("total")) if count_rows else 0

        # Pagination and ordering (newest first)
        offset = max(0, (page - 1) * page_size)
        list_query = f"{select_clause}{where_clause_sql} ORDER BY metadata.created_date DESC LIMIT {page_size} OFFSET {offset}"

        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = self.client.query(list_query, job_config=job_config)
        results = list(query_job.result())
        items = [dict(row) for row in results]

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_test_case_by_id(self, test_case_id: str):
        query = f"""SELECT * FROM `{self.table_id}` WHERE id = @test_case_id"""
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("test_case_id", "STRING", test_case_id),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        rows = list(results)
        if not rows:
            return None
        return dict(rows[0])

    async def create_test_case(self, test_case: TestCaseCreate) -> TestCase:
        # Generate a new test case ID
        # For simplicity, we'll use a similar format to the mock service, but with a UUID to ensure uniqueness
        # In a real-world scenario, you might have a more robust ID generation strategy
        query = f"SELECT COUNT(*) as count FROM `{self.table_id}`"
        query_job = self.client.query(query)
        result = query_job.result()
        row = next(result)
        count = row['count']
        new_id = f"TC-{count + 1:04d}"

        # Create the full TestCase object
        new_test_case = TestCase(
            id=new_id,
            name=test_case.name,
            description=test_case.description,
            metadata=TestCaseMetadata(
                status=TestCaseStatus.DRAFT,
                owner=test_case.owner,
                priority=test_case.priority,
                tags=test_case.tags,
                version="1.0.0",
                created_date=datetime.now().isoformat(),
                source_session="manual",
            ),
            domain=test_case.domain,
            difficulty=test_case.difficulty,
            test_config=test_case.test_config,
            input=test_case.input,
            execution=test_case.execution,
            analysis=test_case.analysis,
        )

        # Convert to a dictionary for insertion
        row_to_insert = new_test_case.model_dump(by_alias=True)

        # BigQuery expects nested objects as dictionaries
        # Pydantic's model_dump handles this conversion

        errors = self.client.insert_rows_json(self.table_id, [row_to_insert])
        if errors:
            # Handle errors
            # For simplicity, we'll raise an exception
            # In a real-world scenario, you might want to log the errors and handle them more gracefully
            raise Exception(f"Failed to insert row into BigQuery: {errors}")

        return new_test_case