# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form_historico_controles.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDateEdit,
    QDoubleSpinBox, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_Form_historico(object):
    def setupUi(self, Form_historico):
        if not Form_historico.objectName():
            Form_historico.setObjectName(u"Form_historico")
        Form_historico.resize(1117, 643)
        self.horizontalLayout_4 = QHBoxLayout(Form_historico)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_ventanaPpal = QHBoxLayout()
        self.horizontalLayout_ventanaPpal.setObjectName(u"horizontalLayout_ventanaPpal")
        self.horizontalLayout_ventanaPpal.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.barra_izq_frame = QFrame(Form_historico)
        self.barra_izq_frame.setObjectName(u"barra_izq_frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.barra_izq_frame.sizePolicy().hasHeightForWidth())
        self.barra_izq_frame.setSizePolicy(sizePolicy)
        self.barra_izq_frame.setStyleSheet(u"background-color: rgb(205, 222, 195);")
        self.barra_izq_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.barra_izq_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.barra_izq_frame)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.pushButton_16 = QPushButton(self.barra_izq_frame)
        self.pushButton_16.setObjectName(u"pushButton_16")
        icon = QIcon()
        icon.addFile(u"logo_isli.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_16.setIcon(icon)
        self.pushButton_16.setIconSize(QSize(150, 150))

        self.verticalLayout_6.addWidget(self.pushButton_16)

        self.label_titBarraIzqda = QLabel(self.barra_izq_frame)
        self.label_titBarraIzqda.setObjectName(u"label_titBarraIzqda")
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.label_titBarraIzqda.setFont(font)
        self.label_titBarraIzqda.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_titBarraIzqda)

        self.label_titUsuario = QLabel(self.barra_izq_frame)
        self.label_titUsuario.setObjectName(u"label_titUsuario")

        self.verticalLayout_6.addWidget(self.label_titUsuario)

        self.label_3 = QLabel(self.barra_izq_frame)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_6.addWidget(self.label_3)

        self.verticalSpacer_barraLatIzqda = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_barraLatIzqda)

        self.pushButton_menuPpal = QPushButton(self.barra_izq_frame)
        self.pushButton_menuPpal.setObjectName(u"pushButton_menuPpal")

        self.verticalLayout_6.addWidget(self.pushButton_menuPpal)

        self.pushButton_pcontrol = QPushButton(self.barra_izq_frame)
        self.pushButton_pcontrol.setObjectName(u"pushButton_pcontrol")

        self.verticalLayout_6.addWidget(self.pushButton_pcontrol)

        self.pushButton_manual = QPushButton(self.barra_izq_frame)
        self.pushButton_manual.setObjectName(u"pushButton_manual")
        self.pushButton_manual.setMinimumSize(QSize(2, 9))

        self.verticalLayout_6.addWidget(self.pushButton_manual)

        self.verticalSpacer_barraLatIzqda2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_barraLatIzqda2)

        self.pushButton_3 = QPushButton(self.barra_izq_frame)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.verticalLayout_6.addWidget(self.pushButton_3)


        self.horizontalLayout_ventanaPpal.addWidget(self.barra_izq_frame)

        self.line = QFrame(Form_historico)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_ventanaPpal.addWidget(self.line)

        self.ventana_dcha = QFrame(Form_historico)
        self.ventana_dcha.setObjectName(u"ventana_dcha")
        sizePolicy.setHeightForWidth(self.ventana_dcha.sizePolicy().hasHeightForWidth())
        self.ventana_dcha.setSizePolicy(sizePolicy)
        self.ventana_dcha.setFrameShape(QFrame.Shape.StyledPanel)
        self.ventana_dcha.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.ventana_dcha)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_umbralDefectos = QFrame(self.ventana_dcha)
        self.frame_umbralDefectos.setObjectName(u"frame_umbralDefectos")
        self.frame_umbralDefectos.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_umbralDefectos.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_umbralDefectos)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_umbralDefectos = QLabel(self.frame_umbralDefectos)
        self.label_umbralDefectos.setObjectName(u"label_umbralDefectos")
        font1 = QFont()
        font1.setBold(True)
        self.label_umbralDefectos.setFont(font1)

        self.horizontalLayout_8.addWidget(self.label_umbralDefectos)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer)

        self.label_numDefectos = QLabel(self.frame_umbralDefectos)
        self.label_numDefectos.setObjectName(u"label_numDefectos")
        font2 = QFont()
        font2.setItalic(True)
        self.label_numDefectos.setFont(font2)
        self.label_numDefectos.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_numDefectos)

        self.spinBox_numDefectos = QSpinBox(self.frame_umbralDefectos)
        self.spinBox_numDefectos.setObjectName(u"spinBox_numDefectos")

        self.horizontalLayout_8.addWidget(self.spinBox_numDefectos)

        self.horizontalSpacer_umbralDefs = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_umbralDefs)

        self.label_dimDefectos = QLabel(self.frame_umbralDefectos)
        self.label_dimDefectos.setObjectName(u"label_dimDefectos")
        self.label_dimDefectos.setFont(font2)
        self.label_dimDefectos.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_dimDefectos)

        self.doubleSpinBox_dimDefectos = QDoubleSpinBox(self.frame_umbralDefectos)
        self.doubleSpinBox_dimDefectos.setObjectName(u"doubleSpinBox_dimDefectos")
        self.doubleSpinBox_dimDefectos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.doubleSpinBox_dimDefectos.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)

        self.horizontalLayout_8.addWidget(self.doubleSpinBox_dimDefectos)

        self.horizontalSpacer_umbralDefs2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_umbralDefs2)


        self.verticalLayout_3.addWidget(self.frame_umbralDefectos)

        self.frame_ComboBoxUsuarios = QFrame(self.ventana_dcha)
        self.frame_ComboBoxUsuarios.setObjectName(u"frame_ComboBoxUsuarios")
        self.frame_ComboBoxUsuarios.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_ComboBoxUsuarios.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_ComboBoxUsuarios)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.comboBox_listaUsuarios = QComboBox(self.frame_ComboBoxUsuarios)
        self.comboBox_listaUsuarios.setObjectName(u"comboBox_listaUsuarios")

        self.horizontalLayout_7.addWidget(self.comboBox_listaUsuarios)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_5)

        self.horizontalLayout_7.setStretch(0, 2)

        self.verticalLayout_3.addWidget(self.frame_ComboBoxUsuarios)

        self.frame_fecha = QFrame(self.ventana_dcha)
        self.frame_fecha.setObjectName(u"frame_fecha")
        self.frame_fecha.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_fecha.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_fecha)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_desde = QLabel(self.frame_fecha)
        self.label_desde.setObjectName(u"label_desde")

        self.horizontalLayout.addWidget(self.label_desde)

        self.dateEdit_desde = QDateEdit(self.frame_fecha)
        self.dateEdit_desde.setObjectName(u"dateEdit_desde")
        self.dateEdit_desde.setCalendarPopup(True)

        self.horizontalLayout.addWidget(self.dateEdit_desde)

        self.label_hasta = QLabel(self.frame_fecha)
        self.label_hasta.setObjectName(u"label_hasta")

        self.horizontalLayout.addWidget(self.label_hasta)

        self.dateEdit_hasta = QDateEdit(self.frame_fecha)
        self.dateEdit_hasta.setObjectName(u"dateEdit_hasta")
        self.dateEdit_hasta.setCalendarPopup(True)

        self.horizontalLayout.addWidget(self.dateEdit_hasta)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.pushButton_filtrar = QPushButton(self.frame_fecha)
        self.pushButton_filtrar.setObjectName(u"pushButton_filtrar")
        self.pushButton_filtrar.setMinimumSize(QSize(0, 50))

        self.horizontalLayout.addWidget(self.pushButton_filtrar)

        self.pushButton_limpiarFiltros = QPushButton(self.frame_fecha)
        self.pushButton_limpiarFiltros.setObjectName(u"pushButton_limpiarFiltros")
        self.pushButton_limpiarFiltros.setMinimumSize(QSize(0, 50))

        self.horizontalLayout.addWidget(self.pushButton_limpiarFiltros)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.horizontalLayout.setStretch(4, 1)
        self.horizontalLayout.setStretch(5, 2)

        self.verticalLayout_3.addWidget(self.frame_fecha)

        self.frame_tablaResults = QFrame(self.ventana_dcha)
        self.frame_tablaResults.setObjectName(u"frame_tablaResults")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_tablaResults.sizePolicy().hasHeightForWidth())
        self.frame_tablaResults.setSizePolicy(sizePolicy1)
        self.frame_tablaResults.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_tablaResults.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_tablaResults)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tableWidget_results = QTableWidget(self.frame_tablaResults)
        if (self.tableWidget_results.columnCount() < 6):
            self.tableWidget_results.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_results.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_results.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_results.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_results.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_results.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_results.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.tableWidget_results.setObjectName(u"tableWidget_results")
        self.tableWidget_results.setStyleSheet(u"QTableWidget::item {\n"
"    padding: 5px;\n"
"}")
        self.tableWidget_results.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget_results.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_results.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidget_results.verticalHeader().setStretchLastSection(False)

        self.horizontalLayout_2.addWidget(self.tableWidget_results)


        self.verticalLayout_3.addWidget(self.frame_tablaResults)

        self.frame_btnsDown = QFrame(self.ventana_dcha)
        self.frame_btnsDown.setObjectName(u"frame_btnsDown")
        self.frame_btnsDown.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_btnsDown.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_btnsDown)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_down = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_down)

        self.pushButton_saveObs = QPushButton(self.frame_btnsDown)
        self.pushButton_saveObs.setObjectName(u"pushButton_saveObs")
        self.pushButton_saveObs.setMinimumSize(QSize(0, 50))
        self.pushButton_saveObs.setStyleSheet(u"QPushButton {\n"
"    padding: 0px 12px; \n"
"}\n"
"")

        self.horizontalLayout_3.addWidget(self.pushButton_saveObs)

        self.pushButton_report = QPushButton(self.frame_btnsDown)
        self.pushButton_report.setObjectName(u"pushButton_report")
        self.pushButton_report.setMinimumSize(QSize(0, 50))
        self.pushButton_report.setStyleSheet(u"QPushButton {\n"
"    padding: 0px 12px; \n"
"}\n"
"")

        self.horizontalLayout_3.addWidget(self.pushButton_report)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.horizontalLayout_3.setStretch(0, 1)

        self.verticalLayout_3.addWidget(self.frame_btnsDown)


        self.horizontalLayout_ventanaPpal.addWidget(self.ventana_dcha)

        self.horizontalLayout_ventanaPpal.setStretch(0, 1)
        self.horizontalLayout_ventanaPpal.setStretch(2, 3)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_ventanaPpal)


        self.retranslateUi(Form_historico)

        QMetaObject.connectSlotsByName(Form_historico)
    # setupUi

    def retranslateUi(self, Form_historico):
        Form_historico.setWindowTitle(QCoreApplication.translate("Form_historico", u"Form", None))
        self.pushButton_16.setText("")
        self.label_titBarraIzqda.setText(QCoreApplication.translate("Form_historico", u"HIST\u00d3RICO CONTROLES", None))
        self.label_titUsuario.setText(QCoreApplication.translate("Form_historico", u"OPERARIO", None))
        self.label_3.setText(QCoreApplication.translate("Form_historico", u"nombre_usuario", None))
        self.pushButton_menuPpal.setText(QCoreApplication.translate("Form_historico", u"Control de calidad", None))
        self.pushButton_pcontrol.setText(QCoreApplication.translate("Form_historico", u"Panel de Control", None))
        self.pushButton_manual.setText(QCoreApplication.translate("Form_historico", u"Manual Usuario", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form_historico", u"Logout", None))
        self.label_umbralDefectos.setText(QCoreApplication.translate("Form_historico", u"TOLERANCIA DEFECTOS", None))
        self.label_numDefectos.setText(QCoreApplication.translate("Form_historico", u"Cantidad m\u00e1x rollo", None))
        self.label_dimDefectos.setText(QCoreApplication.translate("Form_historico", u"Tama\u00f1o m\u00e1x en mm", None))
        self.comboBox_listaUsuarios.setPlaceholderText(QCoreApplication.translate("Form_historico", u"-- Filtra por usuario --", None))
        self.label_desde.setText(QCoreApplication.translate("Form_historico", u"Desde", None))
        self.label_hasta.setText(QCoreApplication.translate("Form_historico", u"Hasta", None))
        self.pushButton_filtrar.setText(QCoreApplication.translate("Form_historico", u"Filtrar", None))
        self.pushButton_limpiarFiltros.setText(QCoreApplication.translate("Form_historico", u"Limpiar", None))
        ___qtablewidgetitem = self.tableWidget_results.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Form_historico", u"New Column", None));
        ___qtablewidgetitem1 = self.tableWidget_results.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Form_historico", u"New Column", None));
        ___qtablewidgetitem2 = self.tableWidget_results.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Form_historico", u"New Column", None));
        ___qtablewidgetitem3 = self.tableWidget_results.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Form_historico", u"New Column", None));
        ___qtablewidgetitem4 = self.tableWidget_results.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Form_historico", u"New Column", None));
        ___qtablewidgetitem5 = self.tableWidget_results.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Form_historico", u"New Column", None));
        self.pushButton_saveObs.setText(QCoreApplication.translate("Form_historico", u"Guardar comentarios", None))
        self.pushButton_report.setText(QCoreApplication.translate("Form_historico", u"Mostrar informe", None))
    # retranslateUi

