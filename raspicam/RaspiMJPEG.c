/*
Copyright (c) 2013, Broadcom Europe Ltd
Copyright (c) 2013, Silvan Melchior
Copyright (c) 2013, James Hughes
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/**
 * \file RaspiMJPEG.c
 * Command line program to capture a camera video stream and encode it to file.
 * Also optionally stream a preview of current camera input with MJPEG.
 *
 * \date 9th Aprl 2015
 * \Author: Silvan Melchior / Robert Tidey
 *
 * Description
 *
 * RaspiMJPEG is an OpenMAX-Application based on the mmal-library, which is
 * comparable to and inspired by RaspiVid and RaspiStill. RaspiMJPEG can record
 * 1080p 30fps videos and 5 Mpx images into a file. But instead of showing the
 * preview on a screen, RaspiMJPEG streams the preview as MJPEG into a file.
 * The update-rate and the size of the preview are customizable with parameters
 * and independent of the image/video. Once started, the application receives
 * commands with a unix-pipe and showes its status on stdout and writes it into
 * a status-file. The program terminates itself after receiving a SIGINT or
 * SIGTERM.
 */

#include "RaspiMJPEG.h"

MMAL_STATUS_T status;
MMAL_COMPONENT_T *camera = 0, *jpegencoder = 0, *jpegencoder2 = 0, *h264encoder = 0, *resizer = 0, *null_sink = 0, *splitter = 0;
MMAL_CONNECTION_T *con_cam_pre = 0, *con_spli_res = 0, *con_spli_h264 = 0, *con_res_jpeg = 0, *con_cam_h264 = 0, *con_cam_jpeg = 0;
FILE *jpegoutput_file = NULL, *jpegoutput2_file = NULL, *h264output_file = NULL, *status_file = NULL, *vector_file = NULL;
MMAL_POOL_T *pool_jpegencoder = 0, *pool_jpegencoder_in = 0, *pool_jpegencoder2 = 0, *pool_h264encoder = 0;
char *cb_buff = NULL;
//pthread_mutex_t	v_mutex;

char header_bytes[29];
int cb_len, cb_wptr, cb_wrap;
int iframe_buff[IFRAME_BUFSIZE], iframe_buff_wpos, iframe_buff_rpos, header_wptr;
unsigned int tl_cnt=0, mjpeg_cnt=0, image_cnt=0, image2_cnt=0, lapse_cnt=0, video_cnt=0, video_stoptime=0, video_frame;
char *filename_recording = 0, *filename_image = 0;
unsigned char timelapse=0, running=1, autostart=1, idle=0, a_error=0, v_capturing=0, i_capturing=0, v_boxing=0;
unsigned char buffering=0, buffering_toggle=0;
char *box_files[MAX_BOX_FILES];
int box_head=0;
int box_tail=0;
char *cfg_strd[KEY_COUNT + 1];
char *cfg_stru[KEY_COUNT + 1];
long int cfg_val[KEY_COUNT + 1];

char *cfg_key[] ={
   "annotation","anno_background",
   "anno3_custom_background_colour","anno3_custom_background_Y","anno3_custom_background_U","anno3_custom_background_V",
   "anno3_custom_text_colour","anno3_custom_text_Y","anno3_custom_text_U","anno3_custom_text_V","anno_text_size",
   "sharpness","contrast","brightness","saturation","iso",
   "metering_mode","video_stabilisation","exposure_compensation","exposure_mode","white_balance","image_effect",
   "autowbgain_r","autowbgain_b",
   "colour_effect_en","colour_effect_u","colour_effect_v",
   "rotation","hflip","vflip",
   "sensor_region_x","sensor_region_y","sensor_region_w","sensor_region_h",
   "shutter_speed","raw_layer",
   "width","quality","divider",
   "video_width","video_height","video_fps","video_bitrate","video_buffer",
   "MP4Box","MP4Box_fps","boxing_path",
   "image_width","image_height","image_quality","tl_interval",
   "base_path","preview_path","image_path","lapse_path","video_path","status_file","control_file","media_path","macros_path","subdir_char",
   "thumb_gen","autostart","motion_detection","motion_file","vector_preview","vector_mode", "motion_external",
   "motion_noise","motion_threshold","motion_image","motion_startframes","motion_stopframes","motion_pipe","motion_clip",
   "user_config","log_file","watchdog_interval","watchdog_errors","h264_buffers","callback_timeout",
   "error_soft", "error_hard", "end_img", "start_vid", "end_vid", "end_box", "do_cmd",
   "camera_num","stat_pass","user_annotate"
};


void term (int signum) {
   running = 0;
}

void set_counts() {
   image2_cnt = findNextCount(cfg_stru[c_image_path], "it");
   video_cnt = findNextCount(cfg_stru[c_video_path], "v");
}

int getKey(char *key) {
   int i;
   for(i=0; i < KEY_COUNT; i++) {
      if(strcmp(key, cfg_key[i]) == 0) {
         return i;
      }
   }
   return KEY_COUNT;
}

void addValue(int keyI, char *value, int both){
   
   free(cfg_stru[keyI]);
   cfg_stru[keyI] = 0;
   if (both) {free(cfg_strd[keyI]);cfg_strd[keyI] = 0;}
   
   if (value == NULL || strlen(value) == 0) {
      cfg_val[keyI] = 0;
   } else {
      int val=strtol(value, NULL, 10);
      asprintf(&cfg_stru[keyI],"%s", value);
      if (both) {
         asprintf(&cfg_strd[keyI],"%s", value);
      }
      if (strcmp(value, "true") == 0)
         val = 1;
      else if (strcmp(value, "false") == 0)
         val = 0;
      switch(keyI) {
         case c_autostart:
            if(strcmp(value, "idle") == 0) {
               val = 0;
               idle = 1;
            }else if(strcmp(value, "standard") == 0) { 
               val = 1;
               idle = 0;
            };
            updateStatus();
            break;
         case c_MP4Box:
            if(strcmp(value, "background") == 0)
               val = 2;
      }
      cfg_val[keyI] = val;
   }
}

void addUserValue(int key, char *value){
   printLog("Change: %s = %s\n", cfg_key[key], value);
   addValue(key, value, 0);
}

void saveUserConfig(char *cfilename) {
   FILE *fp;
   int i;
   fp = fopen(cfilename, "w");
   if(fp != NULL) {
      for(i = 0; i < KEY_COUNT; i++) {
         if(strlen(cfg_key[i]) > 0) {
            if(cfg_stru[i] != 0 && cfg_strd[i] != 0 && strcmp(cfg_strd[i], cfg_stru[i]) != 0) {
               fprintf(fp, "%s %s\n", cfg_key[i], cfg_stru[i]);
            } else if (cfg_stru[i] != 0 && cfg_strd[i] == 0) {
               fprintf(fp, "%s %s\n", cfg_key[i], cfg_stru[i]);
            } else if (cfg_stru[i] == 0 && cfg_strd[i] != 0) {
               fprintf(fp, "%s\n", cfg_key[i]);
            }
         }
      }
      fclose(fp);
   }
}

void read_config(char *cfilename, int type) {
   FILE *fp;
   int length;
   unsigned int len = 0;
   char *line = NULL;
   char *value = NULL;
   int key;

   fp = fopen(cfilename, "r");
   if(fp != NULL) {
      while((length = getline(&line, &len, fp)) != -1) {
         if (length > 3 && *line != '#') {
            line[length-1] = 0;
            value = strchr(line, ' ');
            if (value != NULL) {
               // split line into key, value
               *value = 0;
               value++;
            }
            key = getKey(line);
            if (key < KEY_COUNT) {
               if (key != c_annotation) {
                  value = trim(value);
               }
               addValue(key, value, type);
            }
         }
      }
      if(line) free(line);
   }   
}

void monitor() {
   while(1) {
      int pid = fork();
      switch(pid) {
         case -1: //error
            error("fork failed", 1);
         case 0: //child
            return; //continue to execute the code from main
         default: //parent
            printLog("start monitoring for pid: %d\n", pid);
            int child_status;
            //wait for child process to terminate
            wait(&child_status);
            //child pid has terminated
            sleep(5);
      }
   }
}
int main (int argc, char* argv[]) {
   monitor();
   int i, fd, length;
   int watchdog = 0, watchdog_errors = 0;
   int onesec_check = 0;
   time_t last_pv_time = 0, pv_time;
   char readbuf[MAX_COMMAND_LEN];

   bcm_host_init();
   //
   // read arguments
   //
   for(i=1; i<argc; i++) {
      if(strcmp(argv[i], "--version") == 0) {
         printf("RaspiMJPEG Version %s\n", VERSION);
         exit(0);
      }
      else if(strcmp(argv[i], "-md") == 0) {
         cfg_val[c_motion_detection] = 1;
      }
   }

   //default base media path
   asprintf(&cfg_stru[c_media_path], "%s", "/var/www/media");
   
   //
   // read configs and init
   //
   read_config("/etc/raspimjpeg", 1);
   if (cfg_stru[c_user_config] != 0)
      read_config(cfg_stru[c_user_config], 0);

   createPath(cfg_stru[c_log_file], cfg_stru[c_base_path]);
   if (cfg_stru[c_boxing_path] != NULL) {
      char *bpath;
      asprintf(&bpath, "%s/temp", cfg_stru[c_boxing_path]);
      createPath(bpath, cfg_stru[c_base_path]);
      free(bpath);
   }
   
   printLog("RaspiMJPEG Version %s\n", VERSION);
   
   if(cfg_val[c_autostart]) start_all(0);

   //
   // run
   //
   if(cfg_val[c_autostart]) {
      if(cfg_stru[c_control_file] != 0){
         printLog("MJPEG streaming, ready to receive commands\n");
         //kick off motion detection at start if required.
         if(cfg_val[c_motion_detection] && cfg_val[c_motion_external]) {
            printLog("Autostart external motion kill any runnng motion\n");
            if(system("killall motion") == -1) error("Could not stop external motion", 1);
            sleep(1);
            printLog("Autostart external motion start external motion\n");
            if(system("motion") == -1) error("Could not start external motion", 1);
         }
      } else {
         printLog("MJPEG streaming\n");
      }
   }
   else {
      if(cfg_stru[c_control_file] != 0) printLog("MJPEG idle, ready to receive commands\n");
      else printLog("MJPEG idle\n");
   }

   updateStatus();
 
   struct sigaction action;
   memset(&action, 0, sizeof(struct sigaction));
   action.sa_handler = term;
   sigaction(SIGTERM, &action, NULL);
   sigaction(SIGINT, &action, NULL);
   
   //Clear out anything in FIFO first
   do {
      fd = open(cfg_stru[c_control_file], O_RDONLY | O_NONBLOCK);
      if(fd < 0) error("Could not open PIPE", 1);
      fcntl(fd, F_SETFL, 0);
      length = read(fd, readbuf, 60);
      close(fd);
   } while (length != 0); 
  
  //Send restart signal to scheduler
  send_schedulecmd("9");
   // Main forever loop
   if(cfg_stru[c_control_file] != 0) {
      fd = open(cfg_stru[c_control_file], O_RDONLY | O_NONBLOCK);
      if(fd < 0) error("Could not open PIPE", 1);
      fcntl(fd, F_SETFL, 0);
   } else {
      error("No PIPE defined", 1);
   }
   printLog("Starting command loop\n");
   while(running) {
      length = read(fd, readbuf, MAX_COMMAND_LEN -2);

      if(length) {
         process_cmd(readbuf, length);
      }

      if(timelapse) {
         tl_cnt++;
         if(tl_cnt >= cfg_val[c_tl_interval]) {
            if(i_capturing == 0) {
               capt_img();
               tl_cnt = 0;
            }
         }
      }
      // check to see if image preview changing
      if (!idle && cfg_val[c_watchdog_interval] > 0) {
         if(watchdog++ > cfg_val[c_watchdog_interval]) {
            watchdog = 0;
            pv_time = get_mtime(cfg_stru[c_preview_path]);
            if (pv_time == 0) {
               watchdog_errors++;
            } else {
               if (pv_time > last_pv_time) {
                  watchdog_errors = 0;
               } else {
                  watchdog_errors++;
               }
               last_pv_time = pv_time;
            }
            if (watchdog_errors >= cfg_val[c_watchdog_errors]) {
               printLog("Watchdog detected problem. Stopping");
               running = 0;
            }
         }
      } else {
         watchdog_errors = 0;
      }
      if (++onesec_check >= 10) {
         //run check on background boxing every 10 ticks and check for video timer if capturing
         onesec_check = 0;
         // 4.9 compiler seems to want a print after the box finish to get input FIFO working again
         if (check_box_files()) printLog("Removed item from Box Queue\n");
         // Check to make sure image operation not stuck (no callback) if enabled
         if ((cfg_val[c_callback_timeout] > 0) && i_capturing) {
            i_capturing--;
            if (i_capturing == 0) {
               printLog("Image capture timed out %s\n", filename_image);
               close_img(0);
            }
         }
         if (v_capturing && video_stoptime > 0) {
            if (time(NULL) >= video_stoptime) {
               printLog("Stopping video from timer\n");
               stop_video(0);
            }
         }
      }
      usleep(100000);
   }
         
   close(fd);
   if(system("killall motion") == -1) error("Could not stop external motion", 1);
  
   printLog("SIGINT/SIGTERM received, stopping\n");
   //
   // tidy up
   //
   if(!idle) stop_all();
   return 0;
}