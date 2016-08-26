
$(document).ready(function(){
        setInterval(function() {
            $("#leak").load("js/sensors_leak.html");	
            $("#temperature").load("js/sensors_temperature.html");
            $("#depth_current").load("js/sensors_depth_current.html");
            $("#heading_current").load("js/sensors_heading_current.html");
            var theta = parseInt($("#heading_current").text().replace("Heading: ", ""))
	    x = Math.cos((90+360-theta)/180*Math.PI)*150
	    y = Math.sin((90+360-theta)/180*Math.PI)*150
	    $("#rovHeading").attr("style", "right:"+parseInt(150-x)+"px;bottom:" + parseInt(150+y) + "px;background-color:red;width:20px;height:20px;position: absolute;border-radius: 10px;")
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
		var y = 120 - Number($("#ctrlrod").css("top" ).replace("px", ""))
		var z = parseInt(Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2))/1.69) 

		if (x >= 0) {
			theta = parseInt(Math.atan2(x,y)/Math.PI*180)
		} else {
			theta = parseInt(360 + Math.atan2(x,y)/Math.PI*180)
		}

		var mode = $("#drivemode").val()
		var powerscale = $("#powerscale").val()
		if (powerscale == "slow") {
			var scale = 3; 
		} else { 
			var scale = 9; 
		}
		var z = parseInt(Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2))/1.69) * scale + 1000


		if (mode == "free") {
			var pwm1 = parseInt(Math.abs(y))
			var pwm2 = parseInt(Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2)))			
			if (x < 0) {
				var pwmLft = pwm2*scale + 1000
				var pwmRgt = pwm1*scale + 1000
			} else {
				var pwmLft = pwm1*scale + 1000
				var pwmRgt = pwm2*scale + 1000
			}
			if (y < 0) {
				var pwmLft = -pwmLft
				var pwmRgt = -pwmRgt
			}
			if (pwmLft != pwmLft0) {
				pwmLft0 = pwmLft
				$("#pwm_target").text('PWM_Left: '+ pwmLft);
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: domain + 'doStuff.py?mod=fre&lft='+pwmLft
				});
			}
			if (pwmRgt != pwmRgt0) {
				pwmRgt0 = pwmRgt
				$("#pwm_target").text('PWM_Right: ' + pwmRgt);
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: domain + 'doStuff.py?mod=fre&rgt=' + pwmRgt
				});
			}
		} else if (mode == "yaw") {
			$("#heading_target").text("Heading_target: "+ theta);
			$("#pwm_target").text('PWM: ' + z);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?yaw='+ theta
			});	
		} else {
			$("#heading_target").text("Heading_target: "+ theta);
			$("#pwm_target").text('PWM: ' + z);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?mod=fix&pwm='+ z + '&theta=' + theta
			});	
		}
	},
	stop: function () {
		$("#pwm_target").text('Stop propellers!');
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?mod=stp'
		});				
	}
});

$("#depth_slider").slider({
	orientation: "vertical",
	min:1014,
	max:1300,
    	step:1,
	value: 1300,
	slide: function() {
        	var depth = 1300 - $("#depth_slider").slider("value") + 1014
        	$("#depth_target").text('Pressure_target: ' + depth + ' mbar');
	},

	stop: function() {
        	var depth = 1300 - $("#depth_slider").slider("value") + 1014
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?depth=' + depth
		});	
		console.log(domain + 'doStuff.py?depth=' + depth)
        $("#depth_target").text('Pressure_target: ' + depth + ' mbar');
	}
});

$("#updown").slider({
	orientation: "vertical",
	min:0,
	max:30,
    	step:1,
	value: 15,
	slide: function() {
        	var stp = $("#updown").slider("value") - 15
        	$("#depth_target").text('Step: ' + stp);
	},

	stop: function() {
        	var stp = $("#updown").slider("value") - 15
		$.ajax({
			type: 'GET',
			dataType: 'jsonp',
			url: domain + 'doStuff.py?stp=' + stp
		});	
		console.log(domain + 'doStuff.py?stp=' + stp)
        	$("#depth_target").text('Step: ' + stp );
        	$("#updown").slider({value: 15})
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





