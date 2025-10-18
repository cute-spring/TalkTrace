"""历史记录服务"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.history import HistoryRecord, HistorySearchRequest, SessionDetail
from app.services.demo_data import MOCK_HISTORY_DATA, AVAILABLE_MODELS, generate_more_history_data
from app.utils.logger import logger

class HistoryService:
    """历史记录服务类"""

    def __init__(self):
        """初始化历史记录服务"""
        # 加载演示数据
        base_data = MOCK_HISTORY_DATA + generate_more_history_data(15)

        # 转换为pandas DataFrame便于数据处理
        self.df = pd.DataFrame(base_data)

        # 确保created_at是datetime类型，使用更灵活的解析方式
        self.df['created_at'] = pd.to_datetime(self.df['created_at'], utc=True)

        logger.info("HistoryService initialized", record_count=len(self.df))

    async def search_history(self, request: HistorySearchRequest) -> Dict[str, Any]:
        """搜索历史记录"""
        logger.info("Searching history",
                   start_time=request.start_time,
                   end_time=request.end_time,
                   model_ids=request.model_ids,
                   keywords=request.keywords)

        # 复制DataFrame进行过滤
        filtered_df = self.df.copy()

        # 时间范围过滤
        start_dt = pd.to_datetime(request.start_time)
        end_dt = pd.to_datetime(request.end_time)

        mask = (filtered_df['created_at'] >= start_dt) & (filtered_df['created_at'] <= end_dt)
        filtered_df = filtered_df[mask]

        # 模型过滤
        if request.model_ids:
            filtered_df = filtered_df[filtered_df['model_id'].isin(request.model_ids)]

        # 评分范围过滤
        if request.rating_range and len(request.rating_range) == 2:
            min_rating, max_rating = request.rating_range
            filtered_df = filtered_df[
                (filtered_df['user_rating'] >= min_rating) &
                (filtered_df['user_rating'] <= max_rating)
            ]

        # 关键词搜索
        if request.keywords and request.keywords.strip():
            keywords = request.keywords.lower().strip()
            keyword_mask = (
                filtered_df['user_query'].str.lower().str.contains(keywords, na=False) |
                filtered_df['ai_response'].str.lower().str.contains(keywords, na=False)
            )
            filtered_df = filtered_df[keyword_mask]

        # 按时间倒序排序
        filtered_df = filtered_df.sort_values('created_at', ascending=False)

        # 分页
        total = len(filtered_df)
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        page_data = filtered_df.iloc[start_idx:end_idx]

        # 转换为字典格式
        items = []
        for _, row in page_data.iterrows():
            items.append({
                "session_id": row["session_id"],
                "user_query": row["user_query"],
                "ai_response": row["ai_response"],
                "user_rating": int(row["user_rating"]),
                "model_id": row["model_id"],
                "created_at": row["created_at"].isoformat() + "Z",
                "retrieval_chunks": row["retrieval_chunks"]
            })

        result = {
            "items": items,
            "total": total,
            "page": request.page,
            "page_size": request.page_size,
            "total_pages": (total + request.page_size - 1) // request.page_size
        }

        logger.info("History search completed",
                   total_results=total,
                   page=request.page,
                   items_returned=len(items))

        return result

    async def get_session_details(self, session_id: str) -> List[SessionDetail]:
        """获取指定会话的详细信息"""
        logger.info("Getting session details", session_id=session_id)

        # 查找指定会话的所有记录
        session_data = self.df[self.df['session_id'] == session_id].sort_values('created_at')

        if session_data.empty:
            logger.warning("Session not found", session_id=session_id)
            raise ValueError(f"Session {session_id} not found")

        # 转换为SessionDetail对象
        details = []
        for _, row in session_data.iterrows():
            detail = SessionDetail(
                session_id=row["session_id"],
                model_id=row["model_id"],
                user_query=row["user_query"],
                ai_response=row["ai_response"],
                created_at=row["created_at"],
                retrieval_chunks=row["retrieval_chunks"],
                user_feedback=None  # 演示数据中没有user_feedback
            )
            details.append(detail)

        logger.info("Session details retrieved",
                   session_id=session_id,
                   record_count=len(details))

        return details

    async def get_model_ids(self) -> List[str]:
        """获取所有可用的模型ID列表"""
        logger.info("Getting available model IDs")

        # 从数据中获取唯一的模型ID
        model_ids = sorted(self.df['model_id'].unique().tolist())

        logger.info("Model IDs retrieved",
                   model_count=len(model_ids),
                   models=model_ids)

        return model_ids

    async def test_connection(self) -> bool:
        """测试服务连接状态"""
        try:
            # 简单检查DataFrame是否可用
            _ = len(self.df)
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            return False