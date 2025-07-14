import re
import logging
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

# 初始化日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# 获取html页面文件
def read_html_file(file_path: str) -> BeautifulSoup:
    """
    读取html文件
    从剪切板读取html文件
    如果读取失败则手动选择html文件
    Returns:
        BeautifulSoup: html文件的BeautifulSoup对象
    """
    try:
        # 读取html文件
        with open(file_path, 'rb') as file:
            html = file.read()
        # 从html中解析课程表
        soup = BeautifulSoup(html, 'html.parser')
        soup_course_table = soup.find(id='manualArrangeCourseTable')
        if soup_course_table == None:
            logging.error("文件中不存在课程表")
            return None
    except Exception as e:
        logging.error("读取文件失败", e)
        return None
    return soup


# 获取课程名称
def get_course_name(soup: BeautifulSoup) -> str:
    """
    获取课程名称
    Args:
        soup (BeautifulSoup): html文件的BeautifulSoup对象
    Returns:
        str: 课程名称
    """
    table = soup.find('h3', align='center')
    return table.text


# 从BeautifulSoup对象中解析课程表
def parse_soup_to_table(soup: BeautifulSoup) -> list[list]:
    """
    从BeautifulSoup对象中解析课程表
    Args:
        soup_course_table (BeautifulSoup): 课程表的BeautifulSoup对象
    Returns:
        list: 课程表的二维列表
    """
    try:
        # 定义课程表的二维列表
        table = []
        # 获取所有课程
        soup_course_table = soup.find(id='manualArrangeCourseTable')
        course_list = soup_course_table.find_all('tr')
        # 获取表头
        thead = course_list[0]
        # 获取表头中的所有列
        th = thead.find_all('th')
        # 将表头中的单元格内容添加到table中
        table.append([header.text.strip() for header in th])
        # 获取表格主体中的所有课程
        tbody = course_list[1:]
        for course in tbody:
            tabletr = []
            # 获取课程中的所有列
            course_name = course.find_all('td')
            for course_name in course_name:
                # 获取课程详细信息
                tabletr.append(course_name.text.strip())
            # 如果tabletr[1:]中全为''则删除tabletr
            # 如果列表长度小于8则填充''
            if len(tabletr) < 8:
                tabletr.extend([''] * (8 - len(tabletr)))
            table.append(tabletr)
    except Exception as e:
        logging.error("解析课程表失败", e)
        return []
    return table


# 双2-4 7,1-11,1-6 8-12,单1-9,1 3-4 6-12
# 解析周数
def parse_week(week_str: str) -> list:
    """
    解析周数
    Args:
        week_str (str): 周数字符串
    Returns:
        list: 周数列表
    """
    # 定义周数列表
    week_list = []
    # 空格分割字符串
    week_str = week_str.split(' ')
    for week in week_str:
        # 如果字符串中包含 单
        if '单' in week:
            # 去除单字
            week = week.replace('单', '')
            if '-' in week:
                week = week.split('-')
                for i in range(int(week[0]), int(week[1]) + 1, 2):
                    week_list.append(i)
            else:
                week_list.append(int(week))
        elif '双' in week:
            # 去除双字
            week = week.replace('双', '')
            if '-' in week:
                week = week.split('-')
                for i in range(int(week[0]), int(week[1]) + 1, 2):
                    week_list.append(i)
            else:
                week_list.append(int(week))
        elif '-' in week:
            week = week.split('-')
            for i in range(int(week[0]), int(week[1]) + 1):
                week_list.append(i)
        else:
            week_list.append(int(week))
    week_list = sorted(week_list)
    return week_list


# 解析课程字符串
def parse_course_str_to_list(course_str: str) -> list:
    """
    解析课程字符串
    Args:
        course_str (str): 课程字符串
    Returns:
        list: 课程列表
    """
    course_list = []
    # print(course_str.strip())
    # 删除字符串中所有'(B'到')'之间的内容
    # 使用 re.sub 替换匹配的内容为空字符串
    course_str = re.sub(r"\(B.*?\)", "", course_str)
    # 按( ) , 分割字符串
    parts = re.split(r'[()]', course_str)
    # 删除空字符串
    parts = [part for part in parts if part.strip()]
    # 使用字典存储课程信息
    course_dict = {}
    for i, part in enumerate(parts):
        if (i % 3 == 0):
            course_dict['name'] = part.strip()
        elif (i % 3 == 1):
            course_dict['teacher'] = part.strip()
        elif (i % 3 == 2):
            parts = re.split(r'[,]', part)
            week_list = parse_week(parts[0].strip())
            course_dict['week'] = week_list
            course_dict['location'] = parts[1].strip()
            course_list.append(course_dict)
            course_dict = {}
    return course_list


# 解析课程表格
def table_to_list(table: list) -> list:
    """
    将课程表格解析为课程列表
    Args:
        table (list): 课程表格的二维列表
    Returns:
        list: 课程列表
    """
    course_end_list = []
    # 删除表头
    # table.pop(0)
    # 删除表格中没有课程的行 删除row[1:]中全为''的行
    table = [row for row in table if any(row[1:])]
    # 遍历table中的每一行 不包含表头
    for row, course in enumerate(table[1:]):
        # 遍历每一行中的每一列
        for col, course_name in enumerate(course):
            # print(col,course_name)
            if col > 0 and course_name != '':
                course_dict_list = parse_course_str_to_list(course_name)
                for course_dict in course_dict_list:
                    course_end_list.append({
                        'name': course_dict['name'],
                        'teacher': course_dict['teacher'],
                        'location': course_dict['location'],
                        'week': course_dict['week'],
                        'weekday': table[0][col],
                        'period': table[row + 1][0]
                    })
    return course_end_list


# 根据学期开始时间 周数 星期数 和 课程节数 计算课程开始时间
def calculate_course_start_datetime(course_start_date, week_num, weekday,
                                    course_number):
    """
    根据学期开始时间 周数 星期数 和 课程节数 计算课程开始时间
    Args:
        week_num (int): 周数
        weekday (int): 星期数
        course_number (int): 课程节数
    Returns:
        datetime.datetime: 课程开始时间
    """
    diff_date = datetime.timedelta(weeks=week_num - 1, days=weekday - 1)
    course_date = course_start_date + diff_date
    course_time = course_scheduled(course_date, course_number)
    # print(course_time)
    return course_time


# 课程时间表
def course_scheduled(course_date, course_period) -> datetime.datetime:
    """
    课程时间表
    Args:
        course_date (datetime.date): 课程日期
        course_period (int): 课程节数
    Returns:
        datetime.datetime: 课程日期和开始时间
    """
    scheduled_datatime = []
    summer_schedule = [[8, 0], [9, 0], [10, 10], [11, 10], [14, 30], [15, 30],
                       [16, 40], [17, 40], [19, 30], [20, 30], [21, 30]]
    winter_schedule = [[8, 0], [9, 0], [10, 10], [11, 10], [14, 00], [15, 00],
                       [16, 10], [17, 10], [19, 00], [20, 00], [21, 00]]
    if course_date.month >= 5 and course_date.month < 10:
        for summer_time in summer_schedule:
            scheduled_datatime.append(
                datetime.time(summer_time[0], summer_time[1], 0))
    else:
        for winter_time in winter_schedule:
            scheduled_datatime.append(
                datetime.time(winter_time[0], winter_time[1], 0))
    return datetime.datetime.combine(course_date.date(),
                                     scheduled_datatime[course_period - 1])


# 计算课程开始时间
def calculate_course_start_time(course_start_date, course_dict) -> list:
    """
    计算课程开始时间
    Args:
        course_start_date (datetime.datetime): 学期开始日期时间
        course_dict (dict): 课程字典
    Returns:
        list: 课程开始时间列表
    """
    weekday_dict = {
        '星期一': 1,
        '星期二': 2,
        '星期三': 3,
        '星期四': 4,
        '星期五': 5,
        '星期六': 6,
        '星期日': 7
    }
    weekday = weekday_dict[course_dict['weekday']]
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
    period = period_dict[course_dict['period']]
    course_start_time_list = []
    for week in course_dict['week']:
        # 当前日期时间等于学期开始日期时间加上（周数-1）*7
        current_week_datetime = course_start_date + datetime.timedelta(
            weeks=week - 1)
        current_date = current_week_datetime + datetime.timedelta(
            days=weekday - 1)
        current_datetime = course_scheduled(current_date, period)
        # print(current_datetime)
        course_start_time_list.append(current_datetime)
        # 计算课程开始日期
    return course_start_time_list


# 初始化日历
def init_calendar(calendar_name) -> Calendar:
    # 创建日历对象
    cal = Calendar()
    # 设置日历的版本
    cal.add('version', '2.0')
    # 设置日历的名称
    cal.add('X-WR-CALNAME', calendar_name)
    # 设置日历的时区
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
    return cal


# 添加课程事件
def add_course_event(cal, course_dict, date_time_list):
    # 添加课程事件
    for date_time in date_time_list:
        # 创建事件对象
        event = Event()
        # 设置事件的名称
        event.add('summary', course_dict['name'])
        # 设置事件的开始时间和结束时间
        event.add('dtstart', date_time)
        event.add('dtend', date_time + datetime.timedelta(hours=1, minutes=50))
        # 设置事件的地点
        event.add('location', course_dict['location'])
        # 设置事件的描述
        event.add('description', course_dict['teacher'])
        # 将事件添加到日历中
        cal.add_component(event)


# 添加周事件
def add_week_event(cal, week_num, course_start_date):
    # 创建事件对象
    event = Event()
    # 设置事件的名称
    event.add('summary', f'第{week_num}周')
    # 设置事件的开始日期和结束日期
    course_start_date = course_start_date.date()
    event.add('dtstart', course_start_date + datetime.timedelta(weeks=week_num - 1))
    event.add('dtend', course_start_date + datetime.timedelta(weeks=week_num))
    # 设置事件的地点
    event.add('location', '学校')
    # 将事件添加到日历中
    cal.add_component(event)


# 写入字符串到日历文件
def write_calendar_file(str, calendar_name):
    try:
        # 读取当前目录下的所有ics文件
        current_dir = Path(__file__).resolve().parent
        # 读取当前目录下的所有ics文件
        ics_files = current_dir.glob('*.ics')
        # 遍历ics文件列表
        for ics_file in ics_files:
            # 删除空文件
            if ics_file.stat().st_size == 0:
                ics_file.unlink()
                continue
            # 读取ics文件的内容
            with open(ics_file, 'rb') as f:
                ics_content = f.read()
                # 如果文件内容相同则跳过
                if str == ics_content:
                    return ics_file
        version = 0
        # 写入日历文件
        file_path = current_dir / f"{calendar_name}_V{version}.ics"
        # 如果文件存在则版本号加1
        while file_path.exists():
            version += 1
            file_path = current_dir / f"{calendar_name}_V{version}.ics"
        with open(file_path, 'wb') as f:
            f.write(str)
    except Exception as e:
        logging.error("写入日历文件失败", e)
    return file_path


# 主函数
def main(course_start_date: datetime.datetime, file_path: str):

    # 读取html文件
    soup = read_html_file(file_path)
    if soup == None or soup == -1:
        logging.error("文件读取失败")
        exit()

    # 读取课程名称
    calendar_name = get_course_name(soup)
    if soup == None or soup == -1:
        logging.error("文件读取失败")
        exit()

    # 从soup中解析课程表格
    table = parse_soup_to_table(soup)
    if table == []:
        logging.error("解析课程表失败")
        exit()

    # 将课程表格解析为课程列表
    course_dict_list = table_to_list(table)
    if course_dict_list == []:
        logging.error("解析课程表格失败")
        exit()
    for course_dict in course_dict_list:
        print(course_dict)

    # 初始化日历
    cal = init_calendar(calendar_name)
    # 将课程列表写入日历
    for course_dict in course_dict_list:
        # 课程字典
        date_time_list = calculate_course_start_time(course_start_date,
                                                     course_dict)
        add_course_event(cal, course_dict, date_time_list)

    # 添加周事件
    for week in range(1, 21):
        add_week_event(cal, week, course_start_date)

    # 写入日历文件
    str = cal.to_ical()
    name = write_calendar_file(str, calendar_name)
    print(f"日历文件已保存到 {name}")


if __name__ == "__main__":
    # 输入文件路径
    file_path = input("请输入文件路径:")
    file_path = Path(file_path)
    if not file_path.exists():
        logging.error("文件不存在")
        exit()
    # 设置学期开始日期 课表第一周的星期一
    course_start_date = input("请输入学期开始日期(格式:2024-02-24):")
    try:
        course_start_date = datetime.datetime.strptime(course_start_date,
                                                       "%Y-%m-%d")
    except Exception as e:
        logging.error("日期格式错误", e)
        exit()

    if file_path == None or file_path == "":
        print("没有选择文件")
        exit()
    # 运行主函数
    main(course_start_date, file_path)
