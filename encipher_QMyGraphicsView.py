from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import pyqtSignal, QPoint

class QMyGraphicsView(QGraphicsView):

    sigMouseMovePoint = pyqtSignal(QPoint)
    # 自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    # QPoint--传递的是view坐标

    def __init__(self, parent = None):
        super(QMyGraphicsView,self).__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.sigMouseMovePoint.emit(event.pos())                # 获取鼠标坐标(view坐标),发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, event)

# from encipher_QMyGraphicsView import *