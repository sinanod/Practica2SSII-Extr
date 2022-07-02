import hashlib
import os
import sqlite3
import json
import pandas
import pandas as pd
from urllib.request import urlopen
import plotly.express as px
import plotly.utils
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from flask import Flask, render_template, request,redirect, session, app
from matplotlib import pyplot as plt

fLegal = open('legal.json')
fUsers = open('users.json')
dataLegal = json.load(fLegal)
dataUsers = json.load(fUsers)


def probClick(cliclados, total):
    if (total != 0):
        return (cliclados / total) * 100
    else:
        return 0


def checkPass(password):
    md5hash = password
    try:
        password_list = str(urlopen(
            "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(),
                            'utf-8')
        for password in password_list.split('\n'):
            guess = hashlib.md5(bytes(password, 'utf-8')).hexdigest()
            if guess == md5hash:
                return 1
                break
            elif guess != md5hash:
                continue
            else:
                return 2
        return 2
    except Exception as exc:
        return 2


con = sqlite3.connect('PRACTICA1.DB')
cursor = con.cursor()

cursor.execute("DROP TABLE legal")
cursor.execute("DROP TABLE users")

cursor.execute(
    "CREATE TABLE IF NOT EXISTS legal (nombrel,cookies,aviso,proteccionDatos,politicas,creacion,primary key(nombrel))")
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,probClick,fechas,num_fechas,ips,num_ips,passVul,primary key (nombre))")
insert_legal = """INSERT INTO legal (nombrel,cookies,aviso,proteccionDatos,politicas,creacion) VALUES (?,?,?,?,?,?)"""
insert_users = """INSERT INTO users (nombre,telefono,password,provincia,permisos,total_emails,phishing_email,cliclados_email,probClick,fechas,num_fechas,ips,num_ips,passVul) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

for i in dataLegal['legal']:
    for j in i.keys():
        for k in i.values():
            dLegal = (
                j, k['cookies'], k['aviso'], k['proteccion_de_datos'],
                k['cookies'] + k['aviso'] + k['proteccion_de_datos'],
                k['creacion'])
        cursor.execute(insert_legal, dLegal)
        con.commit()

for i in dataUsers['usuarios']:
    for j in i.keys():
        for k in i.values():
            dUsers = (j, k['telefono'], k['contrasena'], k['provincia'], k['permisos'], k['emails']['total'],
                      k['emails']['phishing'], k['emails']['cliclados'],
                      probClick(k['emails']['cliclados'], k['emails']['phishing']), str(k['fechas']), len(k['fechas']),
                      str(k['ips']), len(k['ips']), checkPass(k['contrasena']))
        cursor.execute(insert_users, dUsers)
        con.commit()

con.commit()

dataFrame = pd.DataFrame()


def ejercicio2():
    cursor.execute('SELECT num_fechas FROM users')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dataFrame['Numero fechas'] = resultado

    cursor.execute('SELECT num_ips FROM users')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dataFrame['Numero IPS'] = resultado

    cursor.execute('SELECT num_fechas FROM users')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dataFrame['Numero IPS'] = resultado

    cursor.execute('SELECT total_emails FROM users')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dataFrame['Total Emails'] = resultado

    print("EJERCICIO 2\n")
    print("Numero de muestras")
    print(dataFrame.count(), "\n")
    print("Media y desviación estándar\n")
    print("Media\n", dataFrame.mean(), "\n")
    print("Desviación\n", dataFrame.std(), "\n")
    print("Maximo y mínimo de total fechas\n")
    print("Maximo", dataFrame['Numero fechas'].max())
    print("Minimo", dataFrame['Numero fechas'].min())
    print("Maximo", dataFrame['Total Emails'].max())
    print("Minimo", dataFrame['Total Emails'].min())

dfUsuarios = pd.DataFrame()
dfAdmins = pd.DataFrame()
dfMenor200 = pd.DataFrame()
dfMayor200 = pd.DataFrame()
totalDF = pd.DataFrame()


def ejercicio3():


    cursor.execute('SELECT phishing_email FROM users where permisos="0"')
    rows = cursor.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    dfUsuarios['Phishing Emails Permisos Usuario'] = res

    cursor.execute('SELECT phishing_email FROM users where permisos="1"')
    rows = cursor.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    dfAdmins['Phishing Emails Permisos Admin'] = res

    cursor.execute('SELECT phishing_email FROM users where total_emails<200')
    rows = cursor.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    dfMenor200['Phishing Emails De Gente con < 200 correos'] = res

    cursor.execute('SELECT phishing_email FROM users where total_emails>=200')
    rows = cursor.fetchall()
    res = []
    for i in rows:
        res += [i[0]]
    dfMayor200['Phishing Emails de Gente >= 200 correos'] = res

    print("\nEJERCICIO 3\n")
    print("Phishing Emails de Permisos Usuario\n")
    print(dfUsuarios.describe())
    print(dfUsuarios)
    num_missing = dfUsuarios.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Permisos Administrador\n")
    print(dfAdmins.describe())
    print(dfAdmins)
    num_missing = dfAdmins.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Personas con menos de 200 correos\n")
    print(dfMenor200.describe())
    print(dfMenor200)
    num_missing = dfMenor200.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    print("Phishing Emails de Personas con mas o igual de 200 correos\n")
    print(dfMayor200)
    print(dfMayor200.describe())
    num_missing = dfMayor200.isna().sum()
    print("Valores Missing de", num_missing)
    print("\n")

    totalDF = pd.concat([dfAdmins,dfUsuarios,dfMayor200,dfMenor200],axis = 1)
    print("Numero de Observaciones\n")
    print(totalDF.count(),"\n")
    print("Numero de valores Missing\n")
    print(totalDF.isna().sum(),"\n")
    print("Medianas\n")
    print(totalDF.median(),"\n")
    print("Medias\n")
    print(totalDF.mean(),"\n")
    print("Desviaciones\n")
    print(totalDF.std(),"\n")
    print("Maximos\n")
    print(totalDF.max(),"\n")
    print("Minimos\n")
    print(totalDF.min(),"\n")



dfLegal = pd.DataFrame()
dfPrivacidad = pd.DataFrame()
dfVulnerable = pd.DataFrame()
dfConexiones = pd.DataFrame()
dfCritico = pd.DataFrame()

def ejercicio4():
    cursor.execute('SELECT nombrel, cookies, aviso, proteccionDatos FROM legal ORDER BY politicas')
    cols = cursor.fetchall()
    nombre = []
    cookies = []
    avisos = []
    proteccionDatos = []
    for i in range(len(cols)):
        nombre += [cols[i][0]]
        cookies += [cols[i][1]]
        avisos += [cols[i][2]]
        proteccionDatos += [cols[i][3]]
    dfLegal['Nombre'] = nombre
    dfLegal['Cookies'] = cookies
    dfLegal['Avisos'] = avisos
    dfLegal['Proteccion de Datos'] = proteccionDatos

    cursor.execute('SELECT DISTINCT creacion FROM legal ORDER BY creacion')
    cols = cursor.fetchall()
    creacion = []
    for i in range(len(cols)):
        creacion += [cols[i][0]]
    dfPrivacidad['Creacion'] = creacion

    cursor.execute('SELECT creacion, proteccionDatos FROM legal WHERE proteccionDatos=1 ORDER BY creacion')
    cols = cursor.fetchall()
    seCumple = [0]*len(creacion)
    for i in range(len(creacion)):
        for j in range(len(cols)):
            if cols[j][0] == creacion[i]:
                seCumple[i] += 1
    dfPrivacidad['Se cumple'] = seCumple

    cursor.execute('SELECT creacion, proteccionDatos FROM legal WHERE proteccionDatos=0 ORDER BY creacion')
    cols = cursor.fetchall()
    noSeCumple = [0] * len(creacion)
    for i in range(len(creacion)):
        for j in range(len(cols)):
            if cols[j][0] == creacion[i]:
                noSeCumple[i] += 1
    dfPrivacidad['No se cumple'] = noSeCumple

    cursor.execute('SELECT COUNT(num_ips) FROM users where num_ips>=10')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dfVulnerable['Comprometidas'] = resultado

    cursor.execute('SELECT COUNT(num_ips) FROM users where num_ips<10')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dfVulnerable['No Comprometidas'] = resultado


    cursor.execute('SELECT AVG (num_ips) FROM users where passVul=1')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dfConexiones['Vulnerables'] = resultado

    cursor.execute('SELECT AVG(num_ips) FROM users where passVul=2')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dfConexiones['No Vulnerables'] = resultado



    cursor.execute('SELECT probClick FROM users where passVul=1 ORDER BY probClick DESC')
    cols = cursor.fetchall()
    resultado = []
    for i in cols:
        resultado += [i[0]]
    dfCritico['Probabilidad de Click'] = resultado

class PDF(FPDF):
    pass

ejercicio2()
ejercicio3()
ejercicio4()


con.close()

@app.route('/')
def index():  # put application's code here
    return render_template('login.html')

@app.route('/home.html')
def home():  # put application's code here
        return render_template("home.html")

users = [["admin","admin"],["user","user"]]
app.secret_key = "SecretKey"

@app.route('/login.html',methods=["GET","POST"])
def login():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        for i in range(len(users)):
            if (users[i][0]==username and users[i][1]==password):
                session['user'] = username
                return redirect('/Casa.html')

        return "<h1>Wrong username or password</h1>"

    return render_template("login.html")

@app.route('/register.html',methods=["GET","POST"])
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        users.append([username,password])

    return render_template("register.html")

@app.route('/topUsuariosCriticos.html', methods=["GET","POST"])
def topUssersCrit():
    num = request.form.get('numero', default=10)
    probNum = request.form.get('porcentaje',default='0')
    if(num==''):
        num = 10
    dfCritico = pandas.DataFrame()

    con = sqlite3.connect('PRACTICA1.DB')
    cursor = con.cursor()

    if(probNum == '0'):
        query = """SELECT nombre,probClick FROM users where passVul=1 ORDER BY probClick DESC LIMIT (?)"""
    elif(probNum == '1'):
        query = """SELECT nombre,probClick FROM users where passVul=1 AND probClick>=50 ORDER BY probClick DESC LIMIT (?)"""
    elif(probNum =='2'):
        query = """SELECT nombre,probClick FROM users where passVul=1 AND probClick<50 ORDER BY probClick DESC LIMIT (?)"""

    cursor.execute(query, (num,))
    rows = cursor.fetchall()
    nombre = []
    prob = []
    for i in range(len(rows)):
        nombre += [rows[i][0]]
        prob += [rows[i][1]]
    dfCritico['Nombre'] = nombre
    dfCritico['Probabilidad de Click'] = prob
    fig = px.bar(dfCritico, x=dfCritico['Nombre'], y=dfCritico['Probabilidad de Click'])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSONUno = json.dumps(fig, cls=a)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf_w = 210
    pdf_h = 297
    plotly.io.write_image(fig, file='pltx.png', format='png', width=700, height=450)
    pltx = (os.getcwd() + '/' + "pltx.png")
    pdf.set_xy(40.0, 25.0)
    pdf.image(pltx, link='', type='', w=700 / 5, h=450 / 5)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    txt = "Se muestra el top de usuarios críticos. En el eje X podemos ver los nombres de los usuarios cuestion. El eje Y representa la probabilidad de que el usuario pulse un correo spam."
    pdf.set_xy(10.0, 130.0)
    pdf.multi_cell(w=0, h=10, txt=txt, align='L')
    pdf.output('static/topUsuariosCriticos.pdf', 'F')
    con.close()
    return render_template('topUsuariosCriticos.html', graphJSONUno=graphJSONUno)


@app.route('/topPaginasVulnerables.html', methods=["GET","POST"])
def topWebsVuln():
    num = request.form.get('numero', default=10)
    if (num == ''):
        num = 10
    df_topWebs =pandas.DataFrame()

    con = sqlite3.connect('PRACTICA1.DB')
    cursor = con.cursor()

    query = """SELECT nombrel,cookies,aviso,proteccionDatos FROM legal ORDER BY politicas LIMIT (?)"""
    cursor.execute(query, (num,))
    rows = cursor.fetchall()
    nombre = []
    cookies = []
    avisos = []
    proteccionDatos = []
    for i in range(len(rows)):
        nombre += [rows[i][0]]
        cookies += [rows[i][1]]
        avisos += [rows[i][2]]
        proteccionDatos += [rows[i][3]]
    df_topWebs['Nombre'] = nombre
    df_topWebs['Cookies'] = cookies
    df_topWebs['Avisos'] = avisos
    df_topWebs['Proteccion de Datos'] = proteccionDatos
    fig = go.Figure(data=[
        go.Bar(name='Cookies', x=df_topWebs['Nombre'], y=df_topWebs['Cookies'], marker_color='steelblue'),
        go.Bar(name='Avisos', x=df_topWebs['Nombre'], y=df_topWebs['Avisos'], marker_color='lightsalmon'),
        go.Bar(name='Proteccion de datos', x=df_topWebs['Nombre'], y=df_topWebs['Proteccion de Datos'], marker_color='red')
    ])

    fig.update_layout(title_text="Peores Webs", title_font_size=41, barmode='group')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf_w = 210
    pdf_h = 297
    plotly.io.write_image(fig, file='pltx.png', format='png', width=700, height=450)
    pltx = (os.getcwd() + '/' + "pltx.png")
    pdf.set_xy(40.0, 25.0)
    pdf.image(pltx, link='', type='', w=700 / 5, h=450 / 5)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0,0,0)
    txt="Se muestra el grafico de las paginas web mas vulnerables. " \
        "En el eje X se ven los nombres de las paginas web. El eje Y muestra que si esta a 0 la politica no esta activada y en caso de que esté a 1, está activada. "
    pdf.set_xy(10.0, 140.0)
    pdf.multi_cell(w=0, h=10, txt=txt,align='L')
    pdf.output('static/topPaginasVulnerables.pdf', 'F')
    return render_template('topPaginasVulnerables.html', graphJSON=graphJSON)

def ejerCuatro():
    page = requests.get("https://cve.circl.lu/api/last")
    jsons = page.json()
    lista1 = []
    lista2 = []
    for i in range(0,10):
        lista1 += [jsons[i]['id']]
        lista2 += [jsons[i]['summary']]
    fig = go.Figure(data=[go.Table(header=dict(values=['Vulnerability','Description']),cells=dict(values=[lista1,lista2]))])
    table = plotly.io.to_html(fig)
    return render_template('Ultimas10Vulnerabilidades.html',tableHTML=table)

@app.route('/ej4a')
def ej4a():
    fig = px.bar(dfCritico, x=dfCritico['Nombre'], y=dfCritico['Probabilidad de Click'])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/ej4b')
def ej4b():
    fig = go.Figure(data=[
        go.Bar(name='Cookies', x=dfLegal['Nombre'], y=dfLegal['Cookies'], marker_color='steelblue'),
        go.Bar(name='Avisos', x=dfLegal['Nombre'], y=dfLegal['Avisos'], marker_color='lightsalmon'),
        go.Bar(name='Proteccion de datos', x=dfLegal['Nombre'], y=dfLegal['Proteccion de Datos'], marker_color='red')
    ])
    # Change the bar mode
    fig.update_layout(title_text="Cinco Peores", title_font_size=41, barmode='group')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/ej4c')
def ej4c():
    labels = ['Vulnerables', 'No Vulnerables']
    values = [dfConexiones.at[0, 'Vulnerables'], dfConexiones.at[0, 'No Vulnerables']]
    fig = go.Figure(data=[
        go.Pie(labels=labels, values=values)])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/ej4d')
def ej4d():
    fig = go.Figure(data=[
        go.Bar(name='Se cumple', x=dfPrivacidad['Creacion'], y=dfPrivacidad['Se cumple'], marker_color='steelblue'),
        go.Bar(name='No se cumple', x=dfPrivacidad['Creacion'], y=dfPrivacidad['No se cumple'], marker_color='lightsalmon')
    ])
    # Change the bar mode
    fig.update_layout(title_text="Comparativa Privacidad segun el Año de Creación", title_font_size=41, barmode='stack')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)

@app.route('/ej4e')
def ej4e():
    labels = ['No Comprometidas', 'Comprometidas']
    values = [dfVulnerable.at[0, 'No Comprometidas'], dfVulnerable.at[0, 'Comprometidas']]
    fig = go.Figure(data=[
        go.Pie(labels=labels, values=values)])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('cuatroApartados.html', graphJSON=graphJSON)


### define a method
def charts(self):
        self.set_xy(40.0,25.0)
        self.image(plt,  link='', type='', w=700/5, h=450/5)


if __name__ == '__main__':
    app.run()

