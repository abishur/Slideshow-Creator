# Slideshow-Creator
 Matthew Bennett (Life With Matthew) (2019-09-10)

 This script takes in images from a folder and makes a slideshow video from the images in a specific folder using ffmpeg.
 Make sure you have ffmpeg installed before running.
 
 Standard usage:
     py slideshow.py -i VIDEO.MP4
This will take a video in the same folder and create a slideshow video named outvideo.mp4 with each image lasting 3 seconds and a crossfade transition between each image.

To specify a video from a different directory or output to a different directory simply provide the full path as part of the -i parameter:
     py slideshow.py -i C:\FULL\PATH\TO\VIDEO.mp4 -o C:\DIFFERENT\PATH\TO\OUTPUT.MP4

Slideshow video will by default be the same height and width of the source video, but this can be resized by specifying -w and -h parameters:
    py slideshow.py -i VIDEO.MP4 -w 1920 -h 1080

How long each image will be displayed can be set with the -d flag.  This variable must be a whole number.  So to have a slideshow where each image is displayed for 5 seconds:
    py slideshow.py -i VIDEO.mp4 -d 5

The transition duration can also be manually set, with -c flag.  Though if manually set the slideshow video length will most likely not be the same length as the original video. This command will create a slideshow where each image is shown for 5 seconds and each transition last for 2 seconds
    py slideshow.py -i VIDEO.mp4 -d 5 -c 2

All pictures created will be automatically deleted unless the -k flag is listed in which case the pictures will remain even after the slideshow video is created.   This command will create a slideshow where each image is shown for 5 seconds and each transition last for 2 seconds and will NOT delete the pictures when finished
    py slideshow.py -i VIDEO.mp4 -d 5 -c 2 -k

Currently there are two transition types.  By default a crossfade transition will be used but by using the -t 0 flag then a hard cut to the next picture will be used instead.  This command will create a slideshow where each image is shown for 5 seconds with no transition between each image
    py slideshow.py -i VIDEO.mp4 -d 5 -c 2 -t 0
