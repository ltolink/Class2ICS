# Class2ICS

## 简介
Class2ICS是一个用于将课程表转换为ICS格式的工具。

转换后的ICS文件可以方便的导入各种日历软件。

## 功能
- 从教务系统导出的xls课程表中提取课程信息
- 将课程信息转换为ICS格式

## 使用方法
### 安装库
```shell
pip install bs4 icalendar
```
### 使用 Class2ICS.py 命令行版本
1. 从教务系统导出课程表.xls文件
2. 运行Class2ICS.py
3. 输入文件路径
4. 输入学期开始日期（第一周的周一）
5. 显示文件保存路径（默认为当前目录）

### 使用 Class2ICS_GUI.py 图形界面版本
1. 从教务系统导出课程表.xls文件
2. 运行Class2ICS_GUI.py
3. 将课程表使用Class2ICS打开
4. 打开后显示课程预览信息
5. 点击“文件-导出ICS文件”按钮
6. 输入学期开始日期（第一周的周一），点击“保存”按钮
7. 选择保存位置并保存
8. 将文件导入到日历应用中，即可查看课程表

## 注意事项
- 学期开始日期必须为第一周的周一
- 课程表必须为教务系统导出的课程表