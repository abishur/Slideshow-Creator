# Matthew Bennett (Life With Matthew) (2019-09-10)

# This script takes in images from a folder and makes a slideshow video from the images in a specific folder using ffmpeg.
# Make sure you have ffmpeg installed before running.
# Standard usage:
    # py slideshow.py -i VIDEO.MP4

import argparse
import os
import subprocess
import json
import sys
import platform
import fnmatch
from subprocess import Popen,PIPE
import math


#Update revisions for sanity's sake please future me!
revisionNumber=1.7

#This line and the function that follows will sort images correctly
#instead of putting 1000 between 100 and 101 or 1110 between 111 and 112
#numbers = re.compile(r'(\d+)')
#def numericalSort(value):
#    parts = numbers.split(value)
#    parts[1::2] = map(int, parts[1::2])
#    return parts
    
#This function searches a directory for a specific file name.
def find(name, path):
    for root, dirs, files, in os.walk(path):
        if name in files:
            return os.path.join(root,name)
            
def get_sec(time_str):
    #Get Seconds from time.
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def __name__ == "__main__":
    #Parse through the command line arguments
    #Note that the only required input is the FilePattern.  Everything else will default to some value.
    #It probably won't be the value you want, but it will be *A* value.
    try:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-?', '--help', action="help", help="Displays Help Information")
        parser.add_argument('-e', '--verbose', action='store_true', help="increase output verbosity")
        parser.add_argument('-v', '--version', action='store_true', help="display current version")
        parser.add_argument('-f', '--ffmpegpath', dest='FFmpegPath', default=os.getcwd(), help="specifies the location of ffmpeg, necessary if ffmpeg is not in defined in your PATH")
        parser.add_argument('-i', '--inputfile', dest='InputPath', required=True, help="specifies the video file to turn into a slide show")
        parser.add_argument('-o', '--outputpath', dest='OutputPath', default=os.getcwd(), help="specifies the location and filename of the directory to place video in")
        parser.add_argument('-s', '--startnum', dest='StartNumber', default="0", help="optionally allows you start as a specific file number (as defined by filepattern)")
        parser.add_argument('-d', '--duration', dest='Duration', type=int, default=-1, help="specifies how long each picture should be shown, the default is automatically calculated.")
        parser.add_argument('-c', '--crossfade', dest='CrossFade', type=float, default=-1, help="specifies the length of the crossfade affect, the default is automatically calculated.")
        parser.add_argument('-h', '--height', dest='OutHeight', type=int, default=0, help="Specifies the output height.  defaults to input video's height")
        parser.add_argument('-w', '--width', dest='OutWidth', type=int, default=0, help="Specifies the output width.  defaults to input video's height")
        parser.add_argument('-r', '--framerate', dest='FrameRate', type=int, default=30, help="Specifies the output framerate.  Default is 30 fps")
        parser.add_argument('-t', '--transitiontype', dest='TransitionType', type=int, default=1, choices=[0,1], help="Specifies Image transition type.  0 = No transition, (Default)1 = Crossfade).")
        parser.add_argument('-k', '--keepfiles', dest='KeepFiles', action='store_true', help="When selected this will keep the pictures generated rather than deleting them when done.")
        #parser.add_argument('-b', '--bypass', dest=BypassPics, action='store_true', help="When selected this will bypass creating pictures from a video.")
        args = parser.parse_args()
    except SystemExit:
        print ("There was an error while trying to parse your arguments")
        print ("Please check your syntax and try again")
        sys.exit(0)
    
    #This block of code is responsible for confirming existence of FFmpeg
    #If FFmpeg is not in the current folder than common places for it will be search before failing.
    try:
        if (platform.system() == 'Windows'):
            ffmpegFind=find("ffmpeg.exe", args.FFmpegPath)
            if ffmpegFind is None:
                if args.verbose:
                    print ("Could not find ffmpeg.exe in current directory checking C:\\Program Files\\ffmpeg\\bin")
                ffmpegFind=find("ffmpeg.exe", "C:\\Program Files\\ffmpeg\\bin")
                if ffmpegFind is None:
                    if args.verbose:
                        print ("Could not find ffmpeg.exe in C:\\Program Files\\ffmpeg\\bin checking C:\\Program Files (x86)\\ffmpeg\\bin")
                    ffmpegFind=find("ffmpeg.exe", "C:\\Program Files (x86)\\ffmpeg\\bin")
                    if ffmpegFind is None:
                        print ("ffmpeg could not be found.  Please specify ffmpeg location using -p flag")
                        sys.exit(0)
                            
                    else:
                        if args.verbose:
                            print ("ffmpeg found, using ffmpeg in C:\\Program Files (x86)\\ffmpeg\\bin")
                        args.FFmpegPath="C:\\Program Files (x86)\\ffmpeg\\bin"
                else:
                    if args.verbose:
                        print ("ffmpeg found, using ffmpeg in C:\\Program Files\\ffmpeg\\bin")
                    args.FFmpegPath="C:\\Program Files\\ffmpeg\\bin"
        elif (platform.system() == 'Linux'):
            pass
            #fill this section of code in after testing on Linux
    except:
        print ("An error occured while confirming location of ffmpeg.exe")
        print ("Please confirm syntax of --ffmpegpath")
        sys.exit(0)
        
    #Display program version number and quit
    if args.version:
        print ("Currently on Revision: {0}".format(revisionNumber))
        sys.exit(0)
    
    #get the meta information from the file to turn into slideshow
    try:
        FFMPEG_PATH=args.FFmpegPath+'\\ffmpeg.exe'
        FFPROBE_PATH=args.FFmpegPath+'\\ffprobe.exe'
        jsondata = subprocess.check_output([FFPROBE_PATH,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        args.InputPath
        ])
    except:
        print ("An error occured while executing check on video file")
        print ("Please confirm existance of ffmpeg and ffprobe")
        sys.exit(0)
    
    #parse the results of ffprobe
    parsed = json.loads(jsondata)
    videoDuration = math.ceil(float(parsed['streams'][0]['duration']))
    if (args.OutHeight==0):
        args.OutHeight=parsed['streams'][0]['height']
    if (args.OutWidth==0):
        args.OutWidth=parsed['streams'][0]['width']
    
    #Place video's metadata information in appropriate variables
    videoFPS= parsed['streams'][0]['r_frame_rate'] #math.ceil(float(parsed['format']['tags']['MinSourceFps']))
    #maxVideoFPS= float(parsed['format']['tags']['MaxSourceFps'])
    FPSindx=videoFPS.index("/")
    FPSnumerator=int(videoFPS[:FPSindx])
    FPSdenominator=int(videoFPS[FPSindx+1:])
    videoFPS=round(FPSnumerator/FPSdenominator)
    
    #If Verbosity is enable display the working values of our variables and outputs of commands
    if args.verbose:
        print ("Verbosity is turned on")
    
    #When verbosity is turned on display the values of the variables and OS/Python information
    if args.verbose:
        print ("Expected Python version is 3.7.4 or greater")
        print ("Python version found is: {0}".format(sys.version.split('\n')))
        print ("Script is running on: {0}".format(platform.system()))
        print ("FFmpegPath is set to: {0}".format(args.FFmpegPath))
        print ("Input Path is set to: {0}".format(args.InputPath))
        print ("Output Path is set to: {0}".format(args.OutputPath))
        print ("FFmpeg will begin with image number: {0}".format(args.StartNumber))
        print ("Video Height is: {0}".format(args.OutHeight))
        print ("Video Width is: {0}".format(args.OutWidth))
        print ("Video FPS is: {0}".format(videoFPS))
        print ("Slide Duration is set to: {0} seconds".format(args.Duration))
        print ("Video Duration is: {0} seconds".format(videoDuration))
        print ("Slideshow Video FrameRate is: {0} seconds".format(args.FrameRate))
        print ("Slide Transition Type is set to: {0}".format(args.TransitionType))
        
    #If a Duration has not been set assume a 3 second duration
    if (args.Duration == -1):
        args.Duration = 3
       
    #turn video file into images using desired image duration rate
    p2 = subprocess.Popen([FFMPEG_PATH,
    '-i', args.InputPath,
    '-vf', 'select=not(mod(n\,{0}))'.format(videoFPS*args.Duration),
    '-vsync', 'vfr',
    '-hide_banner',
    '{0}\img_%03d.png'.format(args.OutputPath)
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
    for line in iter(p2.stdout.readline,''):
        
        if args.verbose:
            print(line.rstrip())
        else:
            if (line[:6]=='frame='):
                sys.stdout.flush()
                x=line.rstrip()
                xindx=x.index("fps=")
                print("Created {0} out of an estimated {1} images".format(x[7:xindx],math.ceil(videoDuration/args.Duration)), end='\r')
    
    #prevents weird overlays caused by the line update command
    print()
                
    #Find total number of files in input directory that matches pattern file extension
    if not (os.path.isabs(args.InputPath)):
        args.InputPath = os.getcwd() + '\\'
    try:
        files = fnmatch.filter(os.listdir(args.InputPath), 'img_*.png')
        fileCount=int(len(files))
    except:
        print ("An Error occurred while trying to find total number of pictures in Input Directory")
        print ("Please check syntax and try again")
        sys.exit(0)
    
    
    #Calculate Crossfade duration so end file is the same length as beginning video
    if ((args.Duration != -1) and (args.CrossFade == -1)):
        args.CrossFade = float(format(float(float(fileCount*args.Duration)/float(videoDuration)), '.1f'))
    #The way I have currently written this code, this statement will never be true.
    #However to calculate fileCount I have to first use the Duration setting to grab my pictures
    #I don't have a good solution for this currently and will have to think about it.
    elif ((args.Duration == -1) and (args.CrossFade != -1)):
        args.Duration = round(float(float(fileCount*videoDuration)/float(args.CrossFade)))
    else:
        pass
    
    #Print out additional job information if verbosity is enabled
    if args.verbose:
        print ("Number of images found in directory is: {0}".format(fileCount))
        print ("Image Duration is set to: {0} Seconds".format(args.Duration))
        print ("Crossover Transition Duration is set to: {0} Seconds".format(args.CrossFade))
    
    
    #Get the extension type of the images to be used.
    #This exists for a planned future expansion to the program where
    #A slide show could be assembled from an existing directory of images.
    outExtension=os.path.splitext(args.OutputPath)[1]
    print(outExtension)
    if not(os.path.isabs(args.OutputPath)):
        if (outExtension is ""):
            vidOutputPath = os.getcwd() + '\\outvideo.mp4'
        else:
            vidOutputPath = os.getcwd() + '\\{0}'.format(args.OutputPath)
    elif (outExtension is ""):
        vidOutputPath = '{0}\\outvideo.mp4'.format(args.OutputPath)
    
    
    #these variable are used to print out any error messages and allow user feedback (I.e. would you like to overwrite the existing file.
    datacombined = ""
    xindx = 0
    yindx = 0
    cnt=0
    
    #create the ffmpeg command based on the transition type
    if args.TransitionType == 0: ## Transition is a hard cut
        outArgs=[FFMPEG_PATH, '-s', '{0}x{1}'.format(args.OutWidth, args.OutHeight), '-framerate', '1/{0}'.format(args.Duration), '-i', 'img_%03d.png', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', vidOutputPath]
    if args.TransitionType == 1: ## Transition is crossfade
        outArgs=[FFMPEG_PATH, '-i', 'img_%03d.png', '-vf', 'zoompan=d={0}:s={1}x{2}:fps={3},framerate={4}:interp_start=0:interp_end=255:scene=100'.format(args.Duration, args.OutWidth, args.OutHeight, args.CrossFade ,args.FrameRate), '-hide_banner', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', vidOutputPath]
        
    #I'd like to add additional transition types, however the more complex transition require huge complex_filter commands that exceed the max length python can handle
    #I may look into splitting it into smaller commands and then combining the videos
    
    #Create the slideshow video
    with subprocess.Popen(outArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as outProcess:
        while outProcess.poll() is None:
            data = outProcess.stdout.read(1)
            #The subprocess Pipes send one character at a time in byte formate 
            #decode turns it into a standard string character and I add it to a growing string
            datacombined += data.decode()
            
            if (args.verbose):
                #If verbosity is enabled just print each character as it appears.  By using end='' the print command will not insert newlines arbitrarily 
                print (data.decode(), end='', flush=True)
            else:
                #If verbosity is not enabled then dump the contents of datacombined whenever a new line is encountered as we won't care about messages
                #but we still need to make sure we're clearing the buffer
                if data.decode()=='\n':  
                    datacombined=""
                    sys.stdout.flush()
                #Whenever the first 4 characters of datacombined is file print the information to the screen
                #The only time the word "File" appears is when there is an error message asking if you want to overwrite a pre-existing file.
                if datacombined[:4] == 'File':
                    #This exists because without it a random "e" appears on screen.  I thinik it's a timing issue thing, but for now
                    #simply skipping the first letter solves the issue.
                    if cnt > 0:
                        print(data.decode(), end='', flush=True)
                    cnt+=1
                
                #The final scenario is its actually creating the video slideshow.
                #Find the location of the word time and bitrate, their locations will be used to display ongoing status
                xindx=datacombined.find("time=")
                yindx=datacombined.find("bitrate=")
                #As long as both time and bitrate are found parse the string to show how many minutes of the video have been encoded and how many total minutes there are.
                if xindx is not -1 and yindx is not -1:
                    timeString = datacombined[xindx+5:yindx]
                    timeStringInt = get_sec(timeString.split('.')[0])
                    print ("Slide show encoding is {0:.2f}% complete".format(float(timeStringInt)/float(videoDuration)*100), end='\r', flush=True)
                   # print(data.decode(), end='', flush=True)
                    xindx=-1
                    yindx=-1
                    datacombined=""
    
    #Delete all picture files created unless the keep pictures flag has been set                      
    if not args.KeepFiles:
        for file in files:
            os.remove(file)
    
