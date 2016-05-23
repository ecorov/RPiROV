<!DOCTYPE html>
<html>
   <head>
      <meta name="viewport" content="width=550, initial-scale=1">
      <title>RPi ROV</title>
      <script src="js/script.js"></script>
      <script src="js/pipan.js"></script>
   </head>
   <body onload="setTimeout('init(0, 25, 1);', 100);">

      <div class="container-fluid text-center liveimage">
   
		 <div><img id="mjpeg_dest" <?php if(file_exists("pipan_on")) echo "ontouchstart=\"pipan_start()\""; ?> onclick="toggle_fullscreen(this);" src="/loading.jpg"></div>

         <div id="main-buttons" style="display:block;" >
            <input id="video_button" type="button" class="btn btn-primary">
            <input id="image_button" type="button" class="btn btn-primary">
            <input id="timelapse_button" type="button" class="btn btn-primary">
            <input id="halt_button" type="button" class="btn btn-danger">
         </div>
      </div>
	  
      <div id="secondary-buttons" class="container-fluid text-center" style="display:block;" >
         <a href="preview.php" class="btn btn-default">Download Videos and Images</a>
      </div>
    
      <div class="container-fluid text-center">
         <div class="panel-group" id="accordion" style="display:block;" >
			<input id="shutdown_button" type="button" value="shutdown system" onclick="sys_shutdown();" class="btn btn-danger">
			<input id="reboot_button" type="button" value="reboot system" onclick="sys_reboot();" class="btn btn-danger">
         </div>
      </div>
   </body>
</html>
