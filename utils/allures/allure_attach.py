import json
import allure
from models.models import AllureAttachmentType


def allure_attach(source: str, name: str, extension: str) -> None:
    """allure报告上传附件、图片、excel等"""

    # 获取附件的拓展类型
    file_extension = name.split(".")[-1].upper()
    attachment_type = getattr(AllureAttachmentType, file_extension, None)

    allure.attach.file(
        source=source,
        name=name,
        attachment_type=attachment_type.value if attachment_type else None,
        extension=extension,
    )


def allure_step_without_attach(step: str) -> None:
    """无附件的操作步骤"""

    with allure.step(step):
        pass


def allure_step_with_attach(step: str, content: str) -> None:
    """
    Generate a report of the test steps with JSON attachments.
    Args:
        step (str): The name of the step and attachment.
        var (str): The content of attachemnt.
    """

    with allure.step(step):
        allure.attach(
            json.dumps(content, ensure_ascii=False, indent=4),
            step,
            allure.attachment_type.JSON,
        )
