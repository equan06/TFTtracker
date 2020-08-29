class View {
    // all UI functions, buttons, etc.
    constructor() {
        this.game = new Game();
        this.mode = "default"; // default, rename, delete
        this.boundPlayerFxn = this.handlePlayer.bind(this);
        this.enableCmdButtons();
        this.enablePlayerButtons();
        this.enableForms();
        this.cmdBackgroundColor = document.getElementById("rename").style.backgroundColor;
        this.cmdAltColor = "#737373";
        this.plrGreen = document.getElementById("0").style.backgroundColor;
        this.plrRed = "#570109";
    }

    handleNewGame() {
        this.game = new Game();
        this.mode = "default";
        this.game.reset();
        this.updateButtonView(true);
    }

    handleReset() {
        this.game.reset();
        this.updateButtonView();
    }

    
    handleRename() {
        // can consolidate rename/delete into tne function probably
        if (this.mode === "rename") {
            this.mode = "default";
            document.getElementById("rename").style.backgroundColor = this.cmdBackgroundColor;
        } else {
            this.mode = "rename";
            document.getElementById("rename").style.backgroundColor = this.cmdAltColor;
        }
    }
    
    handleDelete() {
        if (this.mode === "delete") {
            this.mode = "default";
            document.getElementById("delete").style.backgroundColor = this.cmdBackgroundColor;
        } else {
            this.mode = "delete";
            document.getElementById("delete").style.backgroundColor = this.cmdAltColor;
        }
    }

    handleUndo() {
        this.game.undo();
        this.updateButtonView();
    }

    handlePlayer(e) {
        // handlePlayer is bound to a view instance, so this refers to the view instance instead of the button
        // to access the button, use e.target
       
        let btn = e.target;
        let id = Number(btn.id);

        if (typeof btn.state === "undefined") {
            btn.state = true;
        }
        
        console.log("mode: " + this.mode);
        if (this.mode === "default") {
            this.game.updateCanFight(id);
        } else if (this.mode === "rename") {
            this.renamePlayer(btn);
            this.game.updateName(id, btn.innerText);
            document.getElementById("rename").style.backgroundColor = this.cmdBackgroundColor;
            // some code to update player names
        } else if (this.mode === "delete") {
            this.deletePlayer(btn);
            this.game.deletePlayer(id);
            document.getElementById("delete").style.backgroundColor = this.cmdBackgroundColor;
        }
        this.mode = "default";
        this.updateButtonView();
    }

    handleSubmit(e) {
        // regex matches by /r (old mac), /n (unix/new mac), /r/n (Windows)
        let names = document.getElementById("textarea").value.split(/\r?\n/);
        for (let id = 0; id < 7; id++) {
            document.getElementById(String(id)).innerText = names[id];
            this.game.updateName(id, names[id]);
        }
        this.updateButtonView();
    }


    
    enableCmdButtons() {
        // bind is required since these methods still need to access the view object. 
        // without bind, this would refer to the button

        document.getElementById("newgame").addEventListener("click", this.handleNewGame.bind(this));
        document.getElementById("reset").addEventListener("click", this.handleReset.bind(this));
        document.getElementById("rename").addEventListener("click", this.handleRename.bind(this));
        document.getElementById("delete").addEventListener("click", this.handleDelete.bind(this));
        document.getElementById("undo").addEventListener("click", this.handleUndo.bind(this));
    }

    enablePlayerButtons() {
        document.querySelectorAll(".player").forEach(
            player => player.addEventListener("click", this.handlePlayer.bind(this))
        )
    }

    enableForms() {
        document.getElementById("submit").addEventListener("click", this.handleSubmit.bind(this));
    }

    renamePlayer(element) {
        element.innerHTML = prompt("Enter a name:");
    }

    deletePlayer(element) {
        element.style.visibility = "hidden";
    }

    showPlayer(element) {
        element.style.visibility = "visible";
    }

    updateButtonView(newGame=false) {
        // update colors of playerbuttons based on matchmaking 

        document.querySelectorAll(".player").forEach(
            player => {
                if (newGame) {
                    player.style.visibility = "visible";
                }
                player.style.backgroundColor = (this.game.canFightPlayer(Number(player.id))) ? this.plrGreen : this.plrRed; 
            }
        )
        // update display
        this.updateDisplay(this.game.getNamesFromIds());
    }

    updateDisplay(names) {
        let opponents = document.getElementById("opponents");
        opponents.innerHTML = "Opponents:&emsp;&emsp;" + names[0].join("&emsp;&emsp;");

        let history = document.getElementById("history");
        history.innerHTML = "History:&emsp;&emsp;" + names[1].join("&emsp;&emsp;");
    }


}

class Game {
    // all game related stuff (matchmaking, player info)
    constructor() {
        this.canFight = [0, 1, 2, 3, 4, 5, 6];
        this.cannotFight = [];
        this.numAlive = 7;
        this.lastOpponent = null;
        this.matchHistory = [[this.canFight.slice(), []]];
        this.playerNames = {0:"0", 1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6"}; // note that property names can be literals, accessible with a[1] or a['1']
    }

    canFightPlayer(id) {
        return this.canFight.includes(id);
    }

    updateCanFight(id) {
        if (this.canFightPlayer(id)) {
            this.lastOpponent = id;

            this.canFight.splice(this.canFight.indexOf(id), 1); // remove from canFight
            if (this.canFight.length < 3 && this.numAlive > 3) {
                this.canFight.push(this.cannotFight.shift()) // remove & return 0th element, add to canFight
            }
            this.cannotFight.push(id); // append to end of cannotFight

            this.updateMatchHistory();
            console.log(this.canFight);
            console.log(this.cannotFight);
        }
    }

    deletePlayer(id) {
        // rules: cannot fight lastOpponent or the the person you deleted
        this.canFight = [...this.canFight, ...this.cannotFight];
        searchDeleteFromArr(this.canFight, id);
        searchDeleteFromArr(this.canFight, this.lastOpponent);
        this.cannotFight = (this.lastOpponent === null || this.lastOpponent === id) ? [] : [this.lastOpponent];
        this.matchHistory = [[this.canFight.slice(), this.cannotFight.slice()]];
        console.log(this.canFight);
        console.log(this.cannotFight);
    }

    updateMatchHistory() {
        this.matchHistory.push([this.canFight.slice(), this.cannotFight.slice()]);
        console.log(this.matchHistory);
    }

    updateName(id, newName) {
        this.playerNames[id] = newName; 
        console.log(this.playerNames);
    }


    getNamesFromIds(ids) {
        return [this.canFight.map(id => this.playerNames[id]), this.cannotFight.map(id => this.playerNames[id])];
    }

    undo() {
        console.log("undo");
        if (this.matchHistory.length > 1) {
            this.matchHistory.pop();
            this.canFight = this.matchHistory[this.matchHistory.length - 1][0].slice();
            this.cannotFight = this.matchHistory[this.matchHistory.length - 1][1].slice();
        }
        console.log(this.matchHistory);
        
    }

    reset() {
        this.canFight = [...this.canFight, ...this.cannotFight];
        this.cannotFight = [];
        this.updateMatchHistory();
    }
}

function searchDeleteFromArr(arr, id) {
    let index = arr.indexOf(id);
    if (index != -1) {
        arr.splice(arr.indexOf(id), 1);
    }
}

let view = new View();
