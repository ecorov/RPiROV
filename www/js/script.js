//
// Shutdown
//
function sys_shutdown() {
  ajax_status.open("GET", "cmd_func.php?cmd=shutdown", true);
  ajax_status.send();
}

function sys_reboot() {
  ajax_status.open("GET", "cmd_func.php?cmd=reboot", true);
  ajax_status.send();
}


//
// Init
//

//
// MJPEG
//
var mjpeg_img;
var halted = 0;
var previous_halted = 99;
var mjpeg_mode = 0;
var preview_delay = 0;

function reload_img () {
  if(!halted) mjpeg_img.src = "cam_pic.php?time=" + new Date().getTime() + "&pDelay=" + preview_delay;
  else setTimeout("reload_img()", 500);
}

function error_img () {
  setTimeout("mjpeg_img.src = 'cam_pic.php?time=' + new Date().getTime();", 100);
}

function updatePreview(cycle)
{
	if (mjpegmode && cycle !== undefined && cycle == true)
	{
		mjpeg_img.src = "/img/updating.jpg";
		setTimeout("mjpeg_img.src = \"cam_pic_new.php?time=\" + new Date().getTime()  + \"&pDelay=\" + preview_delay;", 1000);
		return;
	}
	
	if (previous_halted != halted)
	{
		if(!halted)
		{
			mjpeg_img.src = "cam_pic_new.php?time=" + new Date().getTime() + "&pDelay=" + preview_delay;			
		}
		else
		{
			mjpeg_img.src = "/img/unavailable.jpg";
		}
	}
	previous_halted = halted;
}


function init(mjpeg, video_fps, divider) {

  mjpeg_img = document.getElementById("mjpeg_dest");
  preview_delay = Math.floor(divider / Math.max(video_fps,1) * 1000000);
  if (mjpeg) {
    mjpegmode = 1;
  } else {
     mjpegmode = 0;
     mjpeg_img.onload = reload_img;
     mjpeg_img.onerror = error_img;
     reload_img();
  }
  reload_ajax("");
}


//
// Ajax Status
//
var ajax_status;

if(window.XMLHttpRequest) {
  ajax_status = new XMLHttpRequest();
}
else {
  ajax_status = new ActiveXObject("Microsoft.XMLHTTP");
}


ajax_status.onreadystatechange = function() {
  if(ajax_status.readyState == 4 && ajax_status.status == 200) {

    if(ajax_status.responseText == "ready") {
	//	$('#video_button img').attr('src','/img/video-1.png');
	//	$('#video_button img').click(function() {send_cmd("ca 1")});
 
	  document.getElementById("video_button").disabled = false;
      document.getElementById("video_button").value = "record video start";

      document.getElementById("video_button").onclick = function() {send_cmd("ca 1");};
      document.getElementById("image_button").disabled = false;
      document.getElementById("image_button").value = "record image";
      document.getElementById("image_button").onclick = function() {send_cmd("im");};
      document.getElementById("timelapse_button").disabled = false;
      document.getElementById("timelapse_button").value = "timelapse start";
      document.getElementById("timelapse_button").onclick = function() {send_cmd("tl 1");};
      halted = 0;
	  updatePreview();
    } else if(ajax_status.responseText == "md_ready") {
      document.getElementById("video_button").disabled = true;
      document.getElementById("video_button").value = "record video start";
      document.getElementById("video_button").onclick = function() {};
      document.getElementById("image_button").disabled = false;
      document.getElementById("image_button").value = "record image";
      document.getElementById("image_button").onclick = function() {send_cmd("im");};
      document.getElementById("timelapse_button").disabled = true;
      document.getElementById("timelapse_button").value = "timelapse start";
      document.getElementById("timelapse_button").onclick = function() {};
      halted = 0;
	  updatePreview();
    } else if(ajax_status.responseText == "video") {
		//$('#video_button img').attr('src','/img/video-0.png');
		//$('#video_button img').click(function() {send_cmd("ca 0")});
		
      document.getElementById("video_button").disabled = false;
      document.getElementById("video_button").value = "record video stop";
      document.getElementById("video_button").onclick = function() {send_cmd("ca 0");};
      document.getElementById("image_button").disabled = false;
      document.getElementById("image_button").value = "record image";
      document.getElementById("image_button").onclick = function() {send_cmd("im");};
      document.getElementById("timelapse_button").disabled = true;
      document.getElementById("timelapse_button").value = "timelapse start";
      document.getElementById("timelapse_button").onclick = function() {};
    } else if(ajax_status.responseText == "timelapse") {
      document.getElementById("video_button").disabled = true;
      document.getElementById("video_button").value = "record video start";
      document.getElementById("video_button").onclick = function() {};
      document.getElementById("image_button").disabled = true;
      document.getElementById("image_button").value = "record image";
      document.getElementById("image_button").onclick = function() {};
      document.getElementById("timelapse_button").disabled = false;
      document.getElementById("timelapse_button").value = "timelapse stop";
      document.getElementById("timelapse_button").onclick = function() {send_cmd("tl 0");};
    } else if(ajax_status.responseText == "md_video") {
      document.getElementById("video_button").disabled = true;
      document.getElementById("video_button").value = "record video start";
      document.getElementById("video_button").onclick = function() {};
      document.getElementById("image_button").disabled = false;
      document.getElementById("image_button").value = "record image";
      document.getElementById("image_button").onclick = function() {send_cmd("im");};
      document.getElementById("timelapse_button").disabled = true;
      document.getElementById("timelapse_button").value = "timelapse start";
      document.getElementById("timelapse_button").onclick = function() {};
    } else if(ajax_status.responseText == "image") {
      document.getElementById("video_button").disabled = true;
      document.getElementById("video_button").value = "record video start";
      document.getElementById("video_button").onclick = function() {};
      document.getElementById("image_button").disabled = true;
      document.getElementById("image_button").value = "recording image";
      document.getElementById("image_button").onclick = function() {};
      document.getElementById("timelapse_button").disabled = true;
      document.getElementById("timelapse_button").value = "timelapse start";
      document.getElementById("timelapse_button").onclick = function() {};
    } else if(ajax_status.responseText == "halted") {
      document.getElementById("video_button").disabled = true;
      document.getElementById("video_button").value = "record video start";
      document.getElementById("video_button").onclick = function() {};
      document.getElementById("image_button").disabled = true;
      document.getElementById("image_button").value = "record image";
      document.getElementById("image_button").onclick = function() {};
      document.getElementById("timelapse_button").disabled = true;
      document.getElementById("timelapse_button").value = "timelapse start";
      document.getElementById("timelapse_button").onclick = function() {};
      halted = 1;
	  updatePreview();
    } else if(ajax_status.responseText.substr(0,5) == "Error") {
	  alert("Error in RaspiMJPEG: " + ajax_status.responseText.substr(7) + "\nRestart RaspiMJPEG or the whole RPi.");
	}
    reload_ajax(ajax_status.responseText);
  }
}

function reload_ajax (last) {
  ajax_status.open("GET","status_mjpeg.php?last=" + last,true);
  ajax_status.send();
}

//
// Ajax Commands
//
var ajax_cmd;

if(window.XMLHttpRequest) {
  ajax_cmd = new XMLHttpRequest();
}
else {
  ajax_cmd = new ActiveXObject("Microsoft.XMLHTTP");
}

function send_cmd (cmd) {
  ajax_cmd.open("GET","cmd_pipe.php?cmd=" + cmd,true);
  ajax_cmd.send();
}

function update_preview_delay() {
   var video_fps = parseInt(document.getElementById("video_fps").value);
   var divider = parseInt(document.getElementById("divider").value);
   preview_delay = Math.floor(divider / Math.max(video_fps,1) * 1000000);
}
