import uuid
import threading
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from kerag.api import KERAGAPI

# 配置全局logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("kerag_mcp")


class SessionManager:
    """管理基于会话的KERAG API实例"""

    def __init__(self):
        self._sessions: Dict[str, KERAGAPI] = {}
        self._session_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        # self._logger = logging.getLogger("kerag_mcp.SessionManager")
        # self._logger.info("SessionManager initialized")

    def create_session(
        self,
        session_id: Optional[str] = None,
        local_root: Optional[str] = None,
        global_root: Optional[str] = None,
        lang: Optional[str] = None
    ) -> KERAGAPI:
        """创建新会话，返回API实例

        如果提供了session_id且该会话已存在，则更新其配置。
        否则创建新的会话。

        Args:
            session_id: 会话ID（可选）
            local_root: 本地知识库根路径
            global_root: 全局知识库根路径
            lang: 语言偏好

        Returns:
            KERAGAPI实例
        """
        # if not session_id:
            # session_id = str(uuid.uuid4())

        api = KERAGAPI(
            local_root=local_root,
            global_root=global_root,
            lang=lang
        )

        with self._lock:
            self._sessions[session_id] = api
            self._session_metadata[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "request_count": 0,
                "config": {
                    "local_root": local_root,
                    "global_root": global_root,
                    "lang": lang
                }
            }

        return api

    def get_session(self, session_id: str) -> Optional[KERAGAPI]:
        """获取会话的API实例

        Args:
            session_id: 会话ID

        Returns:
            KERAGAPI实例，如果会话不存在返回None
        """
        # if not session_id:
        #     return None

        with self._lock:
            api = self._sessions.get(session_id)
            if api and session_id in self._session_metadata:
                self._session_metadata[session_id]["last_accessed"] = datetime.now()
                self._session_metadata[session_id]["request_count"] += 1
            return api

    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话元数据

        Args:
            session_id: 会话ID

        Returns:
            会话元数据字典，如果会话不存在返回None
        """
        with self._lock:
            return self._session_metadata.get(session_id)

    def destroy_session(self, session_id: str) -> bool:
        """销毁会话

        Args:
            session_id: 要销毁的会话ID

        Returns:
            如果成功销毁返回True，如果会话不存在返回False
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                del self._session_metadata[session_id]
                return True
            return False

    def cleanup_expired_sessions(self, max_idle_seconds: int = 3600) -> int:
        """清理过期会话

        Args:
            max_idle_seconds: 最大空闲时间（秒），默认为3600秒（1小时）

        Returns:
            清理的会话数量
        """
        now = datetime.now()
        expired = []

        with self._lock:
            for session_id, metadata in self._session_metadata.items():
                idle_time = (now - metadata["last_accessed"]).total_seconds()
                if idle_time > max_idle_seconds:
                    expired.append(session_id)

            for session_id in expired:
                self.destroy_session(session_id)

        return len(expired)

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """获取所有会话信息

        Returns:
            会话ID到元数据的字典
        """
        with self._lock:
            return dict(self._session_metadata)


# 全局会话管理器实例
_session_manager: Optional[SessionManager] = None
_session_manager_lock = threading.Lock()


def get_session_manager() -> SessionManager:
    """获取全局会话管理器实例"""
    global _session_manager

    if _session_manager is None:
        with _session_manager_lock:
            if _session_manager is None:
                _session_manager = SessionManager()

    return _session_manager
