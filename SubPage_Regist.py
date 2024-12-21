# SubPage_Regist.py
# 本文件系统子页面：用户登录注册时展示该页面，主要展示开发小组介绍和系统介绍

# 导入所需库
import streamlit    # 系统页面搭建

# 导入系统通用函数
import SystemGeneralFunctionsLib as SGF

# 页面标题
streamlit.title("欢迎来到家庭购物智能分析系统")

# 开发小组介绍容器
GroupInfo = streamlit.container(border = True)

# 系统介绍容器
SystemInfo = streamlit.container(border = True)

# 开发小组介绍容器元素
with GroupInfo:

    # 容器标题
    streamlit.subheader("开发小组简介", divider = "gray")

    # 同期内容
    streamlit.markdown("**学院**：职业技术师范学院")
    streamlit.markdown("**班级**：22计科师资2班")
    streamlit.markdown("**组长**：范嘉俊")
    streamlit.markdown("**组员**：赵宣朗、汪思琦、江淑雅、黄玉馨、梁德晶")

# 系统介绍容器元素
with SystemInfo:
    
    # 容器标题
    streamlit.subheader("当前系统情况", divider = "gray")

    # 列布局：用户总数、家庭总数、账单总数
    UserNumber, FamilyNumber, BillNumber = streamlit.columns(3)

    # 用户总数卡片
    SGF.SystemCur.execute("SELECT COUNT (UserID) FROM User")
    UserNum = SGF.SystemCur.fetchall()[0][0]
    with UserNumber:
        UNC = streamlit.container(border = True)
        with UNC:
            streamlit.metric(
                label = "用户数",
                value = "{} 人".format(UserNum)
            )

    # 家庭总数卡片
    SGF.SystemCur.execute("SELECT COUNT (FamilyID) FROM Family")
    FamilyNum = SGF.SystemCur.fetchall()[0][0]
    with FamilyNumber:
        FNC = streamlit.container(border = True)
        with FNC:
            streamlit.metric(
                label = "家庭数",
                value = "{} 个".format(FamilyNum)
            )

    # 账单总数卡片
    SGF.SystemCur.execute("SELECT COUNT (BillID) FROM Bill")
    BillNum = SGF.SystemCur.fetchall()[0][0]
    with BillNumber:
        BNC = streamlit.container(border = True)
        with BNC:
            streamlit.metric(
                label = "账单数",
                value = "{} 条".format(BillNum)
            )