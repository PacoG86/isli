# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu_principal.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.mainLayout.addLayout(self.horizontalLayout)

        self.leftPanel = QFrame(self.centralwidget)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftPanel.setFrameShape(QFrame.Shape.StyledPanel)
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setObjectName(u"leftLayout")
        self.labelLogo = QLabel(self.leftPanel)
        self.labelLogo.setObjectName(u"labelLogo")
        self.labelLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.leftLayout.addWidget(self.labelLogo)

        self.labelUser = QLabel(self.leftPanel)
        self.labelUser.setObjectName(u"labelUser")
        self.labelUser.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.leftLayout.addWidget(self.labelUser)

        self.btnAdmin = QPushButton(self.leftPanel)
        self.btnAdmin.setObjectName(u"btnAdmin")

        self.leftLayout.addWidget(self.btnAdmin)

        self.btnManual = QPushButton(self.leftPanel)
        self.btnManual.setObjectName(u"btnManual")

        self.leftLayout.addWidget(self.btnManual)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftLayout.addItem(self.verticalSpacer)


        self.mainLayout.addWidget(self.leftPanel)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.topBar = QHBoxLayout()
        self.topBar.setObjectName(u"topBar")
        self.hSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.topBar.addItem(self.hSpacer)

        self.btnLogout = QPushButton(self.centralwidget)
        self.btnLogout.setObjectName(u"btnLogout")

        self.topBar.addWidget(self.btnLogout)


        self.rightLayout.addLayout(self.topBar)

        self.mainStack = QStackedWidget(self.centralwidget)
        self.mainStack.setObjectName(u"mainStack")
        self.pageMenu = QWidget()
        self.pageMenu.setObjectName(u"pageMenu")
        self.menuLayout = QVBoxLayout(self.pageMenu)
        self.menuLayout.setObjectName(u"menuLayout")
        self.btnControlCalidad = QPushButton(self.pageMenu)
        self.btnControlCalidad.setObjectName(u"btnControlCalidad")

        self.menuLayout.addWidget(self.btnControlCalidad)

        self.btnHistorico = QPushButton(self.pageMenu)
        self.btnHistorico.setObjectName(u"btnHistorico")

        self.menuLayout.addWidget(self.btnHistorico)

        self.mainStack.addWidget(self.pageMenu)

        self.rightLayout.addWidget(self.mainStack)


        self.mainLayout.addLayout(self.rightLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 30))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Men\u00fa Principal - App Control Calidad", None))
        self.labelLogo.setText(QCoreApplication.translate("MainWindow", u"\ud83e\uddea ISLI", None))
        self.labelUser.setText(QCoreApplication.translate("MainWindow", u"Operario: Juan P\u00e9rez (ROL)", None))
        self.btnAdmin.setText(QCoreApplication.translate("MainWindow", u"Panel de Administraci\u00f3n", None))
        self.btnManual.setText(QCoreApplication.translate("MainWindow", u"Manual de Usuario", None))
        self.btnLogout.setText(QCoreApplication.translate("MainWindow", u"Cerrar Sesi\u00f3n", None))
        self.btnControlCalidad.setText(QCoreApplication.translate("MainWindow", u"CONTROL DE CALIDAD", None))
        self.btnHistorico.setText(QCoreApplication.translate("MainWindow", u"HIST\u00d3RICO", None))
    # retranslateUi

