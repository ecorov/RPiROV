$(document).ready(function(){
        setInterval(function() {
            $("#temperature").load("js/sensors_temperature.html");
            $("#depth_current").load("js/sensors_depth_current.html");
            $("#heading_current").load("js/sensors_heading_current.html");
        }, 500);
});




$( "#CtrlPannel" ).css( "display", "block" ) 
$( "#CtrlPwd" ).css( "display", "none" ) 
$( "#mjpeg_dest" ).css( "display", "block" ) 

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
		var pwmLft1 = Math.floor(pwmLft/10) * 10
		var pwmRgt1 = Math.floor(pwmRgt/10) * 10
		
		if (y > 0) {
			var pwmLft1 = -pwmLft1
			var pwmRgt1 = -pwmRgt1
		}
		if (pwmLft1 != pwmLft0) {
			console.log("pwmLft0: " + pwmLft0)
			console.log("pwmLft1: " + pwmLft1)
			pwmLft0 = pwmLft1
			$("#debug").text('Left: '+ pwmLft1);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?lft='+pwmLft1
			});
			console.log("send command")
		}
		if (pwmRgt1 != pwmRgt0) {
			console.log("pwmRgt0: " + pwmRgt0)
			console.log("pwmRgt1: " + pwmRgt1)
			pwmRgt0 = pwmRgt1
			$("#debug").text('Right: ' + pwmRgt1);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?rgt=' + pwmRgt1
			});
			console.log("send command")
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

$("#depth_slider").slider({
	orientation: "vertical",
	min:1010,
	max:1300,
    	step:1,
	value: 1010,
	slide: function() {
        var depth = 1300 - $("#depth_slider").slider("value")
        $("#depth_target").text(' 目标深度: ' + depth + 'cm');
	},

	stop: function() {
        	var depth = 1300 - $("#depth_slider").slider("value")
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?depth=' + depth
		});	
		console.log(domain + 'doStuff.py?depth=' + depth)
        $("#depth_target").text('目标深度: ' + depth  + 'cm');
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





