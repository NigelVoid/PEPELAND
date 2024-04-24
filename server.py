import os
import random
import sqlite3
import requests
from flask import Flask
from flask import request, render_template, redirect, url_for, send_from_directory, send_file, Response, abort, \
    make_response, jsonify, session
import json
import secrets
import socket
import shutil
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bibaboba9128'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

token_list = []


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        session['token'] = secrets.token_urlsafe(20)
        token_list.append(session['token'])
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
                response = make_response(
                    render_template('login_continue.html', name=request.form.get('name').strip(), id=fileData['id'],
                                    number=fileData['number'], portal=fileData['portal']))
                return response
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
            fileData['ip'] = f'{session["token"]}'
        with open(f'static/user/{name.strip()}/identification.json', 'w',
                  encoding='utf8') as file:
            json.dump(fileData, file)


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
                os.mkdir(f'static/user/{request.form.get("name").strip()}/avatar')
                os.mkdir(f'static/user/{request.form.get("name").strip()}/photos')
                os.mkdir(f'static/user/{request.form.get("name").strip()}/video')
                os.mkdir(f'static/user/{request.form.get("name").strip()}/entrys')
                os.mkdir(f'static/user/{request.form.get("name").strip()}/entrys/files')
                shutil.copy('avatar.png', f'static/user/{request.form.get("name").strip()}/avatar/avatar.png')
                shutil.copy('profile.json', f'static/user/{request.form.get("name").strip()}/profile.json')
                shutil.copy('invites.json', f'static/user/{request.form.get("name").strip()}/invites.json')
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


@app.route('/addenvideo/<video_name>/<name>')
def addenget_video(video_name, name):
    video_path = f'static/user/{name}/entrys/files/{video_name}'
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
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            if fileData['ip'] != f'{session["token"]}':
                return abort(403)
            else:
                return render_template('addphoto.html')
    elif request.method == 'POST':
        if request.files.get('file'):
            f = request.files['file']
            f.save(f'static/({name}){f.filename}')
            return redirect(f'/acceptPhoto/{name}/{id}/{number}/{portal}/({name}){f.filename}')


@app.route('/addAvatar/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def addAvatar(name, id, number, portal):
    if request.method == 'GET':
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            if fileData['ip'] != f'{session["token"]}':
                return abort(403)
            else:
                return render_template('addAvatar.html')
    elif request.method == 'POST':
        if request.files.get('file'):
            f = request.files['file']
            f.save(f'static/({name}){f.filename}')
            return redirect(f'/acceptAvatar/{name}/{id}/{number}/{portal}/({name}){f.filename}')


@app.route('/acceptAvatar/<name>/<id>/<number>/<portal>/<filename>', methods=['GET', 'POST'])
def acceptAvatar(name, id, number, portal, filename):
    if request.method == 'GET':
        return render_template('acceptAvatar.html', path=f'/static/{filename}')
    elif request.method == 'POST':
        os.remove(f'static/user/{name}/avatar/{os.listdir(f"static/user/{name}/avatar")[0]}')
        shutil.move(f"static/{filename}", f"static/user/{name}/avatar/{filename}")
        return redirect(f'/profile/{name}/{id}/{number}/{portal}')


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
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            if fileData['ip'] != f'{session["token"]}':
                return abort(403)
            else:
                return render_template('addvideo.html')
    elif request.method == 'POST':
        if request.files.get('file'):
            f = request.files['file']
            f.save(f'static/({name}){f.filename}')
            return redirect(f'/acceptVideo/{name}/{id}/{number}/{portal}/({name}){f.filename}')


@app.route('/makeanentry/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def makeanentry(name, id, number, portal):
    if request.method == 'GET':
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            if fileData['ip'] != f'{session["token"]}':
                return abort(403)
            else:
                return render_template('makeanentry.html')
    elif request.method == 'POST':
        files = []
        for key in request.files.keys():
            f = request.files[key]
            if f.filename[-5:] == '.jfif' or f.filename[-5:] == '.jpeg':
                f.save(
                    f'static/user/{name}/entrys/files/{len(os.listdir(f"static/user/{name}/entrys/files")) + 1}file{f.filename[-5:]}')
                files.append(
                    str(len(
                        os.listdir(f"static/user/{name}/entrys/files"))) + f'file{request.files[key].filename[-5:]}')
            else:
                f.save(
                    f'static/user/{name}/entrys/files/{len(os.listdir(f"static/user/{name}/entrys/files")) + 1}file{f.filename[-4:]}')
                files.append(
                    str(len(
                        os.listdir(f"static/user/{name}/entrys/files"))) + f'file{request.files[key].filename[-4:]}')
        data = {'topic': f'{request.form.get("topic")}',
                'text': f'{request.form.get("text")}',
                'url': f'{request.form.get("url")}'}
        if request.files:
            data['files'] = files
        with open(f'static/user/{name}/entrys/entry{len(os.listdir(f"static/user/{name}/entrys"))}.json', 'w',
                  encoding='utf8') as file:
            json.dump(data, file)
        return redirect(f'/profile/{name}/{id}/{number}/{portal}')


@app.route('/text')
def get_text():
    def generate(previous_state=[None]):
        while True:
            current_state = os.stat('text.txt').st_mtime
            if previous_state[0] is None or current_state != previous_state[0]:
                with open('text.txt', 'r') as file:
                    yield 'data: ' + file.read() + '\n\n'
                previous_state[0] = current_state

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/writeToFile/<name>', methods=['POST'])
def write_to_file(name):
    text = request.json['text']
    if str(text).strip() != '':
        if '!/!' in text:
            text = str(text).replace('!/!', ' ')
        with open('text.txt', 'a') as file:
            file.write('!/!' + f'{name}: {text}')


@app.route('/deleteFromInvites/<name>/<name2>', methods=['POST'])
def deleteFromInvites(name, name2):
    print('123')
    with open(f'static/user/{name}/invites.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        data = [str(i) for i in fileData['invites'] if str(i) != name2]
        fileData['invites'] = data
    with open(f'static/user/{name}/invites.json', 'w', encoding='utf8') as file:
        json.dump(fileData, file)
    with open(f'static/user/{name2}/invites.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        data = [str(i) for i in fileData['invites'] if str(i) != name]
        fileData['invites'] = data
    with open(f'static/user/{name2}/invites.json', 'w', encoding='utf8') as file:
        json.dump(fileData, file)


@app.route('/addFriendprofile/<name>/<name2>', methods=['POST'])
def addFriendProfile(name, name2):
    print('dnwidhw')
    with open(f'static/user/{name}/profile.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        if not name2 in fileData['Friends']:
            fileData['Friends'].append(name2)
    with open(f'static/user/{name}/profile.json', 'w', encoding='utf8') as file:
        json.dump(fileData, file)
    with open(f'static/user/{name2}/profile.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        if not name in fileData['Friends']:
            fileData['Friends'].append(name)
    with open(f'static/user/{name2}/profile.json', 'w', encoding='utf8') as file:
        json.dump(fileData, file)
    with open(f'static/user/{name}/invites.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        data = [str(i) for i in fileData['invites'] if str(i) != name2]
        fileData['invites'] = data
    with open(f'static/user/{name}/invites.json', 'w', encoding='utf8') as file:
        json.dump(fileData, file)
    with open(f'static/user/{name2}/invites.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        data = [str(i) for i in fileData['invites'] if str(i) != name]
        fileData['invites'] = data
    with open(f'static/user/{name2}/invites.json', 'w', encoding='utf8') as file:
        json.dump(fileData, file)


@app.route('/addFriend/<name>/<myname>', methods=['POST'])
def addFriend(name, myname):
    with open(f'static/user/{name}/invites.json', 'r') as file:
        fileData = json.load(file)
    if myname not in fileData['invites']:
        fileData['invites'].append(myname)  # Обновляем список приглашений
        with open(f'static/user/{name}/invites.json', 'w') as file:
            json.dump(fileData, file)  # Записываем обновленные данные обратно в файл


@app.route('/chat/<name>')
def chat(name):
    with open(f'static/user/{name.strip()}/identification.json', 'r',
              encoding='utf8') as file:
        fileData = json.load(file)
        if fileData['ip'] != f'{session["token"]}':
            return abort(403)
        else:
            return render_template('writefile.html', name=name)


@app.route('/otherprofile/<name2>/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def otherprofile(name, name2, id, number, portal):
    if request.method == 'GET':
        print(session["token"])
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            print(fileData['ip'], session["token"])
            if fileData['ip'] != f'{session["token"]}' or name == name2:
                return abort(403)
            else:
                with open(f'static/user/{name}/identification.json', 'r', encoding='utf8') as file:
                    fileData = json.load(file)
                path = f'/static/user/{name2}/avatar/{os.listdir(f"static/user/{name2}/avatar")[0]}'
                photos = []
                for photo in os.listdir(f"static/user/{name2}/photos"):
                    photos.append(f'/static/user/{name2}/photos/{photo}')
                videos = []
                for video in os.listdir(f"static/user/{name2}/video"):
                    videos.append(video)
                with open(f'static/user/{name2}/profile.json', 'r', encoding='utf8') as file:
                    fileDataprofile = json.load(file)
                endata = []
                if len(os.listdir(f'static/user/{name2}/entrys')) > 1:
                    for num in range(1, len(os.listdir(f'static/user/{name2}/entrys'))):
                        with open(f'static/user/{name2}/entrys/entry{num}.json', 'r', encoding='utf8') as file:
                            fileDataen = json.load(file)
                            endata.append(fileDataen)
                print(endata)
                with open(f'static/user/{name2}/invites.json', 'r') as file:
                    invites = json.load(file)
                print(invites['invites'])
                if fileData['id'] == id and fileData['number'] == number and fileData['portal'] == portal:
                    return render_template('otherprofile.html', name=name2, path_photos=photos,
                                           Friends=fileDataprofile['Friends'],
                                           id=id,
                                           number=number, portal=portal, path=path, path_videos=videos, endata=endata,
                                           members=os.listdir('static/user'), myname=name, invites=invites['invites'])


@app.route('/notifications/<name>/<id>/<number>/<portal>')
def notifications(name, id, number, portal):
    with open(f'static/user/{name}/invites.json') as file:
        fileData = json.load(file)
    return render_template('notifications.html', name=name, id=id, number=number, portal=portal,
                           invites=fileData['invites'])


@app.route('/profile/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def profile(name, id, number, portal):
    if request.method == 'GET':
        print(session["token"])
        with open(f'static/user/{name.strip()}/identification.json', 'r',
                  encoding='utf8') as file:
            fileData = json.load(file)
            if fileData['ip'] != f'{session["token"]}':
                return abort(403)
            else:
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
                endata = []
                if len(os.listdir(f'static/user/{name}/entrys')) > 1:
                    for num in range(1, len(os.listdir(f'static/user/{name}/entrys'))):
                        with open(f'static/user/{name}/entrys/entry{num}.json', 'r', encoding='utf8') as file:
                            fileDataen = json.load(file)
                            endata.append(fileDataen)
                print(endata)
                if fileData['id'] == id and fileData['number'] == number and fileData['portal'] == portal:
                    return render_template('profile.html', name=name, path_photos=photos,
                                           Friends=fileDataprofile['Friends'],
                                           id=id,
                                           number=number, portal=portal, path=path, path_videos=videos, endata=endata,
                                           members=os.listdir('static/user'))


if __name__ == '__main__':
    app.run()
