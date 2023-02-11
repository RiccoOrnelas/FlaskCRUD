import os
from flask import Flask, render_template, request, url_for, redirect, flash
import urllib.request, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

basedir = os.path.abspath (os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "super secret key"

app.config["SQLALCHEMY_DATABASE_URI"] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy (app)

app.app_context().push()

class cinema (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    cidade = db.Column(db.String)
    preco_entrada = db.Column(db.Float)
    def __init__ (self, nome, cidade, preco_entrada):
        self.nome = nome
        self.cidade = cidade
        self.preco_entrada = preco_entrada

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route('/filmes/<propriedade>')
def filmes(propriedade):
    if propriedade == 'populares':
        url = "https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key=10aba4bf54dc9da3a26637a1945cda93"
    elif propriedade == 'kids':
        url = "https://api.themoviedb.org/3/discover/movie?certification_country=US&certification.lte=G&sort_by=popularity.desc&api_key=10aba4bf54dc9da3a26637a1945cda93"
    elif propriedade == 'drama':
        url = "https://api.themoviedb.org/3/discover/movie?with_genres=18&sort_by=vote_average.desc&vote_count.gte=10&api_key=10aba4bf54dc9da3a26637a1945cda93"
    elif propriedade == 'melhores2010': 
        url = "https://api.themoviedb.org/3/discover/movie?primary_release_year=2010&sort_by=vote_average.desc&api_key=10aba4bf54dc9da3a26637a1945cda93"
    
    resposta = urllib.request.urlopen(url)
    dados = resposta.read()
    jsondata = json.loads(dados)
    return render_template("filmes.html", filmes=jsondata['results'])

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/cinemas")
def cinemas():
    return render_template("cinema.html", cinema=cinema.query.all())
@app.route("/dicas", methods=["GET", "POST"])
def dicas():
    nome = request.form.get('nome')
    local = request.form.get('cidade')
    preco_entrada = request.form.get('preco_entrada')

    if request.method == "POST":
        if not nome or not local or not preco_entrada:
            flash("Preencha todos os Campos", "error")
        else:    
             dica = cinema( nome, local, preco_entrada)  
             db.session.add(dica)
             db.session.commit()
             return redirect("cinemas") 
    return render_template("add_dica.html")    

@app.route('/<int:id>/atualiza_dica', methods=['GET', 'POST'])
def atualiza_dica(id):
    atualiza = cinema.query.filter_by(id=id).first()
    if request.method == "POST":
        nome = request.form['nome']
        cidade = request.form['cidade']
        preco_entrada = request.form['preco_entrada']
        atualiza.query.filter_by(id=id).update({"nome":nome, "cidade":cidade, "preco_entrada": preco_entrada})
        db.session.commit()
        return redirect(url_for('cinemas'))   

    return render_template('atualiza_dica.html', atualiza=atualiza)
@app.route('/<int:id>/excluir_dica')
def excluir_dica(id):
    excluir = cinema.query.filter_by(id=id).first()
    db.session.delete(excluir)
    db.session.commit()
    return redirect(url_for('cinemas'))

if __name__ == "__main__":
    db.create_all()  
    app.run(debug=True)