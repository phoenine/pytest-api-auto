import json
import datetime
import requests
import urllib3
from typing import Any

from models.models import TestcaseMetrics
from models import project_info
from utils.logs.log_control import LOG
from utils.times.time_control import get_current_time

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LarkChatBot:
    """A class to send notifications to Lark ChatBot."""

    def __init__(self, metrics: TestcaseMetrics) -> None:
        """
        Initialize the LarkChatBot with testcase metrics.

        Args:
            metrics (TestcaseMetrics): The metrics related to the test case.
        """
        self.metrics = metrics

    def _send_post_request(self, data: dict, headers: dict) -> dict:
        """
        Helper method to send a POST request to the Lark webhook.

        Args:
            data (dict): The data to send in the request.
            headers (dict): The headers for the request.

        Returns:
            dict: The response data as a dictionary.
        """
        post_data = json.dumps(data)
        response = requests.post(
            project_info.lark_webhook.webhook,
            headers=headers,
            data=post_data,
            verify=False
        )
        return response.json()

    def send_text(self, text: str) -> None:
        """
        Send a simple text message to the Lark chatbot.

        Args:
            text (str): The text message to send.
        """
        data = {
            "msg_type": "text",
            "content": {"text": text}
        }
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        self._send_post_request(data, headers)

    def post(self) -> None:
        """
        Send a detailed message to the Lark chatbot containing test case metrics.
        """
        rich_text = {
            "email": "evan@phoenine.ltd",
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"【{project_info.project_name}自动化测试通知】",
                        "content": [
                            [
                                {"tag": "a", "text": "测试报告", "href": "http://192.168.31.6:39998"},
                                {"tag": "at", "user_id": "7391680670357749762"},
                            ],
                            [
                                {"tag": "text", "text": "项目名称: "},
                                {"tag": "text", "text": f"{project_info.project_name}"},
                            ],
                            [
                                {"tag": "text", "text": "测试人员: "},
                                {"tag": "text", "text": f"{project_info.tester_name}"},
                            ],
                            [
                                {"tag": "text", "text": "运行环境: "},
                                {"tag": "text", "text": f"{project_info.environment}"},
                            ],
                            [
                                {"tag": "text", "text": "成功率: "},
                                {"tag": "text", "text": f"{self.metrics.pass_rate} %"},
                            ],
                            [
                                {"tag": "text", "text": "成功用例数: "},
                                {"tag": "text", "text": f"{self.metrics.passed}"},
                            ],
                            [
                                {"tag": "text", "text": "失败用例数: "},
                                {"tag": "text", "text": f"{self.metrics.failed}"},
                            ],
                            [
                                {"tag": "text", "text": "异常用例数: "},
                                {"tag": "text", "text": f"{self.metrics.failed}"},
                            ],
                            [
                                {"tag": "text", "text": "执行时间: "},
                                {"tag": "text", "text": f"{datetime.datetime.now().strftime('%Y-%m-%d')}"},
                            ],
                        ],
                    }
                }
            },
        }

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        result = self._send_post_request(rich_text, headers)

        # 处理消息发送失败的情况
        if result.get('StatusCode') != 0:
            self._handle_error(result)

    def _handle_error(self, result: dict) -> None:
        """
        Handle errors when sending messages to the Lark chatbot.

        Args:
            result (dict): The result dictionary containing error details.
        """
        time_now = get_current_time()
        result_msg = result.get('errmsg', '未知异常')
        error_data = {
            "msgtype": "text",
            "text": {
                "content": f"[自动通知]飞书机器人消息发送失败，时间：{time_now}, "
                           f"原因：{result_msg}，请及时跟进，谢谢!"
            },
            "at": {"isAtAll": False}
        }
        LOG.error("消息发送失败. \n{}".format(error_data))
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        self._send_post_request(error_data, headers)

