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
  <script src="js/md5.js"></script>  
</head>

<body onload="setTimeout('init(0, 25, 1);', 100);">
	
	
	<div id="CtrlPwd"  style="display:block;">
		Type password to control this ROV: <br>
		<input type="text" id="ctrlpwd">
		<input type="submit" onclick="pwd()" value="Submit">
	</div>
	
	<img id="mjpeg_dest" src="img/loading.jpg"  style="display:none;">
	
	<div id="CtrlPannel"  style="display:none;">
		<div id="camera">
			<a id="video_button"><img class="icon" src="img/video-1.png"></a>
			<a id="image_button"><img class="icon" src="img/camera-1.png"></a>
			<a id="timelapse_button"><img class="icon" src="img/timelapse-1.png"></a>
			<a id="led_button"><img class="icon" src="img/led-1.png"></a>
		</div>
		
		<a id="download" href="preview.php"><img class="icon" src="img/download.png"></a>
<!--		
		<div id="system">
			<a id="showsys"><img class="icon" src="img/power.png"></a><br>
			<div id="syscmd" style="display:none;">
				<input id="reboot_button" type="button" value="reboot" onclick="sys_reboot();" ><br><br><br>
				<input id="shutdown_button" type="button" value="shutdown" onclick="sys_shutdown();" >
			</div>
		</div>
-->		


		<select id="drivemode">
  			<option value="free">自由模式</option>
  			<option value="comp">定向定速</option>
  			<option value="yaw">原地转向</option>
		</select>
		
		<form id="powerscale">
		    <label class="radio-inline">
		      <input type="radio" name="optradio">Option 1
		    </label>
		    <label class="radio-inline">
		      <input type="radio" name="optradio">Option 2
		    </label>
		</form>

		<div id="boundary"><div id="ctrlrod"></div></div>
		<div id="depth_slider"></div>
		
		<p id="temperature"></p>		
		<p id="depth_current"></p>
		<p id="depth_target"></p>
		<p id="heading_current"></p>
		<p id="heading_target"></p>
		<p id="pwm_target"></p>		
	
	</div>

	<script src="js/ctrl.js"></script>
</body>

</html>
