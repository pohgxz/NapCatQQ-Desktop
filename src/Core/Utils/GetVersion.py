# -*- coding: utf-8 -*-
# 标准库导入
import json
from abc import ABC

# 第三方库导入
import httpx
from creart import AbstractCreator, CreateTargetInfo, it, add_creator, exists_module
from loguru import logger
from PySide6.QtCore import QObject

# 项目内模块导入
from src.Core.Utils.PathFunc import PathFunc
from src.Core.NetworkFunc.Urls import Urls


class GetVersion(QObject):
    """
    ## 提供两个方法, 分别获取本地的 NapCat 和 QQ 的版本
    """

    def __init__(self) -> None:
        super().__init__()

    def fetchRemoteData(self, url: str, key: str, log_message: str) -> str | None:
        """
        ## 获取逻辑
        """
        try:
            logger.info(f"获取 {log_message}")
            response = httpx.get(url)
            logger.info(f"响应码: {response.status_code}")
            logger.debug(f"响应头: {response.headers}")
            logger.debug(f"数据: {response.json()}")
            logger.info(f"耗时: {response.elapsed}")
            return response.json().get(key)
        except (httpx.RequestError, FileNotFoundError, PermissionError, Exception) as e:
            # 项目内模块导入
            from src.Ui.common.info_bar import error_bar
            error_bar(self.tr(f"获取远程 {log_message} 时引发错误, 请查看日志"))
            logger.error(f"获取 {log_message} 时引发 {type(e).__name__}: {e}")
            return None
        finally:
            logger.info(f"获取 {log_message} 结束")

    def getRemoteNapCatVersion(self) -> str | None:
        """
        ## 获取远程 NapCat 的版本信息
        """
        return self.fetchRemoteData(Urls.NAPCATQQ_REPO_API.value.url(), "tag_name", "NapCat 版本信息")

    def getRemoteNapCatUpdateLog(self) -> str | None:
        """
        ## 获取 NapCat 的更新日志
        """
        return self.fetchRemoteData(Urls.NAPCATQQ_REPO_API.value.url(), "body", "NapCat 更新日志")

    def getRemoteQQVersion(self) -> str | None:
        """
        ## 获取远程 QQ 的版本信息
        """
        return self.fetchRemoteData(Urls.QQ_Version.value.url(), "version", "QQ 版本信息")

    def getRemoteNCDVersion(self) -> str | None:
        """
        ## 获取远程 NCD 的版本信息
        """
        return self.fetchRemoteData(Urls.NCD_REPO_API.value.url(), "tag_name", "NCD 版本信息")

    def getRemoteNCDUpdateLog(self) -> str | None:
        """
        ## 获取 NCD 的更新日志
        """
        return self.fetchRemoteData(Urls.NCD_REPO_API.value.url(), "body", "NCD 更新日志")

    def getQQDownloadUrl(self) -> str | None:
        """
        ## 获取 QQ 的下载地址
        """
        try:
            logger.info(f"获取 QQ 下载地址")
            response = httpx.get(Urls.QQ_Version.value.url())
            logger.info(f"响应码: {response.status_code}")
            logger.debug(f"响应头: {response.headers}")
            logger.debug(f"数据: {response.json()}")
            logger.info(f"耗时: {response.elapsed}")
            ver = response.json()["version"].replace("-", ".")
            ver_hash = response.json()["verHash"]
            return f"https://dldir1.qq.com/qqfile/qq/QQNT/{ver_hash}/QQ{ver}_x64.exe"
        except (httpx.RequestError, FileNotFoundError, PermissionError, Exception) as e:
            # 项目内模块导入
            from src.Ui.common.info_bar import error_bar
            error_bar(self.tr(f"获取 QQ 下载地址时引发错误, 请查看日志"))
            logger.error(f"获取 QQ 下载地址时引发 {type(e).__name__}: {e}")
            return None
        finally:
            logger.info(f"获取 QQ 下载地址结束")

    @staticmethod
    def getLocalNapCatVersion() -> str | None:
        """
        ## 获取本地 NapCat 的版本信息
        """
        try:
            # 获取 package.json 路径并读取
            with open(str(it(PathFunc).getNapCatPath() / "package.json"), "r", encoding="utf-8") as f:
                # 读取到参数返回版本信息
                return f"v{json.loads(f.read())['version']}"
        except FileNotFoundError:
            # 文件不存在则返回 None
            return None

    @staticmethod
    def getLocalQQVersion() -> str | None:
        """
        ## 获取本地 QQ 的版本信息
        """
        try:
            if (qq_path := it(PathFunc).getQQPath()) is None:
                # 检查 QQ 目录是否存在
                return None

            with open(str(qq_path / "versions" / "config.json"), "r", encoding="utf-8") as file:
                # 读取 config.json 文件获取版本信息
                return json.load(file)["curVersion"]
        except FileNotFoundError:
            # 文件不存在则返回 None
            return None


class GetVersionClassCreator(AbstractCreator, ABC):
    # 定义类方法targets，该方法返回一个元组，元组中包含了一个CreateTargetInfo对象，
    # 该对象描述了创建目标的相关信息，包括应用程序名称和类名。
    targets = (CreateTargetInfo("src.Core.Utils.GetVersion", "GetVersion"),)

    # 静态方法available()，用于检查模块"PathFunc"是否存在，返回值为布尔型。
    @staticmethod
    def available() -> bool:
        return exists_module("src.Core.Utils.GetVersion")

    # 静态方法create()，用于创建PathFunc类的实例，返回值为PathFunc对象。
    @staticmethod
    def create(create_type: list[GetVersion]) -> GetVersion:
        return GetVersion()


add_creator(GetVersionClassCreator)
