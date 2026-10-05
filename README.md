# 基于SM2/SM3的数字签名与验签系统

## 项目简介

本系统基于国家商用密码算法SM2与SM3设计实现，采用Python语言开发，结合Tkinter/ttkbootstrap构建现代化图形界面，实现数字签名、数字验签、文件完整性校验及篡改检测等功能。

系统支持：

* SM2公私钥自动生成
* 密钥保存与加载
* SM3摘要计算
* 文本签名与验签
* TXT文件签名与验签
* PDF文件签名与验签
* DOCX文件签名与验签
* 篡改检测测试
* 错误密钥测试
* 签名导入导出
* 验签报告导出
* 日志记录与导出

---

## 项目结构

SM2_SM3_Sign_System
│
├── config.py
├── main.py
│
├── crypto
│
├── gui
│
├── utils
│
├── keys
│
├── logs
│
└── signatures

---

## 安装依赖

pip install -r requirements.txt

---

## 运行系统

python main.py

---

## 打包部署

pyinstaller -F -w -i icon.ico main.py

打包完成后：

dist/main.exe

即可直接运行。

---

## 测试项目

1. 密钥生成测试
2. 文本签名测试
3. TXT文件签名测试
4. PDF文件签名测试
5. DOCX文件签名测试
6. 正常验签测试
7. 篡改检测测试
8. 错误密钥测试
9. 空数据测试
10. 重复签名测试

---

## 开发环境

Python 3.10+

Windows 10/11

GMSSL 3.2.2

ttkbootstrap 1.10.1
