import flask
from flask import Flask, render_template, request, url_for, send_file
import pytube
from pydub import AudioSegment
import math
import pandas as pd
import requests

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template('home.html')


@app.route("/mediocreator")
def medio_creator():
    message = []
    return render_template('mediocreator.html')


@app.route("/editor", methods=["GET", "POST"])
def fetch_url():
    # url = request.form.get('youtube_url')
    # category = request.form.get('category')
    # name = request.form.get('name') + ".mp3"
    # output_dir = "Audio/" + category
    # full_path = output_dir + "/" + name
    # yt = pytube.YouTube(url)
    # stream = yt.streams.filter(only_audio=True).first()
    # stream.download(output_path=output_dir, filename=name)
    #
    # sound = AudioSegment.from_file(full_path)
    # frame = sound[meme['Time_Start'] * 1000:meme['Time_End'] * 1000]
    # duration = math.ceil(meme['Time_End'] - meme['Time_Start'])
    #
    # # create a new file "first_half.mp3":
    # frame.export(full_path, format="mp3")

    return render_template('editor.html', name=name, full_path=full_path)


@app.route("/memeview", methods=['GET', 'POST'])
def meme_uploader():
    user = request.args.get('user')

    sheet_link_shahzeb = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRLT8HrF93hGGeDbpuPHGenVXtWhg-kr8fPMl3kxtSiPmIV8Uy8iYSFBNRjJBd3RCM5JaNBVY474D3g/pub?gid=0&single=true&output=csv"
    sheet_link_sanjay = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQG9FweuluOr1XbuMyJK82svZ1SSkt7MGEyFDRg5VLgSD4tVAAeNJaSnEB_vYT2E9RwN_3N1OzvIMo5/pub?gid=159538028&single=true&output=csv"

    sheet_link = None
    if user == 'shahzeb':
        sheet_link = sheet_link_shahzeb
    elif user == 'sanjay':
        sheet_link = sheet_link_sanjay

    df = pd.read_csv(sheet_link)

    if request.method == 'POST':
        meme_list = request.form.getlist('memes')
        meme_list = [meme.split("/")[-1].split(".")[0].replace("_", " ") for meme in meme_list]
        print(meme_list)
        print()
        sheet_data = df[df["Title"].isin(meme_list)].to_dict(orient='record')
        print(sheet_data)
        response = []
        for meme in sheet_data:
            link = meme['Link']
            yt = pytube.YouTube(link)
            duration = math.ceil(meme['Time_End'] - meme['Time_Start'])
            with open("static/Audio/" + meme["Category"] + "/" + meme['Title'].replace(" ", "_") + ".mp3", 'rb') as f:
                r = requests.post("https://api.ratrey.co/v1/meme/upload-audio/",
                                  files={'audio_file': f},
                                  data={"title": meme['Title'],
                                        "thumbnail": yt.thumbnail_url,
                                        "duration": duration})
                print(r.text)
                response.append(r.text)
        return "kya matlb ho gyaa complete\n" + str(response)

    sheet_data = df[df["Status"] != 'sent'].to_dict(orient='record')
    print(sheet_data)
    meme_list = []

    for meme in sheet_data:
        link = meme['Link']
        yt = pytube.YouTube(link)
        stream = yt.streams.filter(only_audio=True).first()
        meme_dir = "Audio/" + meme["Category"]
        meme_dir_static = "static/" + meme_dir
        filename = meme['Title'].replace(" ", "_") + ".mp3"
        full_path = meme_dir + "/" + filename
        full_path_static = meme_dir_static + "/" + filename
        stream.download(output_path=meme_dir_static, filename=filename)

        sound = AudioSegment.from_file(full_path_static)

        frame = sound[meme['Time_Start'] * 1000:meme['Time_End'] * 1000]

        duration = math.ceil(meme['Time_End'] - meme['Time_Start'])

        # create a new file "first_half.mp3":
        frame.export(full_path_static, format="mp3")
        meme_list.append([filename, full_path])
        # with open("Audio/" + meme["Category"] + "/" + meme['Title'] + ".mp3", 'rb') as f:
        #     r = requests.post("https://api.ratrey.co/v1/meme/upload-audio/",
        #                       files={'audio_file': f},
        #                       data={"title": meme['Title'],
        #                             "thumbnail": yt.thumbnail_url,
        #                             "duration": duration})
        #     print(r.text)
    return render_template('memeview.html', meme_list=meme_list, sheet_link=sheet_link, user=user)

# @app.route('/upload', methods=['GET', 'POST'])
# def uploader():
#     meme_list = []
#     if request.method == 'POST':
#         meme_list = request.form.getlist('memes')
#         for meme in meme_list:
#             with open(meme, 'rb') as f:
#                 r = requests.post("https://api.ratrey.co/v1/meme/upload-audio/",
#                                   files={'audio_file': f},
#                                   data={"title": meme['Title'],
#                                         "thumbnail": yt.thumbnail_url,
#                                         "duration": duration})
#                 print(r.text)
#     print(meme_list)
#     return "<p>"+'\n'.join(meme_list)+"</p>"
