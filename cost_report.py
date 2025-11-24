# %%
# 导入第三方库
import pandas as pd
import numpy as np
import datetime
from pyecharts import charts
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from bs4 import BeautifulSoup
import re
import AIUESAGENT as AT
from pathlib import Path

# 参数设置
DATA_PATH = 'data/cost_data.xlsx'

# %%
def proc_washing_data(file_path):
    '''
    数据清洗

    参数:
        file_path (str): 数据文件路径

    返回:
        df (DataFrame): 清洗之后的数据
    '''
    df = pd.read_excel(file_path)

    # 列名替换
    idx = df.index
    up_columns = df.columns.values
    low_columns = df.iloc[0,:].fillna('error').values
    new_low_columns = low_columns
    for i,j in enumerate(low_columns):
        if j == 'error':
            new_low_columns[i] = up_columns[i]
    df = df.iloc[1:,:]
    df.columns = new_low_columns

    # 数据格式转换
    df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
    
    return df

# %%
def extract_monthly_expenses(df, year, month):
    """
    提取指定年月的每日消费数据

    参数:
        df (DataFrame): 数据
        year (int): 指定年份，如 2024
        month (int): 指定月份，如 3 表示 3月

    返回:
        pd.DataFrame: 指定月份的消费数据，若无数据则返回空 DataFrame
    """

    # 提取目标年月的数据
    mask = (df['日期'].dt.year == year) & (df['日期'].dt.month == month)
    monthly_data = df[mask].copy()

    # 填充缺失的消费金额
    monthly_data.fillna(0, inplace=True)

    # 按日期排序
    monthly_data.sort_values('日期', inplace=True)

    return monthly_data.reset_index(drop=True)

# %%
def extract_chart_from_html(source_html_path):
    # 读取源HTML文件
    with open(source_html_path, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    # 解析HTML
    soup = BeautifulSoup(source_content, 'html.parser')
    
    # 提取图表容器（通常带有特定ID或class）
    chart_div = soup.find('body').find('div')
    chart_script = soup.find('body').find('script')
    
    # 返回提取的图表内容
    return (chart_div, chart_script)

# print(extract_chart_from_html('bar.html'))

# %%
def save_report_to_html(report, title, tables):
    """
    保存报告到 HTML 文件

    Args:
        report (str): 报告内容
        title (str): 报告标题
        tables (list): 表格列表
        images (list): 图片列表

    Returns:
        None
    """

    images = [0,1,2]

    # 基本数据
    section1 = re.search(re.compile(r"<title 1>(.*?)<title 2>", re.S), report).group().split('\n',1)
    section1_title = section1[0].split('<title 1>')[1]
    section1_content = section1[1].split('<title 2>')[0].split('\n')
    section1_content = '</p><p>'.join(section1_content)
    images[0] = extract_chart_from_html('image/section_1.html')
    
    section2 = re.search(re.compile(r"<title 2>(.*?)<title 3>", re.S), report).group().split('\n',1)
    section2_title = section2[0].split('<title 2>')[1]
    section2_content = section2[1].split('<title 3>')[0].split('\n')
    section2_content = '</p><p>'.join(section2_content)
    images[1] = extract_chart_from_html('image/section_2.html')

    section3 = re.search(re.compile(r"<title 3>(.*?)<title 4>", re.S), report).group().split('\n',1)
    section3_title = section3[0].split('<title 3>')[1]
    section3_content = section3[1].split('<title 4>')[0].split('\n')
    section3_content = '</p><p>'.join(section3_content)
    images[2] = extract_chart_from_html('image/section_3.html')
    df_html_1 = tables[0].to_html(classes="table table-striped", index=True, justify="left")# 输出靠右

    section4 = re.search(re.compile(r"<title 4>.+", re.S), report).group().split('\n',1)
    # print(section4)
    section4_title = section4[0].split('<title 4>')[1]
    section4_content = section4[1]
    df_html_2 = tables[1].to_html(classes="table table-striped", index=False)

    # HTML 模板
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title[:-5]}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <meta charset="UTF-8">
        <script type="text/javascript" src="https://assets.pyecharts.org/assets/v5/echarts.min.js"></script>
    </head>
    <body class="container mt-4">
        <h1 class="text-center mb-4">{title[:-5]}</h1>

        <h3>{section1_title}</h3>
        <p>{images[0][0]}{images[0][1]}</p>
        <p>{section1_content}</p>

        <h3>{section2_title}</h3>
        <p>{images[1][0]}{images[1][1]}</p>
        <p>{section2_content}</p>

        <h3>{section3_title}</h3>
        <p>{images[2][0]}{images[2][1]}</p>
        <p>{section3_content}</p>
        {df_html_1}

        <h3>{section4_title}</h3>
        <p>{section4_content}</p>
        {df_html_2}
    </body>
    </html>
    """
    with open(f"{title}", "w", encoding="utf-8") as f:
        f.write(html)

# %%
def analyze_and_generate_report(df, year, month):
    """
    分析指定年月的消费数据并生成详细报告
    
    参数:
        df (DataFrame): 数据
        year (int): 指定年份
        month (int): 指定月份
    
    返回:
        dict: 包含分析结果和报告的字典
    """
    # 获取指定月份的数据
    monthly_data = extract_monthly_expenses(df, year, month)
    
    if monthly_data.empty:
        return {
            "summary": f"未找到 {year}年{month}月 的消费记录。",
            "data": monthly_data,
            "statistics": None,
            "report": ""
        }
    
    # 数据分析部分
    # 1. 基础统计信息
    total_expense = (monthly_data['总支出/天'].sum()).round(2)
    average_daily_expense = (total_expense / len(monthly_data['日期'].dt.date.unique())).round(2)
    total_common_income = (monthly_data['总收入/天'].sum()).round(2)
    average_daily_income = (total_common_income / len(monthly_data['日期'].dt.date.unique())).round(2)
    total_benefit = (monthly_data['总收入/天'].sum() - monthly_data['总支出/天'].sum()).round(2)
    average_daily_benefit = (total_benefit / len(monthly_data['日期'].dt.date.unique())).round(2)

    # 2. 分类统计（如果有category列）
    category_stats = {}
    for col in df.columns[6:-4]:
        if col != '总支出/天' and col != '日期' and col != '总收入/天':
            # monthly_data[col] = monthly_data[col].astype(str)
            category_stats[col] = monthly_data[col].sum()
    income_stats = {}
    for col in df.columns[-4:]:
        if col != '总支出/天' and col != '日期' and col != '总收入/天':
            # monthly_data[col] = monthly_data[col].astype(str)
            income_stats[col] = monthly_data[col].sum()
    # print(category_stats)
    
    ####
    # 3. 日消费趋势
    daily_expense = {}
    if '总支出/天' in monthly_data.columns:
        daily_expense = monthly_data.groupby(monthly_data['日期'].dt.date)['总支出/天'].sum().to_dict()
    daily_income = {}
    if '总收入/天' in monthly_data.columns:
        daily_income = monthly_data.groupby(monthly_data['日期'].dt.date)['总收入/天'].sum().to_dict()
    # print(daily_expense.keys)
    daily_expense_info = []
    if '总支出/天' in monthly_data.columns:
        daily_expense_info = [monthly_data['总支出/天'].mean().round(2), 
                         monthly_data['总支出/天'].median().round(2), 
                         monthly_data['总支出/天'].mode().values[0].round(2),
                         monthly_data['总支出/天'].max().round(2), 
                         monthly_data['总支出/天'].min().round(2), 
                         monthly_data['总支出/天'].var().round(2), 
                         monthly_data['总支出/天'].std().round(2)]
    daily_income_info = []
    if '总收入/天' in monthly_data.columns:
        daily_income_info = [monthly_data['总收入/天'].mean().round(2), 
                         monthly_data['总收入/天'].median().round(2), 
                         monthly_data['总收入/天'].mode().values[0].round(2),
                         monthly_data['总收入/天'].max().round(2), 
                         monthly_data['总收入/天'].min().round(2), 
                         monthly_data['总收入/天'].var().round(2), 
                         monthly_data['总收入/天'].std().round(2)]
    ####

    # 组织统计数据
    statistics = {
        "total_expense": total_expense,
        "average_daily_expense": average_daily_expense,
        "total_common_income": total_common_income,
        "total_expense_with_income": total_benefit,
        "category_stats": category_stats,
        "daily_expense": daily_expense,
        "income_stats": income_stats,
        "daily_income": daily_income
    }

    # 生成报告文本与图片
    report_lines = []
    system_prompt = '''你是一名数据分析专家，请根据提供的数据，生成一段消费报告，要求字数不超过500字。'''
    report_text = '一、总体概况'

    # 第一部分的文字内容
    if True:
        report_lines.append("<title 1>一、总体概况")
        report_lines.append("")
        report_text += f'''
        下面是就需分析的消费数据。
        总支出金额：¥{total_expense:.2f}，
        日均支出金额：¥{average_daily_expense:.2f}，
        总收入金额：¥{total_common_income:.2f}，
        日均收入金额：¥{average_daily_income:.2f}，
        总净收入：¥{total_benefit:.2f}。
        日均收支金额：¥{average_daily_benefit:.2f}。\n
        '''
        # 第一部分的图片内容
        (charts.Grid()
        .add(
            charts.Bar()
            .add_xaxis(['总支出金额', '总收入金额', '总净收入'])
            .add_yaxis("收支金额", [total_expense, total_common_income, total_benefit])
            .set_global_opts(title_opts=opts.TitleOpts(title="（日均）收支金额"),
                            legend_opts=opts.LegendOpts(pos_right="50%")),
            grid_opts=opts.GridOpts(pos_left="0%", pos_right="55%"))
        .add(
            charts.Bar()
            .add_xaxis(['日均消费金额', '日均收入金额', '日均净收入'])
            .add_yaxis("日均收支金额", 
                    [average_daily_expense, average_daily_income, average_daily_benefit],
                    label_opts=opts.LabelOpts(formatter="{c}"),)
            .set_global_opts(title_opts=opts.TitleOpts(title="（日均）收支金额"),
                            legend_opts=opts.LegendOpts(pos_left="60%")),
            grid_opts=opts.GridOpts(pos_left="55%", pos_right="0%"))
        .render('image/section_1.html'))
    
    if category_stats:
        # 第二部分的文字内容
        report_lines.append("<title 2>二、分类收支统计")

        # 第二部分的图片内容
        #report_lines.append("  以下为消费金额占比:")
        report_text += "二、以下为消费金额占比:"
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
        expense_stats_pie = {}
        for category, amount in sorted_categories:
            percentage = (amount / total_expense * 100).round(2) if total_expense > 0 else 0
            report_text += (f"  {category}: ¥{amount:.2f} ({percentage:.1f}%)")
            expense_stats_pie[category] = percentage
        #report_lines.append("  以下为收入金额占比:")
        report_text += "以下为收入金额占比:"
        sorted_income = sorted(income_stats.items(), key=lambda x: x[1], reverse=True)
        income_stats_pie = {}
        for income, amount in sorted_income:
            percentage = (amount / total_common_income * 100).round(2) if total_common_income > 0 else 0
            report_text += (f"  {income}: ¥{amount:.2f} ({percentage:.1f}%)")
            income_stats_pie[income] = percentage
        report_lines.append("")
        (charts.Grid()
         .add(
            charts.Pie()
            .add(
                "总支出金额占比",
                [list(z) for z in zip(expense_stats_pie.keys(), expense_stats_pie.values())],
                radius=["30%", "65%"],
                center=["30%", "50%"],
                rosetype='area'
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="总支出金额占比"),
                             legend_opts=opts.LegendOpts(pos_bottom="0%")),
            grid_opts=opts.GridOpts(pos_left="0%", pos_right="50%")
         )
         .add(
            charts.Pie()
            .add(
                "总收入金额占比",
                [list(z) for z in zip(income_stats_pie.keys(), income_stats_pie.values())],
                radius=["20%", "65%"],
                center=["75%", "50%"]
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="总收入金额占比", pos_right=('20%')),
                             legend_opts=opts.LegendOpts(pos_bottom="90%")),
            grid_opts=opts.GridOpts(pos_left="50%", pos_right="0%")
         )
         .render('image/section_2.html'))
    
    if daily_expense:
        report_lines.append("<title 3>三、日收支概况及趋势")
        df_info_columns = ['平均数','中位数','众数','最大值','最小值','方差','标准差']
        df_info_index = ['消费金额','收入金额']
        df_info = pd.DataFrame([daily_expense_info,daily_income_info],
                               columns=df_info_columns,index=df_info_index)
        # print(df_info)
        report_text += (f'''\n三、日收支概况及趋势：
                        1.消费数据：
                        平均数：{df_info['平均数'][0]}，中位数：{df_info['中位数'][0]}，众数：{df_info['众数'][0]}，最大值：{df_info['最大值'][0]}，最小值：{df_info['最小值'][0]}，方差：{df_info['方差'][0]}，标准差：{df_info['标准差'][0]}；
                        2.收入数据：
                        平均数：{df_info['平均数'][1]}，中位数：{df_info['中位数'][1]}，众数：{df_info['众数'][1]}，最大值：{df_info['最大值'][1]}，最小值：{df_info['最小值'][1]}，方差：{df_info['方差'][1]}，标准差：{df_info['标准差'][1]}；
                        ''')
        report_lines.append("")
        (charts.Bar()
              .add_xaxis(list(daily_expense.keys()))
              .add_yaxis('每日支出', list(daily_expense.values()),yaxis_index=0)#y0
              .add_yaxis('每日收入', list(daily_income.values()),yaxis_index=1)#y1
              .extend_axis(
                  yaxis=opts.AxisOpts(
                      name='收入',
                      type_='value',
                      position='right',
                      axisline_opts=opts.AxisLineOpts(
                          linestyle_opts=opts.LineStyleOpts(color='#00CC00')
                      ),
                  )
              )
              .set_global_opts(title_opts=opts.TitleOpts(title="每日收支流水"),
                               yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value} 元"))) 
              .overlap(charts.Line()
                       .add_xaxis(list(daily_expense.keys()))
                       .add_yaxis('每日支出', list(daily_expense.values()),
                                  label_opts=opts.LabelOpts(is_show=False),
                                  yaxis_index=0)
                       .add_yaxis('每日收入', list(daily_income.values()),
                                  label_opts=opts.LabelOpts(is_show=False),
                                  yaxis_index=1))
         .render('image/section_3.html'))

    # 添加数据详情
    report_lines.append("<title 4>四、详细消费记录")
    report_lines.append("<br>"+AT.AIUESAgent().get_response(report_text, system_prompt)+"</br>")
    report_lines.append('')
    
    report = "\n".join(report_lines)
    
    # 打印报告
    # print(report_text)

    # 保存报告至 html 文件
    save_report_to_html(report, f"{year}年{month}月消费报告.html", [df_info, monthly_data])
    
    # 返回结构化结果
    return {
        "summary": f"{year}年{month}月共消费¥{total_expense:.2f}",
        "data": monthly_data,
        "statistics": statistics,
        "report": report
    }



# %%
# --------------------------
# 使用示例
# --------------------------
if __name__ == "__main__":
    # 示例调用
    df = proc_washing_data(DATA_PATH)
    target_year = 2025 # 2025年
    target_month = 11  # 11月

    result = extract_monthly_expenses(df, target_year, target_month)

    analyze_and_generate_report(df, target_year, target_month)['report']


