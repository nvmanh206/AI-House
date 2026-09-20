from dataclasses import dataclass
from uuid import uuid4
from app.security import household_context

@dataclass(frozen=True)
class AgentContext:
    user_id: str
    household_id: str
    role: str
    permissions: tuple[str,...]
    timezone: str = 'Asia/Ho_Chi_Minh'
    locale: str = 'vi-VN'
    request_id: str = ''

def build_context(auth,repo):
    member=household_context(auth,repo)
    return AgentContext(auth[0].id,member.household_id,member.role,tuple(member.permissions),request_id=str(uuid4()))
