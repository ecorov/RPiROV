var domain = 'http://192.168.10.102:8080/'


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
			var scale = 3
			if (x < 0) {
				var pwmLft = v1*scale + 1000
				var pwmRgt = v0*scale + 1000
			} else {
				var pwmLft = v0*scale + 1000
				var pwmRgt = v1*scale + 1000
			}
			$("#debug").text('Left: '+ pwmLft + "   &   Right: " + pwmRgt);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?lft='+pwmLft+ '&rgt=' + pwmRgt
			});	
		} else {
			$("#debug").text('Left: '+ 1000 + "   &   Right: " + 1000);
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: domain + 'doStuff.py?lft=1000&rgt=1000'
			});	
		}
	},
	stop: function () {
		$("#debug").text('Left: '+ 1000 + "   &   Right: " + 1000);
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
	max:100,
	value: 50,
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

