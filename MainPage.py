# MainPage.py
# 本文件为系统根页面，包含用户登录注册功能模块，另外用于系统子页面调用

# 导入所需库
import streamlit    # 系统页面搭建
import time         # 主要用于响应延迟，提高用户体验感

# 导入系统通用函数
import SystemGeneralFunctionsLib as SGF

# 定义全局变量：用户登录状态（0：未登录 1：登录后未加入家庭 2：登录成功且已加入家庭，可进入主页面）
if "UserSignIn" not in streamlit.session_state:
    streamlit.session_state.UserSignIn = 0

# 定义全局变量：用户账号UserID（记录UserID用于所有页面查询数据库）
if "UserID" not in streamlit.session_state:
    streamlit.session_state.UserID = 0

# 特定功能函数：插入新用户
# UserID：用户号
# UserName：用户姓名
# UserSex：用户性别
# Password：密码
# UserPhone：用户手机号
# UserInFamily：用户家庭号（若没有加入家庭则为0）
# TableName：表名
def InsertNewUser(
    UserID: int, UserName: str, 
    UserSex: str, Password: str, 
    UserPhone: int, UserInFamily: int, 
    TableName: str
):
    # INSERT插入操作
    InsertUser = "INSERT INTO {} (UserID,Password,UserName,UserSex,UserPhone,Family_FamilyID) VALUES (?,?,?,?,?,?)".format(TableName)
    NewUser = (int(UserID), Password, UserName, UserSex, int(UserPhone), int(UserInFamily))
    SGF.SystemCur.execute(InsertUser, NewUser)
    SGF.SystemConn.commit()

# 页面元素：用户登录对话框
@streamlit.dialog(title = "您好，请登录")
def UserSignInCard():

    # 页面元素：用户输入框
    UserInput = streamlit.text_input("请输入账号或手机号")
    Password = streamlit.text_input("请输入密码", type = "password")

    # 页面元素：登录按钮
    # 按下后开始判断输入是否合规
    if streamlit.button("登录"):

        # 检测输入是否空缺
        if len(UserInput) == 0:
            streamlit.error("账号或手机号为空，请输入")
        elif len(Password) == 0:
            streamlit.error("密码为空，请输入")
        
        # 若没有空缺则进入信息核实
        else:

            # 检测用户名或手机号的长度是否正确
            if len(UserInput) == 11 or len(UserInput) == 7:

                # 长度为11：手机号；从手机号查询数据库
                if len(UserInput) == 11:
                    SGF.SystemCur.execute("SELECT * FROM User WHERE UserPhone={}".format(UserInput))
                
                # 长度位7：用户名；从用户名查询数据库
                elif len(UserInput) == 7:
                    SGF.SystemCur.execute("SELECT * FROM User WHERE UserID={}".format(int(UserInput)))
                
                # 获取查询结果
                UserRes = SGF.SystemCur.fetchall()

                # 未查询到该用户数据
                if len(UserRes) == 0:
                    streamlit.error("该账号不存在，请注册或重新输入")
                
                # 查询到用户数据，进行密码核实
                else:

                    # 密码正确，登录成功
                    if Password == UserRes[0][1]:
                        streamlit.success("登录成功", icon = "😎")
                        time.sleep(1)

                        # 更新用户登录状态，跳转检测用户是否加入家庭；记录UserID；刷新页面
                        if UserRes[0][5] == 0:
                            streamlit.session_state.UserSignIn = 1
                        else:
                            streamlit.session_state.UserSignIn = 2
                        streamlit.session_state.UserID = int(UserRes[0][0])
                        streamlit.rerun()
                    
                    # 密码错误
                    else:
                        streamlit.error("密码错误，请重新输入")

            # 其他长度：输入不合规
            else:
                streamlit.error("账号输入错误，请重新输入")

# 页面元素：用户注册对话框
@streamlit.dialog(title = "加入我们！")
def UserSignUpCard():

    # 页面元素：对话框顶部信息条
    streamlit.info("请输入您的个人信息，稍后我们会自动为您生成账号", icon = "🤗")

    # 用于检测用户注册信息的标志变量，相加为4则信息合规
    # 用户电话、用户密码、密码确认、用户家庭
    UserInfoCheck = [0,0,0,0]

    # 页面元素：用户填写注册信息，填写完成检测是否合规

    # 用户姓名、用户性别
    UserName = streamlit.text_input("请输入您的姓名")
    UserSex = streamlit.selectbox("请选择您的性别", ["男","女"])

    # 用户电话：检测长度是否为11、是否包含为纯数字、是否已存在于数据库
    UserPhone = streamlit.text_input("请输入您的电话号")

    # 用户已输入
    if len(UserPhone) != 0:

        # 纯数字、位数检测
        if not SGF.IsPureNumber(UserPhone) or len(UserPhone) != 11:
            streamlit.error("请输入11位数字")
            UserInfoCheck[0] = 0

        # 唯一性检测
        else:
            SGF.SystemCur.execute("SELECT * FROM User WHERE UserPhone={}".format(int(UserPhone)))
            PhoneRes = SGF.SystemCur.fetchall()

            # 若在数据库中查询到数据，则该手机号已被注册
            if len(PhoneRes) != 0:
                streamlit.info("该手机号已注册，请直接登录")
                UserInfoCheck[0] = 0
            
            # 若查询结果为空则该手机号可用
            else:
                UserInfoCheck[0] = 1

    # 用户密码：位数不少于6位
    Password = streamlit.text_input("请输入密码", type = "password")

    # 用户已输入
    if len(Password) != 0:
        if len(Password) < 6:
            streamlit.info("请输入至少6位密码")
            UserInfoCheck[1] = 0
        else:
            UserInfoCheck[1] = 1
    
    # 用户确认密码：是否与用户密码一致
    PasswordConfirm = streamlit.text_input("请确认密码", type = "password")

    # 用户已输入
    if len(PasswordConfirm) != 0:
        if PasswordConfirm != Password:
            streamlit.info("密码不一致，请重新输入")
            UserInfoCheck[2] = 0
        else:
            UserInfoCheck[2] = 1
    
    # 用户家庭
    UserInFamily = streamlit.selectbox("现在加入家庭？", ["加入已有家庭", "暂不加入"])

    # 用户选择暂时不加入家庭
    if UserInFamily == "暂不加入":

        # 登记当前用户家庭号为0
        FamilyID = 0
        UserInfoCheck[3] = 1
    
    # 用户选择加入指定家庭号家庭
    elif UserInFamily == "加入已有家庭":

        # 用户输入家庭号
        GetFamilyID = streamlit.text_input("请输入家庭号")
        if len(GetFamilyID) != 0:

            # 查询家庭号是否存在
            SGF.SystemCur.execute("SELECT * FROM Family WHERE FamilyID={}".format(int(GetFamilyID)))
            FamilyRes = SGF.SystemCur.fetchall()

            # 查询结果为空
            if len(FamilyRes) == 0:
                streamlit.info("未找到该家庭号")
                UserInfoCheck[3] = 0
            
            # 查询到结果并展示家庭名称
            else:
                streamlit.success("可加入：{}".format(FamilyRes[0][1]))
                FamilyID = GetFamilyID
                UserInfoCheck[3] = 1

    # 页面元素：注册确定按钮
    if streamlit.button("马上注册", use_container_width = True):

        # 检测是否有空缺信息
        if len(UserName) == 0:
            streamlit.error("请输入您的姓名")
        elif len(Password) == 0:
            streamlit.error("请输入您的密码")
        elif len(PasswordConfirm) == 0:
            streamlit.error("请输入确认密码")
        elif UserInFamily == "加入已有家庭" and len(GetFamilyID) == 0:
            streamlit.error("请输入家庭号")

        # 若无空缺信息，检测信息是否全部合规
        elif sum(UserInfoCheck) != 4:
            streamlit.error("请检查您填写的信息是否合规")
        
        # 检测全部完成，进行注册操作
        elif sum(UserInfoCheck) == 4:

            # 加入新用户数据
            streamlit.success("注册成功", icon = "😎")
            UserID = SGF.GetRandomID("UserID", 1000000, 9999999, "User")
            InsertNewUser(UserID, UserName, UserSex, Password, UserPhone, FamilyID, "User")

            # 当用户选择加入家庭，更改数据
            if FamilyID != 0:

                # 更新家庭人数
                SGF.SystemCur.execute("SELECT FamilyPeopleNum FROM Family WHERE FamilyID={}".format(FamilyID))
                FamilyNum = SGF.SystemCur.fetchall()[0][0]
                SGF.SystemCur.execute("UPDATE Family SET FamilyPeopleNum={} WHERE FamilyID={}".format(FamilyNum+1, FamilyID))
                SGF.SystemConn.commit()

                # 更新状态
                streamlit.session_state.UserSignIn = 2

            # 当用户选择不加入家庭
            else:
                # 更新状态
                streamlit.session_state.UserSignIn = 1

            # 更新用户登录状态为已登录
            time.sleep(1)
            streamlit.session_state.UserID = UserID
            streamlit.rerun()

# 页面元素： 个人信息对话框
@streamlit.dialog(title = "我的账号")
def UserInfoCard():

    # 获取用户书库
    SGF.SystemCur.execute("SELECT * FROM User WHERE UserID={}".format(streamlit.session_state.UserID))
    UserInfo = SGF.SystemCur.fetchall()[0]

    # 展示个人信息
    streamlit.markdown("**您的账号**：{}".format(UserInfo[0]))
    streamlit.markdown("**您的姓名**：{}".format(UserInfo[2]))
    streamlit.markdown("**您的性别**：{}".format(UserInfo[3]))
    streamlit.markdown("**您的电话**：{}".format(UserInfo[4]))

    # 展示家庭信息
    if UserInfo[5] == 0:
        streamlit.markdown("**您的家庭**：{}".format("您尚未加入家庭"))
    else:
        SGF.SystemCur.execute("SELECT FamilyName FROM Family WHERE FamilyID={}".format(UserInfo[5]))
        UserFamilyName = SGF.SystemCur.fetchall()[0][0]
        streamlit.markdown("**您的家庭**：{}".format(UserFamilyName))

# 页面元素：侧边栏，用户登录/注册
with streamlit.sidebar:

    # 信号判断：当前用户登录状态为未登录
    if streamlit.session_state.UserSignIn == 0:

        # 页面元素：问候标题
        streamlit.title("{}好".format(SGF.GetTimeState()))

        # 页面元素：登录/注册容器
        SignInContainer = streamlit.container(border = True)
        SignUpContainer = streamlit.container(border = True)
        with SignInContainer:
            streamlit.markdown("##### 已有账号？点这里直接登录！")
            SignIn = streamlit.button("用户登录",use_container_width=True)
        with SignUpContainer:
            streamlit.markdown("##### 还没账号？点这里加入我们！")
            SignUp = streamlit.button("用户注册",use_container_width=True)

        # 按钮响应：登录/注册
        if SignIn:
            UserSignInCard()
        elif SignUp:
            UserSignUpCard()

    # 信号判断：当前用户登录状态为已登录
    elif streamlit.session_state.UserSignIn == 1 or streamlit.session_state.UserSignIn == 2:
        
        # 连接数据库，获取当前用户数据
        SGF.SystemCur.execute("SELECT * FROM User WHERE UserID={}".format(streamlit.session_state.UserID))
        CurUserInfo = SGF.SystemCur.fetchall()[0]

        # 页面元素：用户称呼
        HelloText = ""
        if CurUserInfo[3] == "男":
            HelloText = "先生"
        elif CurUserInfo[3] == "女":
            HelloText = "女士"
        streamlit.title("{}{}，欢迎回来".format(CurUserInfo[2], HelloText))

        # 页面元素：用户查看账号信息
        if streamlit.button("我的账号"):
            UserInfoCard()
        
        # 页面元素：用户退出登录
        if streamlit.button("退出登录"):
            streamlit.info("正在退出...")
            time.sleep(1)

            # 更新用户登录状态为未登录，重置UserID
            streamlit.session_state.UserSignIn = 0
            streamlit.session_state.UserID = 0
            streamlit.rerun()

# 页面加载：登录页面
RegistPage = streamlit.Page(
    page = "SubPage_Regist.py",
    title = "登录",
    icon = "🪙", 
    default = True
)

# 页面加载：家庭
FamilyPage = streamlit.Page(
    page = "SubPage_Family.py",
    title = "家庭",
    icon = "🪙"
)

# 页面加载：收支总览页面
ViewPage = streamlit.Page(
    page = "SubPage_View.py",
    title = "总览系统",
    icon = "🪙",
    default = True
)

# 页面加载：收支分析页面
AnalysisPage = streamlit.Page(
    page= "SubPage_Analysis.py",
    title = "分析系统",
    icon = "🪙"
)

# 判断信号：用户为完成登录
if streamlit.session_state.UserSignIn == 0:
    SystemPage = streamlit.navigation(pages = [RegistPage], position="hidden")
    SystemPage.run()

# 判断信号：用户完成登录，需要加入家庭
elif streamlit.session_state.UserSignIn == 1:
    SystemPage = streamlit.navigation(pages = [FamilyPage], position="hidden")
    SystemPage.run()


# 判断信号：用户完成登录且加入家庭：跳转系统主页面
elif streamlit.session_state.UserSignIn == 2:
    SystemPage = streamlit.navigation(pages = [ViewPage, AnalysisPage],position="sidebar")
    SystemPage.run()
