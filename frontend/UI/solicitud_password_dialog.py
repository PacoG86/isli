# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'solicitud_password_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 483)
        Dialog.setStyleSheet(u"background-color: #D1D1D1;")
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_titulo = QLabel(self.frame_3)
        self.label_titulo.setObjectName(u"label_titulo")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_titulo.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_titulo)

        self.label_logo = QLabel(self.frame_3)
        self.label_logo.setObjectName(u"label_logo")
        self.label_logo.setMaximumSize(QSize(60, 60))
        self.label_logo.setPixmap(QPixmap(u"../../logo_isli.png"))
        self.label_logo.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.label_logo)


        self.verticalLayout_2.addWidget(self.frame_3)

        self.label_email = QLabel(self.frame)
        self.label_email.setObjectName(u"label_email")
        font1 = QFont()
        font1.setBold(True)
        self.label_email.setFont(font1)

        self.verticalLayout_2.addWidget(self.label_email)

        self.lineEdit_email = QLineEdit(self.frame)
        self.lineEdit_email.setObjectName(u"lineEdit_email")
        self.lineEdit_email.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.verticalLayout_2.addWidget(self.lineEdit_email)

        self.label_password = QLabel(self.frame)
        self.label_password.setObjectName(u"label_password")
        self.label_password.setFont(font1)

        self.verticalLayout_2.addWidget(self.label_password)

        self.lineEdit_password = QLineEdit(self.frame)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.verticalLayout_2.addWidget(self.lineEdit_password)

        self.label_motivo = QLabel(self.frame)
        self.label_motivo.setObjectName(u"label_motivo")
        self.label_motivo.setFont(font1)

        self.verticalLayout_2.addWidget(self.label_motivo)

        self.textEdit_motivo = QTextEdit(self.frame)
        self.textEdit_motivo.setObjectName(u"textEdit_motivo")
        self.textEdit_motivo.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.verticalLayout_2.addWidget(self.textEdit_motivo)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(Dialog)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_enviar = QPushButton(self.frame_2)
        self.pushButton_enviar.setObjectName(u"pushButton_enviar")
        self.pushButton_enviar.setMinimumSize(QSize(0, 38))
        font2 = QFont()
        font2.setBold(False)
        self.pushButton_enviar.setFont(font2)

        self.horizontalLayout.addWidget(self.pushButton_enviar)

        self.pushButton_cancelar = QPushButton(self.frame_2)
        self.pushButton_cancelar.setObjectName(u"pushButton_cancelar")
        self.pushButton_cancelar.setMinimumSize(QSize(0, 38))

        self.horizontalLayout.addWidget(self.pushButton_cancelar)


        self.verticalLayout.addWidget(self.frame_2)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_titulo.setText(QCoreApplication.translate("Dialog", u"Reestablecer contrase\u00f1a", None))
        self.label_logo.setText("")
        self.label_email.setText(QCoreApplication.translate("Dialog", u"Introduce tu email", None))
        self.lineEdit_email.setText("")
        self.label_password.setText(QCoreApplication.translate("Dialog", u"Nueva Contrase\u00f1a", None))
        self.label_motivo.setText(QCoreApplication.translate("Dialog", u"Motivo", None))
        self.pushButton_enviar.setText(QCoreApplication.translate("Dialog", u"Enviar", None))
        self.pushButton_cancelar.setText(QCoreApplication.translate("Dialog", u"Cancelar", None))
    # retranslateUi

