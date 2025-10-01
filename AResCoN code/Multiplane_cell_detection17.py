# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Multiplane_cell_detection.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# Changes in this version : 
# *  Introduced the case of nan in the XY filtering inside the Mediator.py (lines 179 to 183)
# ** Shifted a block of lines one tab to the right inside the Zfilter.py (lines 474 to 505)


import os
import sys
import time

from os.path import join, isdir, normpath
from os import listdir, scandir
from PyQt5.QtCore import Qt

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap
from pathlib import Path
from collections import defaultdict
import RunFijiMeasurements, FijiFindEdgesMeasurements, RunVisualTest, RunReducedRois, RunMeanMeasurements
import AddMetrics, Checks, PathMaker, EntropyMeasurements, AdditionalMetrics, ConvertLabelstoRois, Mediator, Zfilter
import re
import dill as pickle



current_dir = os.path.dirname(os.path.abspath(__file__))





class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        font = QtGui.QFont()
        font.setPointSize(9)
        MainWindow.setFont(font)
        self.user_selections = {}                                                  # added manually. This is a dict that will save user openfiledialog path selections. For instance, key: images_directory, value: its path
        self.meanmeasurements_selections = {}                                      # similar to user_selections. Used for the 2d filters tab and particularly for autohotkey to run in ROI-background mean differences to run 
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1000, 571))
        self.tabWidget.setObjectName("tabWidget")



        ###### TAB MICROSCOPY ######

        self.tab_microscopy = QtWidgets.QWidget()
        self.tab_microscopy.setObjectName("tab_microscopy")
        MainWindow.setCentralWidget(self.centralwidget)
        self.tabWidget.addTab(self.tab_microscopy, "")

                    ### Scrolls ###
        self.scroll_zplanes = QtWidgets.QComboBox(self.tab_microscopy)
        self.scroll_zplanes.setGeometry(QtCore.QRect(210, 30, 73, 41))
        self.scroll_zplanes.setFont(font)
        self.scroll_zplanes.setObjectName("scroll_zplanes")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")
        self.scroll_zplanes.addItem("")







        self.scroll_bits = QtWidgets.QComboBox(self.tab_microscopy)
        self.scroll_bits.setGeometry(QtCore.QRect(210, 210, 73, 41))
        self.scroll_bits.setFont(font)
        self.scroll_bits.setObjectName("scroll_bits")
        self.scroll_bits.addItem("")
        self.scroll_bits.addItem("")

        self.scroll_system = QtWidgets.QComboBox(self.tab_microscopy)
        self.scroll_system.setGeometry(QtCore.QRect(210, 300, 110, 41))
        self.scroll_system.setFont(font)
        self.scroll_system.setObjectName("scroll_system")
        self.scroll_system.addItem("")
        self.scroll_system.addItem("")

                    ### entries ###
        self.entry_planeDistance = QtWidgets.QLineEdit(self.tab_microscopy)
        self.entry_planeDistance.setGeometry(QtCore.QRect(210, 120, 71, 41))
        self.entry_planeDistance.setFont(font)
        self.entry_planeDistance.setText("")
        self.entry_planeDistance.setFrame(True)
        self.entry_planeDistance.setReadOnly(False)
        self.entry_planeDistance.setObjectName("entry_planeDistance")

                    ### labels ###
        self.label_zplanesNumber = QtWidgets.QLabel(self.tab_microscopy)
        self.label_zplanesNumber.setGeometry(QtCore.QRect(30, 30, 151, 31))
        self.label_zplanesNumber.setFont(font)
        self.label_zplanesNumber.setObjectName("label_zplanesNumber")

        self.label_planeDistance = QtWidgets.QLabel(self.tab_microscopy)
        self.label_planeDistance.setGeometry(QtCore.QRect(30, 140, 151, 31))
        self.label_planeDistance.setFont(font)
        self.label_planeDistance.setObjectName("label_planeDistance")

        self.label_bits = QtWidgets.QLabel(self.tab_microscopy)
        self.label_bits.setGeometry(QtCore.QRect(30, 210, 151, 31))
        self.label_bits.setFont(font)
        self.label_bits.setObjectName("label_bits")

        self.label_system = QtWidgets.QLabel(self.tab_microscopy)
        self.label_system.setGeometry(QtCore.QRect(30, 300, 151, 31))
        self.label_system.setFont(font)
        self.label_system.setObjectName("label_system")

                    ### icons ###
        info_icon_maxgap = QtWidgets.QLabel(self.tab_microscopy)
        info_icon_maxgap.setGeometry(QtCore.QRect(300, 125, 27, 27))  # Position next to the entry
        info_icon_maxgap.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_maxgap.setPixmap(pixmap)
        info_icon_maxgapmessage= ("<p>Maximum z-plane distance that encompasses a single ROI.<br>"
                                  "0 equals to not taking any other plane into account .</p>")
        info_icon_maxgap.setToolTip(info_icon_maxgapmessage)


        ######### TAB MAIN INPUTS #########

        self.tab_mainputs = QtWidgets.QWidget()
        self.tab_mainputs.setObjectName("tab_mainputs")
        self.tabWidget.addTab(self.tab_mainputs, "")


                    ### buttons ###
        self.Button_ImagesFolder = QtWidgets.QPushButton(self.tab_mainputs)
        self.Button_ImagesFolder.setGeometry(QtCore.QRect(640, 55, 131, 31))
        self.Button_ImagesFolder.setFont(font)
        self.Button_ImagesFolder.setObjectName("Button_ImagesFolder")
        self.Button_ImagesFolder.clicked.connect(lambda _, msg="Please select main directory with folders containing images per plane", folderkey = "Images_Folder" \
                                                 : self.FileDialog(message=msg,what_to_select=folderkey))                                                                   # using lambda to prevent running the open dialog before running the main gui. Practically, ignores the state boolean.
        self.Button_RoisFolder = QtWidgets.QPushButton(self.tab_mainputs)
        self.Button_RoisFolder.setGeometry(QtCore.QRect(640, 305, 131, 31))
        self.Button_RoisFolder.setFont(font)
        self.Button_RoisFolder.setObjectName("Button_RoisFolder")
        self.Button_RoisFolder.clicked.connect(lambda _, msg="Please select main directory with folders containing zipped rois per plane ", folderoikey = "Rois_Folder" \
                                                : self.FileDialog(message=msg,what_to_select=folderoikey))                                                                   # using lambda to prevent running the open dialog before running the main gui. Practically, ignores the state boolean.
                    
                    ### labels ###
        self.label = QtWidgets.QLabel(self.tab_mainputs)
        self.label.setGeometry(QtCore.QRect(180, 115, 591, 111))
        self.label.setText("")
        self.label.setPixmap(QPixmap(f"{current_dir}/Screenshot_1.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.label_selectImageFolder = QtWidgets.QLabel(self.tab_mainputs)
        self.label_selectImageFolder.setGeometry(QtCore.QRect(179, 52, 281, 31))
        self.label_selectImageFolder.setFont(font)
        self.label_selectImageFolder.setObjectName("label_selectImageFolder")

        self.label_SelectRoiFolder = QtWidgets.QLabel(self.tab_mainputs)
        self.label_SelectRoiFolder.setGeometry(QtCore.QRect(179, 300, 361, 31))
        self.label_SelectRoiFolder.setFont(font)
        self.label_SelectRoiFolder.setObjectName("label_SelectRoiFolder")

        self.label_6 = QtWidgets.QLabel(self.tab_mainputs)
        self.label_6.setGeometry(QtCore.QRect(180, 365, 591, 111))
        self.label_6.setFont(font)
        self.label_6.setText("")
        self.label_6.setPixmap(QPixmap(f"{current_dir}/Screenshot_2.jpg"))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")

                    ### checkboxes ###
        self.checkBoxCompletedTab2 = QtWidgets.QCheckBox(self.tab_mainputs)
        self.checkBoxCompletedTab2.setGeometry(QtCore.QRect(850, 480, 171, 61))
        self.checkBoxCompletedTab2.setObjectName("checkBoxCompletedTab2")
        

        ###### TAB MEASURE ROIS ######
        
        self.tab_measurois = QtWidgets.QWidget()
        self.tab_measurois.setObjectName("tab_measurois")
        self.tabWidget.addTab(self.tab_measurois, "")
                    ### labels ###
        self.label_saveResults = QtWidgets.QLabel(self.tab_measurois)
        self.label_saveResults.setGeometry(QtCore.QRect(245, 45, 451, 31))
        self.label_saveResults.setFont(font)
        self.label_saveResults.setObjectName("label_saveResults")

        self.label_Fijipath = QtWidgets.QLabel(self.tab_measurois)
        self.label_Fijipath.setGeometry(QtCore.QRect(245, 110, 451, 31))
        self.label_Fijipath.setFont(font)
        self.label_Fijipath.setObjectName("label_Fijipath")

        self.label_warnings = QtWidgets.QLabel(self.tab_measurois)
        self.label_warnings.setGeometry(QtCore.QRect(245, 200, 451, 31))
        self.label_warnings.setFont(font)
        self.label_warnings.setObjectName("warnings")
        self.label_warnings.setStyleSheet("""
        QLabel {
            border: 1px solid lightgray;
            background-color: #f7f7f7;
            padding: 5px;
                }
        """)
        
        
                    ### buttons ###
        self.Button_MeasuresaveFolder = QtWidgets.QPushButton(self.tab_measurois)
        self.Button_MeasuresaveFolder.setGeometry(QtCore.QRect(615, 47, 131, 31))
        self.Button_MeasuresaveFolder.setFont(font)
        self.Button_MeasuresaveFolder.setObjectName("Button_ImagesFolder")
        self.Button_MeasuresaveFolder.clicked.connect(lambda _, msg="Please select directory to save your measurements", folderkey = "Measurements_Folder" \
                                                 : self.FileDialog(message=msg,what_to_select=folderkey)) 
        
        self.Button_Fijipath = QtWidgets.QPushButton(self.tab_measurois)
        self.Button_Fijipath.setGeometry(QtCore.QRect(615, 111, 131, 31))
        self.Button_Fijipath.setFont(font)
        self.Button_Fijipath.setObjectName("Button_Fijipath")
        self.Button_Fijipath.clicked.connect(lambda _, msg="Find and double-click the ImageJ.exe or fiji.exe file", folderkey = "FijiexePath" \
                                                 : self.FileDialog(message=msg,what_to_select=folderkey))
        
        self.Button_GetMeasurements = QtWidgets.QPushButton(self.tab_measurois)
        self.Button_GetMeasurements.setGeometry(QtCore.QRect(363, 480, 251, 31))
        self.Button_GetMeasurements.setFont(font)
        self.Button_GetMeasurements.setObjectName("Button_GetMeasurements")
        self.Button_GetMeasurements.clicked.connect(self.InitializeGetMeasurementsOfRois)
                    
                    ### icons ###
        info_icon_getme = QtWidgets.QLabel(self.tab_measurois)
        info_icon_getme.setGeometry(QtCore.QRect(584, 482, 27, 27))  # Position next to the entry
        info_icon_getme.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_getme.setPixmap(pixmap)
        info_icon_getmessage= ("<p>Generates  csv files in the main save folder.<br>"
                                "These files contain the measurements of rois. "
                                "No measurement data is not saved in AResCoN at this stage .</p>")
        info_icon_getme.setToolTip(info_icon_getmessage)

                    ### checkboxes ###
        
        self.checkBoxCompletedTab3 = QtWidgets.QCheckBox(self.tab_measurois)
        self.checkBoxCompletedTab3.setGeometry(QtCore.QRect(850, 480, 171, 61))
        self.checkBoxCompletedTab3.setObjectName("checkBoxCompletedTab3")
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

                ###### TAB ADD METRICS ######
        self.tab_addmetrics = QtWidgets.QWidget()
        self.tab_addmetrics.setObjectName("tab_addmetrics")
        self.tabWidget.addTab(self.tab_addmetrics, "")

                            ### buttons ###
        self.Button_Addmetrics = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_Addmetrics.setGeometry(QtCore.QRect(100, 160, 200, 31))
        self.Button_Addmetrics.setFont(font)
        self.Button_Addmetrics.setObjectName("Button_Addmetrics")
        self.Button_Addmetrics.clicked.connect(self.InitializeAddMetrics)

        self.Button_Savemetrics = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_Savemetrics.setGeometry(QtCore.QRect(380, 160, 200, 31))
        self.Button_Savemetrics.setFont(font)
        self.Button_Savemetrics.setObjectName("Button_Savemetrics")
        self.Button_Savemetrics.clicked.connect(self.SavePickleMetrics)

        self.Button_Loadmetrics = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_Loadmetrics.setGeometry(QtCore.QRect(650, 160, 200, 31))
        self.Button_Loadmetrics.setFont(font)
        self.Button_Loadmetrics.setObjectName("Button_Loadmetrics")
        self.Button_Loadmetrics.clicked.connect(self.LoadMetrics)

        self.Button_FindEdges = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_FindEdges.setGeometry(QtCore.QRect(100, 360, 200, 31))
        self.Button_FindEdges.setFont(font)
        self.Button_FindEdges.setObjectName("Button_FindEdges")
        self.Button_FindEdges.clicked.connect(self.FindEdges)

        self.Button_SaveEdges = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_SaveEdges.setGeometry(QtCore.QRect(380, 360, 200, 31))
        self.Button_SaveEdges.setFont(font)
        self.Button_SaveEdges.setObjectName("Button_SaveEdges")
        self.Button_SaveEdges.clicked.connect(self.InitializeAddFindEdgesMetrics)

        self.Button_getentropy = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_getentropy.setGeometry(QtCore.QRect(100, 450, 200, 31))
        self.Button_getentropy.setFont(font)
        self.Button_getentropy.setObjectName("Button_getentropy")
        self.Button_getentropy.clicked.connect(self.GetEntropy)

        self.Button_addentropy = QtWidgets.QPushButton(self.tab_addmetrics)
        self.Button_addentropy.setGeometry(QtCore.QRect(380, 450, 200, 31))
        self.Button_addentropy.setFont(font)
        self.Button_addentropy.setObjectName("Button_addentropy")
        self.Button_addentropy.clicked.connect(self.InitializeAddEntropy)



                            ### labels ###
        self.label_mainmeasr  = QtWidgets.QLabel(self.tab_addmetrics)
        self.label_mainmeasr.setGeometry(QtCore.QRect(270, 20, 500, 100))
        custom_mainmeasr_font = QtGui.QFont()
        custom_mainmeasr_font.setPointSize(13)
        self.label_mainmeasr.setFont(custom_mainmeasr_font)
        self.label_mainmeasr.setObjectName("label_mainmeasr")

        self.label_metrics  = QtWidgets.QLabel(self.tab_addmetrics)
        self.label_metrics.setGeometry(QtCore.QRect(270, 240, 500, 100))
        custom_metrics_font = QtGui.QFont()
        custom_metrics_font.setPointSize(13)
        self.label_metrics.setFont(custom_metrics_font)
        self.label_metrics.setObjectName("label_metrics")

        self.or_label = QtWidgets.QLabel("OR", self.tab_addmetrics) 
        self.or_label.setGeometry (600, 160, 28, 28)
        self.or_label.setFont(QtGui.QFont("Arial",12)) 
        self.or_label.setAlignment(Qt.AlignCenter)

                          ### arrow labels ###
        self.arrow1_label = QtWidgets.QLabel("→", self.tab_addmetrics) 
        self.arrow1_label.setGeometry (320, 160, 32, 28)
        self.arrow1_label.setFont(QtGui.QFont("Arial",21))  
        self.arrow1_label.setAlignment(Qt.AlignCenter)

        self.arrow2_label = QtWidgets.QLabel("→", self.tab_addmetrics)  
        self.arrow2_label.setGeometry (320, 360, 32, 28)
        self.arrow2_label.setFont(QtGui.QFont("Arial",21))  
        self.arrow2_label.setAlignment(Qt.AlignCenter)

        self.arrow3_label = QtWidgets.QLabel("→", self.tab_addmetrics) 
        self.arrow3_label.setGeometry (320, 450, 32, 28)
        self.arrow3_label.setFont(QtGui.QFont("Arial",21)) 
        self.arrow3_label.setAlignment(Qt.AlignCenter)

                            ### icons  ### 
        info_icon_addme = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_addme.setGeometry(QtCore.QRect(270, 162, 27, 27))  # Position next to the entry
        info_icon_addme.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_addme.setPixmap(pixmap)
        info_icon_addmessage= ("<p>Adds your newly obtained csv measurements to the software. <br>"
                                "Generate Measurements only creates the csv files, whereas this option adds the data to the program.</p>")
        info_icon_addme.setToolTip(info_icon_addmessage)


        info_icon_saveme = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_saveme.setGeometry(QtCore.QRect(551, 162, 27, 27))  # Position next to the entry
        info_icon_saveme.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_saveme.setPixmap(pixmap)
        info_icon_savemessage= ("<p>Generates a file in your workspace directory under the name saved_metrics.pkl<br>"
                                "In case that you close AResCoN you can load the measurements directly. </p>")
        info_icon_saveme.setToolTip(info_icon_savemessage)


        info_icon_loadme = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_loadme.setGeometry(QtCore.QRect(820, 162, 27, 27))  # Position next to the entry
        info_icon_loadme.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_loadme.setPixmap(pixmap)
        info_icon_loadmessage= ("<p>Loads already saved data in your workspace under the name saved_metrics.pkl <br>"
                                "Useful when you close AResCoN and open it again. </p>")
        info_icon_loadme.setToolTip(info_icon_loadmessage)
              

        info_icon_fe = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_fe.setGeometry(QtCore.QRect(270, 362, 27, 27))  # Position next to the entry
        info_icon_fe.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_fe.setPixmap(pixmap)
        info_icon_message= ("<p>Runs Fiji, executes the Find Edges command and saves StdDev in the path where the main save folder is.<br>"
                             "Do not use mouse or keyboard as long as it is running.</p>")
        info_icon_fe.setToolTip(info_icon_message)

        info_icon_addedge = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_addedge.setGeometry(QtCore.QRect(551, 362, 27, 27))  # Position next to the entry
        info_icon_addedge.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_addedge.setPixmap(pixmap)
        info_icon_addedge_message= ("<p>Adds your newly obtained StdDev find edges measurement as a new <br>"
                                    "column to your main measurements.</p>")
        info_icon_addedge.setToolTip(info_icon_addedge_message)


        info_icon_getentro = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_getentro.setGeometry(QtCore.QRect(271, 452, 27, 27))  # Position next to the entry
        info_icon_getentro.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_getentro.setPixmap(pixmap)
        info_icon_getentro_message= ("<p>Calculates Shannon entropy for each ROI <br>"
                                    "and creates a respective csv with the metric. This will take some time.</p>")
        info_icon_getentro.setToolTip(info_icon_getentro_message)


        info_icon_addentro = QtWidgets.QLabel(self.tab_addmetrics)
        info_icon_addentro.setGeometry(QtCore.QRect(551, 452, 27, 27))  # Position next to the entry
        info_icon_addentro.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_addentro.setPixmap(pixmap)
        info_icon_addentro_message= ("<p>Adds your newly obtained Shannon entropy measurement as a new <br>"
                                    "column to your main measurements.</p>")
        info_icon_addentro.setToolTip(info_icon_addentro_message)


         ###### TAB Filtering ######
        
        self.tab_filtering = QtWidgets.QWidget()
        self.tab_filtering.setObjectName("Filtering")
        self.tabWidget.addTab(self.tab_filtering, "")

                ### labels ###
        self.label_surr_fltr = QtWidgets.QLabel(self.tab_filtering)
        self.label_surr_fltr.setGeometry(QtCore.QRect(315, 30, 550, 30))
        custom_msg_surr_font = QtGui.QFont()
        custom_msg_surr_font.setPointSize(13)
        self.label_surr_fltr.setFont(custom_msg_surr_font)
        self.label_surr_fltr.setObjectName("label_surr_fltr")

        self.label_large_factor = QtWidgets.QLabel(self.tab_filtering)
        self.label_large_factor.setGeometry(QtCore.QRect(70, 105, 550, 30))
        custom_msg_largfac_font = QtGui.QFont()
        custom_msg_largfac_font.setPointSize(10)
        self.label_large_factor.setFont(custom_msg_largfac_font)
        self.label_large_factor.setObjectName("label_large_factor")

        self.label_ahk = QtWidgets.QLabel(self.tab_filtering)
        self.label_ahk.setGeometry(QtCore.QRect(70, 165, 300, 30))
        custom_msg_ahk_font = QtGui.QFont()
        custom_msg_ahk_font.setPointSize(10)
        self.label_ahk.setFont(custom_msg_ahk_font)
        self.label_ahk.setObjectName("label_ahk")

        self.label_exeahk = QtWidgets.QLabel(self.tab_filtering)
        self.label_exeahk.setGeometry(QtCore.QRect(70, 225, 300, 30))
        custom_msg_exeahk_font = QtGui.QFont()
        custom_msg_exeahk_font.setPointSize(10)
        self.label_exeahk.setFont(custom_msg_exeahk_font)
        self.label_exeahk.setObjectName("label_exeahk")


        self.label_delta_mean = QtWidgets.QLabel(self.tab_filtering)
        self.label_delta_mean.setGeometry(QtCore.QRect(70, 225, 550, 30))
        custom_msg_delta_mean = QtGui.QFont()
        custom_msg_delta_mean.setPointSize(10)
        self.label_delta_mean.setFont(custom_msg_delta_mean)
        self.label_delta_mean.setObjectName("label_delta_mean")


        self.label_measure_filter = QtWidgets.QLabel(self.tab_filtering)
        self.label_measure_filter.setGeometry(QtCore.QRect(357, 330, 550, 30))
        custom_msg_measure_filter = QtGui.QFont()
        custom_msg_measure_filter.setPointSize(13)
        self.label_measure_filter.setFont(custom_msg_measure_filter)
        self.label_measure_filter.setObjectName("label_measure_filter")

                ### entries ###
        self.mean_bacgkround_selections:dict = {}                                                                                              
        self.entry_enlarge_roi = QtWidgets.QLineEdit(self.tab_filtering)
        self.entry_enlarge_roi.setGeometry(QtCore.QRect(385, 110, 90, 30))
        self.entry_enlarge_roi.setFont(font)
        self.entry_enlarge_roi.setPlaceholderText("e.g. 30")  
        self.entry_enlarge_roi.setFrame(True)
        self.entry_enlarge_roi.setReadOnly(False)
        self.entry_enlarge_roi.setObjectName("entry_enlarge_roi")


        self.entry_1planefilters = QtWidgets.QTextEdit(self.tab_filtering)
        self.entry_1planefilters.setGeometry(QtCore.QRect(230, 386, 540, 150))
        custom_1planefilters_font = QtGui.QFont()
        custom_1planefilters_font.setPointSize(10)
        self.entry_1planefilters.setFont(custom_1planefilters_font)
        oneplane_filters_msg = ("e.g. (RoiAndBackgrounDifference > SurroundingMean*0.3) or (Area>100 and Circ. > 0.9) \n\n"
                                "Measurement names must be only alphabet characters(. dots allowed) without 'and','nan'(case sensitive) or spaces. "
                                "All conditions must be valid for a ROI to pass. Read the documentation.")
        self.entry_1planefilters.setPlaceholderText(oneplane_filters_msg) 
        self.entry_1planefilters.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.entry_1planefilters.setReadOnly(False)
        self.entry_1planefilters.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.entry_1planefilters.setStyleSheet("""
                                QTextEdit {
                                    border: 1px solid lightgray;
                                    background-color: #f8ecf6;
                                    border-radius: 4px;
                                    padding: 5px;
                                }
                                QTextEdit:focus {
                                    border: 1px solid #b0b0b0; 
                                    outline: none;
                                }
                            """)
        self.entry_1planefilters.setObjectName("entry_1planefilters")

                ### buttons ###

        self.Button_ahk = QtWidgets.QPushButton(self.tab_filtering)
        self.Button_ahk.setGeometry(QtCore.QRect(385, 165, 90, 30))
        self.Button_ahk.setFont(font)
        self.Button_ahk.setObjectName("Button_ahk")  
        self.Button_ahk.clicked.connect(lambda _, msg="Find and double-click the .ahk script", folderkey = "ahk_script" \
                                                 : self.MeanMeasurementsDialog(message=msg,what_to_select=folderkey))

        self.Button_exeahk = QtWidgets.QPushButton(self.tab_filtering)
        self.Button_exeahk.setGeometry(QtCore.QRect(385, 225, 90, 30))
        self.Button_exeahk.setFont(font)
        self.Button_exeahk.setObjectName("Button_exeahk")  
        self.Button_exeahk.clicked.connect(lambda _, msg="Find and double-click the AutoHotkeyUX.exe", folderkey = "ahk_exec" \
                                                 : self.MeanMeasurementsDialog(message=msg,what_to_select=folderkey))

        self.Button_meanfilter = QtWidgets.QPushButton(self.tab_filtering)
        self.Button_meanfilter.setGeometry(QtCore.QRect(620, 215, 340, 31))
        self.Button_meanfilter.setFont(font)
        self.Button_meanfilter.setObjectName("Button_meanfilter")  
        self.Button_meanfilter.clicked.connect(self.InitializeMeanBackground)      

        self.Button_opensave = QtWidgets.QPushButton(self.tab_filtering)
        self.Button_opensave.setGeometry(QtCore.QRect(35, 505, 150, 31))
        self.Button_opensave.setFont(font)
        self.Button_opensave.setObjectName("Button_opensave")
        self.Button_opensave.clicked.connect(self.OpenaCsvFile)

                ### Apply filters ### 
        self.Button_1planefilter = QtWidgets.QPushButton(self.tab_filtering)
        self.Button_1planefilter.setGeometry(QtCore.QRect(820, 505, 150, 31))
        self.Button_1planefilter.setFont(font)
        self.Button_1planefilter.setObjectName("Button_1planefilter")
        self.Button_1planefilter.clicked.connect(self.ApplyOnePlaneFilters)

                ### icons ###

        self.label_enlarge_example = QtWidgets.QLabel(self.tab_filtering)
        self.label_enlarge_example.setGeometry(QtCore.QRect(625, 110, 330, 90))
        self.label_enlarge_example.setFont(font)
        self.label_enlarge_example.setText("")
        self.label_enlarge_example.setPixmap(QPixmap(f"{current_dir}/Example_Photos/enlarge.jpg"))
        self.label_enlarge_example.setScaledContents(True)
        self.label_enlarge_example.setObjectName("enlarge_example")


        ##### TAB z-Filter    #######

        self.tab_zfilter = QtWidgets.QWidget()
        self.tab_zfilter.setObjectName("tab_zfilter")
        self.tabWidget.addTab(self.tab_zfilter, "")

                ### labels ###

        self.label_tot_scor_filter = QtWidgets.QLabel(self.tab_zfilter)
        self.label_tot_scor_filter.setGeometry(QtCore.QRect(305, 50, 550, 30))
        custom_single_filter_msg_font = QtGui.QFont()
        custom_single_filter_msg_font.setPointSize(13)
        self.label_tot_scor_filter.setFont(custom_single_filter_msg_font)
        self.label_tot_scor_filter.setObjectName("label_tot_scor_filter")
        
        self.label_engulfers_section = QtWidgets.QLabel(self.tab_zfilter)
        self.label_engulfers_section.setGeometry(QtCore.QRect(120, 150, 550, 30))
        custom_engulfer_filter_msg_font = QtGui.QFont()
        custom_engulfer_filter_msg_font.setPointSize(13)
        self.label_engulfers_section.setFont(custom_engulfer_filter_msg_font)
        self.label_engulfers_section.setObjectName("label_engulfers_section")
                
        self.label_1to1_section = QtWidgets.QLabel(self.tab_zfilter)
        self.label_1to1_section.setGeometry(QtCore.QRect(400, 150, 550, 30))
        custom_1to1_filter_msg_font = QtGui.QFont()
        custom_1to1_filter_msg_font.setPointSize(13)
        self.label_1to1_section.setFont(custom_1to1_filter_msg_font)
        self.label_1to1_section.setObjectName("label_1to1_section")

        self.label_1tomore_section = QtWidgets.QLabel(self.tab_zfilter)
        self.label_1tomore_section.setGeometry(QtCore.QRect(700, 150, 550, 30))
        custom_1tomore_filter_msg_font = QtGui.QFont()
        custom_1tomore_filter_msg_font.setPointSize(13)
        self.label_1tomore_section.setFont(custom_1tomore_filter_msg_font)
        self.label_1tomore_section.setObjectName("label_1tomore_section")

                ### entries ###

        self.ratio_intersecting = QtWidgets.QLineEdit(self.tab_zfilter)
        self.ratio_intersecting.setGeometry(QtCore.QRect(97, 200, 140, 30))
        self.ratio_intersecting.setFont(font)
        self.ratio_intersecting.setPlaceholderText("I   by default 0.8") 
        self.ratio_intersecting.setFrame(True)
        self.ratio_intersecting.setReadOnly(False)
        self.ratio_intersecting.setObjectName("ratio_intersecting_")
        self.ratio_intersecting.setStyleSheet(
        "QLineEdit { background-color: rgb(218, 227, 243); }")

        self.one_to_1_engulf_size_threshold = QtWidgets.QLineEdit(self.tab_zfilter)
        self.one_to_1_engulf_size_threshold.setGeometry(QtCore.QRect(97, 250, 140, 30))
        self.one_to_1_engulf_size_threshold.setFont(font)
        self.one_to_1_engulf_size_threshold.setPlaceholderText("II  by default 1.5") 
        self.one_to_1_engulf_size_threshold.setFrame(True)
        self.one_to_1_engulf_size_threshold.setReadOnly(False)
        self.one_to_1_engulf_size_threshold.setObjectName("one_to_1_engulf_size_threshold")
        self.one_to_1_engulf_size_threshold.setStyleSheet(
        "QLineEdit { background-color: rgb(218, 227, 243); }")

        self.one_to_1_engulfed_intersection_threshold = QtWidgets.QLineEdit(self.tab_zfilter)
        self.one_to_1_engulfed_intersection_threshold.setGeometry(QtCore.QRect(97, 300, 140, 30))
        self.one_to_1_engulfed_intersection_threshold.setFont(font)
        self.one_to_1_engulfed_intersection_threshold.setPlaceholderText("III by default 0.9") 
        self.one_to_1_engulfed_intersection_threshold.setFrame(True)
        self.one_to_1_engulfed_intersection_threshold.setReadOnly(False)
        self.one_to_1_engulfed_intersection_threshold.setObjectName("self.one_to_1_engulfed_intersection_threshold")
        self.one_to_1_engulfed_intersection_threshold.setStyleSheet(
        "QLineEdit { background-color: rgb(218, 227, 243); }")

        self.negligible_1to1_iou = QtWidgets.QLineEdit(self.tab_zfilter)
        self.negligible_1to1_iou.setGeometry(QtCore.QRect(402, 200, 140, 30))
        self.negligible_1to1_iou.setFont(font)
        self.negligible_1to1_iou.setPlaceholderText("IV   by default 0.2") 
        self.negligible_1to1_iou.setFrame(True)
        self.negligible_1to1_iou.setReadOnly(False)
        self.negligible_1to1_iou.setObjectName("self.negligible_1to1_iou")
        self.negligible_1to1_iou.setStyleSheet(
        "QLineEdit { background-color: rgb(255, 242, 204); }")

        self.minimum_1to1_intersection = QtWidgets.QLineEdit(self.tab_zfilter)
        self.minimum_1to1_intersection.setGeometry(QtCore.QRect(402, 250, 140, 30))
        self.minimum_1to1_intersection.setFont(font)
        self.minimum_1to1_intersection.setPlaceholderText("V    by default 0.8") 
        self.minimum_1to1_intersection.setFrame(True)
        self.minimum_1to1_intersection.setReadOnly(False)
        self.minimum_1to1_intersection.setObjectName("minimum_1to1_intersection")
        self.minimum_1to1_intersection.setStyleSheet(
        "QLineEdit { background-color: rgb(255, 242, 204); }")        

        self.minimum_1to1_size_difference = QtWidgets.QLineEdit(self.tab_zfilter)
        self.minimum_1to1_size_difference.setGeometry(QtCore.QRect(402, 300, 140, 30))
        self.minimum_1to1_size_difference.setFont(font)
        self.minimum_1to1_size_difference.setPlaceholderText("VI   by default 0.6") 
        self.minimum_1to1_size_difference.setFrame(True)
        self.minimum_1to1_size_difference.setReadOnly(False)
        self.minimum_1to1_size_difference.setObjectName("minimum_1to1_size_difference")
        self.minimum_1to1_size_difference.setStyleSheet(
        "QLineEdit { background-color: rgb(255, 242, 204); }")        

        self.minimize_factor = QtWidgets.QLineEdit(self.tab_zfilter)
        self.minimize_factor.setGeometry(QtCore.QRect(402, 350, 140, 30))
        self.minimize_factor.setFont(font)
        self.minimize_factor.setPlaceholderText("VII  by default 0.5") 
        self.minimize_factor.setFrame(True)
        self.minimize_factor.setReadOnly(False)
        self.minimize_factor.setObjectName("self.minimize_factor")
        self.minimize_factor.setStyleSheet(
        "QLineEdit { background-color: rgb(255, 242, 204); }")       

        self.marginal_iou = QtWidgets.QLineEdit(self.tab_zfilter)
        self.marginal_iou.setGeometry(QtCore.QRect(402, 400, 140, 30))
        self.marginal_iou.setFont(font)
        self.marginal_iou.setPlaceholderText("VIII by default 0.5") 
        self.marginal_iou.setFrame(True)
        self.marginal_iou.setReadOnly(False)
        self.marginal_iou.setObjectName("self.marginal_iou")
        self.marginal_iou.setStyleSheet(
        "QLineEdit { background-color: rgb(255, 242, 204); }")


        self.minimum_intersection_to_consider_engulfed = QtWidgets.QLineEdit(self.tab_zfilter)
        self.minimum_intersection_to_consider_engulfed.setGeometry(QtCore.QRect(722, 200, 140, 30))
        self.minimum_intersection_to_consider_engulfed.setFont(font)
        self.minimum_intersection_to_consider_engulfed.setPlaceholderText("IX  by default 0.25") 
        self.minimum_intersection_to_consider_engulfed.setFrame(True)
        self.minimum_intersection_to_consider_engulfed.setReadOnly(False)
        self.minimum_intersection_to_consider_engulfed.setObjectName("self.minimum_intersection_to_consider_engulfed")
        self.minimum_intersection_to_consider_engulfed.setStyleSheet(
        "QLineEdit { background-color: rgb(251, 229, 214); }")

        self.overall_intersecting_ratio = QtWidgets.QLineEdit(self.tab_zfilter)
        self.overall_intersecting_ratio.setGeometry(QtCore.QRect(722, 250, 140, 30))
        self.overall_intersecting_ratio.setFont(font)
        self.overall_intersecting_ratio.setPlaceholderText("X    by default 0.75") 
        self.overall_intersecting_ratio.setFrame(True)
        self.overall_intersecting_ratio.setReadOnly(False)
        self.overall_intersecting_ratio.setObjectName("self.overall_intersecting_ratio")
        self.overall_intersecting_ratio.setStyleSheet(
        "QLineEdit { background-color: rgb(251, 229, 214); }")


        self.proximity_threshold = QtWidgets.QLineEdit(self.tab_zfilter)
        self.proximity_threshold.setGeometry(QtCore.QRect(722, 300, 140, 30))
        self.proximity_threshold.setFont(font)
        self.proximity_threshold.setPlaceholderText("XI   by default 1") 
        self.proximity_threshold.setFrame(True)
        self.proximity_threshold.setReadOnly(False)
        self.proximity_threshold.setObjectName("self.proximity_threshold")
        self.proximity_threshold.setStyleSheet(
        "QLineEdit { background-color: rgb(251, 229, 214); }")

        self.iou_threshold = QtWidgets.QLineEdit(self.tab_zfilter)
        self.iou_threshold.setGeometry(QtCore.QRect(722, 350, 140, 30))
        self.iou_threshold.setFont(font)
        self.iou_threshold.setPlaceholderText("XII  by default 0.5") 
        self.iou_threshold.setFrame(True)
        self.iou_threshold.setReadOnly(False)
        self.iou_threshold.setObjectName("self.iou_threshold")
        self.iou_threshold.setStyleSheet(
        "QLineEdit { background-color: rgb(251, 229, 214); }")

        self.minimize_factor2 = QtWidgets.QLineEdit(self.tab_zfilter)
        self.minimize_factor2.setGeometry(QtCore.QRect(722, 400, 140, 30))
        self.minimize_factor2.setFont(font)
        self.minimize_factor2.setPlaceholderText("XIII by default 0.5") 
        self.minimize_factor2.setFrame(True)
        self.minimize_factor2.setReadOnly(False)
        self.minimize_factor2.setObjectName("self.minimize_factor2")
        self.minimize_factor2.setStyleSheet(
        "QLineEdit { background-color: rgb(251, 229, 214); }")

                ### icons ###

        info_icon_zfilter = QtWidgets.QLabel(self.tab_zfilter)
        info_icon_zfilter.setGeometry(QtCore.QRect(685, 55, 27, 27))  # Position next to the entry
        info_icon_zfilter.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_zfilter.setPixmap(pixmap)
        info_icon_zfilter_message= ("Read the decisiontree.pptx file before making any changes")
        info_icon_zfilter.setToolTip(info_icon_zfilter_message)

                ### buttons ###

        self.Button_zplanefilter = QtWidgets.QPushButton(self.tab_zfilter)
        self.Button_zplanefilter.setGeometry(QtCore.QRect(820, 505, 150, 31))
        self.Button_zplanefilter.setFont(font)
        self.Button_zplanefilter.setObjectName("Button_zplanefilter")
        self.Button_zplanefilter.clicked.connect(self.InitiateZfilter)


        ###### TAB CHANGE ROIS ######


        self.tab_changerois = QtWidgets.QWidget()
        self.tab_changerois.setObjectName("tab_changerois")
        self.tabWidget.addTab(self.tab_changerois, "")

                    ### labels ###
        self.label_testmsg = QtWidgets.QLabel(self.tab_changerois)
        self.label_testmsg.setGeometry(QtCore.QRect(230, 30, 550, 30))
        custom_msg_font = QtGui.QFont()
        custom_msg_font.setPointSize(13)
        self.label_testmsg.setFont(custom_msg_font)
        self.label_testmsg.setObjectName("label_testmsg")

        self.label_asktestinput = QtWidgets.QLabel(self.tab_changerois)
        self.label_asktestinput.setGeometry(QtCore.QRect(290, 90, 160, 31))
        self.label_asktestinput.setFont(font)
        self.label_asktestinput.setObjectName("label_asktestinput")

        self.label_reduce_example = QtWidgets.QLabel(self.tab_changerois)
        self.label_reduce_example.setGeometry(QtCore.QRect(293, 150, 100, 31))
        self.label_reduce_example.setFont(font)
        self.label_reduce_example.setObjectName("reduce_example")

        self.label_maskimg = QtWidgets.QLabel(self.tab_changerois)
        self.label_maskimg.setGeometry(QtCore.QRect(310, 410, 330, 90))
        self.label_maskimg.setFont(font)
        self.label_maskimg.setText("")
        self.label_maskimg.setPixmap(QPixmap(f"{current_dir}/cellpose_convertion.png"))
        self.label_maskimg.setScaledContents(True)
        self.label_maskimg.setObjectName("maskimg")

                    ### entries ### 
        self.entry_reduceroi = QtWidgets.QLineEdit(self.tab_changerois)
        self.entry_reduceroi.setGeometry(QtCore.QRect(430, 90, 61, 30))
        self.entry_reduceroi.setFont(font)
        self.entry_reduceroi.setText("")
        self.entry_reduceroi.setFrame(True)
        self.entry_reduceroi.setReadOnly(False)
        self.entry_reduceroi.setObjectName("entry_reduceroi")


        self.entry_listreduc = QtWidgets.QLineEdit(self.tab_changerois)
        self.entry_listreduc.setGeometry(QtCore.QRect(430, 150, 61, 30))
        self.entry_listreduc.setFont(font)
        self.entry_listreduc.setPlaceholderText("10,30,50")  
        self.entry_listreduc.setFrame(True)
        self.entry_listreduc.setReadOnly(False)
        self.entry_listreduc.setObjectName("entry_listreduc")


                    ### buttons ###
        self.Button_tryfiji = QtWidgets.QPushButton(self.tab_changerois)
        self.Button_tryfiji.setGeometry(QtCore.QRect(530, 90, 160, 32))
        self.Button_tryfiji.setFont(font)
        self.Button_tryfiji.setObjectName("Button_tryfiji")
        self.Button_tryfiji.clicked.connect(self.InitializeVisualCheck)

        self.Button_applyfiji = QtWidgets.QPushButton(self.tab_changerois)
        self.Button_applyfiji.setGeometry(QtCore.QRect(530, 150, 184, 31))
        self.Button_applyfiji.setFont(font)
        self.Button_applyfiji.setObjectName("Button_applyfiji")
        self.Button_applyfiji.clicked.connect(self.InitializeReduceRois)

        self.Button_convert = QtWidgets.QPushButton(self.tab_changerois)
        self.Button_convert.setGeometry(QtCore.QRect(310, 505, 330, 31))
        self.Button_convert.setFont(font)
        self.Button_convert.setObjectName("Button_convert")
        self.Button_convert.clicked.connect(self.InitializeLabeltoROI)
                    
                    ### icons ###
        info_icon_reduce = QtWidgets.QLabel(self.tab_changerois)
        info_icon_reduce.setGeometry(QtCore.QRect(685, 142, 27, 27))  # Position next to the entry
        info_icon_reduce.setCursor(Qt.PointingHandCursor)
        pixmap = QPixmap("info.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        info_icon_reduce.setPixmap(pixmap)
        info_icon_reduce_message= ("The values represent reduction and not desired final size")
        info_icon_reduce.setToolTip(info_icon_reduce_message)



#  -   -   -      R E T R A N S L A T E      -   -   -  
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


####################### Retranslate objects START #######################


    def retranslateUi(self, MainWindow):
            _translate = QtCore.QCoreApplication.translate
            MainWindow.setWindowTitle(_translate("MainWindow", "AResCoN  (A Researcher is Counting Neurons)"))

            ###### TAB MICROSCOPY ######
            self.scroll_zplanes.setItemText(0, _translate("MainWindow", "1"))
            self.scroll_zplanes.setItemText(1, _translate("MainWindow", "2"))
            self.scroll_zplanes.setItemText(2, _translate("MainWindow", "3"))
            self.scroll_zplanes.setItemText(3, _translate("MainWindow", "4"))
            self.scroll_zplanes.setItemText(4, _translate("MainWindow", "5"))
            self.scroll_zplanes.setItemText(5, _translate("MainWindow", "6"))
            self.scroll_zplanes.setItemText(6, _translate("MainWindow", "7"))
            self.scroll_zplanes.setItemText(7, _translate("MainWindow", "8")) 
            self.scroll_zplanes.setItemText(8, _translate("MainWindow", "9"))   
            self.scroll_zplanes.setItemText(9, _translate("MainWindow", "10"))  
            self.scroll_zplanes.setItemText(10, _translate("MainWindow", "11"))  
            self.scroll_zplanes.setItemText(11, _translate("MainWindow", "12"))                       
                     
                     
            self.label_zplanesNumber.setText(_translate("MainWindow", "Number of z planes"))
            self.label_planeDistance.setText(_translate("MainWindow", "Max plane gap"))
            self.label_bits.setText(_translate("MainWindow", "Bit depth"))
            self.label_system.setText(_translate("MainWindow", "System"))
            self.scroll_bits.setItemText(0, _translate("MainWindow", "16bit"))
            self.scroll_bits.setItemText(1, _translate("MainWindow", "8bit"))
            self.scroll_system.setItemText(0, _translate("MainWindow", "Windows"))
            self.scroll_system.setItemText(1, _translate("MainWindow", "Linux"))

            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_microscopy), _translate("MainWindow", "Microscopy"))
            
            ###### TAB MAIN INPUTS ######
            self.Button_ImagesFolder.setText(_translate("MainWindow", "Images Folder"))
            self.Button_RoisFolder.setText(_translate("MainWindow", "Rois Folder"))
            self.label_selectImageFolder.setText(_translate("MainWindow", "Select folder with images (example below)"))
            self.label_SelectRoiFolder.setText(_translate("MainWindow", "Select folder with ROIs (example below)"))
            self.checkBoxCompletedTab2.setText(_translate("MainWindow", " Files uploaded"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_mainputs), _translate("MainWindow", "Main Inputs"))
            ###### TAB MEASURE ROIS ######
            self.label_saveResults.setText(_translate("MainWindow", "Select folder to save your main roi measurements"))
            self.label_Fijipath.setText(_translate("MainWindow", "Select the path of your executable Imagej or Fiji"))
            self.label_warnings.setText(_translate("MainWindow", "           Before Generate Measurements, make sure that :\n\n" 
                                                "1) The names of the subdirectories for images and rois start with\n"
                                                "planeN where n corresponds to a number (as shown in the examples) \n\n"
                                                "2) There is no open instance of ImageJ/Fiji \n\n" 
                                                "3) ImageJ/Fiji will not ask for an update \n\n" 
                                                "4) You double-click on the imagej/fiji.exe file while selecting it\n\n"
                                                "Do not use your mouse or keyboard until all measurements are obtained!\n"))
            self.label_warnings.adjustSize()
            self.Button_MeasuresaveFolder.setText(_translate("MainWindow", "Save Folder"))
            self.Button_Fijipath.setText(_translate("MainWindow", "Find fiji.exe"))
            self.Button_GetMeasurements.setText(_translate("MainWindow", "  Generate Measurements"))
            self.checkBoxCompletedTab3.setText(_translate("MainWindow", " Files uploaded"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_measurois), _translate("MainWindow", "Measure Rois"))
            ###### TAB ADD METRICS ######
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addmetrics), _translate("MainWindow", "Add Metrics"))
            self.Button_Addmetrics.setText(_translate("MainWindow", "Add measurements"))
            self.Button_Savemetrics.setText(_translate("MainWindow", "Save measurements"))
            self.Button_Loadmetrics.setText(_translate("MainWindow", "Load measurements"))
            self.Button_FindEdges.setText(_translate("MainWindow", "Find edges StdDev"))
            self.Button_SaveEdges.setText(_translate("MainWindow", "Add edges StdDev"))
            self.Button_getentropy.setText(_translate("MainWindow", "Get Entropy"))
            self.Button_addentropy.setText(_translate("MainWindow", "Add Entropy"))
            self.label_mainmeasr.setText(_translate("MainWindow", "Add your main measurements to AResCon"))
            self.label_metrics.setText(_translate("MainWindow", "Add new metric columns to csv (Optional)"))
            ###### TAB FILTERING ###### Dont mistake with zfiltering
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_filtering), _translate("MainWindow", "2D Filters"))
            self.label_surr_fltr.setText(_translate("MainWindow", "Calculate ROI-Background difference"))
            self.label_large_factor.setText(_translate("MainWindow", "ROI enlargment factor"))
            self.label_ahk.setText(_translate("MainWindow", "Locate AutoHotkey script for Enter press"))
            self.label_exeahk.setText(_translate("MainWindow", "Locate AutoHotkeyUX.exe"))
            self.label_measure_filter.setText(_translate("MainWindow", "Make your own ROI filters"))
            self.Button_ahk.setText(_translate("MainWindow", "Locate .ahk"))
            self.Button_exeahk.setText(_translate("MainWindow", "Locate .exe"))
            self.Button_meanfilter.setText(_translate("MainWindow", "Get Roi-Background mean gray differences"))
            self.Button_opensave.setText(_translate("MainWindow", "Open metrics"))
            self.Button_1planefilter.setText(_translate("MainWindow", "Apply filters"))
            ###### TAB ZFILTERING ###### dont mistake with filtering
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_zfilter), _translate("MainWindow", "Z Filter"))
            self.label_tot_scor_filter.setText(_translate("MainWindow", "Filter z overlaps based on FindEdges"))
            self.label_engulfers_section.setText(_translate("MainWindow", "Engulfers"))
            self.label_1to1_section.setText(_translate("MainWindow", "1 to 1 overlaps"))
            self.label_1tomore_section.setText(_translate("MainWindow", "1 to many overlaps"))
            self.Button_zplanefilter.setText(_translate("MainWindow", "Apply filters"))



            ###### TAB CHANGE ROIS ######
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_changerois), _translate("MainWindow", "Change ROIs"))
            self.label_testmsg.setText(_translate("MainWindow", "Test a size reduction visually or produce shrinked rois"))
            self.label_asktestinput.setText(_translate("MainWindow", f"Percentage shrink"))
            self.label_reduce_example.setText(_translate("MainWindow", f"Preferred %s"))
            self.Button_convert.setText(_translate("MainWindow", "Convert labels to ROIs"))
            self.Button_tryfiji.setText(_translate("MainWindow", "Try in ImageJ"))
            self.Button_applyfiji.setText(_translate("MainWindow", "Get shrinked ROIs"))          


    ####################### Retranslate objects END #######################


    def FileDialog(self,message= "Select directory",what_to_select="directory"):
        """Adds a key with the folder (or file) selected by the user (default should change) and its path as value to user_selections """
        
        if what_to_select != "FijiexePath":                                                                                      #this is for selecting folders
            selection = QFileDialog.getExistingDirectory(None, message)
            self.user_selections[what_to_select] = selection
            if what_to_select != "Measurements_Folder" :                                                                         # measurements folder is the main save folder and the option button belongs to another tab.
                try :                                                                                                            # ticks the step completed box if both options are set
                    self.user_selections["Images_Folder"]
                    self.user_selections["Rois_Folder"]
                except : pass
                else : self.checkBoxCompletedTab2.setChecked(True)
            if what_to_select == "Measurements_Folder" :                                                                         # The tab that measurements folder belongs has two options, the main measurements folder and the fiji.exe option
                try : self.user_selections["FijiexePath"]                                                                        # checks if fijipath is selected already
                except : pass
                else : self.checkBoxCompletedTab3.setChecked(True)
        elif what_to_select == 'FijiexePath' :
            selection = QFileDialog.getOpenFileName(None, message, current_dir, "Executable Files (*.exe);;All Files (*)")[0]    #this is for selecting files
            self.user_selections[what_to_select] = selection
            try : self.user_selections["Measurements_Folder"]                                                                     # check the folders uploaded box if the main measurement folder has also been selected
            except : pass
            else : self.checkBoxCompletedTab3.setChecked(True)
        
        elif what_to_select == 'Entropy_Folder':
            selection = QFileDialog.getExistingDirectory(None, message)
            self.user_selections[what_to_select] = selection
        
        elif what_to_select == 'Labels' :                                                                                         # this is for the convertion of labels to masks 
            selection = QFileDialog.getExistingDirectory(None, message)
            self.user_selections[what_to_select] = selection

        elif what_to_select == 'EmptyMaskDirectory':
            selection = QFileDialog.getExistingDirectory(None, message)
            self.user_selections[what_to_select] = selection

    def MeanMeasurementsDialog (self,message= "Select file",what_to_select="file"):
        """Adds a key with the file selected by the user (default should change) and its path as value to meanmeasurements_selections 
           Extra description below :
           In this version, the files are the executable file of autohotkey (version is important) and an ahk script that simulates 
           an enter press after a delay of 5 seconds. The reaon AutoHotKey was used to be executed asynchronously before the emergence of
           a contingent error (instead of a complementery python file being executed to simulate enter press) was that the python file was using pyautogui and it was causing errors
           to the pygetwindow, probably because there was already the pyautogui running. Eventually, AutoHotKey started to yield errors too to pygetwindow in the 
           EnsureFijiisActive() inside RunMeanMeasurements module. I inserted a workaround with window minimize,maximize and restore.
           Bottom line is that there can be another version that runs a py file with pyautogui instead of AutoHotKey. """

        if what_to_select == 'ahk_script':
            selection = QFileDialog.getOpenFileName(None, message, current_dir, "All Files (*)")[0]
            self.meanmeasurements_selections[what_to_select] = selection

        if what_to_select == 'ahk_exec':
            selection = QFileDialog.getOpenFileName(None, message, current_dir, "Executable Files (*.exe);;All Files (*)")[0]
            self.meanmeasurements_selections[what_to_select] = selection

    def LocateAcceptedROIspklDialog (self,message= "Locate the Accepted_ROIs.pkl file that contains the x and y axis filtered ROIs"):
        """ Opens a dialog to locate the Accepted_ROIs.pkl file, that is needed to proceed to z filtering. Note that if the user has not 
            run any filtering on X Y, the Z filtering is not possible. """

        usr_selectionpkl = QFileDialog.getOpenFileName(None, message, current_dir, "All Files (*)")[0]    #this is for selecting files
        acceptedROIspath = Path(usr_selectionpkl)
        if acceptedROIspath.suffix not in ['.pickle','.pkl'] :
            Checks.ShowError('Wrong file selection',f'Only .pickle and .pkl files are allowed. The file that you selected has {acceptedROIspath.suffix} extension.')
            return None
        else :
            return acceptedROIspath

    def ExampleImageAndRoiDialog(self, *args):
        message = args[0]
        usr_selection = QFileDialog.getOpenFileName(None, message, current_dir, "All Files (*)")[0]    #this is for selecting files
        return usr_selection


    def Helper_Checks(self):
        """Checks if some user variables have been selected already, before the Ηelper() starts to assign values"""
        if Checks.NotSelectedImagesFolder(self.user_selections) == 'image_folder_not_defined'    : return 'error'        # checks if the user has selected a main directory for image planeN subdirectorie
        if Checks.NotSelectedRoiFolder   (self.user_selections) == 'roi_save_folder_not_defined' : return 'error'        # checks if the main roi folder where the roi subdirs are saved has been selected already #####
        if Checks.NotSelectedFijiFile    (self.user_selections) == 'image.exe_not_defined'       : return 'error'        # checks if the fiji or imageJ.exe file has been selected
        if Checks.NotSelectedSaveFolder  (self.user_selections) == 'save_folder_not_defined'     : return 'error'    # checks if the save folder where the measurements subdirs are saved has been selected already #####


    def Helper (self):
        """defines some variables that are useful for use in more than one functions"""
        
        helper_variables = []
        n_of_planes_h                                   = int(self.scroll_zplanes.currentText())                                    
        foldpath_img_h                                  = self.user_selections["Images_Folder"]
        roiresults_h                                    = self.user_selections["Rois_Folder"]
        fiji_path_h                                     = self.user_selections["FijiexePath"]
        savemeasure_path_h                              = self.user_selections["Measurements_Folder"]

        list_with_all_subdir_folder_images_h            = sorted ([foldpath_img_h+'/'+file for file in os.listdir(foldpath_img_h) if isdir(join(foldpath_img_h, file))])
        list_with_all_subdir_folder__with_zipped_rois_h = sorted ([roiresults_h+'/'+file for file in os.listdir(roiresults_h) if isdir(join(roiresults_h, file))])
        planeNstringPattern_h                           = r'plane\d+'                                                                                                                                                                                    # this code works only with planeN in front of folder names for images and rois
        coupled_foldimages_with_foldroi_paths_h         = zip(list_with_all_subdir_folder_images_h,list_with_all_subdir_folder__with_zipped_rois_h)
        helper_variables.extend ([n_of_planes_h,foldpath_img_h,roiresults_h,savemeasure_path_h,fiji_path_h,list_with_all_subdir_folder_images_h,list_with_all_subdir_folder__with_zipped_rois_h,planeNstringPattern_h,coupled_foldimages_with_foldroi_paths_h])

        return helper_variables

    def InitializeGetMeasurementsOfRois (self) : 
        """Passes the arguments as kwargs to the module of RunFijiMeasurements.py and initiates the automatic start of fiji for getting measurements of rois
           Also creates separate save subdirectories in the main save folder that the user has selected. Each subdirectory will start with planeN and
           contain measurements from that plane only."""
        
        if self.Helper_Checks() == 'error' : return                                                                         # checks if all user_selections have been made
        if Checks.is_fiji_still_open('imageJ-win64.exe') == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return

        # definition is order sensitive, be careful when adding-removing variables from here
        (n_of_planes,foldpath_img,roiresults,savemeasure_path,fiji_path,
         list_with_all_subdir_folder_images,list_with_all_subdir_folder__with_zipped_rois,
         planeNstringPattern,coupled_foldimages_with_foldroi_paths) = self.Helper ()                                        # calling helper to define variables
        
        if Checks.VerifyEmptySaveFolder(savemeasure_path) == 'NotEmpty':  return                                            # Checks if save directory is empty 
        else :                                                                                                              # if so, it creates new subdirs based on planes ######
            all_save_paths = PathMaker.CreateMeasurementSubdirs(n_of_planes,savemeasure_path)
        if Checks.VerifySameplaneNstart(coupled_foldimages_with_foldroi_paths,planeNstringPattern) == 'Unmatched': return   #checks if the subdirectories of images and rois have the same planeN start and the same order #####
        else :
            print('passed verifysameplanstart')

        ##### Passes a particular subdir for images, rois, and save to the module #####
        for plane_index in range(len(list_with_all_subdir_folder_images)):
            oneplane_image = list_with_all_subdir_folder_images [plane_index]
            oneplane_roi   = list_with_all_subdir_folder__with_zipped_rois [plane_index]
            one_save       = all_save_paths[plane_index]                                             
            system         = self.scroll_system.currentText()   
            RunFijiMeasurements.GetMeasurementsOfRois(Rroiresults=oneplane_roi,Ffoldpath_img=oneplane_image, measure_sub_path=one_save, Ffiji_path=fiji_path, winlin = system)
        
        while Checks.is_fiji_still_open('imageJ-win64.exe') == True : time.sleep(3)                                                     # same as is_fiji_running in Run fiji templates. Wont display the message until processes are done
        message = (f"New csv files for each planeN image have been created in {savemeasure_path} . "
                   "Every additional measurement that you are going to take from now on (i.e. Entropy or MeanBackground) "
                   "will be added as a column to the respective csv file of the corresponding planeN image")
        Checks.ShowInfoMessage('Measurements obtained',message)


    def InitializeAddMetrics (self) :
        """Creates the main dictionary where all roi_instances are saved. Each key is an int corresponding to a plane 
           and each value is another dict with the roi name as key (e.g. 001_005-N, where -N corresponds to plane number)
           and the whole instance with all attributes (i.e name, Area, Mean etc ) as value.
           """
        
        planes_n      = int(self.scroll_zplanes.currentText()) 
        planeNpattern = r'plane\d+'                                                                                                                                                                                   # this code works only with planeN in front of folder names for images and rois

        if Checks.OnlyOnePlaneSelected(planes_n)              == 'One_plane_only_by_accident'  : return         # checks if the user has changed the number of planes and if (s)he wants to #
        if Checks.NotSelectedSaveFolder(self.user_selections) == 'save_folder_not_defined'     : return         # checks if the save folder where the measurements subdirs are saved has been selected already #####
        if Checks.NotSelectedRoiFolder(self.user_selections)  == 'roi_save_folder_not_defined' : return         # checks if the main roi folder where the roi subdirs are saved has been selected already #####
        if 'main_dictionary' in globals() : del globals()['main_dictionary']                                    # This is important. Every time we call this function, the main dictionary resets, to accommodate old and new metrics. Performing complete delete to prevent keeping class
                                                                                   
        global main_dictionary
        
        main_dictionary={}                                                                                                        
        mainroi_path         =  self.user_selections["Rois_Folder"] 
        mainmeasr_path       =  self.user_selections["Measurements_Folder"]
        list_with_all_subdir_with_zipped_rois = sorted ([mainroi_path+'/'+file for file in os.listdir(mainroi_path) if isdir(join(mainroi_path, file))])
        list_with_all_subdir_with_measurements= sorted ([mainmeasr_path+'/'+file for file in os.listdir(mainmeasr_path) if isdir(join(mainmeasr_path, file))])
        coupled_foldmeasures_with_foldroi_paths = list(zip(list_with_all_subdir_with_measurements,list_with_all_subdir_with_zipped_rois))


        for c_index in range(len(list_with_all_subdir_with_zipped_rois)) :                                                        # select any of the two lists to get the length               
            couple = coupled_foldmeasures_with_foldroi_paths[c_index]                                                             #iterate across tuples, starting from 0, whereas plane numbers start from 1
            if re.findall(planeNpattern, couple[0]) == re.findall(planeNpattern, couple[1]) :
                main_dictionary[c_index+1] = AddMetrics.LoadRoiMeasurements(run=True,SaveMetricPath=couple[0],PlaneWithRois=couple[1],plane=c_index+1 )
            else :
                Checks.ShowError('Folders not matching','Could not identify a couple of planeN subdirectories between main save folder and main rois folder.')      # looks for a planeN match in the names 
                main_dictionary.clear()
                return
        Checks.ShowInfoMessage('Step completed','All measurements are now added to AResCoN. Consider saving your new measurements to disk now.')
        # Example of accessing a measurement from main directory : main_dictionary[2][0]['plane2Copy.tif']['001_999-2'].Area , where 2 is the planeN, 0 always standard and then imagename and roi-name

    
    def InitializeVisualCheck (self):
        """ User can test visually a % reduction of rois of an image in the main image path and create subdirectories with reduced 
           rois based on the percentage reduction (s)he wants."""
        
        if Checks.is_fiji_still_open('imageJ-win64.exe') == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return        
        if Checks.NotSelectedFijiFile (self.user_selections) == 'image.exe_not_defined'  : return 'error'                    # checks if the fiji or imageJ.exe file has been selected
        percent     = Checks.NotSelectedExamplePercentage(self.entry_reduceroi.text())
        if percent  == 'percentage_not_defined'                                          : return
        prepare_msg = "You will now be prompted to select an image file first and then its respective zip file with rois"
        Checks.ShowInfoMessage (message='Image and rois', boxtitle=prepare_msg)
        example_img = self.ExampleImageAndRoiDialog("      ------------------------> Please select your image first <------------------------")
        Checks.ShowInfoMessage (message=' Selectrois', boxtitle="Now select the matching zip file with the rois if this image")
        example_ziproi = self.ExampleImageAndRoiDialog("      ------------------------> Now select the matching zip file with rois <------------------------>")
        fiji_path_v = self.user_selections["FijiexePath"]
        system_v = self.scroll_system.currentText()

        RunVisualTest.VisualizeReducedRois(impath=example_img,roipath=example_ziproi,prcntg=percent,FFiji_path=fiji_path_v,winlin=system_v)

    def InitializeReduceRois(self):
        """Creates a zip file with rois reduced in size for every N%_reduction folder that will be created following user input"""
        
        if Checks.is_fiji_still_open('imageJ-win64.exe') == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return               
        ## rr stands for reduced rois
        inted_percentages  = Checks.NotSelectedReducePercentages (self.entry_listreduc.text())                                    # if no error in user input, inted_percentages will be a list with integers corresponding to desired reductions in roi size
        if inted_percentages == 'wrong_user_input' : return
        if self.Helper_Checks() == 'error' : return                                                                               # checks if all user_selections have been made

        # definition is order sensitive, be careful when adding-removing variables from here
        (n_of_planes_rr,foldpath_img_rr,roiresults_rr,savemeasure_path_rr,fiji_path_rr,
         list_with_all_subdir_folder_images_rr,list_with_all_subdir_folder_with_zipped_rois_rr,
         planeNstringPattern_rr,coupled_foldimages_with_foldroi_paths_rr) = self.Helper ()                                        # calling helper to define variables
        
        parent_of_main_roi_measurements = os.path.dirname (savemeasure_path_rr)                                                   # gets the parent directory of the main roi measurements directory
        main_RR_path = PathMaker.CreateReducedRoisMainDir(parent_of_main_roi_measurements)                                        # creates a new ReducedRois main directory -if not exists already- for all the contingent percentages subdirs

        new_rr_subdir_paths = [normpath(join(main_RR_path,str(perc))) for perc in inted_percentages]                              # ensures the number is in str format and adds %_reduction to fit the folder names                            # create the name of each new path to be created. Transforms percentages back to strings too. They were ints before to ensure that the input was an int number
        if Checks.ReduceRoiPercentagesExist(new_rr_subdir_paths) == 'name_conflict_detected' : return
        else : all_percentage_paths = PathMaker.CreateReducedRoisSubirs(new_rr_subdir_paths)

        if Checks.OnlyOnePlaneSelected  (n_of_planes_rr) == 'One_plane_only_by_accident'     : return                             # checks if the user has changed the number of planes and if (s)he wants to #
        if Checks.VerifySameplaneNstart(coupled_foldimages_with_foldroi_paths_rr,planeNstringPattern_rr) == 'Unmatched': return   #checks if the subdirectories of images and rois have the same planeN start and the same order. This is related to the original rois, not the reduced
        percentage_and_plane = PathMaker.CreateReducedRoiPlaneSubdirs(n_of_planes_rr,main_RR_path)                                # to create similar planeN structures (per each percentage folder) as the main roi folder# variable is dictionary with percentage folder path as key and sorted list with strings indicating each new created planeN folder path as value                         
        
        ##### Passes a particular subdir for images, rois, and save to the module #####
        ##### this code has one more for loop compared to the rest of initialization methods #####
        for one_percentage_path in new_rr_subdir_paths:
            percent = os.path.basename(one_percentage_path).strip('%_reduction')
            one_percentage_path += '%_reduction'
            for plane_index_rr in range(len(list_with_all_subdir_folder_images_rr)):
                oneplane_image_rr = list_with_all_subdir_folder_images_rr [plane_index_rr]
                oneplane_roi_rr   = list_with_all_subdir_folder_with_zipped_rois_rr [plane_index_rr]
                one_save_rr       = percentage_and_plane[one_percentage_path][plane_index_rr]                                           
                system_rr         = self.scroll_system.currentText()   
                RunReducedRois.RealReduceRois(_roipath=oneplane_roi_rr, _foldpath_image=oneplane_image_rr, rr_sub_path=one_save_rr, _fiji_path=fiji_path_rr, winlin = system_rr,prcntg=percent)
    
    def InitializeLabeltoROI(self):
        
        if Checks.is_fiji_still_open('imageJ-win64.exe')     == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return         

        message = ('You will be now prompted to select the main ROI directory containing all "planeN_Rois" folders for convertion. '
                   'The structure has to be same as the one indicated in Main Inputs tab for ROIs')
        if Checks.NotSelectedFijiFile    (self.user_selections) == 'image.exe_not_defined'       : return                         # checks if the fiji or imageJ.exe file has been selected
        else : fijipath = self.user_selections['FijiexePath']

        Checks.ShowInfoMessage('Selection of main ROI directory', message)

        self.FileDialog("Select main label directory","Labels")
        main_label_for_cnvrt = self.user_selections['Labels']
        system_i = self.scroll_system.currentText()

        planeN_roipaths = [ planeN for planeN in Path(main_label_for_cnvrt).glob('**')]
        planeN_roipaths = sorted(planeN_roipaths[1:])
        newroispath = join(main_label_for_cnvrt,'RoisFromLabels')
        if os.path.exists (newroispath) :
            message = f'There is already a folder created in {newroispath}. Try moving it first.'
            Checks.ShowError('Folder not empty',message)
        else : 
            os.mkdir (newroispath)
            PathMaker.CreatePlaneNSubirdsForLabels (planeN_roipaths)

        for planeN_subdir in planeN_roipaths :
            if planeN_subdir == 'RoisFromLabels':
                continue
            planeN_subdir= normpath(str(planeN_subdir))
            foldername = os.path.basename(planeN_subdir)
            matching_save_folder = normpath(join(newroispath,foldername))
            ConvertLabelstoRois.TransformLabels(planeN_masks=planeN_subdir,savepath=matching_save_folder,fiji_path=fijipath,winlin=system_i)


    def InitializeMeanBackground (self):
        """Calls functions to create a MeanBackgroundResults directory inside the parent directory of the main save roi measurements.
           planeN subdirectories also also created inside the MeanBackgroundResults directore. Also calls functions to initiate fiji
           and get surrounding background of a roi by using an elragment factor of each roi. After doing that, it calls functions to
           submit each surrounding background of a roi to the respective csv file in the main roi measurements as a new column.
           Eventually, it creates one more column which is the difference between mean gray of roi and mean gray of surr. background"""

        if Checks.is_fiji_still_open('imageJ-win64.exe')     == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return        

        if self.Helper_Checks() == 'error' : return

        # definition is order sensitive, be careful when adding-removing variables from here
        (n_of_planes_mg,foldpath_img_mg,roiresults_mg,savemeasure_path_mg,fiji_path_mg,
        list_with_all_subdir_folder_images_mg,list_with_all_subdir_folder_with_zipped_rois_mg,
        planeNstringPattern_mg,coupled_foldimages_with_foldroi_paths_mg)  = self.Helper()

        if Checks.AutoHotKeyInputsMeanMeasurementsExist(self.meanmeasurements_selections) == "incomplete_inputs"             : return   # if the inputs for autohotkey are not passed correctly. Be careful : by correct, we just mean that there are two keys in the dict. One for ahk and for exec. If more vars are implemented in future, this has to change

        ahk_script  = self.meanmeasurements_selections["ahk_script"]
        ahk_exec    = self.meanmeasurements_selections["ahk_exec"]

        parent_dir_mg = os.path.dirname(savemeasure_path_mg)                                                                            # finds the penultimate (parent) directory of the path
        backgr_save_path = join (parent_dir_mg+'/MeanBackgroundResults')      


        if Checks.OnlyOnePlaneSelected  (n_of_planes_mg) == 'One_plane_only_by_accident'                                     : return   # checks if the user has changed the number of planes and if (s)he wants to #
        if Checks.VerifySameplaneNstart(coupled_foldimages_with_foldroi_paths_mg,planeNstringPattern_mg) == 'Unmatched'      : return   # checks if the subdirectories of images and rois have the same planeN start and the same order
        lrg_fctr = self.entry_enlarge_roi.text()
        if Checks.MeanBackgroundInputsExist (lrg_fctr) == 'Not_exists_or_wrong'                                              : return   # checks if the inputs (enlargement factor) are correct
        if Checks.MeanBackgroundFolderExists (parent_dir_mg)     == "Exists_Already"                                         : return   # No MeanBackgroundResults directory should exist at this stage.
        else :        
            os.mkdir(backgr_save_path)
            self.user_selections['MeanBackground_Folder'] = backgr_save_path                                                            # after the directory is created, save it to user_selections too
            all_save_paths_mg = PathMaker.CreateMeanBackgroundSubdirs(n_of_planes_mg,backgr_save_path)                                  # if so, it creates new subdirs based on planes #

        # vis_decis = Checks.UserWantsToVisualizeEnlargedRois()                                                                         # True if the user wants to visualize enlarged ROIs, False if not. I have not managed to run this macro in Fiji without visualizing yet. So it will be set to True anyway for now. Thus, batchmode in fiji macro will be False
        vis_decis  = True 
        Checks.PrepareUserforMaskFolderSelection()
        self.FileDialog(message='Select an empty folder to save your masks',what_to_select='EmptyMaskDirectory')
        try:
            maskpath   = self.user_selections['EmptyMaskDirectory']
        except :
            Checks.ShowError("Wrong Selection",'Something went wrong with your selection since it could not be translated to a path')
            return
        if Checks.VerifyEmptyMaskFolder(maskpath)== 'NotEmpty'                                                               : return   # The mask folder must be empty before initiating Fiji 

         ##### Passes a particular subdir for images, rois, and save to the module #####
        for plane_index_mg in range(len(list_with_all_subdir_folder_images_mg)):
            oneplane_image_mg = list_with_all_subdir_folder_images_mg [plane_index_mg]
            oneplane_roi_mg   = list_with_all_subdir_folder_with_zipped_rois_mg [plane_index_mg]
            one_save_mg       = all_save_paths_mg[plane_index_mg]                                             
            system_mg         = self.scroll_system.currentText()   
            RunMeanMeasurements.GetSurroundingMean(roiresults_mg=oneplane_roi_mg,foldpath_img_mg=oneplane_image_mg, measure_sub_path_mg=one_save_mg,
                                                   enlarge_factor_mg=lrg_fctr,fiji_path=fiji_path_mg, 
                                                   ahk_script=ahk_script, ahk_exec=ahk_exec,
                                                   winlin_mg = system_mg, visuals=vis_decis, maskpath=maskpath)
        
        # this method produces both the execution of Fiji and the addition of mean gray measurement to the main roi measurements
        # thereby, the code templates for initiating fiji measurements (above) and adding to csv (below) are both used in this method

        while Checks.is_fiji_still_open('imageJ-win64.exe') == True : time.sleep(3)                                                     # same as is_fiji_running in Run fiji templates. Wont display the message until processes are done
        message_mg = ('Background measurements for each roi are now saved in each planeN_MeanBackgroundResults '
                     f'subdirectory in {backgr_save_path} . Before adding the background mean gray values to your '
                     'current main roi measurements, it is recommended that you create a backup of both. Will you?')
        if Checks.AskConfirmation('Create Copies',message_mg) == True :
            Checks.CreateCopies (backgr_save_path,savemeasure_path_mg)                                                                  # passes the main MeanBackgroundResults and the main roi meassurements folder because we want zip backups of these two

        mainmeasr_path_mg                      = self.user_selections["Measurements_Folder"]
        list_with_all_subdir_with_meanbgr      = sorted ([backgr_save_path+'/'+file for file in os.listdir(backgr_save_path) if isdir(join(backgr_save_path, file))])
        list_with_all_subdir_with_main_metrics = sorted ([mainmeasr_path_mg+'/'+file for file in os.listdir(mainmeasr_path_mg) if isdir(join(mainmeasr_path_mg, file))])
        coupled_mean_paths_and_metrics         = list(zip(list_with_all_subdir_with_meanbgr,list_with_all_subdir_with_main_metrics))
        planeN_stringPattern_mg                = r'plane\d+'
        
        if Checks.VerifySameplaneNstart(coupled_mean_paths_and_metrics,planeN_stringPattern_mg) == "Unmatched"              : return
        if Checks.VerifySameNamesInsideSubdir(coupled_mean_paths_and_metrics)                   == "names_dont_match"       : return
        if AdditionalMetrics.PassMeasurementsToMainCsv(coupled_mean_paths_and_metrics, metric='Mean',                                   # metric = Mean because the surrounding background metric is registered as mean when we take the fiji measurements
                                                       metric_prefix='Surrounding', extra_calc_col='Mean-SurroundingMean',              # Surrounding is the extra name that will be added to the Mean name, when the surrounding Mean will be added to the csv with all measurements
                                                       extra_col_name='RoiAndBackgrounDifference') == 'failed'              : return    # the failed message can only be output if the minuend of the calculation (Mean in this case) which is part of main roi measurements is not in the main roi csv                
        

            
                       ##### W - A - R - N - I - N - G #####
        # Similar-structured function follows below. Do not mistake them! #
        
    def FindEdges(self):
        """Passes the arguments as kwargs to the module of FijiFindEdgesMeasurements.py and initiates the automatic start of fiji
           for getting measurements of rois in images that have been processed with find edges first. 
           Also creates a main save directory for FindEdges measurements (FindEdgesResults) as well as separate save subdirectories 
           inside it. Each subdirectory will start with planeN and contain measurements from that plane only."""

        if Checks.is_fiji_still_open('imageJ-win64.exe') == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return        

        if self.Helper_Checks() == 'error' : return                                                                               # checks if all user_selections have been made

        (n_of_planes_fe,foldpath_img_fe,roiresults_fe,savemeasure_path_fe,fiji_path_fe,
        list_with_all_subdir_folder_images_fe,list_with_all_subdir_folder__with_zipped_rois_fe,
        planeNstringPattern_fe,coupled_foldimages_with_foldroi_paths_fe)  = self.Helper()

        parent_dir = os.path.dirname(savemeasure_path_fe)                                                                         # finds the penultimate (parent) directory of the path
        edges_save_path = join (parent_dir+'/FindEdgesResults')      

        if Checks.OnlyOnePlaneSelected  (n_of_planes_fe) == 'One_plane_only_by_accident'        : return                          # checks if the user has changed the number of planes and if (s)he wants to #
        if Checks.FindEdgesFolderExists (parent_dir)     == "Exists_Already"                    : return                          # No FindEdgesResults directory should exist at this stage.
        else :        
            os.mkdir(edges_save_path)
            self.user_selections['FindEdges_Folder'] = edges_save_path                                                            # after the directory is created, save it to user_selections too
            all_save_paths_fe = PathMaker.CreateFindEdgesSubdirs(n_of_planes_fe,edges_save_path)                                  # if so, it creates new subdirs based on planes #
        if Checks.VerifySameplaneNstart(coupled_foldimages_with_foldroi_paths_fe,planeNstringPattern_fe) == 'Unmatched': return   #checks if the subdirectories of images and rois have the same planeN start and the same order

        ##### Passes a particular subdir for images, rois, and save to the module #####
        for plane_index_fe in range(len(list_with_all_subdir_folder_images_fe)):
            oneplane_image_fe = list_with_all_subdir_folder_images_fe [plane_index_fe]
            oneplane_roi_fe   = list_with_all_subdir_folder__with_zipped_rois_fe [plane_index_fe]
            one_save_fe       = all_save_paths_fe[plane_index_fe]                                             
            system_fe         = self.scroll_system.currentText()   
            print(f"index is {plane_index_fe} ---  image is {oneplane_image_fe} --- roi is {oneplane_roi_fe} --- and one save {one_save_fe}")
            FijiFindEdgesMeasurements.GetMeasurementsOfRois(Rroiresults=oneplane_roi_fe, Ffoldpath_img=oneplane_image_fe, subdir_edge_path=one_save_fe, Ffiji_path=fiji_path_fe, winlin = system_fe)
        
        while Checks.is_fiji_still_open('imageJ-win64.exe') == True : time.sleep(3)                                                # same as is_fiji_running in Run fiji templates. Wont display the message until processes are done
        message = (f"The standard deviation measurement following Fiji find edges has been added to {edges_save_path}")
        Checks.ShowInfoMessage('Measurements obtained',message)



                       ##### W - A - R - N - I - N - G #####
        # Similar-structured function follows below. Do not mistake them! #
    
    def GetEntropy (self):
        """Passes the arguments as kwargs to the module of EntropyMeasurements.py and initiates the automatic start of fiji
           for getting measurements of Shannon entropy for each roi. 
           Also creates a main save directory for entropy measurements (EntropyResults) as well as separate save subdirectories 
           inside it. Each subdirectory will start with planeN and contain measurements from that plane only. Mind that the fiji
           macro code slightly differes from the entropy_macro.ijm file. There is no need to create further subdirectories here 
           and there is no need to define channel index for locating a particular plane and channel inside a multistack image.
           AResCon is not using multi-stack images, neither in terms of plane nor in terms of channels"""

        # text file with channel number has to be added so that the user knows which channel the folders correspond to
        
        if Checks.is_fiji_still_open('imageJ-win64.exe') == True : 
            Checks.ShowError("Open Fiji proccess detected", 'You have to close all Fiji windows before initiating this function')
            return        

        if self.Helper_Checks() == 'error' : return                                                                                 # checks if all user_selections have been made

        # definition is order sensitive, be careful when adding-removing variables from here
        (n_of_planes_ntr,foldpath_img_ntr,roiresults_ntr,savemeasure_path_ntr,fiji_path_ntr,
        list_with_all_subdir_folder_images_ntr,list_with_all_subdir_folder_with_zipped_rois_ntr,
        planeNstringPattern_ntr,coupled_foldimages_with_foldroi_paths_ntr)  = self.Helper()                                                                        
        
        parent_dir_ntr = os.path.dirname(savemeasure_path_ntr)                                                                      # finds the penultimate (parent) directory of the path
        entropy_save_path = join (parent_dir_ntr+'/EntropyResults')      

        if Checks.OnlyOnePlaneSelected (n_of_planes_ntr) == 'One_plane_only_by_accident' : return                                   # checks if the user has changed the number of planes and if (s)he wants to #
        if Checks.EntropyFolderExists  (parent_dir_ntr)  == "Exists_Already"             : return                                   # No FindEdgesResults directory should exist at this stage.
        else :        
            os.mkdir(entropy_save_path)
            self.user_selections['Entropy_Folder'] = entropy_save_path                                                              # after the directory is created, save it to user_selections too
            all_save_paths_ntr = PathMaker.CreateEntropySubdirs(n_of_planes_ntr,entropy_save_path)                                  # if so, it creates new subdirs based on planes #
         
        if Checks.VerifySameplaneNstart(coupled_foldimages_with_foldroi_paths_ntr,planeNstringPattern_ntr) == 'Unmatched': return   #checks if the subdirectories of images and rois have the same planeN start and the same order
        bitdepth = Checks.CheckBitDepth(self.scroll_bits.currentText())                                                             # gets the user selection for bit depth. If the bitdepth is 16bit, a recommendation for convertion to 8bit first will be made. See the checks module for further info

        ##### Passes a particular subdir for images, rois, and save to the module #####
        for plane_index_ntr in range(len(list_with_all_subdir_folder_images_ntr)):
            oneplane_image_ntr = list_with_all_subdir_folder_images_ntr [plane_index_ntr]
            oneplane_roi_ntr   = list_with_all_subdir_folder_with_zipped_rois_ntr [plane_index_ntr]
            one_save_ntr       = all_save_paths_ntr[plane_index_ntr]                                             
            system_ntr         = self.scroll_system.currentText()   
            EntropyMeasurements.GetShannonEntropy(Rroiresults=oneplane_roi_ntr, Ffoldpath_img=oneplane_image_ntr, subdir_metric_path=one_save_ntr, Ffiji_path=fiji_path_ntr, winlin = system_ntr,bdepth=bitdepth)

    
    def InitializeAddFindEdgesMetrics (self):
        """Adds the StdDev of the Find-Edges results to the respective plane and image file for csv measurements"""
        if Checks.FindEdgesFolderDoesNotExist == 'Does_not_exist'                                          : return
        if Checks.NotSelectedSaveFolder(self.user_selections) == 'save_folder_not_defined'                 : return                                # checks if the save folder where the main measurements subdirs are saved has been selected already #
        if Checks.FindEdgesPythonVariableExists(self.user_selections) == 'missing_user_selection_variable' :   
            Checks.ShowError('Some info were not found','You will now be prompted to locate the FindEdgesResults folder. ' \
            'Please select the main folder and not its planeN subdirectories')
            self.FileDialog(message='Locate the FindEdgesResults folder',what_to_select='FindEdges_Folder')                                            # if the software closes, the user selection for find edges folder will be missing            
        
        main_edges_path                        = self.user_selections["FindEdges_Folder"]                
        mainmeasr_path_edg                     = self.user_selections["Measurements_Folder"]
        list_with_all_subdir_with_find_edges   = sorted ([main_edges_path+'/'+file for file in os.listdir(main_edges_path) if isdir(join(main_edges_path, file))])
        list_with_all_subdir_with_main_metrics = sorted ([mainmeasr_path_edg+'/'+file for file in os.listdir(mainmeasr_path_edg) if isdir(join(mainmeasr_path_edg, file))])
        coupled_edges_paths_and_metrics        = list(zip(list_with_all_subdir_with_find_edges,list_with_all_subdir_with_main_metrics))
        planeN_stringPattern_edg               = r'plane\d+'
        
        if Checks.VerifySameplaneNstart(coupled_edges_paths_and_metrics,planeN_stringPattern_edg) == "Unmatched"        : return
        if Checks.VerifySameNamesInsideSubdir(coupled_edges_paths_and_metrics)                    == "names_dont_match" : return
        if Checks.AskConfirmation('Create Copies','It is recommended that you create a backup of your measurements. Will you ?') == True :
            Checks.CreateCopies (main_edges_path,mainmeasr_path_edg)
        AdditionalMetrics.PassMeasurementsToMainCsv(coupled_edges_paths_and_metrics)


                       ##### W - A - R - N - I - N - G #####
        # Similar-structured function follows below. Do not mistake them! #

    def InitializeAddEntropy (self):
        """Adds the Shannon entropy of each roi as a new column to the respective plane and image file for csv measurements"""
        if Checks.EntropyFolderDoesNotExist == 'Does_not_exist'                                          : return
        if Checks.NotSelectedSaveFolder(self.user_selections) == 'save_folder_not_defined'               : return                                      # checks if the save folder where the main measurements subdirs are saved has been selected already #
        if Checks.EntropyPythonVariableExists(self.user_selections) == 'missing_user_selection_variable' :
            Checks.ShowError('Some info were not found','You will now be prompted to locate the EntropyResults folder. ' \
            'Please select the main folder and not its planeN subdirectories')
            self.FileDialog(message='Locate the EntropyResults folder',what_to_select='Entropy_Folder')

        main_entro_path                        = self.user_selections["Entropy_Folder"]                
        mainmeasr_path_entr                    = self.user_selections["Measurements_Folder"]
        list_with_all_subdir_with_entro        = sorted ([main_entro_path+'/'+file for file in os.listdir(main_entro_path) if isdir(join(main_entro_path, file))])
        list_with_all_subdir_with_main_metrics = sorted ([mainmeasr_path_entr+'/'+file for file in os.listdir(mainmeasr_path_entr) if isdir(join(mainmeasr_path_entr, file))])
        coupled_entro_paths_and_metrics        = list(zip(list_with_all_subdir_with_entro,list_with_all_subdir_with_main_metrics))
        planeN_stringPattern_entr              = r'plane\d+'

        if Checks.VerifySameplaneNstart(coupled_entro_paths_and_metrics,planeN_stringPattern_entr) == "Unmatched"        : return
        if Checks.VerifySameNamesInsideSubdir(coupled_entro_paths_and_metrics,add_csv=True)        == "names_dont_match" : return                      # Entropy filenames do not have .csv in the end (as findedges files have), hence the add_csv=True
        
        if Checks.AskConfirmation('Create Copies','It is recommended that you create a backup of your measurements. Will you ?') == True :
            Checks.CreateCopies (main_entro_path,mainmeasr_path_entr)
        AdditionalMetrics.GatherCsvsToOne(list_with_all_subdir_with_entro, mainmeasr_path_entr)                                                         # Reorganize the files so that a simple csv is created that contains all entropy measurements from all rois (instead of a csv for each roi). Now, organization resembles that of FindEdges.
        AdditionalMetrics.PassMeasurementsToMainCsv(coupled_entro_paths_and_metrics,metric='ShannonEntropy',metric_prefix='')

    def FormRootAndSuffixForEachID(self,the_accepted_rois,plane_patrn):
        """Input the_accepted_rois : dict from the accepted_rois.pkl that was produced after XY filtering in the accepted folder
           Input plane_patrn       : regex pattern for the detection of the planeN in the name.
           Output                  : dict with brain ID names from plane 1 as keys and tuple with str as value.
                                     First element is the root of the name (that is, up to plane-without N) and
                                     second element is the suffix, for instance .tif.
           
           Separates the root (...till plane-without the N) from the suffix (that, is, not keeping the plane number).
           The keys are names from plane1 because all brains should have a plane in plane 1."""
        IDict= {}
        for brainID in the_accepted_rois[1].keys():                              # the keys of accepted_rois are the plane number. We will use only the first plane number because all brains have at least 1 plane. We can reproduce the rest based on the rootname.
            for match in re.finditer(plane_patrn, brainID):                      # the keys of plane one must be like this : 448539_038_01.ome_plane1.tif   plane1 precedes the extension!
                startind, endind = match.span()      
                last_plane_digit_index = endind                                  # index of the last digit in the match
                rootname = brainID[:last_plane_digit_index-1]                    # slice including last digit. This is the unchanged (root) name of the brain ID. only the planeN part changes, which preceds the suffix
                suffix = brainID[last_plane_digit_index:]                        # for instance, the suffix .tif is extracted from 4um_2x2_correct_44_percent.ome_plane1.tif
                IDict[brainID]= (rootname,suffix)                                # assign value as tuple. We call 0 for rootname and 1 for suffix

        return IDict


    def InitiateZfilter(self):
        # Some images have less planes. I have to correct for this here. Similar corrections might be needed in previous stages of the pipeline
        #  Checks.AcceptedROIspicklePathSelected()
        
        default_values = {
        'ratio_intersecting_t'                         : 0.8,
        'one_to_1_engulf_size_threshold_t'             : 1.5,
        'one_to_1_engulfed_intersection_threshold_t'   : 0.9,
        'negligible_1to1_iou_t'                        : 0.2,
        'minimum_1to1_intersection_t'                  : 0.8,
        'minimum_1to1_size_difference_t'               : 0.6,
        'minimize_factor_t'                            : 0.5,
        'marginal_iou_t'                               : 0.5,
        'minimum_intersection_to_consider_engulfed_t'  : 0.25,
        'overall_intersecting_ratio_t'                 : 0.75,
        'proximity_threshold_t'                        : 1,
        'iou_threshold_t'                              : 0.5,
        'minimize_factor2_t'                           : 0.5
        }
        
        # set to default unless the user has inserted some value
        ratio_intersecting_t                        = float(self.ratio_intersecting.text() or default_values['ratio_intersecting_t'])
        one_to_1_engulf_size_threshold_t            = float(self.one_to_1_engulf_size_threshold.text() or default_values['one_to_1_engulf_size_threshold_t'])
        one_to_1_engulfed_intersection_threshold_t  = float(self.one_to_1_engulfed_intersection_threshold.text() or default_values['one_to_1_engulfed_intersection_threshold_t'])
        negligible_1to1_iou_t                       = float(self.negligible_1to1_iou.text() or default_values['negligible_1to1_iou_t'])
        minimum_1to1_intersection_t                 = float(self.minimum_1to1_intersection.text() or default_values['minimum_1to1_intersection_t'])
        minimum_1to1_size_difference_t              = float(self.minimum_1to1_size_difference.text() or default_values['minimum_1to1_size_difference_t'])
        minimize_factor_t                           = float(self.minimize_factor.text() or default_values['minimize_factor_t'])
        marginal_iou_t                              = float(self.marginal_iou.text() or default_values['marginal_iou_t'])
        minimum_intersection_to_consider_engulfed_t = float(self.minimum_intersection_to_consider_engulfed.text() or default_values['minimum_intersection_to_consider_engulfed_t'])
        overall_intersecting_ratio_t                = float(self.overall_intersecting_ratio.text() or default_values['overall_intersecting_ratio_t'])
        proximity_threshold_t                       = int(self.proximity_threshold.text() or default_values['proximity_threshold_t'])
        iou_threshold_t                             = float(self.iou_threshold.text() or default_values['iou_threshold_t'])
        minimize_factor2_t                          = float(self.minimize_factor2.text() or default_values['minimize_factor2_t'])        
        
        Checks.ShowInfoMessage('Locate AcceptedROIs.pkl','Before proceeding to z filtering, you need to indicate the AcceptedROIs.pkl file that contains the ROIs which were filtered based on x and y axis')
        
        pkl_path_accepted = self.LocateAcceptedROIspklDialog()                          # dialog to select the accepted_rois.pkl file that is produced after x,y filtering
        if pkl_path_accepted == None : return                                           # None means that the selection was wrong.
        
        with open(pkl_path_accepted, 'rb') as f:                                        # open the accepted_rois.pkl file that is produced after x,y filtering
            accepted_rois = pickle.load(f) 
        
        planeN_pattern = r'plane\d+'
        maximum_plane  = max(accepted_rois.keys())
        brainIDs:dict  = self.FormRootAndSuffixForEachID(accepted_rois,planeN_pattern)  # create a dict that retains the rootname and suffix information for each image. Value in the form of tuple
        mainzsavepath = PathMaker.CreateZfilteredMainFolder(pkl_path_accepted)          # creates the main folder where final filtered ziped files for each brain will be saved
        if mainzsavepath == 'z folder already exists and not empty': return             # stop the filtering if a zfolder with filtered rois exists already inside the parent path of accepted_ROIs.pkl

        for brainID in brainIDs:
            rootsuffix= brainIDs[brainID]
            writepath_m = join(mainzsavepath,rootsuffix[0])

            
            should_return_None = Zfilter.FilterZplane(accepted_rois,
                                 rootsuffix,
                                 maximum_plane,
                                 writepath_m,
                                 ratio_intersecting = ratio_intersecting_t,
                                 one_to_1_engulf_size_threshold = one_to_1_engulf_size_threshold_t,
                                 one_to_1_engulfed_intersection_threshold = one_to_1_engulfed_intersection_threshold_t,
                                 negligible_1to1_iou = negligible_1to1_iou_t,
                                 minimum_1to1_intersection = minimum_1to1_intersection_t,
                                 minimum_1to1_size_difference = minimum_1to1_size_difference_t,
                                 minimize_factor = minimize_factor_t,
                                 marginal_iou = marginal_iou_t,
                                 minimum_intersection_to_consider_engulfed = minimum_intersection_to_consider_engulfed_t,
                                 overall_intersecting_ratio = overall_intersecting_ratio_t,
                                 proximity_threshold = proximity_threshold_t,
                                 iou_threshold = iou_threshold_t,
                                 minimize_factor2 = minimize_factor2_t)
        
        if should_return_None == "aborted due to missing FindEdges" :
            pass 
        else :
            Checks.ShowInfoMessage("Filtering finished!",f"Your z-filtered ROIs have been generated in {mainzsavepath}")


    def OpenaCsvFile(self):
        """Opens the first csv file from the first planeN of the main roi measurements."""
        if Checks.NotSelectedSaveFolder(self.user_selections) == 'save_folder_not_defined' : return
        first_plane_path = list(Path(self.user_selections["Measurements_Folder"]).iterdir())[0]                                                         # gets the list with plane n subdirectories paths, selects the first,
        single_csvpath   = list(Path(first_plane_path).iterdir())[0]                                                                                    # then gets the list with the paths of the first planeN subdirectory and selects first image roi measurements csv path
        os.startfile(single_csvpath)                                                                                                                    # opens the csv file

    def ApplyOnePlaneFilters (self) :
        """Takes users input for filtering using min and max measurement values and filters out rois from the main_dictionary"""
        try : main_dictionary
        except : 
            Checks.MetricsNotAdded() 
            return
        
        filters_input = self.entry_1planefilters.toPlainText()
        filtered_conditions = Checks.MetricNotInData(filters_input,main_dictionary)                                                          # returns either None (meaning a mistake in filter inputs or the user wants to input again) or a list with conditions inside parentheses. For instance, ['(300>Area>30)','(StdDev>30 and Min<50)'].
        if filtered_conditions is None : return                                                                                                           
                                                                                                                                                      
        filtered_at_conditions = [Mediator.NonWordsToAtSymbol(whole_condition) for whole_condition in filtered_conditions]                   # Do not mistake with filtered_conditions. Here, elements are maintained but (Area>30) becomes @Area@@@  and so on. Example of convertions : @FeretX@@@ and @@@FeretAngle@@@@@@ instead of (FeretX>30 and 30<FeretAngle<300). Mind the one extra @ in the end
        attribute_names        =  Mediator.GetAttributeNamesFromSingleRoi(main_dictionary)
        names_matches          =  Mediator.GetAttributeAndConditioNameMatches(attribute_names,filtered_at_conditions,filtered_conditions)
        if names_matches is None: return
        
        filter_primary_path = Checks.EmptyPathSelections()                                                                                   # primary because inside this path, a FilteredRoisXY_timestamp path will be created
        if filter_primary_path is None : return

        if Checks.WarnIfFindEdgesIsMissing(self) == 'FindEdgesStdDev_not_in_the_main_save_folder_User_Decided_to_stop':
            return

        filterpath=PathMaker.Create2DFilterDirAndSubdirs(names_matches.keys(),filter_primary_path,main_dictionary)                           # this will be the FilteredRoisXY_timestamp path, the parent of which is the filter primary path. All subdirs are created in this method too.
        filtered_out,filtered_in = Mediator.FindViolatingROIs (main_dictionary,names_matches)                            
        if (pkl_save_path:= Mediator.RecreateRoisInsideFilteredDict(filtered_out,filtered_in,filterpath)):                                   # Recreates the Rois from .polygon and pastes them in the right filter subdir. Returns the path of accepted subdir if the user selects to save a pkl file with accepted rois info
            pickle.settings['recurse'] = True
            # IMPORTANT : the structure of the pickle  will change in the innermost level from roi.Area=40 to dict[Area]=40 and so on. This is mandatory to circumvent serialization problems due to RoiClass origin (nested inside an AddMetrics module function)
            serializable_data = Mediator.SimpleSerialize(filtered_in)
            with open(pkl_save_path, 'wb') as f:
                pickle.dump(serializable_data, f)
            Checks.ShowInfoMessage("Accepted ROIs saved",f'A Accepted_ROIs.pkl file that retains all information of your accepted ROIs has been saved in {pkl_save_path}')
        





    def SavePickleMetrics(self):
        """Saves the main_dictionary in pickle format inside the workspace directory"""
        try : main_dictionary
        except : 
            Checks.MetricsNotAdded() 
            return
        with open('saved_metrics.pkl', 'wb') as f:
            pickle.dump(main_dictionary, f)
        message = 'Your pickle file (saved_metrics) has been stored in the workspace directory'
        Checks.ShowInfoMessage ('Saved succesfully!', message)

    def LoadMetrics(self):
        """Loads the pickle file that contains the main_dictionary"""
        global main_dictionary
        if 'saved_metrics.pkl' not in os.listdir(current_dir):
            Checks.ShowError('.pkl file not found', 'There is no saved_metrics.pkl file in the workspace directory')
            return
        with open('saved_metrics.pkl', 'rb') as f:
            main_dictionary = pickle.load(f)    
        QMessageBox.information(None,'.pkl file loaded successfuly', 'The data is now passed to AResCoN')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


