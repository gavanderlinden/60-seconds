var myApp = angular.module("myApp", ["timer"])

myApp.controller("AppController", AppController);

function AppController($scope) {
  $scope.score_player_1 = 0;
  $scope.score_player_2 = 0;
  $scope.terms = [];
  $scope.getTerm = function() {
    ws.send(JSON.stringify({"action":"next"}))
  };
  $scope.timeUp = function() {
    ws.send(JSON.stringify({"action":"end"}))
  };
  $scope.startRound = function() {
    ws.send(JSON.stringify({"action":"start"}));
  };
  $scope.startTimer = function() {
    $scope.$broadcast('timer-start');
    $scope.timerRunning = true;
  }
  $scope.addTerm = function(val) {
    $scope.terms.push(val);
    $scope.$apply();
  }
};

var ws;

  function openWS(uri) {
    ws = new WebSocket("ws://localhost/chat_" + uri);
    scope = angular.element(document.getElementById('MyAng')).scope();
    ws.onmessage = function(e) {
      var data = JSON.parse(e.data);
      console.log(data)
      if (data.action=="start-timer") {
        console.log("starting timer");
        scope.startTimer();
      } else {
        scope.addTerm(data.message);
      }
    };
/*    ws.onopen = function(e) {
      ws.send(JSON.stringify({"register_view": userview}))
    }*/
    ws.onclose = function(e) {
      openWS(uri);
    };
  }

  function sendMessage() {
    var data = {
        author: document.getElementById("username").value,
        message: document.getElementById("message").value
    };

    if(data.author && data.message) {
      ws.send(JSON.stringify(data));
    }
  }

  window.onload = function() {
    var uri = document.URL.split("/").pop() // other option is audience
    if("WebSocket" in window) {
      openWS(uri);
    }
    else {
      alert("WEBSOCKETS NOT SUPPORTED");
    }
  }