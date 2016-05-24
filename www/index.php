<!DOCTYPE html>
<html>
   <head>
      <title>RPi ROV</title>
      <script src="js/script.js"></script>
      <script src="js/pipan.js"></script>
   </head>
   <body onload="setTimeout('init(0, 25, 1);', 100);">
		 <img id="mjpeg_dest" src="/loading.jpg">
         <div id="main-buttons" style="display:block;" >
            <input id="video_button" type="button" class="btn btn-primary">
            <input id="image_button" type="button" class="btn btn-primary">
            <input id="timelapse_button" type="button" class="btn btn-primary">
            <input id="halt_button" type="button" class="btn btn-danger">
			<a href="preview.php" class="btn btn-default">Download Videos and Images</a>
         </div
         <div class="panel-group" id="accordion" style="display:block;" >
			<input id="shutdown_button" type="button" value="shutdown system" onclick="sys_shutdown();" class="btn btn-danger">
			<input id="reboot_button" type="button" value="reboot system" onclick="sys_reboot();" class="btn btn-danger">
         </div>
   </body>
</html>
