import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Pie, Radar, Scatter, Funnel
from pyecharts import options as opts
from pyecharts.globals import SymbolType


def fetch_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        return text
    except Exception as e:
        st.error(f"抓取URL时出错: {e}")
        return ""


def preprocess_text(text):
    words = jieba.lcut(text)
    # 过滤掉一些常见的标点符号和其他不需要的字符
    filtered_words = [word for word in words if len(word) > 1 and word not in ['\u3000', '\xa0']]
    return filtered_words


def generate_wordcloud(word_counter):
    most_common_20 = word_counter.most_common(20)
    data = [(word, freq) for word, freq in most_common_20]
    wordcloud = (
        WordCloud()
            .add("", data, shape='circle', word_size_range=[20, 100])
            .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
    )
    return wordcloud.render_embed()


def generate_bar_chart(word_counter):
    most_common_20 = word_counter.most_common(20)
    x_data = [word for word, _ in most_common_20]
    y_data = [freq for _, freq in most_common_20]
    bar = (
        Bar()
            .add_xaxis(x_data)
            .add_yaxis("频率", y_data)
            .set_global_opts(
            title_opts=opts.TitleOpts(title="前20个词的频率"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90))
        )
    )
    return bar.render_embed()


def generate_line_chart(word_counter):
    most_common_20 = word_counter.most_common(20)
    x_data = [word for word, _ in most_common_20]
    y_data = [freq for _, freq in most_common_20]
    line = (
        Line()
            .add_xaxis(x_data)
            .add_yaxis("频率", y_data)
            .set_global_opts(title_opts=opts.TitleOpts(title="前20个词的频率趋势"))
    )
    return line.render_embed()


def generate_pie_chart(word_counter):
    most_common_20 = word_counter.most_common(20)
    pie = (
        Pie()
            .add(
            "",
            most_common_20,
            radius=["40%", "75%"],
            rosetype="radius",
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="前20个词的分布"),
            legend_opts=opts.LegendOpts(type_='scroll', pos_left="80%", orient='vertical')
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c}", position="outside"),
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)")
        )
    )
    return pie.render_embed()


def generate_radar_chart(word_counter):
    most_common_20 = word_counter.most_common(20)
    indicators = [{"name": word, "max": max([freq for _, freq in most_common_20])} for word, _ in most_common_20]
    values = [freq for _, freq in most_common_20]
    radar = (
        Radar()
            .add_schema(schema=indicators)
            .add("频率", [values], areastyle_opts=opts.AreaStyleOpts(opacity=0.1))
            .set_global_opts(title_opts=opts.TitleOpts(title="前20个词的频率雷达图"))
    )
    return radar.render_embed()


def generate_scatter_chart(word_counter):
    most_common_20 = word_counter.most_common(20)
    x_data = list(range(len(most_common_20)))
    y_data = [freq for _, freq in most_common_20]
    scatter = (
        Scatter()
            .add_xaxis(x_data)
            .add_yaxis("频率", y_data, symbol=SymbolType.ARROW)
            .set_global_opts(title_opts=opts.TitleOpts(title="前20个词的频率散点图"))
    )
    return scatter.render_embed()


def generate_funnel_chart(word_counter):
    most_common_20 = word_counter.most_common(20)
    funnel = (
        Funnel()
            .add(
            "词汇",
            most_common_20,
            sort_="descending",
            gap=2,
            label_opts=opts.LabelOpts(position="inside"),
            itemstyle_opts=opts.ItemStyleOpts(border_color="#fff", border_width=1),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="前20个词的频率漏斗图"),
            legend_opts=opts.LegendOpts(is_show=False)
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c}")
        )
    )
    return funnel.render_embed()


st.title("文本分析与可视化")
url = st.text_input("请输入文章的URL")
if url:
    text = fetch_text_from_url(url)
    if text:
        words = preprocess_text(text)
        min_freq_threshold = st.number_input("最小频率阈值", value=1, step=1)
        word_counter = Counter(words)
        filtered_word_counter = Counter(
            {word: freq for word, freq in word_counter.items() if freq >= min_freq_threshold})

        chart_type = st.sidebar.selectbox("选择图表类型", ["词云", "柱状图", "折线图", "饼图", "雷达图", "散点图", "漏斗图"])
        chart_generators = {
            "词云": generate_wordcloud,
            "柱状图": generate_bar_chart,
            "折线图": generate_line_chart,
            "饼图": generate_pie_chart,
            "雷达图": generate_radar_chart,
            "散点图": generate_scatter_chart,
            "漏斗图": generate_funnel_chart,
        }

        if chart_type in chart_generators:
            chart_html = chart_generators[chart_type](filtered_word_counter)
            st.components.v1.html(chart_html, height=600)

# 显示词频排名前20的词汇
if 'filtered_word_counter' in locals():
    st.write("词频排名前20的词汇:")
    top_20_words = filtered_word_counter.most_common(20)
    for word, freq in top_20_words:
        st.write(f"{word}: {freq}")