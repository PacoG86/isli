# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu_principal_v2.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDoubleSpinBox,
    QFrame, QGraphicsView, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QMainWindow, QMenuBar,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QStatusBar, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1114, 645)
        MainWindow.setMinimumSize(QSize(300, 300))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"background-color: rgb(182, 197, 173);")
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.barra_izq_frame = QFrame(self.centralwidget)
        self.barra_izq_frame.setObjectName(u"barra_izq_frame")
        self.barra_izq_frame.setStyleSheet(u"background-color: rgb(205, 222, 195);")
        self.barra_izq_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.barra_izq_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.barra_izq_frame)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButton_15 = QPushButton(self.barra_izq_frame)
        self.pushButton_15.setObjectName(u"pushButton_15")
        icon = QIcon()
        icon.addFile(u"logo_isli.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_15.setIcon(icon)
        self.pushButton_15.setIconSize(QSize(150, 150))

        self.verticalLayout_5.addWidget(self.pushButton_15)

        self.label = QLabel(self.barra_izq_frame)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.label)

        self.label_2 = QLabel(self.barra_izq_frame)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_5.addWidget(self.label_2)

        self.label_3 = QLabel(self.barra_izq_frame)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_5.addWidget(self.label_3)

        self.label_10 = QLabel(self.barra_izq_frame)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_5.addWidget(self.label_10)

        self.label_11 = QLabel(self.barra_izq_frame)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_5.addWidget(self.label_11)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.pushButton_historico = QPushButton(self.barra_izq_frame)
        self.pushButton_historico.setObjectName(u"pushButton_historico")

        self.verticalLayout_5.addWidget(self.pushButton_historico)

        self.pushButton_pcontrol = QPushButton(self.barra_izq_frame)
        self.pushButton_pcontrol.setObjectName(u"pushButton_pcontrol")

        self.verticalLayout_5.addWidget(self.pushButton_pcontrol)

        self.pushButton_gAlmacen = QPushButton(self.barra_izq_frame)
        self.pushButton_gAlmacen.setObjectName(u"pushButton_gAlmacen")

        self.verticalLayout_5.addWidget(self.pushButton_gAlmacen)

        self.pushButton_manual = QPushButton(self.barra_izq_frame)
        self.pushButton_manual.setObjectName(u"pushButton_manual")
        self.pushButton_manual.setMinimumSize(QSize(2, 9))

        self.verticalLayout_5.addWidget(self.pushButton_manual)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_6)

        self.pushButton_3 = QPushButton(self.barra_izq_frame)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.verticalLayout_5.addWidget(self.pushButton_3)

        self.verticalLayout_5.setStretch(6, 2)

        self.horizontalLayout_5.addWidget(self.barra_izq_frame)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_5.addWidget(self.line)

        self.ventana_dcha = QFrame(self.centralwidget)
        self.ventana_dcha.setObjectName(u"ventana_dcha")
        self.ventana_dcha.setFrameShape(QFrame.Shape.StyledPanel)
        self.ventana_dcha.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.ventana_dcha)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_6 = QFrame(self.ventana_dcha)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_8 = QLabel(self.frame_6)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_8.addWidget(self.label_8)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.label_7 = QLabel(self.frame_6)
        self.label_7.setObjectName(u"label_7")
        font1 = QFont()
        font1.setItalic(True)
        self.label_7.setFont(font1)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_7)

        self.spinBox = QSpinBox(self.frame_6)
        self.spinBox.setObjectName(u"spinBox")

        self.horizontalLayout_8.addWidget(self.spinBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.label_4 = QLabel(self.frame_6)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_4)

        self.doubleSpinBox = QDoubleSpinBox(self.frame_6)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)

        self.horizontalLayout_8.addWidget(self.doubleSpinBox)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)


        self.verticalLayout_3.addWidget(self.frame_6)

        self.comboBox = QComboBox(self.ventana_dcha)
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout_3.addWidget(self.comboBox)

        self.frame_5 = QFrame(self.ventana_dcha)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.pushButton_5 = QPushButton(self.frame_5)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setMinimumSize(QSize(0, 50))
        self.pushButton_5.setMaximumSize(QSize(16777215, 16777215))
        font2 = QFont()
        font2.setBold(True)
        self.pushButton_5.setFont(font2)

        self.horizontalLayout_7.addWidget(self.pushButton_5)

        self.pushButton_4 = QPushButton(self.frame_5)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setMinimumSize(QSize(0, 50))

        self.horizontalLayout_7.addWidget(self.pushButton_4)


        self.verticalLayout_3.addWidget(self.frame_5)

        self.frame_3 = QFrame(self.ventana_dcha)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.graphicsView_2 = QGraphicsView(self.frame_3)
        self.graphicsView_2.setObjectName(u"graphicsView_2")

        self.horizontalLayout.addWidget(self.graphicsView_2)

        self.graphicsView = QGraphicsView(self.frame_3)
        self.graphicsView.setObjectName(u"graphicsView")

        self.horizontalLayout.addWidget(self.graphicsView)


        self.verticalLayout_3.addWidget(self.frame_3)

        self.frame_2 = QFrame(self.ventana_dcha)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label_6)

        self.label_5 = QLabel(self.frame_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label_5)


        self.verticalLayout_3.addWidget(self.frame_2)

        self.progressBar = QProgressBar(self.ventana_dcha)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.verticalLayout_3.addWidget(self.progressBar)

        self.frame = QFrame(self.ventana_dcha)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tableWidget = QTableWidget(self.frame)
        if (self.tableWidget.columnCount() < 5):
            self.tableWidget.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tableWidget.setObjectName(u"tableWidget")

        self.horizontalLayout_2.addWidget(self.tableWidget)


        self.verticalLayout_3.addWidget(self.frame)

        self.frame_4 = QFrame(self.ventana_dcha)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.pushButton_2 = QPushButton(self.frame_4)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(0, 50))
        self.pushButton_2.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_6.addWidget(self.pushButton_2)

        self.pushButton_8 = QPushButton(self.frame_4)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setMinimumSize(QSize(0, 50))

        self.horizontalLayout_6.addWidget(self.pushButton_8)

        self.pushButton_report = QPushButton(self.frame_4)
        self.pushButton_report.setObjectName(u"pushButton_report")
        self.pushButton_report.setMinimumSize(QSize(0, 50))

        self.horizontalLayout_6.addWidget(self.pushButton_report)


        self.verticalLayout_3.addWidget(self.frame_4)


        self.horizontalLayout_5.addWidget(self.ventana_dcha)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(2, 3)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_5)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1114, 30))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_15.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"CONTROL DE CALIDAD", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"OPERARIO", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"nombre_usuario", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"ID CONTROL", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"ref_control", None))
        self.pushButton_historico.setText(QCoreApplication.translate("MainWindow", u"Hist\u00f3rico de controles", None))
        self.pushButton_pcontrol.setText(QCoreApplication.translate("MainWindow", u"Panel de Control", None))
        self.pushButton_gAlmacen.setText(QCoreApplication.translate("MainWindow", u"Gesti\u00f3n Almac\u00e9n", None))
        self.pushButton_manual.setText(QCoreApplication.translate("MainWindow", u"Manual Usuario", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Logout", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"TOLERANCIA DEFECTOS", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Cantidad m\u00e1x rollo", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Tama\u00f1o m\u00e1x en mm", None))
        self.comboBox.setPlaceholderText("")
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Iniciar Control de Calidad", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Interrumpir control", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Detalles imagen", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Detalles imagen", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Reiniciar", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"Guardar resultados", None))
        self.pushButton_report.setText(QCoreApplication.translate("MainWindow", u"Generar informe", None))
    # retranslateUi

