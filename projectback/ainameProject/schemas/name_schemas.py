from pydantic import BaseModel,Field,model_validator
from typing import Annotated,List,Literal

class NameSchema(BaseModel):
    name: Annotated[str,Field(...)]
    reference: Annotated[str,Field(...)]
    moral: Annotated[str,Field(...)]
    # 👇 新增：强迫大模型为每个名字设计一个专属域名
    domain: str = Field(..., description="为该品牌设计的纯小写 .com 域名，例如:astar.com")
    # 👇 新增：默认状态，稍后由我们的工具自动填入
    domain_status: str = Field(default="正在查询...", description="域名的注册状态")

class NameResultSchema(BaseModel):
    names: List[NameSchema]

CategoryLiteral = Literal["人名", "企业名", "宠物名"]
class NameIn(BaseModel):
    category: Annotated[CategoryLiteral,Field("人名")]
    surname: Annotated[str,Field("")]
    gender: Annotated[Literal["男","女","不限"],Field("不限",description="性别")]
    length: Annotated[Literal["单字","两字","不限"],Field("不限",description="字数")]
    other: Annotated[str | None, Field("", description="其他要求")]
    exclude: Annotated[List[str], Field([], description="排除的名字")]

    @model_validator(mode="after")
    def validate_fields_by_category(self):
        if self.category == "人名" and not self.surname:
            raise ValueError("生成人名时，必须填姓氏")
        return self

class NameWithThreadOut(BaseModel):
    thread_id: str
    names: List[NameSchema]

class FeedbackIn(BaseModel):
    thread_id: str = Field(..., description="前端回传的会话ID")
    category: Literal["人名", "企业名", "宠物名"] = Field(..., description="路由依据")
    feedback: str = Field(..., description="用户的修改意见，如：换成带水字旁的字")
