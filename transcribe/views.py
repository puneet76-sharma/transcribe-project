from django.shortcuts import render,HttpResponse
from django.core.files.uploadedfile import UploadedFile
import speech_recognition as sr 
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from django.core.files.storage import FileSystemStorage
from django.conf import settings
 
def index(request):
    if "GET" == request.method:
        return render(request, 'index.html', {})
    else:
        file = request.FILES["vid_file"]
        file_type = file.content_type.split('/')[0]
        print(file_type)
        if file_type=="video":
            # wrapped_file = UploadedFile(file)
            # file = wrapped_file.name
            folder='videos/'
            fs = FileSystemStorage(location=folder)
            file = fs.save(file.name, file)
            file_url = fs.url(file)
            print(file_url)

            ######### Conversion ##########################

            num_seconds_video= 52*60
            print("The video is {} seconds".format(num_seconds_video))
            l=list(range(0,num_seconds_video+1,60))
            print(file)
            # file ="videos\docker-assignment-ajay.mp4"
            # file = "videos\\"+file
            file = str(settings.MEDIA_ROOT) + "\\" + file
            print(file)
            diz={}
            try:
                for i in range(len(l)-1):
                    ffmpeg_extract_subclip(file, l[i]-2*(l[i]!=0), l[i+1], targetname="{}{}.mp4".format(file,i+1))
                    clip = mp.VideoFileClip(r"{}{}.mp4".format(file,i+1)) 
                    clip.audio.write_audiofile(r"{}{}.wav".format(file,i+1))
                    r = sr.Recognizer()
                    audio = sr.AudioFile("{}{}.wav".format(file,i+1))
                    with audio as source:
                        r.adjust_for_ambient_noise(source)  
                        audio_file = r.record(source)
                        result = r.recognize_google(audio_file)
                        diz['chunk{}'.format(i+1)]=result
            except:
                pass

            ################ Saving ##########################
            # file=file+".txt"
            l_chunks=[diz['chunk{}'.format(i+1)] for i in range(len(diz))]
            text='\n'.join(l_chunks)
            print("====================")
            print(text)

            return render(request, 'index.html',{"text":text})
        else:
            return HttpResponse("Sorry., You Choose Wrong file. Please Reload the page")