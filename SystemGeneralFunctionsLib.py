# SystemGeneralFunctionsLib.py
# 本文件为系统自定义通用函数库，包含数据库操作连接和其他通用函数

# 导入所需库
import sqlite3
import datetime
import random

# 商品类别选项
ItemCategoryOption = ["日用", "厨具", "清洁", "食品", "数码", "药物", "鞋服", "其他"]

# 通用数据库连接
SystemConn = sqlite3.connect("HHIAS.db", check_same_thread = False, timeout = 10)
SystemCur = SystemConn.cursor()
    
# 通用功能函数：转换时间类型
# DateStr：日期字符串
def ToDate(DateStr: str):
    DateData = str(DateStr).split("-")
    DateData = list(map(int, DateData))
    return datetime.date(DateData[0], DateData[1], DateData[2])
    
# 通用功能函数：检测字符串是否包含汉字
# TargetString：待检测字符串
def IsContainChinese(TargetString: str):
    for ch in TargetString:
        if '\u4e00' <= ch <= '\u9fa5':
            return True
    return False

# 通用功能函数：检测字符串是否为数字
# TargetString：待检测字符串
def IsPureNumber(TargetString: str):
    for ch in TargetString:
        if ch not in "1234567890":
            return False
    return True

# 通用功能函数：随机分配主码
# ColName：列名
# StartNum：主码起始数字
# EndNum：主码终止数字
# TableName：表名
def GetRandomID(
    ColName: str, StartNum: int, EndNum: int,
    TableName: str
):
    # 获取表中已有编号列表
    AllID = "SELECT '{}' FROM {}".format(ColName, TableName)
    SystemCur.execute(AllID)
    Res = SystemCur.fetchall()

    # 若表中没有有数据，则直接添加
    if len(Res) == 0:
        return random.randint(StartNum, EndNum)

    # 若表中有元素，则循环生成直到出现不重复编号
    else:
        ThisID = random.randint(StartNum, EndNum)
        while ThisID in Res[0]:
            ThisID = random.randint(StartNum, EndNum)
        return ThisID
    
# 通用功能函数：获取用户家庭号
# UserID：用户号
def GetUserFamilyID(UserID: int):
    SystemCur.execute("SELECT Family_FamilyID FROM User WHERE UserID={}".format(int(UserID)))
    return SystemCur.fetchall()[0][0]

# 通用功能函数：月份查询转换
# MonthInput：月份数字
def GetStringMonth(MonthInput: int):

    # 小于10则前加0返回
    if MonthInput < 10:
        return "0{}".format(MonthInput)
    
    # 大于10直接返回
    else:
        return str(MonthInput)
    
# 通用功能函数：月份溢出处理
# Year：输入年份
# Month：输入月份
def MonthOverflowDefense(Year: int, Month: int):

    # 月份列表
    MonthList = [i for i in range(1, 13)]

    # 转换变量
    RightMonth = Month
    YearDelta = 0

    # 当月份大于12
    if Month > 12:

        # 取余操作计算正确月份数字和年份
        RightMonth = MonthList[Month % 12 - 1]
        YearDelta = Month // 12

    # 当月份小于1
    elif Month < 1:

        # 求差操作计算正确月份数字和年份
        RightMonth = MonthList[12 + Month - 1]
        YearDelta = (abs(Month) + 12) // 12
    
    # 返回正确年份和正确月份
    return Year+YearDelta, RightMonth
