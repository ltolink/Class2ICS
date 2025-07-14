import copy
import datetime
import tkinter as tk
from tkinter import ttk, messagebox , filedialog
import Class2ICS

# 版本信息
__version__ = "1.0.0"

# 设置字体
FONT = "Songti SC"
# 设置窗口大小
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 350

# 课程名称
course_schedule_name = ""
# 最大周数
max_week = 0
# 课程列表
course_list = []
# 展示表格
show_table = []


# 创建初始界面
def start_page():
    """
    创建初始界面
    """
    # 清空当前窗口中的所有小部件
    for widget in root.winfo_children():
        widget.destroy()

    label = ttk.Label(root, text="欢迎使用课程表转ICS工具", font=("Songti SC", 22))
    label.pack(pady=20)
    style = ttk.Style()
    style.configure("Custom.TButton", font=("Arial", 12), padding=5)

    # 创建一个按钮读取文件
    button = ttk.Button(root,
                        text="读取文件",
                        command=read_file,
                        style="Custom.TButton")
    button.pack(pady=10)


# 读取文件
def read_file():
    # 清空当前窗口中的所有小部件
    for widget in root.winfo_children():
        widget.destroy()

    label = ttk.Label(root, text="请选择要读取的文件", font=("Songti SC", 22))
    label.pack(pady=20)
    # 打开文件选择对话框，选择要读取的文件
    file_path = filedialog.askopenfilename()
    # 如果用户没有选择文件，则输出提示信息并重新创建初始界面
    if not file_path:
        messagebox.showwarning("Warning", "没有选择文件！")
        start_page()
        return

    global max_week, show_table, course_schedule_name, course_list
    # 读取文件内容
    soup = Class2ICS.read_html_file(file_path)
    table = Class2ICS.parse_soup_to_table(soup)
    course_list = Class2ICS.table_to_list(table)
    # 获取最大周数
    max_week = get_max_week(course_list)
    # 将课程列表转换为展示表格
    show_table = cource_list_to_show_table(course_list, max_week)
    # 获取课程表名称
    course_schedule_name = Class2ICS.get_course_name(soup)

    # 创建表格界面
    create_table()


# 保存文件页面
def save_file_page():
    # 创建一个新窗口
    save_window = tk.Toplevel(root)
    save_window.title("保存文件")
    save_window.geometry("300x200")
    # 置中显示
    screen_width = save_window.winfo_screenwidth()
    screen_height = save_window.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 200) // 2
    save_window.geometry(f"300x200+{x}+{y}")

    label = ttk.Label(save_window, text="请设置课程开始日期", font=("Songti SC", 14))
    label.pack(pady=10)
    label = ttk.Label(save_window,
                      text="格式为: 2025-01-01",
                      font=("Songti SC", 12))
    label.pack(pady=5)
    # 创建一个输入框
    entry_date = ttk.Entry(save_window, font=("Songti SC", 14))
    entry_date.pack(pady=10)
    # 创建一个按钮
    button = ttk.Button(
        save_window,
        text="保存",
        command=lambda: save_ics(course_list, entry_date.get()))
    button.pack(pady=10)


# 保存日历
def save_ics(course_list: list, course_start_date: str):
    """
    保存日历文件
    Args:
        course_list (list): 课程列表
        course_start_date (str): 课程开始日期
    """
    # 转为datatime格式
    try:
        course_start_date = datetime.datetime.strptime(course_start_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("错误", "日期格式错误")
        return
    # 初始化日历
    cal = Class2ICS.init_calendar(course_schedule_name)
    # 将课程列表写入日历
    for course_dict in course_list:
        # 计算课程开始时间
        date_time_list = Class2ICS.calculate_course_start_time(
            course_start_date, course_dict)
        # 添加课程事件
        Class2ICS.add_course_event(cal, course_dict, date_time_list)
    
    for i in range(1, max_week + 3):
        Class2ICS.add_week_event(cal, i, course_start_date)

    # 写入日历文件
    str = cal.to_ical()
    name = Class2ICS.write_calendar_file(str, course_schedule_name)
    if name == "":
        messagebox.showerror("错误", "保存失败")
        return
    messagebox.showinfo("保存成功", f"日历文件已保存到:\n{name}")


# 关于页面
def about_page():
    """
    关于页面
    """
    # 创建一个新窗口
    about_window = tk.Toplevel(root)
    about_window.title("关于")
    about_window.geometry("300x200")
    # 置中显示
    screen_width = about_window.winfo_screenwidth()
    screen_height = about_window.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 200) // 2
    about_window.geometry(f"300x200+{x}+{y}")

    label = ttk.Label(about_window, text="课程表转换工具", font=("Songti SC", 20))
    label.pack(pady=10)
    label = ttk.Label(about_window,
                      text=f"版本: {__version__}",
                      font=("Songti SC", 14))
    label.pack(pady=5)


# 创建菜单
def create_menu(root: tk.Tk):
    # 创建菜单栏
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    # 创建文件菜单
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="文件", menu=file_menu)
    # 添加读取文件菜单选项
    file_menu.add_command(label="读取文件", command=read_file)
    # 添加保存文件菜单选项
    file_menu.add_command(label="导出ICS文件", command=save_file_page)
    # 添加关于菜单选项
    file_menu.add_command(label="关于", command=about_page)


# 创建表格界面
def create_table():
    # 清空当前窗口中的所有小部件
    for widget in root.winfo_children():
        widget.destroy()
    # 创建一个标签
    label = ttk.Label(root, text=course_schedule_name, font=("Songti SC", 20))
    label.pack(pady=0)

    create_menu(root)

    # 创建容器Frame用于放置标签和下拉框
    control_frame = ttk.Frame(root)
    control_frame.pack(pady=10)

    # 添加周数标签和下拉框
    label = ttk.Label(control_frame, text="周数", font=("Songti SC", 14))
    label.grid(row=0, column=0)
    global selected_option
    selected_option = tk.StringVar()
    options = [i for i in range(1, max_week + 1)]
    dropdown = ttk.Combobox(control_frame,
                            textvariable=selected_option,
                            values=options)
    dropdown.grid(row=0, column=1)
    dropdown.set(options[0])  # 默认选择第一个选项
    dropdown.bind("<<ComboboxSelected>>", on_dropdown_change)
    # 表格容器
    table_frame = ttk.Frame(root)
    table_frame.pack(fill=tk.BOTH, expand=True)
    # 初始化表格
    global table
    table = ttk.Treeview(table_frame,
                         columns=show_table[0][0],
                         show="headings")
    # 设置表头
    for col in show_table[0][0]:
        table.heading(col, text=col)
        table.column(col, width=100)
    table.pack(fill=tk.BOTH, pady=5)
    # 初始刷新表格
    refresh_tables(options[0])


# 刷新表格
def refresh_tables(selected_value):
    """
    刷新所有表格的内容
    """
    data = show_table[int(selected_value) - 1]
    # 删除旧数据
    for row in table.get_children():
        table.delete(row)
    # 插入新数据
    for row_data in data[1:]:
        table.insert("", "end", values=row_data)


# 下拉框值改变时触发
def on_dropdown_change(event):
    """
    下拉框值改变时触发
    """
    # 获取下拉框的值
    selected_value = event.widget.get()
    # 刷新表格
    refresh_tables(selected_value)


# 从课程列表中获取最大周数
def get_max_week(course_list: list) -> int:
    """
    从课程列表中获取最大周数
    Args:
        course_list (list): 课程列表
    Returns:
        int: 最大周数
    """
    max_week = 0
    for course in course_list:
        for week in course['week']:
            if week > max_week:
                max_week = week
    return max_week


# 将课程列表转换为展示表格
def cource_list_to_show_table(course_list: list, max_week: int) -> list:
    """
    Args:
        course_list (list): 课程列表
        max_week (int): 最大周数
    Returns:
        list: 课程表
    """
    course_list = copy.deepcopy(course_list)

    first_column = {1: '1-2节', 3: '3-4节', 5: '5-6节', 7: '7-8节', 9: '9-10节'}
    period_dict = {
        '第一节': 1,
        '第二节': 2,
        '第三节': 3,
        '第四节': 4,
        '第五节': 5,
        '第六节': 6,
        '第七节': 7,
        '第八节': 8,
        '第九节': 9,
        '第十节': 10,
        '第十一节': 11
    }
    weekday_dict = {
        '星期一': 1,
        '星期二': 2,
        '星期三': 3,
        '星期四': 4,
        '星期五': 5,
        '星期六': 6,
        '星期日': 7
    }

    for course in course_list:
        course['weekday'] = weekday_dict[course['weekday']]
        course['period'] = period_dict[course['period']]

    all_table = []
    week = 1
    while (week <= max_week):
        weekly_table = [[
            '节次/周次', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'
        ]]
        for i in range(1, 10, 2):
            row = [first_column[i], '', '', '', '', '', '', '']
            for course in course_list:
                if week in course['week'] and course['period'] == i:
                    row[course['weekday']] = course['name'] + '\n' + course[
                        'teacher'] + '\n' + course['location']
            weekly_table.append(row)
        all_table.append(weekly_table)
        week += 1
    return all_table


# 初始化窗口
root = tk.Tk()
root.title("课程表转换工具")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
# 在屏幕中央显示窗口
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - WINDOW_WIDTH) // 2
y = (screen_height - WINDOW_HEIGHT) // 2
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
# 创建初始界面
start_page()
# 运行窗口
root.mainloop()
