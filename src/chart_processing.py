from abc import ABC, abstractmethod
import ast
import inspect
import io
import logging
import re

from bs4 import BeautifulSoup
import matplotlib.pyplot as pyplot
import pandas as pd

from globals import APP_NAME
from helper_functions import add_strong_between_tags
from sn_attachment import ChartStringNSAttachment, ChartImageNSAttachment


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class Chart(ABC):
    def __init__(self):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._chart_type = str
        self._title = str
        self._df = None
        self._x_axis_title = str
        self._y_axis_title = str
        self._x_category_labels = []
        self._y_category_labels = []
        self._csv_chart_data_string = str
        self._html_chart_data_table = str
        self._png_img_buffer = None

    @abstractmethod
    def plot_chart(self):
        pass

    @staticmethod
    def fig_to_img_buf(fig):
        """Convert a Matplotlib figure to png format in an io.Bytes buffer and return it"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png')  # png is often smaller than jpeg for plots
        buf.seek(0)
        return buf

    @staticmethod
    def remove_chart_frame(ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        return ax

    def set_title_and_axes(self, ax):
        ax.set_title(self._x_axis_title, y=-0.15, fontdict=None)
        ax.set_ylabel(self._y_axis_title)
        ax.set_ylim(self._df.min().min() * 0.9, self._df.max().max() * 1.1)
        return ax

    def make_html_chart_data_table(self):
        self._html_chart_data_table = self._df.to_html(formatters={'percent': '{:,.2f}'.format})
        self._html_chart_data_table = self._html_chart_data_table.replace('\n', '')
        self._html_chart_data_table = re.sub(">\s*<", '><', self._html_chart_data_table)
        self._html_chart_data_table = add_strong_between_tags('<th>', '</th>', self._html_chart_data_table)

    def make_csv_chart_data_string(self):
        self._csv_chart_data_string = self._df.to_csv()

    @property
    def x_axis_title(self):
        return self._x_axis_title

    @x_axis_title.setter
    def x_axis_title(self, value):
        self._x_axis_title = value

    @property
    def y_axis_title(self):
        return self._y_axis_title

    @y_axis_title.setter
    def y_axis_title(self, value):
        self._y_axis_title = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        self._df = value

    @property
    def x_category_labels(self):
        return self._x_category_labels

    @x_category_labels.setter
    def x_category_labels(self, value):
        self._x_category_labels = value

    @property
    def y_category_labels(self):
        return self._y_category_labels

    @y_category_labels.setter
    def y_category_labels(self, value):
        self._y_category_labels = value

    @property
    def csv_chart_data_string(self):
        return self._csv_chart_data_string

    @property
    def png_img_buffer(self):
        return self._png_img_buffer

    @property
    def html_chart_data_table(self):
        return self._html_chart_data_table


class PieChart(Chart):
    def __format_data_for_pie_chart(self):
        self._df["sum"] = self._df.sum(axis=1)
        self._df["percent"] = self._df["sum"] / self._df["sum"].sum() * 100

    def plot_chart(self):
        self.logger.info("Creating pie chart")
        self.__format_data_for_pie_chart()
        explode = [0.02 for x in range(len(self._df.index))]
        fig, ax = pyplot.subplots()
        pyplot.title(self._title)
        pyplot.gca().axis("equal")
        pie = pyplot.pie(self._df['sum'], autopct='%1.2f%%', pctdistance=1.2, explode=explode)
        labels = self._y_category_labels
        pyplot.legend(pie[0], labels, bbox_to_anchor=(1, 1), loc="upper right",
                      bbox_transform=pyplot.gcf().transFigure)
        self._png_img_buffer = self.fig_to_img_buf(fig)


class LineChart(Chart):
    def plot_chart(self):
        self.logger.info("Creating line chart")
        df_transposed = self._df.copy().T
        fig2, ax = pyplot.subplots()
        ax = self.set_title_and_axes(ax)
        ax = self.remove_chart_frame(ax)
        x_ticks = [x for x in range(len(df_transposed.index))]
        plot = df_transposed.plot(kind='line', grid=True, ax=ax, rot=0, xticks=x_ticks, title=self._title)
        fig = plot.get_figure()
        self._png_img_buffer = self.fig_to_img_buf(fig)


class BarChart(Chart):
    def plot_chart(self):
        self.logger.info("Creating bar chart")
        df_transposed = self._df.copy().T
        fig2, ax = pyplot.subplots()
        ax = self.set_title_and_axes(ax)
        ax = self.remove_chart_frame(ax)
        plot = df_transposed.plot(kind='bar', grid=True, ax=ax, rot=0, title=self._title)
        fig = plot.get_figure()
        self._png_img_buffer = self.fig_to_img_buf(fig)


class ChartProcessor(ABC):
    def __init__(self, note, html):
        self._note = note
        self._raw_html = html
        self._processed_html = self._raw_html
        self._soup = BeautifulSoup(self._raw_html, 'html.parser')
        self.chart_pre_processing()
        self._chart_config = {}

    @abstractmethod
    def find_all_charts(self):
        pass

    @property
    def processed_html(self):
        return self._processed_html

    def chart_pre_processing(self):
        chart_tags = self.find_all_charts()

        for tag in chart_tags:

            self.fetch_chart_config_from_html(tag)

            chart = self.create_chart_object()

            self.set_chart_config(chart)

            self.retrieve_chart_data(tag, chart)

            chart.plot_chart()
            chart.make_csv_chart_data_string()
            chart.make_html_chart_data_table()
            self.generate_csv_attachment(chart)
            self.generate_png_attachment(chart)

            self.add_new_chart_elements_to_html(tag, chart)

    def add_new_chart_elements_to_html(self, tag, chart):
        search_for = str(tag)
        replace_with = self.new_chart_elements_html(chart)
        self._processed_html = self._processed_html.replace(search_for, replace_with)

    def new_chart_elements_html(self, chart):
        return f"<p>{self._note.attachments[f'{id(chart)}.png'].html_link}</p>" \
               f"<p>{self._note.attachments[f'{id(chart)}.csv'].html_link}</p>" \
               f"<p>{chart.html_chart_data_table}</p>"

    @abstractmethod
    def create_chart_object(self):
        pass

    @abstractmethod
    def fetch_chart_config_from_html(self, tag):
        pass

    @staticmethod
    @abstractmethod
    def retrieve_chart_data(tag, chart):
        pass

    @abstractmethod
    def set_chart_config(self, chart):
        pass

    def generate_csv_attachment(self, chart):
        self._note.attachments[f"{id(chart)}.csv"] = ChartStringNSAttachment(self._note, f"{id(chart)}.csv",
                                                                             chart.csv_chart_data_string)
        self._note.attachment_count += 1

    def generate_png_attachment(self, chart):
        self._note.attachments[f"{id(chart)}.png"] = ChartImageNSAttachment(self._note, f"{id(chart)}.png",
                                                                            chart.png_img_buffer)
        self._note.image_count += 1


class NSXChartProcessor(ChartProcessor):

    def find_all_charts(self):
        return self._soup.select('p.syno-ns-chart-object')

    def fetch_chart_config_from_html(self, tag):
        chart_config = tag.attrs['chart-config']
        chart_config = chart_config.replace('true', 'True')
        chart_config = chart_config.replace('false', 'False')
        self._chart_config = ast.literal_eval(chart_config)

    @staticmethod
    def retrieve_chart_data(tag, chart):
        raw_data = tag.attrs['chart-data']
        raw_data = ast.literal_eval(raw_data)
        chart.x_category_labels = raw_data.pop(0)[1:]
        chart.y_category_labels = [item.pop(0) for item in raw_data]
        chart.df = pd.DataFrame(raw_data, columns=chart.x_category_labels, index=chart.y_category_labels)

    def set_chart_config(self, chart):
        chart.title = self._chart_config['title']
        chart.x_axis_title = self._chart_config['xAxisTitle']
        chart.y_axis_title = self._chart_config['yAxisTitle']

    def create_chart_object(self):
        if self._chart_config['chartType'] == 'pie':
            return PieChart()
        if self._chart_config['chartType'] == 'line':
            return LineChart()
        if self._chart_config['chartType'] == 'bar':
            return BarChart()
