import os
import random
import sqlite3
from flask import Flask
from flask import request, render_template, redirect, url_for
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
                os.mkdir(f'static/user/{request.form.get("name").strip()}/avatar')
                shutil.copy('avatar.png', f'static/user/{request.form.get("name").strip()}/avatar/avatar.png')
                shutil.copy('profile.json', f'static/user/{request.form.get("name").strip()}/profile.json')
                return render_template('main.html')
            else:
                return render_template('register.html', goodReg='ЕТИ', email=request.form.get('email'),
                                       name=request.form.get('name'))


@app.route('/profile/<name>/<id>/<number>/<portal>', methods=['GET', 'POST'])
def profile(name, id, number, portal):
    if request.method == 'GET':
        with open(f'static/user/{name}/сheck.txt', 'r', encoding='utf8') as file:
            if not file.readline():
                return render_template('profileiden.html', name=name, id=id,
                                       number=number, portal=portal)
            else:
                f = open(f'static/user/{name}/сheck.txt', 'w')
                f.close()
                with open(f'static/user/{name}/identification.json', 'r', encoding='utf8') as file:
                    fileData = json.load(file)
                path = f'/static/user/{name}/avatar/{os.listdir(f"static/user/{name}/avatar")[0]}'
                with open(f'static/user/{name}/profile.json', 'r', encoding='utf8') as file:
                    fileDataprofile = json.load(file)
                if fileData['id'] == id and fileData['number'] == number and fileData['portal'] == portal:
                    return render_template('profile.html', name=name, path=path, subs=fileDataprofile['Subs'], id=id,
                                           number=number, portal=portal)


if __name__ == '__main__':
    app.run()
