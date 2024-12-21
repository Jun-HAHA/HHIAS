# SubPage_Family.py
# 本文件为系统子页面，用于提示用户加入家庭

# 导入所需库
import streamlit
import time

# 导入系统通用函数
import SystemGeneralFunctionsLib as SGF

# 页面标题
streamlit.title("您还未家庭，快加入吧！")

# 用户选择
UserInput = streamlit.selectbox("加入家庭", ["加入已有家庭", "新建家庭"])

# 用户选择”加入已有家庭“
if UserInput == "加入已有家庭":

    # 用户输入家庭号
    GetFamilyID = streamlit.text_input("请输入家庭号", key = "GetOld")
    if len(GetFamilyID) != 0:

        # 查询家庭号是否存在
        SGF.SystemCur.execute("SELECT * FROM Family WHERE FamilyID={}".format(int(GetFamilyID)))
        FamilyRes = SGF.SystemCur.fetchall()

        # 查询结果为空
        if len(FamilyRes) == 0:
            streamlit.info("未找到该家庭号")
        
        # 查询到结果并展示家庭名称
        else:
            streamlit.success("可加入：{}".format(FamilyRes[0][1]))
            FamilyID = GetFamilyID


# 用户选择”新建家庭“
elif UserInput == "新建家庭":

    # 用户输入家庭号
    GetFamilyName = streamlit.text_input("请输入家庭名称", key = "GetNew", max_chars = 20)
    streamlit.info("请输入您的家庭名称，稍后系统将自动生成家庭号")

    # 用户确定新建家庭
    if streamlit.button("立即新建新家庭"):

        # 检测家庭名称为空
        if len(GetFamilyName) == 0:
            streamlit.error("家庭名称为空，请输入")

        # 新建家庭处理
        else:
            NewState = streamlit.empty()
            NewState.info("正在新建...")
            time.sleep(0.5)

            # 获取随机家庭号
            GetFamilyID = SGF.GetRandomID("FamilyID", 1000, 9999, "Family")

            # 数据库操作，插入新数据
            NewFamily = "INSERT INTO Family (FamilyID,FamilyName,FamilyPeopleNum) VALUES (?,?,?)"
            NewFamilyData = (GetFamilyID, GetFamilyName, 1)
            SGF.SystemCur.execute(NewFamily, NewFamilyData)
            SGF.SystemConn.commit()

            # 数据库操作，更新用户家庭状态
            UpdateUserFamily = "UPDATE User SET Family_FamilyID={} WHERE UserID={}".format(GetFamilyID, int(streamlit.session_state.UserID))
            SGF.SystemCur.execute(UpdateUserFamily)
            SGF.SystemConn.commit()

            # 提示新建完成
            NewState.success("新建成功")
            time.sleep(0.5)
            streamlit.session_state.UserSignIn = 2
            streamlit.rerun()
