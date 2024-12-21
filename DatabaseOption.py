# DatabaseOption.py
# 本文件为数据库操作

# 导入所需库
import sqlite3

# 连接数据库
SystemConnect = sqlite3.connect("HHIAS.db", check_same_thread = False, timeout = 10)
SystemCursor = SystemConnect.cursor()

'''
主码范围
UserID: 1000000 - 9999999
FamilyID: 1000 - 9999
BillID: 10000000 - 99999999
'''

# 创建家庭表Family的SQL语句
CreateTableFamily = '''
    CREATE TABLE IF NOT EXISTS Family (
    FamilyID INT UNSIGNED NOT NULL PRIMARY KEY,
    FamilyName VARCHAR(45) NOT NULL,
    FamilyPeopleNum INT UNSIGNED ZEROFILL NOT NULL
    )
'''

# 创建用户表User的SQL语句
CreateTableUser = '''
    CREATE TABLE IF NOT EXISTS User (
    UserID INT UNSIGNED NOT NULL PRIMARY KEY,
    Password VARCHAR(45) NOT NULL,
    UserName VARCHAR(45) NOT NULL,
    UserSex CHAR(2) NOT NULL,
    UserPhone INT UNSIGNED NOT NULL UNIQUE,
    Family_FamilyID INT UNSIGNED NOT NULL,
    FOREIGN KEY (Family_FamilyID) REFERENCES Family (`FamilyID`)
    )
'''

# 创建账单表Bill的SQL语句
CreateTableBill = '''
    CREATE TABLE IF NOT EXISTS `Bill` (
    BillID INT UNSIGNED NOT NULL PRIMARY KEY,
    User_UserID INT UNSIGNED NOT NULL,
    User_Family_FamilyID INT UNSIGNED NOT NULL,
    ItemCategory VARCHAR(20) NOT NULL,
    ItemName VARCHAR(20) NOT NULL,
    ItemSaler VARCHAR(20) NOT NULL,
    ItemPrice DECIMAL(2) NOT NULL DEFAULT 0,
    BillDate DATE NOT NULL,
    BillNote TEXT(50) NULL DEFAULT 'NoNote',
    FOREIGN KEY (User_UserID , User_Family_FamilyID) REFERENCES User (UserID , Family_FamilyID)
    )
'''

# 已运行
# 运行已删除