/**
 * Kontranto game.
 *
 * @constructor
 * @param {string} game_id - ID of the current game.
 * @param {string} player_id - TODO remove
 * @param {string} game_state - The state of the game at the loading time.
 * @param {string} csrf_token - CSRF token to include in the calls to the backend.
 * @param {string} chessboard_theme - Chessboard.js piece theme path.
 */
function Kontranto(game_id, player_id, game_state, csrf_token, chessboard_theme) {
  // TODO remove
  this.player_id = player_id;

  // The current game ID
  this.game_id = game_id;

  // The current game state
  this.game_state = game_state;

  // CSRF token required for communicating with the backend
  this.csrf_token = csrf_token;

  // Player's color
  this.player_color = null;

  // The opponent TODO: replace with the name
  this.opponent_player_id = null;

  // The white player score
  this.white_player_score = 0;

  // The black player score
  this.black_player_score = 0;

  // ID of the game loop timer
  this.timer_id = null;

  // How long to wait between two game loop executions (in miliseconds).
  this.game_loop_period_msec = 5000;

  // Figure placement and fields marking. See the backend model for the details.
  this.board_data = Array(4).fill(['','','','']);

  // chessboard.js chessboard for the game
  this.chessboard = null;

  // Attaches the click handler on the color choice buttons
  this.attachColorChoiceHandler = function(button) {
    button.addEventListener('click', event => {
      // TODO notification
      // TODO call
      document.querySelector("#color_choice_widget").style.display = 'none';
    });
  };

  // Shows the error message to the user.
  this.printError = function(error_message) {
    // TODO: add expiration
    document.querySelector("#error_message_widget").textContent = error_message;
  };

  // Shows the info message to the user.
  this.printInfo = function(message) {
    // TODO: add expiration
    document.querySelector("#info_message_widget").textContent = message;
  };

  // Ends the game
  this.endGame = function() {
    if (this.timer_id !== null) {
      clearInterval(this.timer_id);
    }
  };

  // Updates the game according to the new state.
  this.onGameStateChange = function(new_state) {
    if (new_state === this.game_state) return;

    this.game_state = new_state;
    document.querySelector("#game_state").textContent = this.game_state;

    switch (this.game_state) {
      case "FINISHED":
        this.endGame();
        return;
      case "COLOR_CHOICE":
        break;
      case "CLASH":
        break;
      case "SHOCK_MOVE":
        break;
      case "GAME_RUNNING":
        break;
      case "WAITING_OTHER_PLAYER_MOVE":
        break;
    }

    // TODO color choice -- make buttons visible
    // TODO the rest
  };

  // Updates the chess board to the new positions. Does nothing if the new
  // board is equal to the old board data.
  this.updateBoard = function(board_data) {
    if (JSON.stringify(this.board_data) === JSON.stringify(board_data)) {
      // The board remained the same. No need for an update.
      return;
    }

    var bad_board_data = false;
    // Validation
    if (board_data.length !== this.board_data.length) {
      bad_board_data = true;
    }

    // Collect moves
    var moves_black = {
      triangle: [null, null],
      circle: [null, null],
    };
    var moves_white = {
      triangle: [null, null],
      circle: [null, null],
    };
    // Converts array coordinates to chess coordinates
    var axis_to_chess = function(x, y) {
      return String.fromCharCode('a'.charCodeAt(0) + y - 1) + x.toString();
    };
    for (var i = 0; i < board_data.length; i++) {
      // Validation
      if (board_data[i].length !== this.board_data[i].length) {
        bad_board_data = true;
        return;
      }

      for (var j = 0; j < board_data[i]; j++) {
        if (this.board_data[i][j] === "WT") {
          moves_white.triange[0] = axis_to_chess(i, j);
        }
        if (this.board_data[i][j] === "WC") {
          moves_white.circle[0] = axis_to_chess(i, j);
        }

        if (board_data[i][j] === "WT") {
          moves_white.triange[1] = axis_to_chess(i, j);
        }
        if (board_data[i][j] === "WC") {
          moves_white.circle[1] = axis_to_chess(i, j);
        }

        if (this.board_data[i][j] === "BT") {
          moves_black.triange[0] = axis_to_chess(i, j);
        }
        if (this.board_data[i][j] === "BC") {
          moves_black.circle[0] = axis_to_chess(i, j);
        }

        if (board_data[i][j] === "BT") {
          moves_black.triange[1] = axis_to_chess(i, j);
        }
        if (board_data[i][j] === "BC") {
          moves_black.circle[1] = axis_to_chess(i, j);
        }
      }
    }

    if (bad_board_data) {
      this.printError("Primljena je neispravna ploča!");
      console.log("Bad board data. Length mismatch. Have " + this.board_data + " got " + board_data);
      this.printInfo("Prekid igre.");
      this.endGame();
      return;
    }

    // Execute the moves
    this.chessboard.move(moves_black.triangle.join('-'))
    this.chessboard.move(moves_black.circle.join('-'))
    this.chessboard.move(moves_white.triangle.join('-'))
    this.chessboard.move(moves_white.circle.join('-'))

    // Update the local board state
    this.boad_data = board_data;
  };

  // Renders the game data to the player (score, etc.)
  this.updateGameStats = function(current_player_color, opponent_player_id,
      white_player_score, black_player_score) {
    this.player_color = player_color;
    this.opponent_player_id = opponent_player_id;
    this.white_player_score = white_player_score;
    this.black_player_score = black_player_score;

    document.querySelector("#player_color").textContent = this.player_color;
    document.querySelector("#opponent_name").textContent = this.opponent_player_id;
    document.querySelector("#white_player_score").textContent = this.white_player_score;
    document.querySelector("#black_player_score").textContent = this.black_player_score;
  };

  // Executes the game loop.
  this.gameLoop = function() {
    $.ajax({
      type: "POST",
      url: "/game_state/" + this.game_id + "/" + this.player_id,
      contentType: "application/json; charset=utf-8",
      headers: {"X-CSRFTOKEN": this.csrf_token},
      dataType: "json",
      processData: false,
      success: function(data) {
        this.onGameStateChange(data.game_state);
        this.updateGameStats(data.current_player_color, data.opponent_player_id,
           data.white_player_score, data.black_player_score);
        this.printInfo(data.info_message);
        this.updateBoard(data.board);
        if (data.error_message) {
          this.printError(data.error_message);
        }
      },
      error: function() {
        this.printError("Greška pri komunikaciji sa serverom!");
        console.log("Server error");
      }
    });
  };

  // Handles dragging of the chessboard pieces
  this.onPieceDragStart = function(source, piece, position, orientation) {
    if ((orientation === 'white' && piece.search(/^w/) === -1)
        || (orientation === 'black' && piece.search(/^b/) === -1)) {
      return false
    }
  };

  // Initialize the game
  this.onGameStateChange(this.game_state);

  this.attachColorChoiceHandler(document.querySelector("#color_choice_triangle"));
  this.attachColorChoiceHandler(document.querySelector("#color_choice_circle"));

  let chessboard_config = {
    numRows: 4,
    numColumns: 4,
    draggable: true,
    dropOffBoard: 'snapback',
    onDragStart: this.onPieceDragStart,
    sparePieces: true,
    pieceTheme: chessboard_theme,
    position: { }
  }
  this.chessboard = Chessboard('board', chessboard_config)
  $(window).resize(this.chessboard.resize)

  // Start the game loop
  this.timer_id = setInterval(this.gameLoop, this.game_loop_period_msec);
}

