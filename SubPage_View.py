# SubPage_View.py
# 本文件为系统子页面，包含新建账单功能模块和账单检索功能模块

# 导入所需库
import streamlit    # 用于系统页面构建
import time         # 用于操作延迟
import pandas       # 用于数据表处理

# 导入系统通用函数
import SystemGeneralFunctionsLib as SGF

# 特定功能函数：查询账单
# UserInput：用户输入的账单号
def GetTargetBillData(UserInput: str):

    # 数据库查询指定账单号数据
    SGF.SystemCur.execute("SELECT BillID,ItemCategory,ItemName,ItemSaler,ItemPrice,BillDate,BillNote,User_UserID FROM Bill WHERE BillID={}".format(int(UserInput)))
    
    # 返回查询结果
    return SGF.SystemCur.fetchall()

# 特定功能函数：处理查询账单信息
# BillData：订单数据列表
def GetTargetBillTable(BillData: list):

    # 处理后账单信息列表
    TargetBill = []

    # 遍历账单列表
    for bill in BillData:
        for i in range(len(bill)):

            # 处理账单金额
            if i == 4:
                TargetBill.append("{:.2f}￥".format(bill[i]))
            
            # 处理账单日期
            elif i == 5:
                TargetBill.append("{}年{}月{}日".format(bill[i].split("-")[0], bill[i].split("-")[1], bill[i].split("-")[2]))
            
            # 处理账单用户：将查询用户名
            elif i == 7:
                SGF.SystemCur.execute("SELECT UserName FROM User WHERE UserID={}".format(int(bill[i])))
                GetUserName = SGF.SystemCur.fetchall()[0]
                TargetBill.append(GetUserName[0])
            
            # 其他处理
            else:
                TargetBill.append(bill[i])
    
    # 返回处理后账单信息列表
    return TargetBill

# 特定功能函数：处理检索账单信息
# BillData：检索账单数据列表
def GetSelectBillTable(BillData: list):

    # 处理后账单数据列表
    SelectBill = []
    
    # 遍历检索账单信息
    for bill in BillData:

        # 临时账单数据储存
        SelectBillData = []

        # 遍历账单数据
        for i in range(len(bill)):

            # 处理账单用户
            if i == 4:
                SGF.SystemCur.execute("SELECT UserName FROM User WHERE UserID={}".format(bill[i]))
                GetUserName = SGF.SystemCur.fetchall()[0]
                SelectBillData.append(GetUserName[0])
            
            # 处理账单日期
            elif i == 3:
                SelectBillData.append(SGF.ToDate(bill[i]))

            # 处理其他数据
            else:
                SelectBillData.append(bill[i])
            
        # 添加账单数据
        SelectBill.append(SelectBillData)

    # 返回处理后账单数据列表
    return SelectBill

# 特定功能函数：生成指定账单数据表
# BillData：账单数据列表
def GetBillDataTable(BillData: list):

    # 数据处理
    TargetTable = GetTargetBillTable(BillData)

    # 返回数据表
    return pandas.DataFrame(
        data = TargetTable,
        columns = ["账单信息"],
        index = ["账单编号", "商品类型", "商品名称","购买商家", "商品价格", "账单日期", "账单备注", "账单用户"]
    )

# 特定功能函数：生成订单浏览数据表
# BillData：账单数据列表
def GetBillViewTable(BillData: list):

    # 数据处理
    TargetTable = GetSelectBillTable(BillData)

    # 返回数据表
    return pandas.DataFrame(
        data = TargetTable,
        columns = ["账单编号", "商品类型", "商品价格", "账单日期", "账单用户"]
    )



# 页面元素：添加新帐单对话框
@streamlit.dialog(title = "添加新账单")
def AddNewBill():

    # 用户输入
    ItemCategory = streamlit.selectbox("商品类型", SGF.ItemCategoryOption)
    ItemName = streamlit.text_input("商品名称", max_chars = 20)
    ItemSaler = streamlit.text_input("购买商家", max_chars = 20)
    ItemPrice = streamlit.number_input(label = "商品价格（单位：元）", step = 0.01, format = "%0.2f")
    BillNote = streamlit.text_input("账单备注", value = "无", max_chars = 50)
    BillDate = streamlit.date_input(label = "账单日期", value = "today")

    # 输入合规检测
    if streamlit.button("添加账单"):

        # 商品名称为空
        if len(ItemName) == 0:
            streamlit.error("商品名称为空，请输入")
        
        # 商家为空
        elif len(ItemSaler) == 0:
            streamlit.error("购买商家为空，请输入")
        
        # 检测通过，添加处理
        else:
            InfoBar = streamlit.empty()
            InfoBar.info("正在添加...")
            time.sleep(0.5)

            # 获取随机账单编号
            GetBillID = SGF.GetRandomID("BillID", 10000000, 99999999, "Bill")

            # 数据库操作：添加新账单信息
            SGF.SystemCur.execute("SELECT Family_FamilyID FROM User WHERE UserID={}".format(int(streamlit.session_state.UserID)))
            GetFamilyID = SGF.SystemCur.fetchall()[0][0]
            NewBillInsert = "INSERT INTO Bill (BillID,User_UserID,User_Family_FamilyID,ItemCategory,ItemName,ItemSaler,ItemPrice,BillDate,BillNote) VALUES (?,?,?,?,?,?,?,?,?)"
            NewBillData = (GetBillID, streamlit.session_state.UserID, GetFamilyID, ItemCategory, ItemName, ItemSaler, ItemPrice, BillDate, BillNote)
            SGF.SystemCur.execute(NewBillInsert, NewBillData)
            SGF.SystemConn.commit()

            # 提示成功信息
            InfoBar.success("添加成功")
            time.sleep(0.5)
            streamlit.rerun()    

# 标签页功能实现：账单一览
def ViewAllBill():

    # 列布局：检索选择
    CategorySelect, DataSelect, FamilySelect = streamlit.columns(3, vertical_alignment = "bottom")
    
    # 商品类别检索
    with CategorySelect:
        CategoryInput = streamlit.selectbox("商品类别",["全部"]+SGF.ItemCategoryOption)
    
    # 账单日期检索
    with DataSelect:
        DateInput = streamlit.date_input("账单日期", [])
    
    # 个人/家庭检索
    with FamilySelect:
        FamilyInput = streamlit.selectbox("显示个人/家庭", ["个人", "家庭"])

    # 原始检索语句
    SelectSQL = "SELECT BillID,ItemCategory,ItemPrice,BillDate,User_UserID FROM BILL WHERE "

    # 个人检索语句部分
    UserID = "User_UserID={} AND ".format(streamlit.session_state.UserID)

    # 家庭检索语句部分
    FamilyID = "User_Family_FamilyID={} AND ".format(SGF.GetUserFamilyID(streamlit.session_state.UserID))
    
    # 类别检索语句部分
    CategorySelect = "ItemCategory="

    # 日期检索语句部分
    DateSelect = "BillDate "

    # 检索语句组成：个人/家庭
    if FamilyInput == "个人":
        SelectSQL += UserID
    elif FamilyInput == "家庭":
        SelectSQL += FamilyID
    else:
        SelectSQL += ""

    # 检索语句组成：商品类别
    if CategoryInput != "全部":
        CategorySelect += "'{}' AND ".format(CategoryInput)
        SelectSQL += CategorySelect
    else:
        SelectSQL += ""
    
    # 检索语句组成：账单日期
    if len(DateInput) == 2:
        StartDate = str(DateInput[0])
        EndDate = str(DateInput[1])
        DateSelect += "BETWEEN '{}' AND '{}' AND ".format(StartDate, EndDate)
        SelectSQL += DateSelect
    elif len(DateInput) == 1:
        StartDate = str(DateInput[0])
        DateSelect += ">='{}' AND ".format(StartDate)
        SelectSQL += DateSelect
    else:
        SelectSQL += ""

    # 检索语句处理执行
    SelectSQL = SelectSQL.rstrip("AND ")
    SGF.SystemCur.execute(SelectSQL)
    BillTable = SGF.SystemCur.fetchall()

    # 检索结果处理：未找到账单
    if len(BillTable) == 0:
        streamlit.info("未检索到账单")
    
    # 检索结果处理：展示账单表
    else:
        
        # 生成账单数据表
        BillDataTable = GetBillViewTable(BillTable)

        # 显示账单表
        streamlit.data_editor(
            data = BillDataTable,
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
                ),
                "账单日期": streamlit.column_config.DateColumn(
                    label = "账单日期"
                )
            }
        )

# 标签页功能实现：账单查询
def ViewTargetBill():

    # 用户输入账单号
    UserBillID = streamlit.text_input("请输入账单号", key = "View")

    # 检索账单号
    if len(UserBillID) != 0:

        # 检索账单号
        BillRes = GetTargetBillData(UserBillID)

        # 未找到账单号
        if len(BillRes) == 0:
            streamlit.error("未找到该账单，请重新输入")
        
        # 找到账单数据
        else:

            # 展示账单数据
            BillDataTable = GetBillDataTable(BillRes)
            streamlit.table(BillDataTable)

            # 用户选择修改操作
            EditInput = streamlit.selectbox("是否修改该账单？", ["不修改", "修改账单", "删除账单"])

            # 不修改
            if EditInput == "不修改":
                pass

            # 修改账单
            elif EditInput == "修改账单":

                # 用户输入修改信息
                CategoryInput = streamlit.selectbox("商品类型", SGF.ItemCategoryOption)
                NameInput = streamlit.text_input("商品名称", max_chars = 20)
                SalerInput = streamlit.text_input("购买商家", max_chars = 20)
                PriceInput = streamlit.number_input("商品价格", step = 0.01, format = "%.2f")
                DateInput = streamlit.date_input("账单时间", value = SGF.ToDate(BillRes[0][5]))
                NoteInput = streamlit.text_input("账单备注", value="无", max_chars = 50)

                # 检测修改信息合规
                if streamlit.button("确认修改"):

                    # 商品名称为空
                    if len(NameInput) == 0:
                        streamlit.error("请输入商品名称")

                    # 商家为空
                    elif len(SalerInput) == 0:
                        streamlit.error("请输入购买商家")

                    # 检测通过：处理修改
                    else:
                        InfoBar = streamlit.empty()
                        InfoBar.info("正在修改...")

                        # 数据库操作：修改账单数据
                        UpdateBill = "UPDATE Bill SET ItemCategory='{}',ItemName='{}',ItemSaler='{}',ItemPrice={},BillDate='{}',BillNote='{}' WHERE BillID={}".format(CategoryInput, NameInput, SalerInput, PriceInput, DateInput, NoteInput, int(BillRes[0][0]))
                        SGF.SystemCur.execute(UpdateBill)
                        SGF.SystemConn.commit()
                        time.sleep(0.5)

                        # 提示修改成功信息
                        InfoBar.success("修改成功")
                        time.sleep(0.5)
                        streamlit.rerun()
            
            # 删除账单
            elif EditInput == "删除账单":
                if streamlit.button("确认删除"):
                    InfoBar = streamlit.empty()
                    InfoBar.info("正在删除...")

                    # 数据库操作：删除账单数据
                    SGF.SystemCur.execute("DELETE FROM Bill WHERE BillID={}".format(int(BillRes[0][0])))
                    SGF.SystemConn.commit()
                    time.sleep(0.5)

                    # 提示删除成功信息
                    InfoBar.success("删除成功")
                    time.sleep(0.5)
                    streamlit.rerun()

# 页面标题
streamlit.title("收支总览")

# 添加账单按钮
if streamlit.button("添加账单", use_container_width = True):
    AddNewBill()

# 标签页：账单一览，账单查询
ViewAllBillTab, ViewTargetBillTab = streamlit.tabs(["账单一览", "账单查询"])

# 账单一览标签页功能实现
with ViewAllBillTab:
    ViewAllBill()

# 账单查询标签页功能实现
with ViewTargetBillTab:
    ViewTargetBill()