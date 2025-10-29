-- SQL to insert 10 dummy test case records into dogggggg.abc.test_cases_samples
-- You can run this in BigQuery Console or CLI

INSERT INTO `dogggggg.abc.test_cases_samples` (
  id, name, description, domain, difficulty, metadata, test_config, input, execution, analysis
)
VALUES

-- 1
(
  'TC-0001', 'Dummy Case 1', 'This is a dummy test case.', 'search', 'easy',
  STRUCT('active' AS status, 'alice' AS owner, 'high' AS priority, 'v1.0' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-001' AS source_session, [STRUCT('tagA' AS name, 'red' AS color), STRUCT('tagB' AS name, 'blue' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-4' AS name, '4.0' AS version, JSON '{"temperature":0.7,"max_tokens":512}' AS params) AS model,
    STRUCT('system prompt' AS system, 'user instruction' AS user_instruction) AS prompts,
    STRUCT(5 AS top_k, 0.85 AS similarity_threshold, TRUE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('What is AI?' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'What is AI?' AS query, 'AI is artificial intelligence.' AS response, [STRUCT('chunk-1' AS id, 'AI Intro' AS title, 'doc-1' AS source, 'AI is...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'definition' AS chunk_type, 0.99 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-2' AS id, 'AI Details' AS title, 'doc-2' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.95 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('AI is artificial intelligence.' AS response, STRUCT(1.23 AS total_response_time, 0.45 AS retrieval_time, 0.78 AS generation_time, 100 AS tokens_used, 2 AS chunks_considered) AS performance_metrics, STRUCT(0.99 AS max_similarity, 0.98 AS avg_similarity, 0.97 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-1', 'citation-2'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(5 AS rating, 'accuracy' AS category, 'Good answer' AS comment, 'None' AS concern, 'Add more details' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('none' AS issue_type, 'N/A' AS root_cause, 'Expected answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(5 AS context_understanding, 5 AS answer_accuracy, 5 AS answer_completeness, 5 AS clarity, 5 AS citation_quality) AS quality_scores, ['Optimize retrieval'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 2
(
  'TC-0002', 'Dummy Case 2', 'Another dummy test case.', 'qa', 'medium',
  STRUCT('inactive' AS status, 'bob' AS owner, 'medium' AS priority, 'v1.1' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-002' AS source_session, [STRUCT('tagC' AS name, 'green' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-3.5' AS name, '3.5' AS version, JSON '{"temperature":0.5,"max_tokens":256}' AS params) AS model,
    STRUCT('system prompt 2' AS system, 'user instruction 2' AS user_instruction) AS prompts,
    STRUCT(3 AS top_k, 0.75 AS similarity_threshold, FALSE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Explain ML.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Explain ML.' AS query, 'ML is machine learning.' AS response, [STRUCT('chunk-3' AS id, 'ML Intro' AS title, 'doc-3' AS source, 'ML is...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'definition' AS chunk_type, 0.92 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-4' AS id, 'ML Details' AS title, 'doc-4' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.90 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('ML is machine learning.' AS response, STRUCT(1.11 AS total_response_time, 0.41 AS retrieval_time, 0.71 AS generation_time, 80 AS tokens_used, 1 AS chunks_considered) AS performance_metrics, STRUCT(0.95 AS max_similarity, 0.94 AS avg_similarity, 0.93 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-3'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(4 AS rating, 'completeness' AS category, 'Satisfactory' AS comment, 'None' AS concern, 'Clarify definition' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('clarity' AS issue_type, 'Ambiguous' AS root_cause, 'Expected ML answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(4 AS context_understanding, 4 AS answer_accuracy, 4 AS answer_completeness, 4 AS clarity, 4 AS citation_quality) AS quality_scores, ['Improve clarity'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 3
(
  'TC-0003', 'Dummy Case 3', 'Yet another dummy test case.', 'recommendation', 'hard',
  STRUCT('active' AS status, 'carol' AS owner, 'low' AS priority, 'v2.0' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-003' AS source_session, [STRUCT('tagD' AS name, 'yellow' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-4' AS name, '4.0' AS version, JSON '{"temperature":0.9,"max_tokens":1024}' AS params) AS model,
    STRUCT('system prompt 3' AS system, 'user instruction 3' AS user_instruction) AS prompts,
    STRUCT(10 AS top_k, 0.95 AS similarity_threshold, TRUE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Recommend a book.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Recommend a book.' AS query, 'Try "AI Superpowers".' AS response, [STRUCT('chunk-5' AS id, 'Book' AS title, 'doc-5' AS source, 'AI Superpowers...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'recommendation' AS chunk_type, 0.97 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-6' AS id, 'Book Details' AS title, 'doc-6' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.93 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('Try "AI Superpowers".' AS response, STRUCT(2.00 AS total_response_time, 0.60 AS retrieval_time, 1.00 AS generation_time, 120 AS tokens_used, 3 AS chunks_considered) AS performance_metrics, STRUCT(0.97 AS max_similarity, 0.96 AS avg_similarity, 0.95 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-4'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(3 AS rating, 'recommendation' AS category, 'Good suggestion' AS comment, 'None' AS concern, 'Add more options' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('coverage' AS issue_type, 'Limited' AS root_cause, 'Expected book answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(3 AS context_understanding, 3 AS answer_accuracy, 3 AS answer_completeness, 3 AS clarity, 3 AS citation_quality) AS quality_scores, ['Expand recommendations'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 4
(
  'TC-0004', 'Dummy Case 4', 'Dummy for search.', 'search', 'easy',
  STRUCT('inactive' AS status, 'dave' AS owner, 'high' AS priority, 'v1.2' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-004' AS source_session, [STRUCT('tagE' AS name, 'purple' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-3.5' AS name, '3.5' AS version, JSON '{"temperature":0.6,"max_tokens":300}' AS params) AS model,
    STRUCT('system prompt 4' AS system, 'user instruction 4' AS user_instruction) AS prompts,
    STRUCT(2 AS top_k, 0.65 AS similarity_threshold, FALSE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Find AI papers.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Find AI papers.' AS query, 'Here are some papers.' AS response, [STRUCT('chunk-7' AS id, 'Paper' AS title, 'doc-7' AS source, 'AI papers...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'search' AS chunk_type, 0.88 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-8' AS id, 'Paper Details' AS title, 'doc-8' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.85 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('Here are some papers.' AS response, STRUCT(0.95 AS total_response_time, 0.35 AS retrieval_time, 0.55 AS generation_time, 60 AS tokens_used, 1 AS chunks_considered) AS performance_metrics, STRUCT(0.88 AS max_similarity, 0.87 AS avg_similarity, 0.86 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-5'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(2 AS rating, 'search' AS category, 'Useful' AS comment, 'None' AS concern, 'List more papers' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('completeness' AS issue_type, 'Partial' AS root_cause, 'Expected paper list' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(2 AS context_understanding, 2 AS answer_accuracy, 2 AS answer_completeness, 2 AS clarity, 2 AS citation_quality) AS quality_scores, ['Add more papers'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 5
(
  'TC-0005', 'Dummy Case 5', 'Dummy for QA.', 'qa', 'medium',
  STRUCT('active' AS status, 'eve' AS owner, 'medium' AS priority, 'v1.3' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-005' AS source_session, [STRUCT('tagF' AS name, 'orange' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-4' AS name, '4.0' AS version, JSON '{"temperature":0.8,"max_tokens":600}' AS params) AS model,
    STRUCT('system prompt 5' AS system, 'user instruction 5' AS user_instruction) AS prompts,
    STRUCT(7 AS top_k, 0.80 AS similarity_threshold, TRUE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('What is ML?' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'What is ML?' AS query, 'ML is machine learning.' AS response, [STRUCT('chunk-9' AS id, 'ML' AS title, 'doc-9' AS source, 'ML...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'definition' AS chunk_type, 0.91 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-10' AS id, 'ML Details' AS title, 'doc-10' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.89 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('ML is machine learning.' AS response, STRUCT(1.50 AS total_response_time, 0.50 AS retrieval_time, 0.90 AS generation_time, 90 AS tokens_used, 2 AS chunks_considered) AS performance_metrics, STRUCT(0.91 AS max_similarity, 0.90 AS avg_similarity, 0.89 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-6'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(5 AS rating, 'accuracy' AS category, 'Good' AS comment, 'None' AS concern, 'Add more explanation' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('accuracy' AS issue_type, 'Correct' AS root_cause, 'Expected ML answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(5 AS context_understanding, 5 AS answer_accuracy, 5 AS answer_completeness, 5 AS clarity, 5 AS citation_quality) AS quality_scores, ['Clarify ML'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 6
(
  'TC-0006', 'Dummy Case 6', 'Dummy for recommendation.', 'recommendation', 'hard',
  STRUCT('inactive' AS status, 'frank' AS owner, 'low' AS priority, 'v2.1' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-006' AS source_session, [STRUCT('tagG' AS name, 'brown' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-3.5' AS name, '3.5' AS version, JSON '{"temperature":0.4,"max_tokens":200}' AS params) AS model,
    STRUCT('system prompt 6' AS system, 'user instruction 6' AS user_instruction) AS prompts,
    STRUCT(1 AS top_k, 0.55 AS similarity_threshold, FALSE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Suggest a tool.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Suggest a tool.' AS query, 'Try "TensorFlow".' AS response, [STRUCT('chunk-11' AS id, 'Tool' AS title, 'doc-11' AS source, 'TensorFlow...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'recommendation' AS chunk_type, 0.93 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-12' AS id, 'Tool Details' AS title, 'doc-12' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.90 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('Try "TensorFlow".' AS response, STRUCT(1.80 AS total_response_time, 0.70 AS retrieval_time, 1.10 AS generation_time, 110 AS tokens_used, 2 AS chunks_considered) AS performance_metrics, STRUCT(0.93 AS max_similarity, 0.92 AS avg_similarity, 0.91 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-7'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(4 AS rating, 'recommendation' AS category, 'Good tool' AS comment, 'None' AS concern, 'List more tools' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('coverage' AS issue_type, 'Limited' AS root_cause, 'Expected tool answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(4 AS context_understanding, 4 AS answer_accuracy, 4 AS answer_completeness, 4 AS clarity, 4 AS citation_quality) AS quality_scores, ['Expand tools'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 7
(
  'TC-0007', 'Dummy Case 7', 'Dummy for search.', 'search', 'easy',
  STRUCT('active' AS status, 'grace' AS owner, 'high' AS priority, 'v1.4' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-007' AS source_session, [STRUCT('tagH' AS name, 'pink' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-4' AS name, '4.0' AS version, JSON '{"temperature":0.6,"max_tokens":350}' AS params) AS model,
    STRUCT('system prompt 7' AS system, 'user instruction 7' AS user_instruction) AS prompts,
    STRUCT(4 AS top_k, 0.70 AS similarity_threshold, TRUE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Find ML tools.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Find ML tools.' AS query, 'Here are some tools.' AS response, [STRUCT('chunk-13' AS id, 'Tool' AS title, 'doc-13' AS source, 'ML tools...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'search' AS chunk_type, 0.87 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-14' AS id, 'Tool Details' AS title, 'doc-14' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.84 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('Here are some tools.' AS response, STRUCT(1.00 AS total_response_time, 0.30 AS retrieval_time, 0.50 AS generation_time, 70 AS tokens_used, 1 AS chunks_considered) AS performance_metrics, STRUCT(0.87 AS max_similarity, 0.86 AS avg_similarity, 0.85 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-8'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(3 AS rating, 'search' AS category, 'Useful' AS comment, 'None' AS concern, 'List more tools' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('completeness' AS issue_type, 'Partial' AS root_cause, 'Expected tool list' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(3 AS context_understanding, 3 AS answer_accuracy, 3 AS answer_completeness, 3 AS clarity, 3 AS citation_quality) AS quality_scores, ['Add more tools'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 8
(
  'TC-0008', 'Dummy Case 8', 'Dummy for QA.', 'qa', 'medium',
  STRUCT('inactive' AS status, 'heidi' AS owner, 'medium' AS priority, 'v1.5' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-008' AS source_session, [STRUCT('tagI' AS name, 'gray' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-3.5' AS name, '3.5' AS version, JSON '{"temperature":0.7,"max_tokens":400}' AS params) AS model,
    STRUCT('system prompt 8' AS system, 'user instruction 8' AS user_instruction) AS prompts,
    STRUCT(6 AS top_k, 0.78 AS similarity_threshold, FALSE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Explain AI ethics.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Explain AI ethics.' AS query, 'AI ethics is...' AS response, [STRUCT('chunk-15' AS id, 'Ethics' AS title, 'doc-15' AS source, 'AI ethics...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'definition' AS chunk_type, 0.89 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-16' AS id, 'Ethics Details' AS title, 'doc-16' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.86 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('AI ethics is...' AS response, STRUCT(1.30 AS total_response_time, 0.40 AS retrieval_time, 0.80 AS generation_time, 85 AS tokens_used, 2 AS chunks_considered) AS performance_metrics, STRUCT(0.89 AS max_similarity, 0.88 AS avg_similarity, 0.87 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-9'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(4 AS rating, 'accuracy' AS category, 'Good' AS comment, 'None' AS concern, 'Add more explanation' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('accuracy' AS issue_type, 'Correct' AS root_cause, 'Expected ethics answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(4 AS context_understanding, 4 AS answer_accuracy, 4 AS answer_completeness, 4 AS clarity, 4 AS citation_quality) AS quality_scores, ['Clarify ethics'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 9
(
  'TC-0009', 'Dummy Case 9', 'Dummy for recommendation.', 'recommendation', 'hard',
  STRUCT('active' AS status, 'ivan' AS owner, 'low' AS priority, 'v2.2' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-009' AS source_session, [STRUCT('tagJ' AS name, 'cyan' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-4' AS name, '4.0' AS version, JSON '{"temperature":0.5,"max_tokens":250}' AS params) AS model,
    STRUCT('system prompt 9' AS system, 'user instruction 9' AS user_instruction) AS prompts,
    STRUCT(8 AS top_k, 0.90 AS similarity_threshold, TRUE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Suggest a framework.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Suggest a framework.' AS query, 'Try "PyTorch".' AS response, [STRUCT('chunk-17' AS id, 'Framework' AS title, 'doc-17' AS source, 'PyTorch...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'recommendation' AS chunk_type, 0.94 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-18' AS id, 'Framework Details' AS title, 'doc-18' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.91 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('Try "PyTorch".' AS response, STRUCT(1.70 AS total_response_time, 0.65 AS retrieval_time, 1.05 AS generation_time, 115 AS tokens_used, 2 AS chunks_considered) AS performance_metrics, STRUCT(0.94 AS max_similarity, 0.93 AS avg_similarity, 0.92 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-10'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(5 AS rating, 'recommendation' AS category, 'Good framework' AS comment, 'None' AS concern, 'List more frameworks' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('coverage' AS issue_type, 'Limited' AS root_cause, 'Expected framework answer' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(5 AS context_understanding, 5 AS answer_accuracy, 5 AS answer_completeness, 5 AS clarity, 5 AS citation_quality) AS quality_scores, ['Expand frameworks'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
),
-- 10
(
  'TC-0010', 'Dummy Case 10', 'Dummy for search.', 'search', 'easy',
  STRUCT('inactive' AS status, 'judy' AS owner, 'high' AS priority, 'v1.6' AS version, CURRENT_TIMESTAMP() AS created_date, CURRENT_TIMESTAMP() AS updated_date, 'session-010' AS source_session, [STRUCT('tagK' AS name, 'lime' AS color)] AS tags),
  STRUCT(
    STRUCT('gpt-3.5' AS name, '3.5' AS version, JSON '{"temperature":0.3,"max_tokens":150}' AS params) AS model,
    STRUCT('system prompt 10' AS system, 'user instruction 10' AS user_instruction) AS prompts,
    STRUCT(9 AS top_k, 0.60 AS similarity_threshold, FALSE AS reranker_enabled) AS retrieval
  ),
  STRUCT(
    STRUCT('Find AI frameworks.' AS text, CURRENT_TIMESTAMP() AS timestamp) AS current_query,
    [STRUCT(1 AS turn, 'user' AS role, 'Find AI frameworks.' AS query, 'Here are some frameworks.' AS response, [STRUCT('chunk-19' AS id, 'Framework' AS title, 'doc-19' AS source, 'Frameworks...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'search' AS chunk_type, 0.88 AS confidence, 1 AS retrieval_rank) AS metadata)] AS retrieved_chunks, CURRENT_TIMESTAMP() AS timestamp)] AS conversation_history,
    [STRUCT('chunk-20' AS id, 'Framework Details' AS title, 'doc-20' AS source, 'Details...' AS content, STRUCT(CURRENT_TIMESTAMP() AS publish_date, CURRENT_TIMESTAMP() AS effective_date, CURRENT_TIMESTAMP() AS expiration_date, 'details' AS chunk_type, 0.85 AS confidence, 1 AS retrieval_rank) AS metadata)] AS current_retrieved_chunks
  ),
  STRUCT(
    STRUCT('Here are some frameworks.' AS response, STRUCT(1.10 AS total_response_time, 0.40 AS retrieval_time, 0.60 AS generation_time, 75 AS tokens_used, 1 AS chunks_considered) AS performance_metrics, STRUCT(0.88 AS max_similarity, 0.87 AS avg_similarity, 0.86 AS diversity_score) AS retrieval_quality, STRUCT('Reasoning...' AS reasoning_chain, ['citation-11'] AS citation_usage) AS generation_info) AS actual,
    STRUCT(3 AS rating, 'search' AS category, 'Useful' AS comment, 'None' AS concern, 'List more frameworks' AS suggested_improvement, CURRENT_TIMESTAMP() AS feedback_date, 'web' AS feedback_source) AS user_feedback
  ),
  STRUCT('completeness' AS issue_type, 'Partial' AS root_cause, 'Expected framework list' AS expected_answer, 'Criteria' AS acceptance_criteria, STRUCT(3 AS context_understanding, 3 AS answer_accuracy, 3 AS answer_completeness, 3 AS clarity, 3 AS citation_quality) AS quality_scores, ['Add more frameworks'] AS optimization_suggestions, 'No notes' AS notes, 'analyst' AS analyzed_by, CURRENT_TIMESTAMP() AS analysis_date)
);