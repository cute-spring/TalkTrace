-- 数据库初始化脚本
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建索引（Prisma会自动创建基本索引，这里添加额外的性能优化索引）

-- 全文搜索索引
CREATE INDEX IF NOT EXISTS idx_test_case_name_fts ON test_cases USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_test_case_description_fts ON test_cases USING gin(to_tsvector('english', description));

-- 复合索引优化常用查询
CREATE INDEX IF NOT EXISTS idx_test_cases_status_created ON test_cases(status, created_date DESC);
CREATE INDEX IF NOT EXISTS idx_test_cases_domain_status ON test_cases(domain, status);
CREATE INDEX IF NOT EXISTS idx_test_cases_owner_status ON test_cases(owner, status);

-- JSON字段索引（PostgreSQL 12+）
CREATE INDEX IF NOT EXISTS idx_test_cases_config_gin ON test_cases USING gin(test_config);
CREATE INDEX IF NOT EXISTS idx_test_cases_input_gin ON test_cases USING gin(input_data);

-- 导入任务状态和创建时间复合索引
CREATE INDEX IF NOT EXISTS idx_import_tasks_status_created ON import_tasks(status, created_date DESC);

-- 质量评分复合索引
CREATE INDEX IF NOT EXISTS idx_quality_scores_test_case_date ON quality_scores(test_case_id, scored_date DESC);

-- 标签名称的模糊搜索索引
CREATE INDEX IF NOT EXISTS idx_tags_name_trgm ON tags USING gin(name gin_trgm_ops);

-- 数据库统计信息更新
ANALYZE;

-- 设置时区
SET timezone = 'UTC';

-- 创建数据库用户（如果需要）
-- CREATE USER talk_trace_user WITH PASSWORD 'your_secure_password';
-- GRANT CONNECT ON DATABASE talk_trace TO talk_trace_user;
-- GRANT USAGE ON SCHEMA public TO talk_trace_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO talk_trace_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO talk_trace_user;