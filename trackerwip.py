import sys

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QWidget



class View(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.reset()

    def reset(self, new_game=True):
        self.mode = "Normal"  # 3 states: Normal, Rename, Delete

        self.setWindowTitle('matchmakin')
        self.setMinimumSize(800, 400)
        self.setStyleSheet("background-color: #212121")
        self.generalLayout = QVBoxLayout()  # vertical widget layout

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.generalLayout)  # set layout of central widget


        if new_game:
            self.initializeNames()

        self.createCmdButtons()
        self.createPlayerButtons()
        self.createOpponentDisplay()
        self.createDisplay()


        self.connectCmdButtons()
        self.connectPlayerButtons()
        self.updateDisplays()


    def initializeNames(self, rename=True):
        dialog = QInputDialog()
        dialog.setStyleSheet("background-color: #212121;")
        text, pressed = dialog.getMultiLineText(None, "Names", "Enter 7 names on new lines or cancel to exit. ")

        if pressed:
            names = [x for x in text.splitlines() if x != ""]
            if len(names) != 7:
                names = self.initializeNames(False) # reprompt but don't rename
        else:
            sys.exit()

        if rename:
            for pid in range(1, 8):
                self.model.rename(pid, names[pid-1])
        return names

    def connectPlayerButtons(self):
        if self.mode == "Rename":
            for pid, plr_btn in self.playerButtons.items():
                try:
                    plr_btn.disconnect()
                except TypeError:
                    pass
                plr_btn.clicked.connect(partial(self.createRenameInput, pid))
                plr_btn.clicked.connect(self.updateDisplays)

        elif self.mode == "Delete":
            for pid, plr_btn in self.playerButtons.items():
                try:
                    plr_btn.disconnect()
                except TypeError:
                    pass
                plr_btn.clicked.connect(partial(self.deletePlayer, pid))
                plr_btn.clicked.connect(partial(self.model.deletePlayer, pid))
                plr_btn.clicked.connect(self.cmd_buttons["Reset"].click)


        else:
            for pid, plr_btn in self.playerButtons.items():
                try:
                    plr_btn.disconnect()
                except TypeError:
                    pass

                if pid in self.model.opponents:
                    plr_btn.setStyleSheet("QPushButton {color: #ffffff; background-color: #19451c; font-size:12px}")
                    plr_btn.clicked.connect(partial(self.model.fightPlayer, pid))
                    plr_btn.clicked.connect(self.updateDisplays)
                    plr_btn.clicked.connect(self.connectPlayerButtons)
                elif pid in self.model.notOpponents:
                    plr_btn.setStyleSheet("QPushButton {color: #ffffff; background-color: #45191f; font-size:12px}")

                # don't do anything if player dead




    def createCmdButtons(self):
        self.cmd_buttons = {}
        button_names = ["Reset", "Rename", "Delete", "Undo Fight", "New Game"]
        cmd_layout = QHBoxLayout()
        for btn in button_names:
            self.cmd_buttons[btn] = QPushButton(btn)
            self.cmd_buttons[btn].setMinimumSize(100, 40)
            self.cmd_buttons[btn].setMaximumSize(220, 80)
            self.cmd_buttons[btn].setStyleSheet("color: white; background-color: grey; font-size: 14px")
            self.cmd_buttons[btn].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            if (btn == "Rename") | (btn == "Delete"):
                self.cmd_buttons[btn].setCheckable(True)
                self.cmd_buttons[btn].setStyleSheet("QPushButton {color:white; background-color: grey; font-size: 14px}"
                                                    "QPushButton:checked {color: white; background-color: #705e43; font-size: 14px}")
            cmd_layout.addWidget(self.cmd_buttons[btn])
        self.generalLayout.addLayout(cmd_layout)

    def createPlayerButtons(self):
        player_layout = QHBoxLayout()
        self.playerButtons = {}
        for pid, name in self.model.names.items():
            if (pid in self.model.opponents):
                self.playerButtons[pid] = QPushButton(name)
                self.playerButtons[pid].setMinimumSize(100, 40)
                self.playerButtons[pid].setMaximumSize(200, 60)
                self.playerButtons[pid].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

                player_layout.addWidget(self.playerButtons[pid])

        self.generalLayout.addLayout(player_layout)




    def connectCmdButtons(self):

        self.cmd_buttons["Reset"].clicked.connect(self.model.reset)
        self.cmd_buttons["Reset"].clicked.connect(partial(self.reset, False))

        self.cmd_buttons["New Game"].clicked.connect(self.model.newGame)
        self.cmd_buttons["New Game"].clicked.connect(partial(self.reset, True))

        self.cmd_buttons["Rename"].clicked.connect(partial(self.toggleMode, "Rename"))
        self.cmd_buttons["Rename"].clicked.connect(self.connectPlayerButtons)

        self.cmd_buttons["Delete"].clicked.connect(partial(self.toggleMode, "Delete"))
        self.cmd_buttons["Delete"].clicked.connect(self.connectPlayerButtons)

        self.cmd_buttons["Undo Fight"].clicked.connect(self.model.undo)
        self.cmd_buttons["Undo Fight"].clicked.connect(self.connectPlayerButtons)
        self.cmd_buttons["Undo Fight"].clicked.connect(self.updateDisplays)

    def createDisplay(self):
        self.display = QLineEdit()
        self.display.setFixedHeight(50)
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignLeft)

        self.display.setStyleSheet("color:white; font-size: 20px")
        self.generalLayout.addWidget(self.display)

    def createOpponentDisplay(self):
        self.opponentDisplay = QLineEdit()
        self.opponentDisplay.setFixedHeight(50)
        self.opponentDisplay.setReadOnly(True)
        self.opponentDisplay.setAlignment(Qt.AlignLeft)

        self.opponentDisplay.setStyleSheet("color: white; font-size: 20px")
        
        self.generalLayout.addWidget(self.opponentDisplay)

    def toggleMode(self, mode):
        if self.mode != mode:
            self.mode = mode
        else:
            self.mode = "Normal"

        if self.mode == "Delete":
            self.cmd_buttons["Rename"].setChecked(False)
        elif self.mode == "Rename":
            self.cmd_buttons["Delete"].setChecked(False)
        else:
            self.cmd_buttons["Delete"].setChecked(False)
            self.cmd_buttons["Rename"].setChecked(False)

    def deletePlayer(self, pid):
        self.playerButtons[pid].hide()

    def unhideButtons(self):
        for pid, btn in self.playerButtons.items():
            btn.show()


    def updateDisplays(self):
        text = "History:    "
        for pid in self.model.notOpponents:
            text += self.model.names[pid] + "        "
        self.display.setText(text)

        text = "Opponents:    "
        for pid in self.model.opponents:
            text += self.model.names[pid] + "        "
        self.opponentDisplay.setText(text)


    def clearDisplay(self):
        self.display.setText("History: ")

    def createRenameInput(self, pid):
        text, pressed = QInputDialog.getText(None, "Rename", "Enter name: ", QLineEdit.Normal, self.model.names[pid])
        if pressed:
            new_name = text
            self.model.rename(pid, new_name)
            self.playerButtons[pid].setText(new_name)








class Model:

    def __init__(self):
        self.newGame()

    def rename(self, pid, new):
        self.names[pid] = new

    def reset(self):
        self.opponents = self.opponents + self.notOpponents
        self.notOpponents = []


    def newGame(self):
        self.opponents = [1, 2, 3, 4, 5, 6, 7]
        self.names = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7"}
        self.notOpponents = []
        self.numOpponents = 7
        self.numAlive = 8
        self.opponentHistory = []

    def fightPlayer(self, pid):
        self.opponentHistory.append((self.opponents.copy(), self.notOpponents.copy()))
        self.opponents.remove(pid)
        self.notOpponents.append(pid)
        self.numOpponents = len(self.opponents)




        if len(self.notOpponents) > self.numAlive - 4:
            if self.numAlive > 3 & self.numOpponents < 3:
                self.opponents.insert(0, self.notOpponents.pop(0))

        print(self.opponents)
        print(self.notOpponents)
        print(self.opponentHistory)

    def undo(self):
        print(self.opponentHistory)
        if len(self.opponentHistory) > 0:

            self.opponents, self.notOpponents = self.opponentHistory.pop()


            print(self.opponents)
            print(self.notOpponents)



    def deletePlayer(self, pid):


        try:
            self.opponents.remove(pid)
        except ValueError:
            pass
        try:
            self.notOpponents.remove(pid)
        except ValueError:
            pass

        self.opponentHistory = []
        self.numAlive -= 1
        self.numOpponents = len(self.opponents)







def main():

    tracker = QApplication([])
    model = Model()
    view = View(model=model)
    view.show()
    sys.exit(tracker.exec_())



if __name__ == '__main__':
    main()