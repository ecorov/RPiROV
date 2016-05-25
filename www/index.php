<!DOCTYPE html>
<html>

<head>
  <title>RPi ROV</title>
  <script src="js/script.js"></script>
  <script src="js/pipan.js"></script>
  
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css"> 
    <script src="http://code.jquery.com/jquery-1.10.2.js"></script>
    <script src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
	<script src="http://cdnjs.cloudflare.com/ajax/libs/jqueryui-touch-punch/0.2.2/jquery.ui.touch-punch.min.js"></script>
	<style>
	body {
		margin: 0px;
	}
	#boundary {
	  position: absolute;
	  width: 300px;
	  height: 300px;
	  border-radius: 150px;
	  background-color: rgb(250,250,250);
	  opacity: 0.2;
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
		height: 400px;
		bottom: 10px;
		left:10px;		
	}

	#download {
		position: absolute;
		top: 10px;
		left:10px;	
	}
	
	#camera{
		position: absolute;
		bottom: 10px;
		left: 200px;
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
	#debug{
		position: absolute;
		top: 10px;
		left: 200px;
		background-color: white;
	}
	.icon {
		width:50px;
		height:50px;
	}
  </style>
  
  
</head>

<body onload="setTimeout('init(0, 25, 1);', 100);">
  <img id="mjpeg_dest" src="/img/loading.jpg">
  
  <div id="camera">
  <input id="video_button" type="button" class="btn btn-primary">
  <input id="image_button" type="button" class="btn btn-primary">
  <input id="timelapse_button" type="button" class="btn btn-primary">
  </div>
  
  <a id="download" href="preview.php"><img class="icon" src="/img/download.png"></a>
  
  <div id="system">
      <a id="showsys"><img class="icon" src="/img/power.png"></a>
	  
	  <div id="syscmd" style="display:none;">
		  <input id="halt_button" type="button" class="btn btn-danger">
		  <input id="reboot_button" type="button" value="reboot system" onclick="sys_reboot();" class="btn btn-danger">
		  <input id="shutdown_button" type="button" value="shutdown system" onclick="sys_shutdown();" class="btn btn-danger">
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
			document.getElementById("debug").innerHTML = $( this ).css( "left" ) + ":" + $( this ).css( "top" );
		},
		stop: function () {
			document.getElementById("debug").innerHTML = $( this ).css( "left" ) + ":" + $( this ).css( "top" );
        }
      });
	  
	  
	  $( "#slider" ).slider({
		orientation: "vertical",
		min:0,
		max:100,
		value: 50,
		slide: function() {
		console.log($( "#slider" ).slider( "value" ))
		document.getElementById("debug").innerHTML = $( "#slider" ).slider( "value" );
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