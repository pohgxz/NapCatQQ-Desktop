# -*- coding: utf-8 -*-

# 第三方库导入
from qfluentwidgets import FluentIcon, ScrollArea, ExpandLayout
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

# 项目内模块导入
from src.Ui.common.InputCard import UrlCard, WsConfigCard, HttpConfigCard, SwitchConfigCard
from src.Core.Config.ConfigModel import ConnectConfig


class ConnectWidget(ScrollArea):
    """
    ## Connect Item 项对应的 QWidget
    """

    def __init__(self, parent=None, config: ConnectConfig = None) -> None:
        super().__init__(parent=parent)
        self.setObjectName("ConnectWidget")
        self.view = QWidget()
        self.cardLayout = ExpandLayout(self)

        # 设置 ScrollArea
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setObjectName("ConnectWidgetView")

        # 调用方法
        self._initWidget()
        self._setLayout()

        if config is not None:
            # 如果传入了 config 则进行解析并填充内部卡片
            self.config = config
            self.fillValue()

    def _initWidget(self) -> None:
        """
        ## 初始化 QWidget 所需要的控件并配置
        创建 InputCard
        """
        self.httpConfigCard = HttpConfigCard(self.view)
        self.httpPostUrlCard = UrlCard(
            icon=FluentIcon.SCROLL,
            title=self.tr("Http 上报地址"),
            content=self.tr("例如 http://127.0.0.1:8080/onebot/v11/http"),
            parent=self.view,
        )
        self.wsCard = WsConfigCard(self.view)
        self.wsReverseCard = SwitchConfigCard(
            icon=FluentIcon.SCROLL,
            title=self.tr("启用 反向WebSocket"),
            content=self.tr("是否启用反向websocket服务"),
            parent=self.view,
        )
        self.wsReverseUrlCard = UrlCard(
            icon=FluentIcon.SCROLL,
            title=self.tr("反向 WebSocket 地址"),
            content=self.tr("反向 WebSocket 对接的地址"),
            parent=self.view,
        )

        # 当 反向WS 地址被删除至空时, 设置为 False
        self.wsReverseUrlCard.emptiedSignal.connect(lambda: self.wsReverseCard.switchButton.setChecked(False))

        # 隐藏卡片，并设置条件显示
        self.httpPostUrlCard.hide()
        self.wsReverseUrlCard.hide()
        self.wsReverseUrlCard.hide()

        self.httpConfigCard.httpEnablePost.button.checkedChanged.connect(
            lambda checked: self.httpPostUrlCard.show() if checked else self.httpPostUrlCard.hide()
        )
        self.wsReverseCard.switchButton.checkedChanged.connect(
            lambda checked: self.wsReverseUrlCard.show() if checked else self.wsReverseUrlCard.hide()
        )

        self.cards = [
            self.httpConfigCard,
            self.httpPostUrlCard,
            self.wsCard,
            self.wsReverseCard,
            self.wsReverseUrlCard,
        ]

    def fillValue(self) -> None:
        """
        ## 如果传入了 config 则对其内部卡片的值进行填充
        """
        self.httpConfigCard.fillValue(self.config.http)
        self.httpPostUrlCard.fillValue(self.config.http.postUrls)
        self.wsCard.fillValue(self.config.ws)
        self.wsReverseCard.fillValue(self.config.reverseWs.enable)
        self.wsReverseUrlCard.fillValue(self.config.reverseWs.urls)

    def _setLayout(self) -> None:
        """
        ## 将 QWidget 内部的 InputCard 添加到布局中
        """
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(2)
        for card in self.cards:
            self.cardLayout.addWidget(card)
            self.adjustSize()

        self.view.setLayout(self.cardLayout)

    def getValue(self) -> dict:
        """
        ## 返回内部卡片的配置结果
        """
        http = self.httpConfigCard.getValue()
        http["postUrls"] = self.httpPostUrlCard.getValue()
        ws = self.wsCard.getValue()  # 单纯为了下面字典整齐)
        reverseWs = {"enable": self.wsReverseCard.getValue(), "urls": self.wsReverseUrlCard.getValue()}

        return {
            "http": http,
            "ws": ws,
            "reverseWs": reverseWs,
        }

    def clearValues(self) -> None:
        """
        ## 清空(还原)内部卡片的配置
        """
        for card in self.cards:
            card.clear()

    def adjustSize(self) -> None:
        h = self.cardLayout.heightForWidth(self.width()) + 46
        return self.resize(self.width(), h)
