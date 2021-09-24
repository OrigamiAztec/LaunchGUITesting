
       #  Main battery - LiFe
        mainLab = QtGui.QLabel("Main\n[LiFe]")
        mainLab.setAlignment(Qt.AlignCenter)

        self.mainNum = QtGui.QLabel()
        self.mainNum.setText("12.8 V")
        self.mainNum.setStyleSheet("background-color: white")
        self.mainNum.setAlignment(Qt.AlignCenter)
        self.mainNum.setFrameShape(QtGui.QFrame.Panel)
        self.mainNum.setFrameShadow(QtGui.QFrame.Sunken)
        self.mainNum.setLineWidth(3)

        self.gridPack.addWidget(mainLab,0,9,1,1)
        self.gridPack.addWidget(self.mainNum,0,10,1,1)

       #  Servo battery - LiPo
        mainLab = QtGui.QLabel("Servo\n[LiPo]")
        mainLab.setAlignment(Qt.AlignCenter)

        self.mainNum = QtGui.QLabel()
        self.mainNum.setText("8.4 V")
        self.mainNum.setStyleSheet("background-color: white")
        self.mainNum.setAlignment(Qt.AlignCenter)
        self.mainNum.setFrameShape(QtGui.QFrame.Panel)
        self.mainNum.setFrameShadow(QtGui.QFrame.Sunken)
        self.mainNum.setLineWidth(3)

        self.gridPack.addWidget(mainLab,0,11,1,1)
        self.gridPack.addWidget(self.mainNum,0,12,1,1)

       #  TeleMega battery - LiPo
        mainLab = QtGui.QLabel("TeleMega\n[LiPo]")
        mainLab.setAlignment(Qt.AlignCenter)

        self.mainNum = QtGui.QLabel()
        self.mainNum.setText("3.7 V")
        self.mainNum.setStyleSheet("background-color: white")
        self.mainNum.setAlignment(Qt.AlignCenter)
        self.mainNum.setFrameShape(QtGui.QFrame.Panel)
        self.mainNum.setFrameShadow(QtGui.QFrame.Sunken)
        self.mainNum.setLineWidth(3)

        self.gridPack.addWidget(mainLab,0,13,1,1)
        self.gridPack.addWidget(self.mainNum,0,14,1,1)