import sys
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene, QMessageBox, QWidget, QGraphicsRectItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QEvent
from encipher_ui import *
from encipher_calculate import *
import time

class Encipher_MainWindow(QMainWindow,Ui_MainWindow):

    def __init__(self, parent=None):
        super(Encipher_MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 新增的数据结构
        self.imageScene = QGraphicsScene()
        self.graphicsView.setScene(self.imageScene)

        self.key = ''
        self.nowImage = ''                                              # 当前正常处理的图像的地址
        self.nowImageF = 0                                              # 0未打开 1明文图像 2密文图像
        self.nowImageM = 0                                              # 当前正常处理的图像的M
        self.nowImageN = 0                                              # 当前正常处理的图像的N
        self.thickness = 0                                              # 画笔粗细
        self.pointX = 0                                                 # 鼠标x位置
        self.pointY = 0                                                 # 鼠标y位置
        self.ifPress = 0                                                # 鼠标是否被按下

        # 加密矩阵
        self.Mp = [[0 for i in range(self.nowImageN)] for i in range(self.nowImageM)]

        # ui再设计
        self.statusbar.showMessage('毕业设计 - 基于多重hash函数与一次一密的图像加密算法'
                                   '                      '
                                   '作者：汪钇钰  指导老师：王兴元')

        # 绑定signals和slots
        self.button_openM0.clicked.connect(self.slot_button_openM0)
        self.button_openC.clicked.connect(self.slot_button_openC)
        self.button_encrypt.clicked.connect(self.slot_button_encrypt)
        self.button_openKey.clicked.connect(self.slot_button_openKey)
        self.button_decrypt.clicked.connect(self.slot_button_decrypt)
        self.horSli_chooseThickness.valueChanged[int].connect(self.slot_horSli_chooseThickness)
        self.graphicsView.sigMouseMovePoint.connect(self.slot_graphicsView_MouseMovePoint)
        self.pushButton.clicked.connect(self.slot_pushButton)

        self.graphicsView.viewport().installEventFilter(self)


    # 在graphicsView内移动鼠标的动作
    def slot_graphicsView_MouseMovePoint(self, point):
        scenePoint = self.graphicsView.mapToScene(point)
        self.pointX = scenePoint.x()
        self.pointY = scenePoint.y()
        self.label_pos.setText('当前坐标：(' + str(self.pointX) + ',' + str(self.pointY) + ')')
        if self.ifPress == 1 and self.checkBox_ifChoose.isChecked():
            for i in range(max(int(self.pointX - self.thickness), 0),
                           min(int(self.pointX + self.thickness), self.nowImageM - 1) + 1):
                for j in range(max(int(self.pointY - self.thickness), 0),
                               min(int(self.pointY + self.thickness), self.nowImageN - 1) + 1):
                    self.Mp[i][j] = 1

    # 鼠标按下/松开时的动作
    def eventFilter(self, obj, event):
        if obj is self.graphicsView.viewport():
            if event.type() == QEvent.MouseButtonPress:
                self.ifPress = 1
            elif event.type() == QEvent.MouseButtonRelease:
                self.ifPress = 0
        return QWidget.eventFilter(self, obj, event)

    # 点击打开明文图像按钮的动作
    def slot_button_openM0(self):
        # 打开图像
        fname = QFileDialog.getOpenFileName(self, '请选择明文图像...', './'
                                            , 'Image Files(*.jpg *.png *.gif)')
        if fname[0]:
            self.openImage(fname[0])
            self.nowImageF = 1
            self.textBrowser_debug.insertPlainText('[*]打开明文图像成功：' + fname[0] + '\n')
            self.Mp = [[0 for i in range(self.nowImageN)] for i in range(self.nowImageM)]
        else:
            self.textBrowser_debug.insertPlainText('[!]打开明文图像失败\n')
        # 解锁按钮
        self.checkBox_ifChoose.setEnabled(True)
        self.pushButton.setEnabled(True)
        self.button_encrypt.setEnabled(True)
        self.button_openKey.setEnabled(False)
        self.button_decrypt.setEnabled(False)

    # 点击打开密文图像按钮的动作
    def slot_button_openC(self):
        # 打开图像
        fname = QFileDialog.getOpenFileName(self, '请选择密文图像...', './'
                                            , 'Image Files(*.jpg *.png *.gif)')
        if fname[0]:
            self.openImage(fname[0])
            self.nowImageF = 2
            self.textBrowser_debug.insertPlainText('[*]打开密文图像成功：' + fname[0] + '\n')
        else:
            self.textBrowser_debug.insertPlainText('[!]打开密文图像失败\n')
        # 解锁按钮
        self.checkBox_ifChoose.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.button_encrypt.setEnabled(False)
        self.button_openKey.setEnabled(True)
        self.button_decrypt.setEnabled(False)

    # 点击加密按钮的动作
    def slot_button_encrypt(self):
        reply = QMessageBox.question(self, '提醒', "您确定要加密吗?", QMessageBox.Yes |
                             QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        encrypt_start = time.time()
        # 生成密钥
        self.key = creatKey(self.nowImage)
        self.textBrowser_debug.insertPlainText('[*]生成密钥成功！\n')
        # 生成加密矩阵
        if self.checkBox_ifChoose.isChecked():
            self.textBrowser_debug.insertPlainText('[*]局部加密矩阵生成成功！\n')
        else:
            # Mp[m][n]对应图像M*N
            self.Mp = [[1 for i in range(self.nowImageN)] for i in range(self.nowImageM)]
            self.textBrowser_debug.insertPlainText('[*]默认为全局加密，加密矩阵生成成功！\n')
        # 加密
        tempImage = encrypt_diff(self.nowImage, self.key , self.Mp)
        tempImage = encrypt_rep(tempImage, self.key, self.Mp)
        imageSaveName = self.nowImage[:self.nowImage.find('.')] + '_encrypted' + self.nowImage[self.nowImage.find('.'):]
        self.textBrowser_debug.insertPlainText('[*]加密成功！\n')
        encrypt_end = time.time()
        QMessageBox.about(self, '提醒', "加密完成！共用时" +
                          str(round(encrypt_end - encrypt_start, 2))
                            + "s。文件保存在：\n" + imageSaveName)
        # 保存
        tempImage.save(imageSaveName)
        keyAndMp = np.array([self.key, self.Mp])
        np.save(self.nowImage[:self.nowImage.find('.')] + '_encrypted.key.npy', keyAndMp)
        # 解锁按钮
        self.openImage(imageSaveName)
        self.nowImageF = 0
        self.checkBox_ifChoose.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.button_encrypt.setEnabled(False)
        self.button_openKey.setEnabled(False)
        self.button_decrypt.setEnabled(False)

    # 点击打开密钥文件按钮的动作
    def slot_button_openKey(self):
        # 打开密钥文件
        fname = QFileDialog.getOpenFileName(self, '请选择密钥文件...', './'
                                            , 'npy Files(*.npy)')
        if fname[0]:
            keyAndMp = np.load(fname[0], allow_pickle=True)
            self.key = keyAndMp[0]
            self.Mp = keyAndMp[1]
            self.textBrowser_debug.insertPlainText('[*]打开密钥文件成功：' + fname[0] + '\n')
            self.button_decrypt.setEnabled(True)

    # 点击解密按钮的动作
    def slot_button_decrypt(self):
        reply = QMessageBox.question(self, '提醒', "您确定要解密吗?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        decrypt_start = time.time()
        # 解密过程
        tempImage = decrypt_rep(self.nowImage, self.key, self.Mp)
        tempImage = decrypt_diff(tempImage, self.key, self.Mp)
        imageSaveName = self.nowImage[:self.nowImage.find('.')] + '_decrypt' + self.nowImage[self.nowImage.find('.'):]
        decrypt_end = time.time()
        QMessageBox.about(self, '提醒', "解密完成！" +
                          str(round(decrypt_end - decrypt_start, 2))
                          + "s。文件保存在：\n" + imageSaveName)
        self.textBrowser_debug.insertPlainText('[*]加密成功！\n')
        # 保存
        tempImage.save(imageSaveName)
        # 解锁按钮
        self.openImage(imageSaveName)
        self.nowImageF = 0
        self.checkBox_ifChoose.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.button_encrypt.setEnabled(False)
        self.button_openKey.setEnabled(False)
        self.button_decrypt.setEnabled(False)

    # 滑动调节粗细栏的动作
    def slot_horSli_chooseThickness(self, value):
        self.thickness = value
        self.label_nowthickness.setText("当前画笔粗细：" + str(value))

    # 点击重置后的动作
    def slot_pushButton(self):
        self.Mp = [[0 for i in range(self.nowImageN)] for i in range(self.nowImageM)]
        self.checkBox_ifChoose.setChecked(False)

    # 打开图像后一系列操作
    def openImage(self, imageName):
        # 打开图片
        image = QPixmap(imageName)
        self.nowImage = imageName
        self.nowImageM = image.width()
        self.nowImageN = image.height()
        # 显示图片信息
        self.setWindowTitle('基于多重hash函数与一次一密的图像加密器(' + imageName + ')')
        self.label_picName.setText('图像名称：' + imageName[imageName.rfind('/')+1:])
        self.ifOpenPic.setText('图片状态：已打开')
        self.label_picSize.setText('图像大小：' + str(self.nowImageM) + 'x' + str(self.nowImageN))
        # 显示图片
        self.imageScene.addPixmap(image)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Encipher_MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())