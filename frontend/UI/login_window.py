# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(640, 480)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(640, 480))
        Form.setMaximumSize(QSize(640, 480))
        self.gridLayoutWidget = QWidget(Form)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 0, 621, 471))
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.gridLayoutWidget)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setStyleSheet(u"background-color: rgb(205, 222, 195)")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(0, 20, 619, 150))
        self.pushButton.setStyleSheet(u"border:0;\n"
"border-radius:5;")
        icon = QIcon()
        icon.addFile(u"logo_isli.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QSize(150, 150))
        self.scrollArea = QScrollArea(self.frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(80, 240, 451, 201))
        self.scrollArea.setStyleSheet(u"border: 1 solid;\n"
"border-color: rgb(170, 170, 0);\n"
"border-radius: 5;")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 449, 199))
        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 20, 411, 31))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"border: 2 solid;\n"
"border-color: rgb(170, 170, 127);\n"
"font: 700 11pt \"Segoe UI\";\n"
"border-radius: 5;\n"
"background-color: rgb(227, 227, 169);")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.label_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 80, 411, 31))
        self.label_4.setFont(font)
        self.label_4.setStyleSheet(u"border: 2 solid;\n"
"border-color: rgb(170, 170, 127);\n"
"font: 700 11pt \"Segoe UI\";\n"
"border-radius: 5;\n"
"background-color: rgb(227, 227, 169);")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.lineEdit = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(140, 20, 291, 31))
        self.lineEdit.setStyleSheet(u"background-color: rgb(241, 241, 241);\n"
"border: 2 solid;\n"
"border-color: rgb(170, 170, 0);\n"
"border-radius: 5;\n"
"color: rgb(170, 170, 127);")
        self.lineEdit.setMaxLength(40)
        self.lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.lineEdit.setClearButtonEnabled(True)
        self.pushButton_login = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_login.setObjectName(u"pushButton_login")
        self.pushButton_login.setGeometry(QRect(240, 150, 191, 33))
        self.pushButton_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_login.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.pushButton_login.setAcceptDrops(False)
        self.pushButton_login.setStyleSheet(u"QPushButton {\n"
"    font: 700 11pt \"Segoe UI\";\n"
"    border: 2px solid rgb(170, 170, 127);\n"
"    border-radius: 10;\n"
"    background-color: rgb(227, 227, 169);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(240, 240, 180);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(200, 200, 140);\n"
"}")
        self.pushButton_login.setCheckable(False)
        self.pushButton_login.setAutoDefault(False)
        self.pushButton_login.setFlat(False)
        self.lineEdit_3 = QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setGeometry(QRect(140, 80, 291, 31))
        self.lineEdit_3.setStyleSheet(u"background-color: rgb(241, 241, 241);\n"
"border: 2 solid;\n"
"border-color: rgb(170, 170, 0);\n"
"border-radius: 5;\n"
"color: rgb(170, 170, 127);")
        self.lineEdit_3.setMaxLength(40)
        self.lineEdit_3.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.lineEdit_3.setClearButtonEnabled(True)
        self.pushButton_login_2 = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_login_2.setObjectName(u"pushButton_login_2")
        self.pushButton_login_2.setGeometry(QRect(20, 160, 131, 33))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(8)
        font1.setBold(False)
        font1.setItalic(False)
        self.pushButton_login_2.setFont(font1)
        self.pushButton_login_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_login_2.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.pushButton_login_2.setAcceptDrops(False)
        self.pushButton_login_2.setStyleSheet(u"QPushButton {\n"
"    border: none;\n"
"    background: transparent;\n"
"    color: rgb(0, 85, 255);\n"
"    text-align: left;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    text-decoration: underline;\n"
"    color: rgb(0, 0, 180);\n"
"}")
        self.pushButton_login_2.setCheckable(False)
        self.pushButton_login_2.setAutoDefault(False)
        self.pushButton_login_2.setFlat(True)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(100, 190, 411, 21))
        font2 = QFont()
        font2.setPointSize(14)
        font2.setBold(True)
        self.label.setFont(font2)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_3.addWidget(self.frame, 0, 0, 1, 1)


        self.retranslateUi(Form)

        self.pushButton_login.setDefault(False)
        self.pushButton_login_2.setDefault(False)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"Usuario", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Contrase\u00f1a", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u" Escribe tu email de usuario", None))
        self.pushButton_login.setText(QCoreApplication.translate("Form", u"Login", None))
        self.lineEdit_3.setPlaceholderText(QCoreApplication.translate("Form", u" Escribe tu contrase\u00f1a", None))
        self.pushButton_login_2.setText(QCoreApplication.translate("Form", u"Olvid\u00e9 mi contrase\u00f1a", None))
        self.label.setText(QCoreApplication.translate("Form", u"Bienvenid@ a ISLI", None))
    # retranslateUi

