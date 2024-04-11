import os
import random
import sqlite3
from flask import Flask
from flask import request, render_template, redirect, url_for, send_from_directory, send_file, Response
import json
import socket
import shutil

app = Flask(__name__)


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if not request.form.get('email'):
            return render_template('login.html', goodReg='НЭП', password=request.form.get('password'),
                                   name=request.form.get('name'))
        elif not request.form.get('name'):
            return render_template('login.html', goodReg='ННН', password=request.form.get('password'),
                                   email=request.form.get('email'))
        elif not request.form.get('password'):
            return render_template('login.html', goodReg='ПП', email=request.form.get('email'),
                                   name=request.form.get('name'))
        else:
            sqlite_connection = sqlite3.connect('users.sqlite')
            cursor = sqlite_connection.cursor()
            cursor.execute(
                f"""SELECT Nickname FROM Users WHERE Nickname == '{request.form.get('name').strip()}' 
                AND Email == '{request.form.get('email').strip()}' 
                AND Password == '{request.form.get('password').strip()}';""")
            results = cursor.fetchall()
            if results:
                data = {'id': f'{random.randint(255, 637456364837648326)}',
                        'number': f'{random.randint(25, 345)}',
                        'portal': f'{random.randint(2, 64574)}'}
                with open(f'static/user/{request.form.get("name").strip()}/identification.json', 'w',
                          encoding='utf8') as file:
                    json.dump(data, file)
                with open(f'static/user/{request.form.get("name").strip()}/identification.json', 'r',
                          encoding='utf8') as file:
                    fileData = json.load(file)
                return render_template('login_continue.html', name=request.form.get('name').strip(), id=fileData['id'],
                                       number=fileData['number'], portal=fileData['portal'])
            else:
                cursor.close()
                return render_template('login.html', goodReg='ВТН', email=request.form.get('email'),
                                       name=request.form.get('name'), password=request.form.get('password'))


@app.route('/login_continue/<name>', methods=['GET', 'POST'])
def login_continue(name):
    if request.data:
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            fileData['ip'] = f'{str(request.data)[9:-3]}'
        with open(f'static/user/{name.strip()}/identification.json', 'w',
                  encoding='utf8') as file:
            json.dump(fileData, file)


@app.route('/login_check/<name>', methods=['GET', 'POST'])
def login_check(name):
    if request.data:
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
        if fileData['ip'] == f'{str(request.data)[9:-3]}':
            with open(f'static/user/{name.strip()}/сheck.txt', 'w', encoding='utf8') as file:
                file.write('done')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        if not request.form.get('email'):
            return render_template('register.html', goodReg='НЭП', password=request.form.get('password'),
                                   repeat_password=request.form.get('repeat_password'), name=request.form.get('name'))
        elif not request.form.get('name'):
            return render_template('register.html', goodReg='ННН', password=request.form.get('password'),
                                   repeat_password=request.form.get('repeat_password'), email=request.form.get('email'))
        elif request.form.get('password') != request.form.get('repeat_password'):
            return render_template('register.html', goodReg='ПНС', name=request.form.get('name'),
                                   email=request.form.get('email'))
        elif not request.form.get('password'):
            return render_template('register.html', goodReg='ПП', email=request.form.get('email'),
                                   name=request.form.get('name'))
        else:
            sqlite_connection = sqlite3.connect('users.sqlite')
            cursor = sqlite_connection.cursor()
            cursor.execute(
                f"""SELECT Nickname FROM Users WHERE Nickname == '{request.form.get('name').strip()}';""")
            results = cursor.fetchall()
            if not results:
                sqlite_connection = sqlite3.connect('users.sqlite')
                cursor = sqlite_connection.cursor()
                cursor.execute(
                    f"""INSERT INTO Users (Nickname, Email, Password) VALUES ('{request.form.get('name').strip()}',
                    '{request.form.get('email').strip()}', '{request.form.get('password').strip()}');""")
                sqlite_connection.commit()
                cursor.close()
                os.mkdir(f'static/user/{request.form.get("name").strip()}')
                iden_file = open("identification.json", "w")
                iden_file.close()
                os.replace("identification.json", f"static/user/{request.form.get('name').strip()}/identification.json")
                check_file = open('сheck.txt', 'w')
                check_file.close()
                os.replace("сheck.txt", f"static/user/{request.form.get('name').strip()}/сheck.txt")
                os.mkdir(f'static/user/{request.form.get("name").strip()}/avatar')
                os.mkdir(f'static/user/{request.form.get("name").strip()}/photos')
                os.mkdir(f'static/user/{request.form.get("name").strip()}/video')
                shutil.copy('avatar.png', f'static/user/{request.form.get("name").strip()}/avatar/avatar.png')
                shutil.copy('profile.json', f'static/user/{request.form.get("name").strip()}/profile.json')
                return render_template('main.html')
            else:
                return render_template('register.html', goodReg='ЕТИ', email=request.form.get('email'),
                                       name=request.form.get('name'))


@app.route('/video/<video_name>/<name>')
def get_video(video_name, name):
    video_path = f'static/user/{name}/video/{video_name}'
    file_size = os.path.getsize(video_path)
    headers = {}

    if 'Range' in request.headers:
        range_header = request.headers.get('Range')
        start = 0
        end = file_size - 1
        chunk_size = file_size
        status_code = 200
        headers['Content-Range'] = f"bytes {start}-{end}/{file_size}"
        headers['Content-Length'] = chunk_size
    else:
        chunk_size = file_size

    headers['Accept-Ranges'] = 'bytes'

    return Response(
        open(video_path, mode='rb').read(chunk_size),
        status=status_code,
        headers=headers,
        content_type='video/mp4'
    )


@app.route('/addvideo/<video_name>')
def addget_video(video_name):
    video_path = f'static/{video_name}'
    file_size = os.path.getsize(video_path)
    headers = {}

    if 'Range' in request.headers:
        range_header = request.headers.get('Range')
        start = 0
        end = file_size - 1
        chunk_size = file_size
        status_code = 200
        headers['Content-Range'] = f"bytes {start}-{end}/{file_size}"
        headers['Content-Length'] = chunk_size
    else:
        chunk_size = file_size

    headers['Accept-Ranges'] = 'bytes'

    return Response(
        open(video_path, mode='rb').read(chunk_size),
        status=status_code,
        headers=headers,
        content_type='video/mp4'
    )


@app.route('/acceptPhoto/<name>/<id>/<number>/<portal>/<filename>', methods=['GET', 'POST'])
def acceptPhoto(name, id, number, portal, filename):
    if request.method == 'GET':
        return render_template('acceptPhoto.html', path=f'/static/{filename}')
    elif request.method == 'POST':
        shutil.move(f"static/{filename}", f"static/user/{name}/photos/{filename}")
        return redirect(f'/profile/{name}/{id}/{number}/{portal}')


@app.route('/addphoto/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def addphoto(name, id, number, portal):
    if request.method == 'GET':
        with open(f'static/user/{name}/сheck.txt', 'r', encoding='utf8') as file:
            if not file.readline():
                return render_template('profileiden.html', name=name, id=id,
                                       number=number, portal=portal, place='addphoto')
            else:
                f = open(f'static/user/{name}/сheck.txt', 'w')
                f.close()
                return render_template('addphoto.html')
    elif request.method == 'POST':
        if request.files.get('file'):
            f = request.files['file']
            f.save(f'static/({name}){f.filename}')
            return redirect(f'/acceptPhoto/{name}/{id}/{number}/{portal}/({name}){f.filename}')


@app.route('/acceptVideo/<name>/<id>/<number>/<portal>/<filename>', methods=['GET', 'POST'])
def acceptVideo(name, id, number, portal, filename):
    if request.method == 'GET':
        return render_template('acceptVideo.html', video=f'{filename}')
    elif request.method == 'POST':
        shutil.move(f"static/{filename}", f"static/user/{name}/video/{filename}")
        return redirect(f'/profile/{name}/{id}/{number}/{portal}')


@app.route('/addvideo/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def addvideo(name, id, number, portal):
    if request.method == 'GET':
        with open(f'static/user/{name}/сheck.txt', 'r', encoding='utf8') as file:
            if not file.readline():
                return render_template('profileiden.html', name=name, id=id,
                                       number=number, portal=portal, place='addvideo')
            else:
                f = open(f'static/user/{name}/сheck.txt', 'w')
                f.close()
                return render_template('addvideo.html')
    elif request.method == 'POST':
        if request.files.get('file'):
            f = request.files['file']
            f.save(f'static/({name}){f.filename}')
            return redirect(f'/acceptVideo/{name}/{id}/{number}/{portal}/({name}){f.filename}')


@app.route('/profile/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def profile(name, id, number, portal):
    if request.method == 'GET':
        with open(f'static/user/{name}/сheck.txt', 'r', encoding='utf8') as file:
            if not file.readline():
                return render_template('profileiden.html', name=name, id=id,
                                       number=number, portal=portal, place='profile')
            else:
                f = open(f'static/user/{name}/сheck.txt', 'w')
                f.close()
                with open(f'static/user/{name}/identification.json', 'r', encoding='utf8') as file:
                    fileData = json.load(file)
                path = f'/static/user/{name}/avatar/{os.listdir(f"static/user/{name}/avatar")[0]}'
                photos = []
                for photo in os.listdir(f"static/user/{name}/photos"):
                    photos.append(f'/static/user/{name}/photos/{photo}')
                videos = []
                for video in os.listdir(f"static/user/{name}/video"):
                    videos.append(video)
                with open(f'static/user/{name}/profile.json', 'r', encoding='utf8') as file:
                    fileDataprofile = json.load(file)
                if fileData['id'] == id and fileData['number'] == number and fileData['portal'] == portal:
                    return render_template('profile.html', name=name, path_photos=photos, subs=fileDataprofile['Subs'],
                                           id=id,
                                           number=number, portal=portal, path=path, path_videos=videos)


if __name__ == '__main__':
    app.run()
