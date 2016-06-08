
function pwd () {
	if (md5($( "#ctrlpwd" )[0].value) == "8caf447c1cd0db7adbec6c890eb82c70") {
		$( "#CtrlPannel" ).css( "display", "block" ) 
		$( "#CtrlPwd" ).css( "display", "none" ) 
		$( "#mjpeg_dest" ).css( "display", "block" ) 
	} else {
		$( "#CtrlPwd" ).css( "display", "none" ) 
		alert("You can't control this ROV, but you can receive its video stream");
		$( "#mjpeg_dest" ).css( "display", "block" ) 
	}
}




var domain = 'http://' + document.domain + ':8080/'

var pwmLft0 = 1000
var pwmRgt0 = 1000
$("#ctrlrod").draggable ({
	containment : "#boundary",
	revert: "invalid",
	revertDuration: 10,
	drag: function() {	
		var x = Number($("#ctrlrod").css("left").replace("px", "")) - 120
		var y = Number($("#ctrlrod").css("top" ).replace("px", "")) - 120
		if (y < 0) {
			var v0 = parseInt(Math.abs(y))
			var v1 = parseInt(Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2)))
			var scale = 2
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
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: domain + 'doStuff.py?lft='+pwmLft1
				});	
			}
			if (pwmRgt1 != pwmRgt0) {
				pwmRgt0 != pwmRgt1
				$("#debug").text('Right: ' + pwmRgt1);
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: domain + 'doStuff.py?rgt=' + pwmRgt1
				});	
			}
		} else {
			$("#debug").text('Left: '+ 1000 + '   &   Right: ' + 1000);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?lft=1000&rgt=1000'
			});	
		}
	},
	stop: function () {
		$("#debug").text('Left: '+ 1000 + '   &   Right: ' + 1000);
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?lft=1000&rgt=1000'
		});				
	}
});

var p0
$( "#slider" ).slider({
	orientation: "vertical",
	min:0,
	max:380,
	value: 200,
	start: function() {
		p0 = $( "#slider" ).slider( "value" )
		console.log(p0)
	}, 
	stop: function() {
		var step = $( "#slider" ).slider( "value" )-p0
		$("#debug").text('Current:' + $( "#slider" ).slider( "value" ) + "; moved: " + step);
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?stp=' + step
		});	
		console.log(domain + 'doStuff.py?stp=' + step)
	}
});


$( "#led_button" ).on('click', function() {
	var led = $('#led_button img').attr('src');
	if (led.match(/led-1/g) != null) {
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?led=on'
		});	
		$('#led_button img').attr('src', "img/led-0.png");
	} else {
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?led=off'
		});	
		$('#led_button img').attr('src', "img/led-1.png");
	}
});



$("#showsys").on('click', function() {
	if ($( "#syscmd" ).css( "display" ) == "none") {
		$( "#syscmd" ).css( "display", "block" ) 
  } else if ($( "#syscmd" ).css( "display" ) == "block") {
		$( "#syscmd" ).css( "display", "none" ) 
  }
});












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
  }



  console.log('changed');
});
