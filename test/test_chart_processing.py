import re

import pytest

import chart_processing
import conversion_settings


class Note:
    """Fake Note class to support testing"""
    def __init__(self):
        self.attachments = {}
        self.attachment_count = 0
        self.nsx_file = 'hello'
        self.note_json = {}
        self.notebook_folder_name = 'notebook_folder_name'
        self.conversion_settings = conversion_settings.ConversionSettings()
        self.image_count = 0


@pytest.mark.parametrize(
    'input_html, output_html_regx', [
        ("""<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"bar chart title","chartType":"bar","xAxisTitle":"x-axis title","yAxisTitle":"y-axis title"}' chart-data='[["","Number 1","Number 2","Number 3","Number 4"],["Category A",500,520,540,520],["Category B",520,540,560,540],["Category C",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
         r"""<p><img src='attachments/\d{15}\.png'></p><p><a href='attachments/\d{15}\.csv'>Chart data file</a></p><p><table border="1" class="dataframe"><thead><tr style="text-align: right;"><th><strong></strong></th><th><strong>Number 1</strong></th><th><strong>Number 2</strong></th><th><strong>Number 3</strong></th><th><strong>Number 4</strong></th></tr></thead><tbody><tr><th><strong>Category A</strong></th><td>500</td><td>520</td><td>540</td><td>520</td></tr><tr><th><strong>Category B</strong></th><td>520</td><td>540</td><td>560</td><td>540</td></tr><tr><th><strong>Category C</strong></th><td>540</td><td>560</td><td>580</td><td>560</td></tr></tbody></table></p>"""),
        ("""<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"Line Chart Title","chartType":"line","xAxisTitle":"x-axis title","yAxisTitle":"y-axis title"}' chart-data='[["","Number 1","Number 2","Number 3","Number 4"],["Category A",500,520,540,520],["Category B",520,540,560,540],["Category C",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
         """<p><img src='attachments/\d{15}\.png'></p><p><a href='attachments/\d{15}\.csv'>Chart data file</a></p><p><table border="1" class="dataframe"><thead><tr style="text-align: right;"><th><strong></strong></th><th><strong>Number 1</strong></th><th><strong>Number 2</strong></th><th><strong>Number 3</strong></th><th><strong>Number 4</strong></th></tr></thead><tbody><tr><th><strong>Category A</strong></th><td>500</td><td>520</td><td>540</td><td>520</td></tr><tr><th><strong>Category B</strong></th><td>520</td><td>540</td><td>560</td><td>540</td></tr><tr><th><strong>Category C</strong></th><td>540</td><td>560</td><td>580</td><td>560</td></tr></tbody></table></p>"""),
        ("""<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"Pie chart title","chartType":"pie","xAxisTitle":"x-axis title","yAxisTitle":"y axis ttile"}' chart-data='[["","cost","price","value","total value"],["something",500,520,540,520],["something else",520,540,560,540],["another thing",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
         """<p><img src='attachments/\d{15}\.png'></p><p><a href='attachments/\d{15}\.csv'>Chart data file</a></p><p><table border="1" class="dataframe"><thead><tr style="text-align: right;"><th><strong></strong></th><th><strong>cost</strong></th><th><strong>price</strong></th><th><strong>value</strong></th><th><strong>total value</strong></th><th><strong>sum</strong></th><th><strong>percent</strong></th></tr></thead><tbody><tr><th><strong>something</strong></th><td>500</td><td>520</td><td>540</td><td>520</td><td>2080</td><td>32.10</td></tr><tr><th><strong>something else</strong></th><td>520</td><td>540</td><td>560</td><td>540</td><td>2160</td><td>33.33</td></tr><tr><th><strong>another thing</strong></th><td>540</td><td>560</td><td>580</td><td>560</td><td>2240</td><td>34.57</td></tr></tbody></table></p>""")
    ], ids=['bar-chart', 'line-chart', 'pie-chart']
)
def test_nsx_chart_processor_check_produced_html(input_html, output_html_regx, image_regression):
    note = Note()
    chart_processor = chart_processing.NSXChartProcessor(note, input_html)

    result = chart_processor.processed_html
    match = re.findall(output_html_regx, result)
    # Note output_html_regx string uses '\d{15}\' to replace the chart id number in the actual html output
    # and escapes the full stop before the file extension

    assert result == match[0]


@pytest.mark.parametrize(
    'input_html', [
        """<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"bar chart title","chartType":"bar","xAxisTitle":"x-axis title","yAxisTitle":"y-axis title"}' chart-data='[["","Number 1","Number 2","Number 3","Number 4"],["Category A",500,520,540,520],["Category B",520,540,560,540],["Category C",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
        """<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"Line Chart Title","chartType":"line","xAxisTitle":"x-axis title","yAxisTitle":"y-axis title"}' chart-data='[["","Number 1","Number 2","Number 3","Number 4"],["Category A",500,520,540,520],["Category B",520,540,560,540],["Category C",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
        """<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"Pie chart title","chartType":"pie","xAxisTitle":"x-axis title","yAxisTitle":"y axis ttile"}' chart-data='[["","cost","price","value","total value"],["something",500,520,540,520],["something else",520,540,560,540],["another thing",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
    ], ids=['bar-chart', 'line-chart', 'pie-chart']
)
def test_plot_chart_image_regression_test(input_html, image_regression):
    note = Note()
    chart_processor = chart_processing.NSXChartProcessor(note, input_html)

    for chart in chart_processor.charts:
        image_regression.check(chart._png_img_buffer.getvalue())


@pytest.mark.parametrize(
    'input_html, csv', [
        ("""<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"bar chart title","chartType":"bar","xAxisTitle":"x-axis title","yAxisTitle":"y-axis title"}' chart-data='[["","Number 1","Number 2","Number 3","Number 4"],["Category A",500,520,540,520],["Category B",520,540,560,540],["Category C",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
         ',Number 1,Number 2,Number 3,Number 4\nCategory A,500,520,540,520\nCategory B,520,540,560,540\nCategory C,540,560,580,560\n'
         ),
        ("""<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"Line Chart Title","chartType":"line","xAxisTitle":"x-axis title","yAxisTitle":"y-axis title"}' chart-data='[["","Number 1","Number 2","Number 3","Number 4"],["Category A",500,520,540,520],["Category B",520,540,560,540],["Category C",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
         ',Number 1,Number 2,Number 3,Number 4\nCategory A,500,520,540,520\nCategory B,520,540,560,540\nCategory C,540,560,580,560\n'
         ),
        ("""<div chart-config='{"range":"A1:E4","direction":"row","rowHeaderExisted":true,"columnHeaderExisted":true,"title":"Pie chart title","chartType":"pie","xAxisTitle":"x-axis title","yAxisTitle":"y axis ttile"}' chart-data='[["","cost","price","value","total value"],["something",500,520,540,520],["something else",520,540,560,540],["another thing",540,560,580,560]]' class="syno-ns-chart-object" style="width: 520px; height: 350px;"></div>""",
         ',cost,price,value,total value,sum,percent\nsomething,500,520,540,520,2080,32.098765432098766\nsomething else,520,540,560,540,2160,33.33333333333333\nanother thing,540,560,580,560,2240,34.5679012345679\n'
         )
    ], ids=['bar-chart', 'line-chart', 'pie-chart']
)
def test_plot_chart_check_csv_content(input_html, csv):
    note = Note()
    chart_processor = chart_processing.NSXChartProcessor(note, input_html)

    for chart in chart_processor.charts:
        assert chart.csv_chart_data_string == csv

