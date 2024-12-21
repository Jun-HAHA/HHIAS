# SubPage_Analysis.py
# 本文件为系统子页面，包含账单分析功能模块，其下包含账单总体分析模块，物价分析模块，购物推荐模块

# 导入所需库
import streamlit        # 系统页面构建
import pandas           # 数据表处理
import plotly.express   # 可视化数据图表
import random           # 选取随机商品
import datetime         # 日期处理

# 导入系统通用函数
import SystemGeneralFunctionsLib as SGF

# 获取可选年份列表
# IsUser：用户选择个人或家庭
def GetYearOption(IsUser: bool):
    if IsUser:
        SGF.SystemCur.execute("SELECT DISTINCT strftime('%Y',BillDate) FROM Bill WHERE User_UserID={}".format(streamlit.session_state.UserID))
    else:
        SGF.SystemCur.execute("SELECT DISTINCT strftime('%Y',BillDate) FROM Bill WHERE User_Family_FamilyID={}".format(SGF.GetUserFamilyID(streamlit.session_state.UserID)))
    
    # 返回可选年份的列表
    return [YearOp[0] for YearOp in SGF.SystemCur.fetchall()]

# 获取当前年份的可选月份列表
# TargetYear：指定年份
# IsUser：用户选择个人或家庭
def GetMonthOption(TargetYear: int, IsUser: bool):

    # 个人查询
    if IsUser:
        SGF.SystemCur.execute("SELECT DISTINCT strftime('%m',BillDate) FROM Bill WHERE User_UserID={} AND strftime('%Y',BillDate)='{}'".format(streamlit.session_state.UserID, TargetYear))
    
    # 家庭查询
    else:
        SGF.SystemCur.execute("SELECT DISTINCT strftime('%m',BillDate) FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y',BillDate)='{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), TargetYear))
    
    # 返回可选月份的列表
    return [MonthOp[0] for MonthOp in SGF.SystemCur.fetchall()]

# 获取全部账单数据
# IsUser：用户选择个人或家庭
def GetAllBillData(IsUser: bool):

    # 个人查询
    if IsUser: 
        SGF.SystemCur.execute("SELECT * FROM Bill WHERE User_UserID={}".format(streamlit.session_state.UserID))
    
    # 家庭查询
    else:
        SGF.SystemCur.execute("SELECT * FROM Bill WHERE User_Family_FamilyID={}".format(SGF.GetUserFamilyID(streamlit.session_state.UserID)))
    
    # 返回全部账单数据（二维列表）
    return SGF.SystemCur.fetchall()

# 获取指定年份账单数据
# TargetYear：指定年份
# IsUser：用户选择个人或家庭
def GetTargetYearBillData(TargetYaer: int, IsUser: bool):

    # 个人查询
    if IsUser: 
        SGF.SystemCur.execute("SELECT * FROM Bill WHERE User_UserID={} AND strftime('%Y', BillDate)='{}'".format(streamlit.session_state.UserID, TargetYaer))
    
    # 家庭查询
    else:
        SGF.SystemCur.execute("SELECT * FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y', BillDate)='{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), TargetYaer))
    
    # 返回指定年份账单数据（二维列表）
    return SGF.SystemCur.fetchall()

# 获取指定月份账单数据
# TargetYear：指定年份
# TargetMonth：指定月份
# IsUser：用户选择个人或家庭
def GetTargetYearMonthBillData(TargetYaer: int, TargetMonth: int, IsUser: bool):

    # 月份溢出处理
    Year, Month = SGF.MonthOverflowDefense(TargetYaer, TargetMonth)

    # 个人查询
    if IsUser: 
        SGF.SystemCur.execute("SELECT * FROM Bill WHERE User_UserID={} AND strftime('%Y-%m', BillDate)='{}-{}'".format(streamlit.session_state.UserID, Year, SGF.GetStringMonth(Month)))
    
    # 家庭查询
    else:
        SGF.SystemCur.execute("SELECT * FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y-%m', BillDate)='{}-{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), Year, SGF.GetStringMonth(Month)))
    
    # 返回指定月份账单数据（二位列表）
    return SGF.SystemCur.fetchall()

# 计算获取账单数据中的部分数据（0：金额总和 1：条目总和 2：类别字典）
# BillData：账单数据（二维数组）
def BillDataSum(BillData: list):

    # 账单金额列表
    PriceList = [b[6] for b in BillData]

    # 商品类别金额字典
    CategoryDict = {}
    for bill in BillData:
        if bill[3] not in CategoryDict.keys():
            CategoryDict[bill[3]] = bill[6]
        else:
            CategoryDict[bill[3]] += bill[6]

    # 返回数据元组（0：金额总和 1：条目总和 2：类别字典）
    return sum(PriceList), len(PriceList), CategoryDict

# 获取近三天账单数据（金额总和和条目总和，用于仪表数据展示）
# IsUser：用户选择个人或家庭
def GetLastThreeDaysSumData(IsUser: bool):

    # 个人查询
    if IsUser:
        SGF.SystemCur.execute("SELECT ItemPrice FROM Bill WHERE User_UserID={} AND strftime('%Y-%m-%d', BillDate) BETWEEN '{}-{}-{}' AND '{}-{}-{}'".format(streamlit.session_state.UserID, str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day - 2), str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day)))
    
    # 家庭查询
    else:
        SGF.SystemCur.execute("SELECT ItemPrice FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y-%m-%d', BillDate) BETWEEN '{}-{}-{}' AND '{}-{}-{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day - 2), str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day)))
    
    # 查询结果处理
    GetRes = SGF.SystemCur.fetchall()
    PriceList = [b[0] for b in GetRes]

    # 返回金额总和和条目总和（0：金额总和 1：条目总和）
    return sum(PriceList), len(PriceList)

# 获取指定年份的月度金额列表
# TargetYear：指定年份
# IsUser：用户选择个人或家庭
def GetYearMonthPriceList(TargetYear: int, IsUser: bool):

    # 全年金额列表
    YearPriceList = []

    # 每月查询
    for month in ["01","02","03","04","05","06","07","08","09","10","11","12"]:

        # 个人查询
        if IsUser:
            SGF.SystemCur.execute("SELECT ItemPrice FROM Bill WHERE User_UserID={} AND strftime('%Y-%m', BillDate)='{}-{}'".format(streamlit.session_state.UserID, TargetYear, month))
        
        # 家庭查询
        else:
            SGF.SystemCur.execute("SELECT ItemPrice FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y-%m', BillDate)='{}-{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), TargetYear, month))
        
        # 查询结果处理
        PriceList = [b[0] for b in SGF.SystemCur.fetchall()]
        YearPriceList.append(sum(PriceList))

    # 返回数据（0：金额列表，1：条目总和）
    return YearPriceList

# 获取近五年消费金额数据
# TargetYear：指定年份
# IsUser：用户选择个人或家庭
def GetNearYearPriceSum(TargetYear: int, IsUser: bool):

    # 年度金额列表
    NearYearPriceList = []

    # 年度检索
    for year in [TargetYear-2, TargetYear-1, TargetYear, TargetYear+1, TargetYear+2]:

        # 个人检索
        if IsUser:
            SGF.SystemCur.execute("SELECT SUM (ItemPrice) FROM Bill WHERE User_UserID={} AND strftime('%Y', BillDate)='{}'".format(streamlit.session_state.UserID, year))
        
        # 家庭检索
        else:
            SGF.SystemCur.execute("SELECT SUM (ItemPrice) FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y', BillDate)='{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), year))
        
        # 检索结果处理
        GetRes = SGF.SystemCur.fetchall()[0][0]
        if GetRes == None:
            NearYearPriceList.append(0)
        else:
            NearYearPriceList.append(GetRes)

    # 返回年度金额列表
    return NearYearPriceList

# 获取近五月消费金额数据
# TargetYear：指定年份
# TargetMonth：指定月份
# IsUser：用户选择个人或家庭
def GetNearMonthPriceSum(TatgetYear: int, TargetMonth: int, IsUser: bool):

    # 月度金额列表
    NearMonthPriceList = []

    # 日期列表
    NearMonthDateList = []

    # 月度检索
    for month in [TargetMonth-2, TargetMonth-1, TargetMonth, TargetMonth+1, TargetMonth+2]:

        # 日期溢出处理
        Year, Month = SGF.MonthOverflowDefense(TatgetYear, month)
        
        # 添加日期
        NearMonthDateList.append("{}年{}日".format(Year, Month))

        # 个人检索
        if IsUser:
            SGF.SystemCur.execute("SELECT SUM (ItemPrice) FROM Bill WHERE User_UserID={} AND strftime('%Y-%m', BillDate)='{}-{}'".format(streamlit.session_state.UserID, Year, SGF.GetStringMonth(Month)))
        
        # 家庭检索
        else:
            SGF.SystemCur.execute("SELECT SUM (ItemPrice) FROM Bill WHERE User_Family_FamilyID={} AND strftime('%Y-%m', BillDate)='{}-{}'".format(SGF.GetUserFamilyID(streamlit.session_state.UserID), Year, SGF.GetStringMonth(Month)))
        
        # 检索结果处理
        GetRes = SGF.SystemCur.fetchall()[0][0]
        if GetRes == None:
            NearMonthPriceList.append(0)
        else:
            NearMonthPriceList.append(GetRes)
    
    # 返回月度金额列表
    return NearMonthPriceList, NearMonthDateList

# 获取所有商品类别
def GetAllItemCategory():
    SGF.SystemCur.execute("SELECT DISTINCT ItemCategory FROM Bill")
    GetRes = SGF.SystemCur.fetchall()
    return [c[0] for c in GetRes]

# 获取指定商品类别的所有商品名称
# ItemCategory：指定商品类别
def GetAllItemName(ItemCategory: str):
    SGF.SystemCur.execute("SELECT DISTINCT ItemName FROM Bill WHERE ItemCategory='{}'".format(ItemCategory))
    GetRes = SGF.SystemCur.fetchall()
    return [n[0] for n in GetRes]

# 获取指定商品类别指定商品名称的离散数据列表（0：购买商家列表 1：购买价格列表 2:购买月份列表）
# ItemCategory：指定商品类别
# ItemName：指定商品名称
def GetTargetItemData(ItemCategory: str, ItemName: str):
    SGF.SystemCur.execute("SELECT ItemPrice,ItemSaler,strftime('%m', BillDate) FROM Bill WHERE ItemCategory='{}' AND ItemName='{}'".format(ItemCategory, ItemName))
    GetRes = SGF.SystemCur.fetchall()
    SalerList = [s[1] for s in GetRes]
    PriceList = [s[0] for s in GetRes]
    MonthList = [s[2] for s in GetRes]
    return SalerList, PriceList, MonthList

# 获取指定商品类别指定商品名称本月份的数据（0：平均售价 1：商品销量 2：最高售价 3：最低售价）
# ItemCategory：指定商品类别
# ItemName：指定商品名称
def GetThisMonthTargetItemData(ItemCategory: str, ItemName: str):
    SGF.SystemCur.execute("SELECT ItemPrice FROM Bill WHERE ItemCategory='{}' AND ItemName='{}' AND strftime('%Y-%m', BillDate)='{}-{}'".format(ItemCategory, ItemName, datetime.date.today().year, datetime.date.today().month))
    GetRes = sorted([p[0] for p in SGF.SystemCur.fetchall()])
    if len(GetRes) == 0:
        return [0, 0, 0, 0]
    return [sum(GetRes)/len(GetRes), len(GetRes), GetRes[-1], GetRes[0]]

# 获取指定商品类别指定商品名称的其实年份
# ItemCategory：指定商品类别
# ItemName：指定商品名称
def GetTargetItemStartYear(ItemCategory: str, ItemName: str):
    SGF.SystemCur.execute("SELECT MIN(strftime('%Y', BillDate)),MAX(strftime('%Y', BillDate))  FROM Bill WHERE ItemCategory='{}' AND ItemName='{}'".format(ItemCategory, ItemName))
    return SGF.SystemCur.fetchall()[0]

# 获取指定商品类别指定商品名称全时期数据（0：平均售价 1：商品平均销量 2：第二高售价 3：第二低售价）
# ItemCategory：指定商品类别
# ItemName：指定商品名称
def GetAllTimeTargetItemData(ItemCategory: str, ItemName: str):

    # 查询历史平均价格信息
    SGF.SystemCur.execute("SELECT ItemPrice FROM Bill WHERE ItemCategory='{}' AND ItemName='{}'".format(ItemCategory, ItemName))
    GetRes = sorted([p[0] for p in SGF.SystemCur.fetchall()])

    # 查询历史月均销量信息
    ItemYear = GetTargetItemStartYear(ItemCategory, ItemName)
    NumRes = []
    if ItemYear[0] == ItemYear[1]:
        for month in ["01","02","03","04","05","06","07","08","09","10","11","12"]:
            SGF.SystemCur.execute("SELECT BillID FROM Bill WHERE ItemCategory='{}' AND ItemName='{}' AND strftime('%Y-%m', BillDate)='{}-{}'".format(ItemCategory, ItemName, ItemYear[0], month))
            NumRes.append(len(SGF.SystemCur.fetchall()))
    else:
        for year in ItemYear:
            for month in ["01","02","03","04","05","06","07","08","09","10","11","12"]:
                SGF.SystemCur.execute("SELECT BillID FROM Bill WHERE ItemCategory='{}' AND ItemName='{}' AND strftime('%Y-%m', BillDate)='{}-{}'".format(ItemCategory, ItemName, year, month))
                NumRes.append(len(SGF.SystemCur.fetchall()))
    
    # 返回全时期数据（0：平均售价 1：商品平均销量 2：第二高售价 3：第二低售价）
    if len(GetRes) < 3:
        return sum(GetRes)/len(GetRes), sum(NumRes)//len(NumRes), GetRes[-1], GetRes[0]
    return sum(GetRes)/len(GetRes), sum(NumRes)//len(NumRes), GetRes[-2], GetRes[1]

# 获取指定商品类别指定商品近6个月的价格数据
# ItemCategory：指定商品类别
# ItemName：指定商品名称
def GetNearMonthItemPriceData(ItemCategory: str, ItemName: str):

    # 价格列表和日期列表
    PriceList = []
    DateList = []

    # 获取月份的价格总和
    for MonthDelta in range(6):

        # 月份溢出处理
        Year = str(datetime.date.today().year)
        Month = str(datetime.date.today().month)
        Year, Month = SGF.MonthOverflowDefense(int(Year), int(Month) - MonthDelta)

        # 查询价格列表
        SGF.SystemCur.execute("SELECT SUM(ItemPrice), COUNT(BillID) FROM Bill WHERE ItemCategory='{}' AND ItemName='{}' AND strftime('%Y-%m', BillDate)='{}-{}'".format(ItemCategory, ItemName, Year, Month))

        # 处理查询结果
        GetRes = SGF.SystemCur.fetchall()
        for p in GetRes:
            if p[0] == None:
                PriceList.append(0)
            else:
                PriceList.append(round(p[0]/p[1], 2))
        DateList.append((Year, Month))
    
    # 补全数据
    AutoFitPrice = GetAllTimeTargetItemData(ItemCategory, ItemName)[0]
    for p in range(6):
        if PriceList[p] == 0:
            PriceList[p] = AutoFitPrice

    # 返回日期列表和价格列表
    return PriceList[::-1], DateList[::-1]

# 获取个人购买最多的商品名称
def GetPresonItemCount():

    # 查询个人购买最多的商品名称
    SGF.SystemCur.execute("SELECT ItemName,COUNT(*) AS count FROM Bill WHERE User_UserID={} GROUP BY ItemName ORDER BY count DESC LIMIT 1".format(streamlit.session_state.UserID))
    
    # 检测是否有结果
    GetItemRes = SGF.SystemCur.fetchall()

    # 为空停止查找
    if len(GetItemRes) == 0:
        return "没有商品", 0

    # 不为空继续查找
    else:

        # 查询该商品的均价
        SGF.SystemCur.execute("SELECT AVG(ItemPrice) FROM Bill WHERE ItemName='{}'".format(GetItemRes[0][0]))
        GetPriceRes = SGF.SystemCur.fetchall()[0][0]

        # 返回推荐信息（0：物品 1：均价）
        return GetItemRes[0][0], GetPriceRes

# 获取家庭购买最多的商品名称
def GetFamilyItemCount():

    # 查询家庭购买最多的商品名称
    SGF.SystemCur.execute("SELECT ItemName,COUNT(*) AS count FROM Bill WHERE User_Family_FamilyID={} GROUP BY ItemName ORDER BY count DESC LIMIT 1".format(SGF.GetUserFamilyID(streamlit.session_state.UserID)))

    # 检测是否有结果
    GetItemRes = SGF.SystemCur.fetchall()

    # 为空停止查找
    if len(GetItemRes) == 0:
        return "没有商品", 0
    
    # 不为空继续查找
    else:

        # 查询该商品的均价
        SGF.SystemCur.execute("SELECT AVG(ItemPrice) FROM Bill WHERE ItemName='{}'".format(GetItemRes[0][0]))
        GetPriceRes = SGF.SystemCur.fetchall()[0][0]

        # 返回推荐信息（0：物品 1：均价）
        return GetItemRes[0][0], GetPriceRes

# 获取本月均价下降最多的商品名称
def GetItemPriceFlowData():

    # 查询商品名称列表
    SGF.SystemCur.execute("SELECT DISTINCT ItemName FROM Bill")
    ItemNameList = [i[0] for i in SGF.SystemCur.fetchall()]

    # 商品价格波动表
    FlowPriceList = []

    # 全商品检索
    for item in ItemNameList:
        SGF.SystemCur.execute("SELECT AVG(ItemPrice) FROM Bill WHERE ItemName='{}'".format(item))
        AllTimeAvgPrice = SGF.SystemCur.fetchall()[0][0]
        SGF.SystemCur.execute("SELECT AVG(ItemPrice) FROM Bill WHERE ItemName='{}' AND strftime('%Y-%m', BillDate)='{}-{}'".format(item, str(datetime.date.today().year), str(datetime.date.today().month)))
        ThisMonthAvgPrice = SGF.SystemCur.fetchall()[0][0]
        if ThisMonthAvgPrice == None:
            ThisMonthAvgPrice = AllTimeAvgPrice
        FlowPriceList.append([item, AllTimeAvgPrice, ThisMonthAvgPrice, ThisMonthAvgPrice-AllTimeAvgPrice])

    # 排序函数
    def FlowPriceSort(PriceList):
        return PriceList[3]
    
    # 按价格波动排序
    FlowPriceList = sorted(FlowPriceList, key = FlowPriceSort)
    
    # 返回商品价格波动表
    return FlowPriceList

# 获取随机推荐商品信息
def GetRandomItemData():

    # 查询商品名称列表
    SGF.SystemCur.execute("SELECT DISTINCT ItemName FROM Bill")
    ItemNameList = [i[0] for i in SGF.SystemCur.fetchall()]

    # 随机抽取
    RandomItem = random.sample(ItemNameList, 1)[0]

    # 获取数据
    SGF.SystemCur.execute("SELECT AVG(ItemPrice) FROM Bill WHERE ItemName='{}'".format(RandomItem))
    AllTimeAvgPrice = SGF.SystemCur.fetchall()[0][0]
    SGF.SystemCur.execute("SELECT AVG(ItemPrice) FROM Bill WHERE ItemName='{}' AND strftime('%Y-%m', BillDate)='{}-{}'".format(RandomItem, str(datetime.date.today().year), str(datetime.date.today().month)))
    ThisMonthAvgPrice = SGF.SystemCur.fetchall()[0][0]
    if ThisMonthAvgPrice == None:
        ThisMonthAvgPrice = AllTimeAvgPrice

    # 返回商品名称和本月均价
    return [RandomItem, ThisMonthAvgPrice]

# 标签页功能实现：账单分析
def BillAnalysis():

    # 韩式通用变量
    IsUser = True   # True：个人 False：家庭
    SumArea = 0     # 0：全部 1：年份 2：月份

    # 用户选择容器
    SelectContainer = streamlit.container(border = True, key = "SelectContainer")

    # 账单分析容器
    AnalysisContainer = streamlit.container(border = True, key = "AnalysisContainer")

    # 账单浏览容器
    ViewContainer = streamlit.container(border = True, key = "ViewContainer")

    # 用户选择容器元素
    with SelectContainer:

        # 容器标题
        streamlit.subheader("分析检索", divider = "gray")

        # 列布局：角色选择，时间选择
        RoleCol, TimeCol = streamlit.columns(2, vertical_alignment = "bottom")
        with RoleCol:
            CharInput = streamlit.selectbox("分析角色", ["个人", "家庭"])
        with TimeCol:
            ViewInput = streamlit.selectbox("分析时间", ["全部", "年视图", "月视图"], key = "UserAll")

        # 角色变量更新
        IsUser = True if CharInput == "个人" else False

        # 检索全部
        if ViewInput == "全部":

            # 时间变量更新
            SumArea = 0

            # 获取全部账单数据
            BillData = GetAllBillData(IsUser)
        
        # 检索年份
        elif ViewInput == "年视图":

            # 时间变量更新
            SumArea = 1

            # 选择年份
            YearOption = GetYearOption(IsUser)
            YearChoose = int(streamlit.selectbox("选择年份", YearOption, key = "UserYear1"))

            # 获取指定年份账单数据
            BillData = GetTargetYearBillData(YearChoose, IsUser)

        # 检索月份
        elif ViewInput == "月视图":

            # 时间变量更新
            SumArea = 2

            # 列布局：选择年份和月份
            YearCol, MonthCol = streamlit.columns(2)
            
            # 选择年份
            with YearCol:

                # 获取可选年份列表
                YearOption = GetYearOption(IsUser)

                # 用户选择
                YearChoose = int(streamlit.selectbox("选择年份", YearOption, key = "UserMonth1"))
            
            # 选择月份
            with MonthCol:

                # 获取可选月份列表
                MonthOption = GetMonthOption(YearChoose, IsUser)

                # 用户选择
                MonthChoose = int(streamlit.selectbox("选择月份", MonthOption, key = "UserYear2"))
            
            # 获取指定月份账单数据
            BillData = GetTargetYearMonthBillData(YearChoose, MonthChoose, IsUser)

    # 账单分析容器元素
    with AnalysisContainer:

        # 处理当前检索的账单数据
        CurSumData = BillDataSum(BillData)

        # 全部检索
        if SumArea == 0:

            # 总和数据总览：近三天数据
            LastSumData = GetLastThreeDaysSumData(IsUser)

            # 折线图数据
            PriceData = GetYearMonthPriceList(str(datetime.date.today().year), IsUser)
            X_Label = ["{}月".format(year) for year in range(1, 13)]
            Y_Value = PriceData
            TimeIndex = "月份"
            LineTitle = "本年各月份消费金额变化折线图"

        # 年份检索
        elif SumArea == 1:

            # 总和数据总览：去年数据
            LastSumData = BillDataSum(GetTargetYearBillData(YearChoose-1, IsUser))

            # 折线图数据
            X_Label = ["{}年".format(year) for year in range(YearChoose-2, YearChoose+3)]
            Y_Value = GetNearYearPriceSum(YearChoose, IsUser)
            TimeIndex = "年份"
            LineTitle = "近五年消费金额变化折线图"
        
        # 月份检索
        elif SumArea == 2:

            # 总和数据总览：上月数据
            LastSumData = BillDataSum(GetTargetYearMonthBillData(YearChoose, MonthChoose-1, IsUser))

            # 折线图数据
            PriceData = GetNearMonthPriceSum(YearChoose, MonthChoose, IsUser)
            X_Label = PriceData[1]
            Y_Value = PriceData[0]
            TimeIndex = "月份"
            LineTitle = "近五月消费金额变化折线图"

        # 差值计算
        DeltaPrice = CurSumData[0] - LastSumData[0]
        DeltaItem = CurSumData[1] - LastSumData[1]
        
        # 生成折线图数据表
        LineDataFrame = pandas.DataFrame(
            data = {
                "{}".format(TimeIndex): X_Label,
                "金额": Y_Value
            }
        )

        # 生成折线图
        LineFig = plotly.express.line(
            data_frame = LineDataFrame,
            x = "{}".format(TimeIndex),
            y = "金额"
        )
        LineFig.update_layout(title = "{}".format(LineTitle))

        # 生成饼图数据表
        PieDataFrame = pandas.DataFrame(
            data = {
                "商品类别": CurSumData[2].keys(),
                "消费总额": CurSumData[2].values(),
            }
        )

        # 生成饼图
        PieFig = plotly.express.pie(
            data_frame = PieDataFrame,
            names = "商品类别",
            values = "消费总额"
        )
        PieFig.update_layout(title = "各商品消费占比")

        # 容器标题
        streamlit.subheader("账单分析", divider = "gray")

        # 总和数据总览容器
        SumDataContainer = streamlit.container(border = False, key = "SumDataContainer")

        # 消费变化折线图容器
        LineChartContainer = streamlit.container(border = True, key = "LineChartContainer")

        # 各商品消费占比饼图容器
        PieChartContainer = streamlit.container(border = True, key = "PieChartContainer")

        # 总和数据总览容器元素
        with SumDataContainer:

            # 列布局：金额总和，条目总和
            SumPriceCol, SumItemCol = streamlit.columns(2)   

            # 金额总和展示卡片
            with SumPriceCol:
                with streamlit.container(border = True, key = "SmPriceCol"):
                    streamlit.metric(
                        label = "{}消费总额".format(["", "年度", "月度"][SumArea]),
                        value = "{:.2f}元".format(CurSumData[0]),
                        delta = "{:.2f}元".format(DeltaPrice),
                        delta_color = "inverse"
                    )

            # 条目总和展示卡片
            with SumItemCol:
                with streamlit.container(border = True, key = "SumItemCol"):
                    streamlit.metric(
                        label = "{}账单总数".format(["", "年度", "月度"][SumArea]),
                        value = "{}条".format(CurSumData[1]),
                        delta = "{}条".format(DeltaItem),
                        delta_color = "inverse"
                    )
        
        # 消费变化折线图容器元素
        with LineChartContainer:

            # 显示折线图
            streamlit.plotly_chart(LineFig, use_container_width = True)
        
        # 各商品消费占比饼图容器元素
        with PieChartContainer:
            
            # 显示饼图
            streamlit.plotly_chart(PieFig, use_container_width = True)

    # 账单浏览容器元素
    with ViewContainer:

        # 容器标题
        streamlit.subheader("账单浏览", divider = "gray")

        # 账单数据处理
        BillID = []
        ItemCategory = []
        ItemPrice = []
        BillDate = []
        BillUser = []
        for bill in BillData:
            BillID.append(bill[0])
            ItemCategory.append(bill[3])
            ItemPrice.append(bill[6])
            BillDate.append(bill[7])
            SGF.SystemCur.execute("SELECT UserName FROM User WHERE UserID={}".format(bill[1]))
            GetUserName = SGF.SystemCur.fetchall()[0][0]
            BillUser.append(GetUserName)

        # 生成账单数据表
        BillDataFrame = pandas.DataFrame(
            data = {
                "账单编号": BillID,
                "商品类别": ItemCategory,
                "商品价格": ItemPrice,
                "账单时间": BillDate,
                "账单用户": BillUser
            },
        )

        # 展示账单表格
        streamlit.data_editor(
            data = BillDataFrame,
            use_container_width = True,
            disabled = True,
            hide_index = True,
            column_config = {
                "账单编号": streamlit.column_config.NumberColumn(
                    label = "账单编号",
                    format = "%d"
                ),
                "商品价格": streamlit.column_config.NumberColumn(
                    label = "商品价格",
                    format = "%.2f￥"
                )
            } 
        )

# 标签页功能实现：物价分析
def ItemPriceAnalysis():

    # 商品检索容器
    ItemSelectContainer = streamlit.container(border = True, key = "ItemSelectContainer")

    # 物价分析容器
    ItemPriceAnalysisContainer = streamlit.container(border = True, key = "ItemPriceAnalysisContainer")

    # 商品检索容器元素
    with ItemSelectContainer:

        # 容器标题
        streamlit.subheader("商品检索", divider = "gray")
    
        # 列布局：商品检索
        ICC, INC = streamlit.columns(2)

        # 商品类别检索
        with ICC:
            ItemCategoryChoose = streamlit.selectbox(
                label = "商品类别",
                options = GetAllItemCategory()
            )
        
        # 商品名称检索
        with INC:
            ItemNameChoose = streamlit.selectbox(
                label = "商品名称",
                options = GetAllItemName(ItemCategoryChoose)
            )

    # 物价分析容器元素
    with ItemPriceAnalysisContainer:
        
        # 容器标题
        streamlit.subheader("商品分析", divider = "gray")

        # 商品数据总体浏览容器
        ItemDataCardContainer = streamlit.container(border = False, key = "ItemDataCardContainer")

        # 月度商品售价变化折线图容器
        MonthItemPriceLineContainer = streamlit.container(border = True, key = "MonthItemPriceLineContainer")
        
        # 商品售价分布柱状图和商品销售商家分布饼图容器
        ItemBarAndPieContainer = streamlit.container(border = False, key = "ItemBarAndPieContainer")

        # 商品销售数量月份分布柱状图容器
        ItemSaleMonthHistogramContainer = streamlit.container(border = True, key = "ItemSaleMonthHistogramContainer")
        
        # 商品数据总体浏览容器元素
        with ItemDataCardContainer:
            
            # 列布局：平均价格波动，平均销量波动
            AveragePriceCol, AverageSaleCol = streamlit.columns(2)

            # 价格数据获取
            ItemData = GetThisMonthTargetItemData(ItemCategoryChoose, ItemNameChoose)
            ItemChangeData = GetAllTimeTargetItemData(ItemCategoryChoose, ItemNameChoose)

            # 数据空缺处理
            if ItemData[0] == 0:
                ItemData[0] = ItemChangeData[0]

            # 平均价格波动
            with AveragePriceCol:
                with streamlit.container(border = True):
                    streamlit.metric(
                        label = "本月平均售价",
                        value = "{:.2f}元".format(ItemData[0]),
                        delta = "{:.2f}元".format(ItemData[0] - ItemChangeData[0]),
                        delta_color = "inverse",
                        help = "波动差值对比历史平均售价"
                    )

            # 平均销量波动
            with AverageSaleCol:
                with streamlit.container(border = True):
                    streamlit.metric(
                        label = "本月商品销量",
                        value = "{}件".format(int(ItemData[1])),
                        delta = "{}件".format(int(ItemData[1] - ItemChangeData[1])),
                        delta_color = "inverse",
                        help = "波动差值对比历史月均销量"
                    )

            # 列布局：最高价格，最低价格
            MaxPriceCol, MinPriceCol = streamlit.columns(2)

            # 最高价格
            with MaxPriceCol:
                with streamlit.container(border = True):
                    streamlit.metric(
                        label = "本月最高售价",
                        value = "{:.2f}元".format(ItemData[2]),
                        delta = "{:.2f}元".format(ItemData[2] - ItemChangeData[2]),
                        delta_color = "inverse",
                        help = "波动差值对比历史最高售价"
                    )

            # 最低价格
            with MinPriceCol:
                with streamlit.container(border = True):
                    streamlit.metric(
                        label = "本月最低售价",
                        value = "{:.2f}元".format(ItemData[3]),
                        delta = "{:.2f}元".format(ItemData[3] - ItemChangeData[3]),
                        delta_color = "inverse",
                        help = "波动差值对比历史最低售价"
                    )
        
        # 月度商品售价变化折线图容器元素
        with MonthItemPriceLineContainer:

            # 获取近六月价格波动数据
            MonthPriceData = GetNearMonthItemPriceData(ItemCategoryChoose, ItemNameChoose)

            # 生成折线图数据表
            MonthItemPriceLineDataFrame = pandas.DataFrame(
                data = {
                    "日期": ["{}年{}月".format(MonthPriceData[1][i][0], MonthPriceData[1][i][1]) for i in range(6)],
                    "均价": MonthPriceData[0]
                }
            )

            # 生成折线图
            MonthItemPriceLineFig = plotly.express.line(
                data_frame = MonthItemPriceLineDataFrame,
                x = "日期",
                y = "均价"
            )
            MonthItemPriceLineFig.update_layout(title = "近六月价格波动")

            # 显示折线图
            streamlit.plotly_chart(MonthItemPriceLineFig)
        
        # 商品售价分布柱状图和商品销售商家分布饼图容器
        with ItemBarAndPieContainer:
        
            # 列布局：商品售价分布柱状图和商品销售商家分布饼图
            BarCol, PieCol = streamlit.columns(2)

            # 商品售价分布柱状图
            with BarCol:
            
                # 商品售价分布柱状图容器
                ItemPriceHistogramContainer = streamlit.container(border = True, key = "ItemPriceHistogramContainer")

                # 商品售价分布柱状图容器元素
                with ItemPriceHistogramContainer:

                    # 价格数据处理
                    PriceDataFrame = pandas.DataFrame(
                        data = {
                            "价格": GetTargetItemData(ItemCategoryChoose, ItemNameChoose)[1]
                        }
                    )
                    PriceDataFrame["价格区间"], xList = pandas.cut(
                        x = PriceDataFrame["价格"],
                        bins = 5,
                        retbins = True,
                        labels = [i+1 for i in range(5)]
                    )
                    xP1 = xList[0:-1]
                    xP2 = xList[1:]

                    # 柱状图数据
                    X_Label = ["{:.2f}-{:.2f}元".format(xP1[i], xP2[i]) for i in range(5)]
                    Y_Value = PriceDataFrame["价格区间"].value_counts().sort_index()
                    
                    # 生成柱状图数据表 
                    ItemPriceHistogramDataFrame = pandas.DataFrame(
                        data = {
                            "价格区间": X_Label,
                            "商品销量": Y_Value
                        }
                    )

                    # 生成柱状图
                    ItemPriceHistogramFig = plotly.express.bar(
                        data_frame = ItemPriceHistogramDataFrame,
                        x = "价格区间",
                        y = "商品销量",
                        height = 300
                    )
                    ItemPriceHistogramFig.update_layout(title = "商品售价分布")

                    streamlit.plotly_chart(ItemPriceHistogramFig, use_container_width = True)

            # 商品销售商家分布饼图
            with PieCol :
                
                # 商品销售商家分布饼图容器
                ItemSalerPieContainer = streamlit.container(border = True, key = "ItemSalerPieContainer")

                # 商品销售商家分布饼图容器
                with ItemSalerPieContainer:

                    # 商家数据处理
                    SalerDict = {}
                    for saler in GetTargetItemData(ItemCategoryChoose, ItemNameChoose)[0]:
                        if saler not in SalerDict.keys():
                            SalerDict[saler] = 1
                        else:
                            SalerDict[saler] += 1
                    
                    # 生成饼图数据表
                    PieDataFrame = pandas.DataFrame(
                        data = {
                            "商家名称": SalerDict.keys(),
                            "销售数量": SalerDict.values()
                        }
                    )

                    # 生成饼图
                    PieFig = plotly.express.pie(
                        data_frame = PieDataFrame,
                        names = "商家名称",
                        values = "销售数量",
                        height = 300
                    )
                    PieFig.update_layout(title = "商品销售商家分布")

                    # 显示饼图
                    streamlit.plotly_chart(PieFig, use_container_width = True)

        # 商品销售数量月份分布柱状图容器元素
        with ItemSaleMonthHistogramContainer:
            
            # 月份数据处理
            MonthDict = {}
            for month in range(1,13):
                MonthDict[month] = 0
            for month in GetTargetItemData(ItemCategoryChoose, ItemNameChoose)[2]:
                MonthDict[int(month)] += 1
            
            # 生成柱状图数据表
            ItemSaleMonthHistogramDataFrame = pandas.DataFrame(
                data = {
                    "月份": ["{}月".format(month) for month in range(1,13)],
                    "销量": MonthDict.values()
                }
            )

            # 生成柱状图
            ItemSaleMonthHistogramFig = plotly.express.bar(
                data_frame = ItemSaleMonthHistogramDataFrame,
                x = "月份",
                y = "销量"
            )
            ItemSaleMonthHistogramFig.update_layout(title = "商品销售数量月份分布")

            # 显示柱状图
            streamlit.plotly_chart(ItemSaleMonthHistogramFig, use_container_width = True)

# 标签页功能实现：购买推荐
def MerchantReferralsAnalysis():

    # 降价最多的商品：推荐购买且推荐商家为价格最低的
    # 随机推荐商品

    # 商品推荐第一排容器
    FirstRowContainer = streamlit.container(border = False, key = "FirstRowContainer")

    # 商品推荐第二排容器
    SecondRowContainer = streamlit.container(border = False, key = "SecondRowContainer")

    # 商品推荐第一排容器元素
    with FirstRowContainer:

        # 列布局：个人购买最多商品推荐，家庭购买最多商品推荐容器
        PresonReCol, FamilyReCol = streamlit.columns(2)

        # 个人购买最多商品推荐
        with PresonReCol:

            # 获取数据
            PresonReData = GetPresonItemCount()
            with streamlit.container(border = True):
                streamlit.metric(
                    label = "根据您的个人购物记录推荐",
                    value = "{}".format(PresonReData[0]),
                    delta = "历史均价{}元".format(PresonReData[1]),
                    delta_color = "off"
                )
        
        # 家庭购买最多商品推荐
        with FamilyReCol:

            # 获取数据
            FamilyReData = GetFamilyItemCount()
            with streamlit.container(border = True):
                streamlit.metric(
                    label = "根据您的家庭购物记录推荐",
                    value = "{}".format(FamilyReData[0]),
                    delta = "历史均价{}元".format(FamilyReData[1]),
                    delta_color = "off"
                )

    # 商品推荐第二一容器元素
    with SecondRowContainer:
        
        # 列布局：降价商品推荐，随机推荐
        LowerPriceReCol, OtherReCol = streamlit.columns(2)

        # 降价商品推荐
        LowerItemData = GetItemPriceFlowData()
        with LowerPriceReCol:
            with streamlit.container(border = True):
                streamlit.metric(
                    label = "根据物价走势推荐",
                    value = LowerItemData[0][0],
                    delta = "本月均价变化{}元".format(LowerItemData[0][3]),
                    delta_color = "off"
                )

        # 随机推荐
        RandomItemData = GetRandomItemData()
        with OtherReCol:
            with streamlit.container(border = True):
                streamlit.metric(
                    label = "还为您推荐",
                    value = RandomItemData[0],
                    delta = "本月均价{}元".format(RandomItemData[1]),
                    delta_color = "off"
                )

# 页面标题
streamlit.title("分析")

# 标签页：账单分析，物价分析，购买推荐
BillAna, PriceAna, MerchantReferrals = streamlit.tabs(["账单分析", "物价分析", "购买推荐"])

# 账单分析标签页功能实现
with BillAna:
    BillAnalysis()

# 物价分析标签页功能实现
with PriceAna:
    ItemPriceAnalysis()

# 购买推荐标签页功能实现
with MerchantReferrals:
    MerchantReferralsAnalysis()
