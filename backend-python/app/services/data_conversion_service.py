"""数据转换服务 - 将会话记录转换为测试用例"""
import json
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from app.models.test_case import (
    TestCase, TestCaseCreate, ModelConfig, PromptsConfig, RetrievalConfig,
    TestConfig, CurrentQuery, TurnRecord, RetrievedChunk, ChunkMetadata,
    TestCaseInput, ActualExecution, PerformanceMetrics, RetrievalQuality,
    Execution, UserFeedback, QualityScores, Analysis, Tag,
    TestCaseStatus, PriorityLevel, DifficultyLevel
)
from app.models.history import HistoryRecord, RetrievalChunk as HistoryRetrievalChunk
from app.services.bigquery_service import ConversationRow, RetrievalChunkRow
from app.utils.logger import logger


class DataConversionService:
    """数据转换服务类"""

    def __init__(self):
        """初始化数据转换服务"""
        logger.info("DataConversionService initialized")

    async def convert_session_to_test_case(
        self,
        session_data: List[ConversationRow],
        retrieval_chunks_map: Dict[str, RetrievalChunkRow],
        config: Optional[Dict[str, Any]] = None
    ) -> TestCaseCreate:
        """
        将会话数据转换为测试用例

        Args:
            session_data: 会话中的对话记录列表
            retrieval_chunks_map: 检索片段映射表 {chunk_id: RetrievalChunkRow}
            config: 转换配置参数

        Returns:
            TestCaseCreate: 创建测试用例的请求数据
        """
        logger.info("Converting session to test case",
                   session_length=len(session_data),
                   chunks_count=len(retrieval_chunks_map))

        if not session_data:
            raise ValueError("Session data cannot be empty")

        # 获取配置参数
        default_config = {
            "default_owner": "system@company.com",
            "default_priority": PriorityLevel.MEDIUM,
            "default_difficulty": DifficultyLevel.MEDIUM,
            "auto_generate_tags": True,
            "include_analysis": False
        }
        if config:
            # 确保传入的配置值也是正确的类型
            if "default_owner" in config and config["default_owner"]:
                default_config["default_owner"] = str(config["default_owner"])

            if "default_priority" in config and config["default_priority"]:
                # 将字符串转换为枚举
                if isinstance(config["default_priority"], str):
                    priority_map = {
                        "low": PriorityLevel.LOW,
                        "medium": PriorityLevel.MEDIUM,
                        "high": PriorityLevel.HIGH
                    }
                    default_config["default_priority"] = priority_map.get(config["default_priority"].lower(), PriorityLevel.MEDIUM)
                else:
                    default_config["default_priority"] = config["default_priority"]

            if "default_difficulty" in config and config["default_difficulty"]:
                # 将字符串转换为枚举
                if isinstance(config["default_difficulty"], str):
                    difficulty_map = {
                        "easy": DifficultyLevel.EASY,
                        "medium": DifficultyLevel.MEDIUM,
                        "hard": DifficultyLevel.HARD
                    }
                    default_config["default_difficulty"] = difficulty_map.get(config["default_difficulty"].lower(), DifficultyLevel.MEDIUM)
                else:
                    default_config["default_difficulty"] = config["default_difficulty"]

            # 其他配置项
            for key in ["auto_generate_tags", "include_analysis"]:
                if key in config:
                    default_config[key] = config[key]

        # 分析会话数据
        session_analysis = self._analyze_session(session_data)

        # 构建测试用例数据
        test_case_id = f"TC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"

        # 基本信息
        name = self._generate_test_case_name(session_data, session_analysis)
        description = self._generate_test_case_description(session_data, session_analysis)

        # 元数据
        metadata = {
            "status": TestCaseStatus.DRAFT,
            "owner": default_config["default_owner"],
            "priority": default_config["default_priority"],
            "tags": self._generate_tags(session_data, session_analysis, default_config["auto_generate_tags"]),
            "version": "1.0",
            "created_date": datetime.now().isoformat(),
            "source_session": session_data[0].session_id
        }

        # 领域和难度
        domain = session_analysis.get("domain", "general")
        difficulty = default_config["default_difficulty"]

        # 测试配置
        test_config = self._build_test_config(session_data, session_analysis)

        # 输入数据
        test_input = self._build_test_input(session_data, retrieval_chunks_map, session_analysis)

        # 执行结果
        execution = self._build_execution(session_data, session_analysis)

        # 分析数据（可选）
        analysis = None
        if default_config["include_analysis"]:
            analysis = self._generate_analysis(session_data, session_analysis)

        return TestCaseCreate(
            name=name,
            description=description,
            owner=metadata["owner"],
            priority=metadata["priority"],
            domain=domain,
            difficulty=difficulty,
            tags=metadata["tags"],
            test_config=test_config,
            input=test_input,
            execution=execution,
            analysis=analysis
        )

    def _analyze_session(self, session_data: List[ConversationRow]) -> Dict[str, Any]:
        """分析会话数据，提取关键信息"""
        if not session_data:
            return {}

        # 基础统计
        total_messages = len(session_data)
        user_messages = [msg for msg in session_data if msg.message_type == "user"]
        assistant_messages = [msg for msg in session_data if msg.message_type == "assistant"]

        # 时间分析
        start_time = min(msg.timestamp for msg in session_data)
        end_time = max(msg.timestamp for msg in session_data)
        duration = (end_time - start_time).total_seconds()

        # 模型信息
        models_used = list(set(msg.model_id for msg in session_data if msg.model_id))
        primary_model = max(set(msg.model_id for msg in session_data),
                          key=lambda x: sum(1 for msg in session_data if msg.model_id == x))

        # 评分分析
        ratings = [msg.user_rating for msg in session_data if msg.user_rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        # 话题分析（简单关键词提取）
        all_content = " ".join(msg.content for msg in user_messages if msg.content)
        topics = self._extract_topics(all_content)

        # 复杂度评估
        avg_message_length = sum(len(msg.content) for msg in session_data) / total_messages
        complexity = self._assess_complexity(session_data, avg_message_length)

        return {
            "total_messages": total_messages,
            "user_messages_count": len(user_messages),
            "assistant_messages_count": len(assistant_messages),
            "duration_seconds": duration,
            "models_used": models_used,
            "primary_model": primary_model,
            "avg_rating": avg_rating,
            "topics": topics,
            "domain": self._infer_domain(topics, all_content),
            "complexity": complexity,
            "avg_message_length": avg_message_length,
            "has_multiturn": len(user_messages) > 1,
            "has_context_references": self._has_context_references(session_data),
            "retrieval_activity": len(set(chunk_id for msg in session_data for chunk_id in msg.retrieval_chunk_ids or []))
        }

    def _extract_topics(self, content: str) -> List[str]:
        """提取话题关键词"""
        # 简单的关键词提取逻辑
        topic_keywords = {
            "finance": ["投资", "基金", "股票", "理财", "收益", "风险", "资产", "金融"],
            "technology": ["编程", "代码", "技术", "开发", "软件", "算法", "数据", "系统"],
            "healthcare": ["健康", "医疗", "疾病", "治疗", "药物", "医生", "症状", "诊断"],
            "education": ["学习", "教育", "课程", "知识", "技能", "培训", "考试", "学校"],
            "general": ["问题", "帮助", "信息", "建议", "方法", "解决方案", "情况", "如何"]
        }

        topics = []
        content_lower = content.lower()

        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ["general"]

    def _infer_domain(self, topics: List[str], content: str) -> str:
        """推断主要领域"""
        if not topics:
            return "general"

        # 优先级排序
        domain_priority = ["finance", "technology", "healthcare", "education", "general"]

        for domain in domain_priority:
            if domain in topics:
                return domain

        return topics[0]

    def _assess_complexity(self, session_data: List[ConversationRow], avg_length: float) -> str:
        """评估对话复杂度"""
        # 基于多个因素评估复杂度
        factors = {
            "length_score": min(avg_length / 200, 1.0),  # 消息长度
            "turn_score": min(len(session_data) / 10, 1.0),  # 对话轮次
            "context_score": 1.0 if self._has_context_references(session_data) else 0.5,  # 上下文引用
        }

        total_score = sum(factors.values()) / len(factors)

        if total_score >= 0.7:
            return DifficultyLevel.HARD
        elif total_score >= 0.4:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.EASY

    def _has_context_references(self, session_data: List[ConversationRow]) -> bool:
        """检查是否有上下文引用"""
        context_indicators = ["上面", "前面", "刚才", "之前", "那个", "这个", "第", "首先", "其次"]

        for msg in session_data:
            if msg.message_type == "user" and msg.content:
                content_lower = msg.content.lower()
                if any(indicator in content_lower for indicator in context_indicators):
                    return True

        return False

    def _generate_test_case_name(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> str:
        """生成测试用例名称"""
        # 获取第一个用户问题
        first_user_msg = next((msg for msg in session_data if msg.message_type == "user"), None)

        if first_user_msg and first_user_msg.content:
            # 截取前50个字符作为名称
            name = first_user_msg.content[:50]
            if len(first_user_msg.content) > 50:
                name += "..."
        else:
            # 基于分析信息生成名称
            topics = analysis.get("topics", [])
            domain = analysis.get("domain", "general")
            name = f"{domain}领域对话测试"

            if topics:
                name += f" - {', '.join(topics[:2])}"

        return name

    def _generate_test_case_description(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> str:
        """生成测试用例描述"""
        desc_parts = []

        # 基础信息
        desc_parts.append(f"包含 {analysis.get('total_messages', 0)} 条对话记录")
        desc_parts.append(f"使用模型: {analysis.get('primary_model', 'unknown')}")

        if analysis.get("avg_rating"):
            desc_parts.append(f"平均评分: {analysis['avg_rating']:.1f}/5")

        if analysis.get("has_multiturn"):
            desc_parts.append("多轮对话场景")

        if analysis.get("has_context_references"):
            desc_parts.append("包含上下文引用")

        # 话题信息
        topics = analysis.get("topics", [])
        if topics:
            desc_parts.append(f"涉及话题: {', '.join(topics)}")

        return "；".join(desc_parts)

    def _generate_tags(self, session_data: List[ConversationRow], analysis: Dict[str, Any], auto_generate: bool) -> List[Tag]:
        """生成标签"""
        tags = []

        if auto_generate:
            # 基于分析自动生成标签
            if analysis.get("has_multiturn"):
                tags.append(Tag(name="多轮对话", color="blue"))

            if analysis.get("has_context_references"):
                tags.append(Tag(name="上下文理解", color="orange"))

            if analysis.get("avg_rating", 0) >= 4:
                tags.append(Tag(name="高质量", color="green"))
            elif analysis.get("avg_rating", 0) <= 2:
                tags.append(Tag(name="需改进", color="red"))

            # 复杂度标签
            complexity = analysis.get("complexity", "medium")
            complexity_colors = {"easy": "green", "medium": "orange", "hard": "red"}
            tags.append(Tag(name=f"复杂度:{complexity}", color=complexity_colors.get(complexity, "default")))

            # 领域标签
            domain = analysis.get("domain", "general")
            domain_colors = {
                "finance": "gold",
                "technology": "blue",
                "healthcare": "green",
                "education": "purple"
            }
            tags.append(Tag(name=domain, color=domain_colors.get(domain, "default")))

        return tags

    def _build_test_config(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> TestConfig:
        """构建测试配置"""
        # 获取主要模型配置
        primary_model = analysis.get("primary_model", "gpt-4o-mini")

        model_config = ModelConfig(
            name=primary_model,
            version="latest",  # 默认版本
            params={
                "temperature": 0.0,  # 默认参数
                "max_tokens": 512,
                "top_p": 0.9
            }
        )

        # 默认提示词配置
        prompts_config = PromptsConfig(
            system="你是一个有用的AI助手，请基于提供的文档信息回答用户的问题。",
            user_instruction="使用提供的检索到的文档片段来回答用户的当前查询。请确保答案准确、相关且有帮助。"
        )

        # 检索配置
        retrieval_config = RetrievalConfig(
            top_k=5,
            similarity_threshold=0.7,
            reranker_enabled=True
        )

        return TestConfig(
            model=model_config,
            prompts=prompts_config,
            retrieval=retrieval_config
        )

    def _build_test_input(
        self,
        session_data: List[ConversationRow],
        retrieval_chunks_map: Dict[str, RetrievalChunkRow],
        analysis: Dict[str, Any]
    ) -> TestCaseInput:
        """构建测试输入数据"""
        # 获取最后一条用户消息作为当前查询
        user_messages = [msg for msg in session_data if msg.message_type == "user"]
        if not user_messages:
            raise ValueError("No user messages found in session")

        last_user_msg = user_messages[-1]
        current_query = CurrentQuery(
            text=last_user_msg.content,
            timestamp=last_user_msg.timestamp.isoformat()
        )

        # 构建对话历史（包含上下文重建）
        conversation_history = self._build_conversation_history_with_context(
            session_data, analysis
        )

        # 构建当前检索片段
        current_retrieved_chunks = self._build_retrieved_chunks(
            last_user_msg.retrieval_chunk_ids or [],
            retrieval_chunks_map
        )

        return TestCaseInput(
            current_query=current_query,
            conversation_history=conversation_history,
            current_retrieved_chunks=current_retrieved_chunks
        )

    def _build_conversation_history_with_context(
        self,
        session_data: List[ConversationRow],
        analysis: Dict[str, Any]
    ) -> List[TurnRecord]:
        """构建包含上下文信息的对话历史"""
        conversation_history = []
        turn = 1

        # 获取所有对话轮次
        dialog_turns = self._extract_dialogue_turns(session_data)

        for turn_data in dialog_turns:
            # 处理上下文引用
            processed_query = self._process_context_references(
                turn_data.get("query", ""),
                conversation_history,
                turn
            )

            turn_record = TurnRecord(
                turn=turn,
                role=turn_data["role"],
                query=processed_query if turn_data["role"] == "user" else None,
                response=turn_data.get("response"),
                retrieved_chunks=turn_data.get("retrieved_chunks", []),
                timestamp=turn_data["timestamp"]
            )
            conversation_history.append(turn_record)
            turn += 1

        return conversation_history

    def _extract_dialogue_turns(self, session_data: List[ConversationRow]) -> List[Dict[str, Any]]:
        """提取对话轮次"""
        dialog_turns = []
        current_turn = {}

        for msg in session_data:
            if msg.message_type == "user":
                # 如果当前轮次有AI回复，先保存
                if current_turn.get("role") == "assistant":
                    dialog_turns.append(current_turn)

                # 开始新的用户轮次
                current_turn = {
                    "role": "user",
                    "query": msg.content,
                    "retrieved_chunks": msg.retrieval_chunk_ids or [],
                    "timestamp": msg.timestamp.isoformat()
                }
            elif msg.message_type == "assistant" and current_turn.get("role") == "user":
                # 添加AI回复到当前轮次
                current_turn["role"] = "assistant"
                current_turn["response"] = msg.content
                current_turn["retrieved_chunks"] = msg.retrieval_chunk_ids or []
                current_turn["timestamp"] = msg.timestamp.isoformat()
                dialog_turns.append(current_turn)
                current_turn = {}

        # 保存最后一个轮次
        if current_turn.get("role"):
            dialog_turns.append(current_turn)

        return dialog_turns

    def _process_context_references(
        self,
        query: str,
        conversation_history: List[TurnRecord],
        current_turn: int
    ) -> str:
        """处理上下文引用，重建完整查询"""
        if not query:
            return query

        # 上下文引用标识符
        context_patterns = [
            r"上面[^\n]*?说",
            r"前面[^\n]*?提",
            r"刚才[^\n]*?讲",
            r"之前[^\n]*?提",
            r"那个[^\n]*?问题",
            r"这个[^\n]*?方案",
            r"第[一二三四五六七八九十\d]+[^\n]*?个",
            r"首先",
            r"其次",
            r"然后"
        ]

        # 检测是否有上下文引用
        has_context_reference = any(
            re.search(pattern, query, re.IGNORECASE)
            for pattern in context_patterns
        )

        if not has_context_reference or current_turn <= 2:
            return query

        # 获取历史上下文
        context_info = self._extract_context_info(conversation_history, current_turn)

        # 构建包含上下文的查询
        if context_info:
            context_prefix = self._build_context_description(context_info)
            return f"[上下文: {context_prefix}]\n\n当前问题: {query}"

        return query

    def _extract_context_info(self, conversation_history: List[TurnRecord], current_turn: int) -> Dict[str, Any]:
        """提取上下文信息"""
        if len(conversation_history) < 2:
            return {}

        # 获取前几轮对话作为上下文
        relevant_turns = conversation_history[-3:-1]  # 最近3轮对话

        context_info = {
            "previous_queries": [],
            "previous_responses": [],
            "topics": set(),
            "entities": set()
        }

        for turn in relevant_turns:
            if turn.query:
                context_info["previous_queries"].append(turn.query)
                # 简单的实体提取（后续可以优化为更复杂的NLP处理）
                entities = self._extract_simple_entities(turn.query)
                context_info["entities"].update(entities)

            if turn.response:
                context_info["previous_responses"].append(turn.response)
                # 提取话题关键词
                topics = self._extract_topic_keywords(turn.response)
                context_info["topics"].update(topics)

        # 转换set为list
        context_info["topics"] = list(context_info["topics"])
        context_info["entities"] = list(context_info["entities"])

        return context_info

    def _extract_simple_entities(self, text: str) -> List[str]:
        """简单的实体提取"""
        # 这里可以集成更复杂的实体识别服务
        # 目前使用简单的规则匹配
        import re

        # 提取可能的实体（名词、专有名词等）
        entities = []

        # 提取引号中的内容
        quoted = re.findall(r'["""]([^"""]+)["""]', text)
        entities.extend(quoted)

        # 提取大写开头的词汇（可能是专有名词）
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.extend(proper_nouns)

        # 提取数字和单位
        numbers = re.findall(r'\d+\s*(?:个|条|种|项|美元|元|%)', text)
        entities.extend(numbers)

        return list(set(entities))  # 去重

    def _extract_topic_keywords(self, text: str) -> List[str]:
        """提取话题关键词"""
        # 预定义的话题关键词
        topic_keywords = {
            "finance": ["投资", "基金", "股票", "理财", "收益", "风险", "资产", "金融", "利率", "保险"],
            "technology": ["编程", "代码", "技术", "开发", "软件", "算法", "数据", "系统", "网络", "数据库"],
            "healthcare": ["健康", "医疗", "疾病", "治疗", "药物", "医生", "症状", "诊断", "护理"],
            "education": ["学习", "教育", "课程", "知识", "技能", "培训", "考试", "学校", "专业"],
            "business": ["商业", "企业", "管理", "市场", "销售", "客户", "产品", "服务", "竞争"],
            "general": ["问题", "帮助", "信息", "建议", "方法", "解决方案", "情况", "如何"]
        }

        found_topics = []
        text_lower = text.lower()

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)

        return found_topics if found_topics else ["general"]

    def _build_context_description(self, context_info: Dict[str, Any]) -> str:
        """构建上下文描述"""
        descriptions = []

        # 添加最近的问题
        if context_info.get("previous_queries"):
            last_query = context_info["previous_queries"][-1]
            descriptions.append(f"用户刚才询问了关于'{last_query[:50]}...'的问题")

        # 添加主要话题
        if context_info.get("topics"):
            topics_str = "、".join(context_info["topics"][:3])
            descriptions.append(f"讨论话题包括: {topics_str}")

        # 添加关键实体
        if context_info.get("entities"):
            entities_str = "、".join(context_info["entities"][:5])
            descriptions.append(f"涉及实体: {entities_str}")

        return "；".join(descriptions)

    def _build_retrieved_chunks(
        self,
        chunk_ids: List[str],
        retrieval_chunks_map: Dict[str, RetrievalChunkRow]
    ) -> List[RetrievedChunk]:
        """构建检索片段列表"""
        retrieved_chunks = []

        for rank, chunk_id in enumerate(chunk_ids):
            if chunk_id in retrieval_chunks_map:
                chunk_row = retrieval_chunks_map[chunk_id]

                # 计算内容摘要
                content_preview = self._generate_content_preview(chunk_row.content)

                chunk_metadata = ChunkMetadata(
                    publish_date=chunk_row.metadata.get("publish_date"),
                    effective_date=chunk_row.metadata.get("effective_date"),
                    expiration_date=chunk_row.metadata.get("expiration_date"),
                    chunk_type=chunk_row.metadata.get("chunk_type", "text"),
                    confidence=chunk_row.similarity_score or 0.8,
                    retrieval_rank=rank + 1
                )

                retrieved_chunk = RetrievedChunk(
                    id=chunk_row.chunk_id,
                    title=chunk_row.title or content_preview[:50] + "...",
                    source=chunk_row.metadata.get("source", "未知来源"),
                    content=chunk_row.content,
                    metadata=chunk_metadata
                )
                retrieved_chunks.append(retrieved_chunk)

        return retrieved_chunks

    def _generate_content_preview(self, content: str, max_length: int = 100) -> str:
        """生成内容预览"""
        if not content:
            return "无内容"

        # 移除多余的空白字符
        cleaned_content = re.sub(r'\s+', ' ', content.strip())

        if len(cleaned_content) <= max_length:
            return cleaned_content

        # 在句号、问号或感叹号处截断
        for i in range(max_length, max(0, max_length-50), -1):
            if cleaned_content[i] in '。！？.!?':
                return cleaned_content[:i+1]

        # 如果没有合适的标点符号，直接截断
        return cleaned_content[:max_length] + "..."

    def _build_execution(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> Execution:
        """构建执行结果数据"""
        # 获取最后一条AI回复作为实际执行结果
        assistant_messages = [msg for msg in session_data if msg.message_type == "assistant"]
        if not assistant_messages:
            raise ValueError("No assistant messages found in session")

        last_assistant_msg = assistant_messages[-1]

        # 性能指标（基于现有数据估算）
        performance_metrics = PerformanceMetrics(
            total_response_time=last_assistant_msg.processing_time_ms / 1000.0 if last_assistant_msg.processing_time_ms else 2.0,
            retrieval_time=0.3,  # 默认检索时间
            generation_time=(last_assistant_msg.processing_time_ms / 1000.0 - 0.3) if last_assistant_msg.processing_time_ms else 1.7,
            tokens_used=last_assistant_msg.token_count or 300,
            chunks_considered=len(last_assistant_msg.retrieval_chunk_ids or [])
        )

        # 检索质量（如果有检索片段数据）
        retrieval_quality = None
        if last_assistant_msg.retrieval_chunk_ids:
            # 这里可以根据实际的检索片段质量数据来设置
            retrieval_quality = RetrievalQuality(
                max_similarity=0.85,
                avg_similarity=0.75,
                diversity_score=0.65
            )

        actual_execution = ActualExecution(
            response=last_assistant_msg.content,
            performance_metrics=performance_metrics,
            retrieval_quality=retrieval_quality
        )

        # 用户反馈
        user_feedback = None
        if last_assistant_msg.user_rating is not None:
            user_feedback = UserFeedback(
                rating=last_assistant_msg.user_rating,
                category=self._categorize_feedback(last_assistant_msg.user_rating),
                comment=last_assistant_msg.feedback_text or "",
                concern="",  # 可以从反馈文本中提取
                suggested_improvement="",  # 可以从反馈文本中提取
                feedback_date=last_assistant_msg.timestamp.isoformat(),
                feedback_source="user"
            )

        return Execution(
            actual=actual_execution,
            user_feedback=user_feedback
        )

    def _categorize_feedback(self, rating: int) -> str:
        """根据评分分类反馈"""
        if rating >= 4:
            return "positive"
        elif rating >= 3:
            return "neutral"
        else:
            return "negative"

    def _generate_analysis(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> Analysis:
        """生成分析数据"""
        # 基于会话数据生成初步分析
        avg_rating = analysis.get("avg_rating", 3)

        # 质量评分
        quality_scores = QualityScores(
            context_understanding=4 if analysis.get("has_context_references") else 3,
            answer_accuracy=min(max(avg_rating, 1), 5),
            answer_completeness=min(max(avg_rating * 0.9, 1), 5),
            clarity=min(max(avg_rating * 1.1, 1), 5),
            citation_quality=4 if analysis.get("retrieval_activity", 0) > 0 else 2
        )

        # 问题类型分析
        issue_type = self._identify_issue_type(session_data, avg_rating)
        root_cause = self._identify_root_cause(session_data, analysis)

        # 生成期望答案和验收标准
        expected_answer = self._generate_expected_answer(session_data)
        acceptance_criteria = self._generate_acceptance_criteria(session_data, analysis)

        # 优化建议
        optimization_suggestions = self._generate_optimization_suggestions(session_data, analysis)

        return Analysis(
            issue_type=issue_type,
            root_cause=root_cause,
            expected_answer=expected_answer,
            acceptance_criteria=acceptance_criteria,
            quality_scores=quality_scores,
            optimization_suggestions=optimization_suggestions,
            notes="系统自动生成的初步分析，建议人工审核和补充。",
            analyzed_by="system@company.com",
            analysis_date=datetime.now().isoformat()
        )

    def _identify_issue_type(self, session_data: List[ConversationRow], avg_rating: float) -> str:
        """识别问题类型"""
        if avg_rating >= 4:
            return "good_example"
        elif avg_rating >= 3:
            return "minor_improvement"
        else:
            # 分析具体问题
            user_messages = [msg for msg in session_data if msg.message_type == "user"]
            if self._has_context_references(user_messages):
                return "context_understanding"
            else:
                return "answer_quality"

    def _identify_root_cause(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> str:
        """识别根本原因"""
        complexity = analysis.get("complexity", "medium")
        retrieval_activity = analysis.get("retrieval_activity", 0)

        if retrieval_activity == 0:
            return "缺少相关检索内容"
        elif complexity == "hard":
            return "问题复杂度高，需要更深入的推理"
        elif analysis.get("has_context_references"):
            return "上下文理解不准确"
        else:
            return "回答质量需要改进"

    def _generate_expected_answer(self, session_data: List[ConversationRow]) -> str:
        """生成期望答案"""
        # 获取最后一条用户问题
        user_messages = [msg for msg in session_data if msg.message_type == "user"]
        if not user_messages:
            return ""

        last_question = user_messages[-1].content
        return f"针对问题'{last_question}'，期望得到准确、完整且相关的回答。"

    def _generate_acceptance_criteria(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> str:
        """生成验收标准"""
        criteria = []

        criteria.append("1. 回答必须准确且相关")
        criteria.append("2. 回答必须完整，解决用户问题")

        if analysis.get("has_context_references"):
            criteria.append("3. 必须正确理解对话上下文")

        if analysis.get("retrieval_activity", 0) > 0:
            criteria.append("4. 应该有效利用检索到的文档片段")

        criteria.append("5. 语言表达清晰易懂")

        return "\n".join(criteria)

    def _generate_optimization_suggestions(self, session_data: List[ConversationRow], analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        avg_rating = analysis.get("avg_rating", 3)
        if avg_rating < 3:
            suggestions.append("提高回答的准确性和相关性")
            suggestions.append("增加回答的详细程度")

        if analysis.get("has_context_references"):
            suggestions.append("改进对话上下文的理解和跟踪")

        if analysis.get("retrieval_activity", 0) == 0:
            suggestions.append("考虑启用检索功能以获得更多信息")

        complexity = analysis.get("complexity", "medium")
        if complexity == "hard":
            suggestions.append("对于复杂问题，建议分步骤回答")

        if not suggestions:
            suggestions.append("继续保持当前质量水平")

        return suggestions


# 全局实例
data_conversion_service = DataConversionService()