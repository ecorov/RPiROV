
/*
  var haveEvents = 'GamepadEvent' in window;
  var controllers = [];
  var rAF = window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.requestAnimationFrame;
  
  function connecthandler(e) {
    addgamepad(e.gamepad);
  }
  function addgamepad(gamepad) {
    controllers[gamepad.index] = gamepad; 
    rAF(updateStatus);
  }
  function updateStatus() {
    scangamepads();
    var controller = controllers[0];
    var btn_0 = controller.buttons[6];
    var btn_1 = controller.buttons[7];
    if (btn_0.pressed) {
    	$("#debug").text('sink: 1')
    }
    if (btn_1.pressed) {
    	$("#debug").text('float: 1')
    }
    
    var x = controller.axes[0].toFixed(2);
    var y = controller.axes[1].toFixed(2);
    if (y < 0) {
      var v0 = Math.abs(y)
      var v1 = Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2))
      var scale = 300
      if (x < 0) {
        var pwmLft = v1*scale + 1000
        var pwmRgt = v0*scale + 1000
      } else {
        var pwmLft = v0*scale + 1000
        var pwmRgt = v1*scale + 1000
      }
      console.log(pwmLft)
      console.log(pwmRgt)
      var pwmLft1 = Math.floor(pwmLft/10) * 10
      var pwmRgt1 = Math.floor(pwmRgt/10) * 10
      
      if (pwmLft1 != pwmLft0) {
        pwmLft0 = pwmLft1
        $("#debug").text('Left: '+ pwmLft1);
      }
      if (pwmRgt1 != pwmRgt0) {
        pwmRgt0 != pwmRgt1
        $("#debug").text('Right: ' + pwmRgt1);
      }
    } else {
      $("#debug").text('Left: '+ 1000 + '   &   Right: ' + 1000);
    }
    rAF(updateStatus);
  }
  function scangamepads() {
    var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
    for (var i = 0; i < gamepads.length; i++) {
      if (gamepads[i]) {
        if (!(gamepads[i].index in controllers)) {
          addgamepad(gamepads[i]);
        } else {
          controllers[gamepads[i].index] = gamepads[i];
        }
      }
    }
  }
  
  if (haveEvents) {
    window.addEventListener("gamepadconnected", connecthandler);
  }
  
  //if (controllers.length == 0) {
  //  document.getElementById("btn").innerHTML = "No gamepad connected"
  //} 
  
  
  
  
  
$('#debug').bind("DOMSubtreeModified",function(){
  var innText = $("#debug").text();
  var res = innText.split("&");
  if (res.length == 2) {
	  $.ajax({
		type: 'GET',
		dataType: 'jsonp',
		url: domain + 'doStuff.py?lft=1000&rgt=1000'
	});	
  } 
  
  if (res.length == 1) {
  	if (res[0].match(/Left/g) != null) {
  	  var strLft1 = res[0].split(": ")	
  	  var pwmLft1 = strLft1[1]
    		$.ajax({
		type: 'GET',
		dataType: 'jsonp',
		url: domain + 'doStuff.py?lft='+pwmLft1
	});
  	}
  	if (res[0].match(/Right/g) != null) {
  	  var strRgt1 = res[0].split(": ")	
  	  var pwmRgt1 = strRgt1[1]
    		$.ajax({
		type: 'GET',
		dataType: 'jsonp',
		url: domain + 'doStuff.py?rgt='+pwmRgt1
	});
  	}
  	
  	if (res[0].match(/sink/g) != null) {
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?stp=' + 1
		});
		$("#debug").text('')
  	}
  	
  	if (res[0].match(/float/g) != null) {
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?stp=' + -1
		});
		$("#debug").text('')
  	}
  	
  }
  console.log('changed');
});
*/
