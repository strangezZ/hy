from sqlalchemy import Column, String, Numeric
from entities.base import Base

class Task(Base):

    __tablename__ = 'shengchanRequire'
    code = Column('code',String(4),primary_key=True)
    introducer = Column('introducer', String(10))
    introducerDate = Column('introducerDate', String(17))
    Auditing = Column('Auditing',String(4))      #审核码  Y审核，N未审核
    defineStr1 = Column('defineStr1',Numeric)     #状态码  8结案，非8有效
    defineStr2 = Column('defineStr2', String(20))   # 工作中心/车间编号
    defineStr3 = Column('defineStr3',String(10))   #生产线
    refercode = Column('refercode',String(10))  #订单单号
    defineStr4 = Column('defineStr4',String(10))   #订单项次
    materalcode = Column('materalcode', String(20))  # 产品编码
    quantity = Column('quantity', Numeric)  # 生产数量
    defineStr8 = Column('defineStr8',Numeric)    #发料套数
    defineStr9 = Column('defineStr9',Numeric)     #入库量
    finishdate = Column('finishdate', String(8))  # 预计完工(YMD)
    modifydate = Column('modifydate',String(20))      #提交时间

