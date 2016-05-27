<!DOCTYPE html>
<html>

<head>
  <title>RPi ROV</title>

  
    <link rel="stylesheet" href="css/jquery-ui.css"> 
    <script src="js/jquery-1.10.2.js"></script>
    <script src="js/jquery-ui.js"></script>
	<script src="js/jquery.ui.touch-punch.min.js"></script>
	<script src="js/script.js"></script>
    <script src="js/pipan.js"></script>
	<!--<script src="http://friedcell.si/js/jQuery.windowName/jQuery.windowName.plugin.js"></script> -->
	<style>
	body {
		margin: 0px;
	}
	#boundary {
	  position: absolute;
	  width: 300px;
	  height: 300px;
	  border-radius: 150px;
	  background-color: rgb(200,200,200);
	  opacity: 0.1;
	  bottom: 10px;
	  right:10px;
	}

	#ctrlrod {
		z-index: 99;
	  position: relative;
	  top:120px;
	  left:120px;
	  width: 60px;
	  height: 60px;
	  border-radius: 30px;
	  background-color: red;

	}
	#slider {
		position: absolute;
		height: 75vh;
		bottom: 20px;
		left:38px;
	    border: 1px solid white;
		background-color: rgb(0, 102, 255);
		opacity: 0.2;
	
	}
	.ui-widget-content, .ui-slider-handle.ui-state-default.ui-corner-all {
		background: none;
	}
	#slider a{
	    border: 1px solid white;
		background-color: rgb(255, 51, 0);
		height: 0px;
		padding-top: 10px;
		padding-bottom: 10px;
		width: 30px;
	}

	#download {
		position: absolute;
		top: 10px;
		left:10px;	
	}
	
	#camera{
		position: absolute;
		bottom: 10px;
		right: calc(50vw - 109px); 
	}
	img {
		width: 100vw;
		height: 100vh;
	}
	#system{
		position: absolute;
		top: 10px;
		right: 10px;
		display: inline;
	}
	#showsys, #syscmd input {
		float: right;
	}
	#debug{
		position: absolute;
		top: 10px;
		left: 200px;
		background-color: white;
	}
	.icon {
		width:50px;
		height:50px;
		margin-left: 10px;
		margin-right: 10px;
	}
	#reboot_button, #shutdown_button {
		width: auto;
		height: 20px;
		border-radius: 5px;
		padding-left: 20px;
		padding-right: 20px;
		margin-top: 20px;
		border-style: none;
		background-color: rgb(255, 51, 0);
	}
  </style>
  
  
</head>

<body onload="setTimeout('init(0, 25, 1);', 100);">
  <img id="mjpeg_dest" src="/img/loading.jpg">
  
  <div id="camera">

	<a id="video_button"><img class="icon" src="/img/video-1.png"></a>
	<a id="image_button"><img class="icon" src="/img/camera-1.png"></a>
	<a id="timelapse_button"><img class="icon" src="/img/timelapse-1.png"></a>

  </div>
  
  <a id="download" href="preview.php"><img class="icon" src="/img/download.png"></a>
  
  <div id="system">
      <a id="showsys"><img class="icon" src="/img/power.png"></a><br>
	  
	  <div id="syscmd" style="display:none;">
		  <input id="reboot_button" type="button" value="reboot" onclick="sys_reboot();" ><br><br><br>
		  <input id="shutdown_button" type="button" value="shutdown" onclick="sys_shutdown();" >
	  </div>
  </div>
  
  <div id="boundary"><div id="ctrlrod"></div></div>
  <p id="debug"></p>
  <div id="slider"></div>
  
    <script>
      $("#ctrlrod").draggable ({
        containment : "#boundary",
		revert: "invalid",
		revertDuration: 10,
		drag: function() {
			$("#debug").text($("#ctrlrod").css("left") + ":" + $("#ctrlrod").css("top"));
			if (Number($("#ctrlrod").css("left").replace("px", "")) < 120) {
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: 'http://192.168.201.55:8080/doStuff.py?q=w',
				});		
			} else {
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: 'http://192.168.201.55:8080/doStuff.py?q=g',
				});			
			}
		},
		stop: function () {
			$("#debug").text($("#ctrlrod").css("left") + ":" + $("#ctrlrod").css("top"));
			$.ajax({
				type: 'GET',
				dataType: 'jsonp',
				url: 'http://192.168.201.55:8080/doStuff.py?q=s',
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
			console.log($( "#slider" ).slider( "value" )-p0)
			$("#debug").text($( "#slider" ).slider( "value" ));
			
			if ($( "#slider" ).slider( "value" ) % 2 == 1) {
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: 'http://192.168.201.55:8080/doStuff.py?q=w',
				});				
			} else {
				$.ajax({
					type: 'GET',
					dataType: 'jsonp',
					url: 'http://192.168.201.55:8080/doStuff.py?q=s',
				});				
			}
			
		}
	  });
	  
	  $("#showsys").on('click', function() {
		   if ($( "#syscmd" ).css( "display" ) == "none") {
			   $( "#syscmd" ).css( "display", "block" ) 
		   } else if ($( "#syscmd" ).css( "display" ) == "block") {
			   $( "#syscmd" ).css( "display", "none" ) 
		   }
		});
		
    </script>
	
	
</body>

</html>