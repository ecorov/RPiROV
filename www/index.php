<!DOCTYPE html>
<html>

<head>
  <title>RPi ROV</title>
	<link rel="stylesheet" href="css/jquery-ui.css"> 
	<link rel="stylesheet" href="css/style.css"> 	
	<script src="js/jquery-1.10.2.js"></script>
	<script src="js/jquery-ui.js"></script>
	<script src="js/jquery.ui.touch-punch.min.js"></script>
	<script src="js/script.js"></script>
	<script src="js/pipan.js"></script>  
</head>

<body onload="setTimeout('init(0, 25, 1);', 100);">
  <img id="mjpeg_dest" src="img/loading.jpg">
  
  <div id="camera">
		<a id="video_button"><img class="icon" src="img/video-1.png"></a>
		<a id="image_button"><img class="icon" src="img/camera-1.png"></a>
		<a id="timelapse_button"><img class="icon" src="img/timelapse-1.png"></a>
  </div>
  
  <a id="download" href="preview.php"><img class="icon" src="img/download.png"></a>
  
  <div id="system">
    <a id="showsys"><img class="icon" src="img/power.png"></a><br>
	  <div id="syscmd" style="display:none;">
		  <input id="reboot_button" type="button" value="reboot" onclick="sys_reboot();" ><br><br><br>
		  <input id="shutdown_button" type="button" value="shutdown" onclick="sys_shutdown();" >
	  </div>
  </div>
  
  <div id="boundary"><div id="ctrlrod"></div></div>
  <p id="debug"></p>
  <div id="slider"></div>
	<a id="led_button"><img class="icon" src="img/led-1.png"></a>
	
	
	<script src="js/ctrl.js"></script>
</body>

</html>