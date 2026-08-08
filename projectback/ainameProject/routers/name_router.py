from fastapi import APIRouter, HTTPException
from fastapi import APIRouter,Depends
router = APIRouter(prefix="/name")

from core.authtools import AuthHandler

from schemas.name_schemas import NameIn
from core.nametools import generate_name
from schemas.name_schemas import NameWithThreadOut
from repository.credit_repo import  CreditRepository
auth_handler = AuthHandler()
from dependencies import  get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from core.workflow import genrate_naming


# 第一次生成名字的接口
@router.post("/generate", response_model=NameWithThreadOut)
async def get_names(data:NameIn,user_id:int = Depends(auth_handler.auth_access_dependency),
                    session:AsyncSession=Depends(get_session)):

      creditRepository =  CreditRepository(session)
      balance = await creditRepository.get_credit(user_id)
      # 1.先查询剩余的起名次数，如果有，调用起名工具，如果没有，告诉用户充值
      if balance<=0:
            raise HTTPException(status_code=400,detail="余额不足，请充值后使用")

      # 2.调用起名接口
      # name_result = await generate_name(data)
      name_result = await genrate_naming(data,user_id)
      # 3.起名后，在账户中次数减1，日志中添加一条数据，消费成功
      await creditRepository.consume_name_credit(user_id=user_id)

      thread_id = name_result.get("thread_id")
      final_output = name_result.get("final_output")
      names = final_output["names"]
      print(names)
      try:
            return NameWithThreadOut(thread_id=thread_id,names=final_output["names"])
      except Exception as e:
            print(e)

from schemas.name_schemas import FeedbackIn
from core.workflow import feedback_naming
# 第n次，n>=2 调整大模型生成的名字
@router.post("/feedback", response_model=NameWithThreadOut)
async def take_names_feedback(data:FeedbackIn
                              ,user_id:int=Depends(auth_handler.auth_access_dependency)
                              ,session:AsyncSession=Depends(get_session)):
      creditRepository = CreditRepository(session)
      balance = await creditRepository.get_credit(user_id)
      # 1.先查询剩余的起名次数，如果有，调用起名工具，如果没有，告诉用户充值
      if balance <= 0:
            raise HTTPException(status_code=400, detail="余额不足，请充值后使用")

      # 2.调用起名接口
      name_result = await feedback_naming(data, user_id)
      # 3.起名后，在账户中次数减1，日志中添加一条数据，消费成功
      await creditRepository.consume_name_credit(user_id=user_id)

      thread_id = name_result.get("thread_id")
      final_output = name_result.get("final_output")
      names = final_output["names"]
      print(names)
      try:
            return NameWithThreadOut(thread_id=thread_id, names=final_output["names"])
      except Exception as e:
            print(e)

# @router.post("/get_names", response_model=NameResultSchema)
# async def get_names(data:NameIn,user_id:int = Depends(auth_handler.auth_access_dependency),
#                     session:AsyncSession=Depends(get_session)):
#
#       creditRepository =  CreditRepository(session)
#       balance = await creditRepository.get_credit(user_id)
#       # 1.先查询剩余的起名次数，如果有，调用起名工具，如果没有，告诉用户充值
#       if balance<=0:
#             raise HTTPException(status_code=400,detail="余额不足，请充值后使用")
#
#       print(user_id)
#       # 2.调用起名接口
#       # name_result = await generate_name(data)
#       name_result = await genrate_naming(data,user_id)
#       # 3.起名后，在账户中次数减1，日志中添加一条数据，消费成功
#       await creditRepository.consume_name_credit(user_id=user_id)
#
#       return name_result

