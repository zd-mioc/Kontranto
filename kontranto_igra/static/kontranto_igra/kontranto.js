// The client side of Kontranto game.
//
// Depends on: chessboard.js, jquery

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
function Kontranto(
  game_id,
  player_id,
  game_state,
  csrf_token,
  chessboard_theme
) {
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
  this.game_loop_period_msec = 8000;

  // Figure placement and fields marking. See the backend model for the details.
  this.board_data = Array(4).fill(["", "", "", ""]);

  // chessboard.js chessboard for the game
  this.chessboard = null;

  // Initialize the game
  this.onGameStateChange(this.game_state);

  this.attachColorChoiceHandler(
    document.querySelector("#color_choice_triangle")
  );
  this.attachColorChoiceHandler(document.querySelector("#color_choice_circle"));
  this.attachSubmitMoveHandler(document.querySelector("#submit_move_btn"));

  let chessboard_config = {
    numRows: 4,
    numColumns: 4,
    draggable: true,
    dropOffBoard: "snapback",
    onDragStart: this.onPieceDragStart.bind(this),
    onDrop: this.onPieceMove.bind(this),
    sparePieces: true,
    pieceTheme: chessboard_theme,
    position: {},
  };
  this.chessboard = Chessboard("board", chessboard_config);
  $(window).resize(this.chessboard.resize);
  // Hide the spare pieces until the color is known
  document.querySelectorAll("div.spare-pieces-7492f").forEach(function (d) {
    d.style.display = "none";
  });

  // Run initial game loop to setup the state without waiting.
  this.gameLoop(this);
  // Start the loop
  this.timer_id = setInterval(this.gameLoop, this.game_loop_period_msec, this);
}

// Shows the error message to the user.
Kontranto.prototype.printError = function (error_message) {
  if (!error_message) {
    return;
  }
  // TODO: add expiration
  document.querySelector("#error_message_widget").textContent = error_message;
};

// Shows the info message to the user.
Kontranto.prototype.printInfo = function (message) {
  if (!message) {
    return;
  }
  // TODO: add expiration
  document.querySelector("#info_message_widget").textContent = message;
};

// Ends the game
Kontranto.prototype.endGame = function () {
  if (this.timer_id !== null) {
    clearInterval(this.timer_id);
  }
};

// Updates the game according to the new state.
Kontranto.prototype.onGameStateChange = function (new_state) {
  if (new_state === this.game_state) return;

  this.game_state = new_state;
  document.querySelector("#game_state").textContent = this.game_state;

  switch (this.game_state) {
    case "FINISHED":
      this.endGame();
      break;
    case "COLOR_CHOICE":
      document.querySelector("#color_choice_widget").style.display = "";
      break;
    case "INITIAL_PLACEMENT":
      // Show the spare pieces
      document.querySelectorAll("div.spare-pieces-7492f").forEach(function (d) {
        d.style.display = "";
      });
      document.querySelector("#submit_move_widget").style.display = "";
      break;
    case "CLASH":
      break;
    case "SHOCK_MOVE":
      break;
    case "GAME_RUNNING":
      document.querySelector("#submit_move_btn").disabled = false;
      break;
    case "WAITING_OTHER_PLAYER_MOVE":
      break;
  }
};

// Updates the chess board to the new positions. Does nothing if the new
// board is equal to the old board data.
Kontranto.prototype.updateBoard = function (board_data) {
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
  var axis_to_chess = function (x, y) {
    return String.fromCharCode("a".charCodeAt(0) + y - 1) + x.toString();
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
    console.log(
      "Bad board data. Length mismatch. Have " +
        this.board_data +
        " got " +
        board_data
    );
    this.printInfo("Prekid igre.");
    this.endGame();
    return;
  }

  // Execute the moves
  this.chessboard.move(moves_black.triangle.join("-"));
  this.chessboard.move(moves_black.circle.join("-"));
  this.chessboard.move(moves_white.triangle.join("-"));
  this.chessboard.move(moves_white.circle.join("-"));

  // Update the local board state
  this.boad_data = board_data;
};

// Updates the internal game state and the visible data based on the data
// received from the backend.
function updateGameInfo(kontranto, data) {
  kontranto.onGameStateChange(data.game_state);
  kontranto.updateGameStats(
    data.opponent_player_id,
    data.white_player_score,
    data.black_player_score,
    data.current_player_color
  );
  kontranto.printInfo(data.info_message);
  kontranto.updateBoard(data.board);
  kontranto.printError(data.error_message);
}

// Renders the game data to the player (score, etc.)
Kontranto.prototype.updateGameStats = function (
  opponent_player_id,
  white_player_score,
  black_player_score,
  current_player_color
) {
  this.opponent_player_id = opponent_player_id;
  this.white_player_score = white_player_score;
  this.black_player_score = black_player_score;
  this.player_color = current_player_color;

  document.querySelector("#opponent_name").textContent =
    this.opponent_player_id;
  document.querySelector("#white_player_score").textContent =
    this.white_player_score;
  document.querySelector("#black_player_score").textContent =
    this.black_player_score;
  document.querySelector("#player_color").textContent = this.player_color;
};

// Attaches the click handler on the submit move button
Kontranto.prototype.attachSubmitMoveHandler = function (button) {
  var self = this;
  button.addEventListener("click", function (e) {
    button.disabled = true;

    // Converts chess coordinates (a2) to axis coordinates (1, a) which are
    // (row, column)
    var chess_to_axis = function (p) {
      if (p.length !== 2) {
        console.log("Invalid chess position: " + p);
        return null;
      }
      let y = p.charCodeAt(0) - "a".charCodeAt(0);
      let x = p.charCodeAt(1) - "1".charCodeAt(0);
      if (y < 0 || y > 3 || x < 0 || x > 3) {
        console.log("Invalid axis coordinates from position: " + p);
        return null;
      }
      return [x, y];
    };

    var move_data = { player_id: self.player_id, game_id: self.game_id };
    // Get the positions from the chessboard
    for (const [pos, piece] of Object.entries(self.chessboard.position())) {
      console.log(pos);
      console.log(piece);
      console.log(piece[0].toUpperCase());
      console.log(self.player_color[0]);
      if (piece[0].toUpperCase() !== self.player_color[0]) {
        continue;
      }
      const coord = chess_to_axis(pos);
      if (coord === null) {
        return;
      }
      if (piece[1] === "K") {
        move_data.new_circle_position = coord;
      } else if (piece[1] === "Q") {
        move_data.new_triangle_position = coord;
      } else {
        console.log("Invalid piece: " + piece);
        return;
      }
    }

    $.ajax({
      type: "POST",
      url: "/move",
      contentType: "application/json; charset=utf-8",
      headers: { "X-CSRFTOKEN": self.csrf_token },
      dataType: "json",
      processData: false,
      cache: false,
      data: JSON.stringify(move_data),
      success: function (data) {
        updateGameInfo(self, data);
      },
      error: function (request, status, error) {
        button.disabled = false;
        self.printError("Greška pri komunikaciji sa serverom!");
        console.log("Server error: " + error);
      },
    });
  });
};

// Attaches the click handler on the color choice buttons
Kontranto.prototype.attachColorChoiceHandler = function (button) {
  var self = this;
  button.addEventListener("click", function (e) {
    document.querySelector("#color_choice_widget").style.display = "none";
    $.ajax({
      type: "POST",
      url: "/move",
      contentType: "application/json; charset=utf-8",
      headers: { "X-CSRFTOKEN": self.csrf_token },
      dataType: "json",
      processData: false,
      cache: false,
      data: JSON.stringify({
        player_id: self.player_id,
        game_id: self.game_id,
        color_choice_shape: button.value,
      }),
      success: function (data) {
        updateGameInfo(self, data);
      },
      error: function (request, status, error) {
        self.printError("Greška pri komunikaciji sa serverom!");
        console.log("Server error: " + error);
      },
    });
  });
};

// TODO
//  - valid move positions (edge case: two figures of the same color are in reach -- one would 'eat' the other)

// Executes the game loop.
Kontranto.prototype.gameLoop = function (kontranto) {
  $.ajax({
    type: "POST",
    url: "/game_state/" + kontranto.game_id + "/" + kontranto.player_id,
    contentType: "application/json; charset=utf-8",
    headers: { "X-CSRFTOKEN": kontranto.csrf_token },
    dataType: "json",
    processData: false,
    cache: false,
    success: function (data) {
      updateGameInfo(kontranto, data);
    },
    error: function (request, status, error) {
      kontranto.printError("Greška pri komunikaciji sa serverom!");
      console.log("Server error: " + error);
    },
  });
};

// Handles dragging of the chessboard pieces
Kontranto.prototype.onPieceDragStart = function (
  source,
  piece,
  position,
  orientation
) {
  if (
    (orientation === "white" && piece.search(/^w/) === -1) ||
    (orientation === "black" && piece.search(/^b/) === -1)
  ) {
    return false;
  }
  const valid_move_states = ["GAME_RUNNING", "CLASH", "INITIAL_PLACEMENT"];
  if (!valid_move_states.includes(this.game_state)) {
    return false;
  }
};

// Runs after the piece gets moved. Removes the pieces from the spares.
Kontranto.prototype.onPieceMove = function (
  source,
  target,
  piece,
  newPos,
  oldPos,
  orientation
) {
  if (source === "spare" && target !== "offboard") {
    console.log("Spare piece " + piece + " was moved to the board");
    document.querySelector(
      "div.spare-pieces-7492f > img[data-piece='" + piece + "']"
    ).style.display = "none";
  }
};
