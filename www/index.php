<!DOCTYPE html>
<html>

<head>
  <title>RPi ROV</title>
  <script src="js/script.js"></script>
  <script src="js/pipan.js"></script>
  
      
    <script src="http://code.jquery.com/jquery-1.10.2.js"></script>
    <script src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
	<style>
	#boundary {
	  position: absolute;
	  width: 300px;
	  height: 300px;
	  border-radius: 150px;
	  background-color: rgb(192,192,192);
	  opacity: 0.2;
	}

	#ctrlrod {
	z-index: 99;
	  position: relative;
	  top:135px;
	  left:135px;
	  width: 30px;
	  height: 30px;
	  border-radius: 15px;
	  background-color: red;

	}
  </style>
  
</head>

<body onload="setTimeout('init(0, 25, 1);', 100);">
  <img id="mjpeg_dest" src="/loading.jpg">
  <input id="video_button" type="button" class="btn btn-primary">
  <input id="image_button" type="button" class="btn btn-primary">
  <input id="timelapse_button" type="button" class="btn btn-primary">
  <input id="halt_button" type="button" class="btn btn-danger">
  <a href="preview.php" class="btn btn-default">Download Videos and Images</a>
  <input id="reboot_button" type="button" value="reboot system" onclick="sys_reboot();" class="btn btn-danger">
  <input id="shutdown_button" type="button" value="shutdown system" onclick="sys_shutdown();" class="btn btn-danger">
  
  <div id="boundary"><div id="ctrlrod"></div></div>
  <p id="debug"></p>

    <script>
      $("#ctrlrod").draggable ({
        containment : "#boundary",
		revert: "invalid",
		revertDuration: 10,
		drag: function() {
		    console.log($( this ).css( "left" ))
			console.log($( this ).css( "top" ))
			document.getElementById("debug").innerHTML = $( this ).css( "left" ) + ":" + $( this ).css( "top" );
		},
		stop: function () {
		    console.log($( this ).css( "left" ))
			console.log($( this ).css( "top" ))
			document.getElementById("debug").innerHTML = $( this ).css( "left" ) + ":" + $( this ).css( "top" );
        }
      });
	  
    </script>
	
	
</body>

</html>