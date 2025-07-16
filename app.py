from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
#Bibliotecas simplelogin e login_required são necessárias para fazer um sistema simples de login
from flask_simplelogin import SimpleLogin, login_required
import os

#Criando o cenário da aplicação
app = Flask(__name__)
#Criando o arquivo de configuração e passando qual será o banco utilizado
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padaria.db"
#Criando as Configurações de Login, aqui são as autenticações
app.config["SECRET_KEY"] = "MinhaChave10000#"
app.config["SIMPLELOGIN_USERNAME"] = "tiago"
app.config["SIMPLELOGIN_PASSWORD"] = "bemvindoaoaplicativo"
#iniciando a variável do banco
db = SQLAlchemy()
#passando aplicação no qual o banco está funcionando
db.init_app(app)
#Fazendo com que o Flask gere a rota de login
SimpleLogin(app)

#Fazendo o mapeamento da tabela [Objeto relacional] com seu construtor, deixando os arquivos privados para evitar falhas em segurança.
class Product(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    ingredientes = db.Column(db.String(500))
    origem = db.Column(db.String(100))
    imagem = db.Column(db.String(100))

    def __init__(self, nome:str, descricao:str, ingredientes:str, origem:str, imagem:str) -> None:
        self.nome = nome
        self.descricao = descricao
        self.ingredientes = ingredientes
        self.origem = origem
        self.imagem = imagem


#Rota principal da aplicação
@app.route("/")
@login_required
def home():
    return render_template('index.html')

#Rota de listar produtos e pesquisar por um
@app.route("/listar_produtos", methods=["GET", "POST"])
@login_required
def listar_produtos():
    if request.method== "POST":
        #Termo recebido da pesquisa
        termo = request.form["pesquisa"]
        #Variavel que recebe o resultado da busca filtrada do termo no banco de dados
        resultado = db.session.execute(db.select(Product).filter(Product.nome.like(f'%{termo}%'))).scalars()
        return render_template('produtos.html', produtos=resultado)
    else:
        #Cria variável produtos para receber os dados, inicia uma sessão no banco de dados e faz um select de Produtos que foram declarados acima
        produtos = db.session.execute(db.select(Product)).scalars()
        return render_template('produtos.html', produtos=produtos)

#Rota para cadastrar produtos
@app.route("/cadastrar_produto", methods=["GET", "POST"])
@login_required
def cadastrar_produto():
    if request.method== "POST":
        status = {"type": "sucesso", "message": "Produto cadastrado com sucesso"}
        dados=request.form
        imagem=request.files['imagem']
        try:
            produto = Product(dados['nome'],
                            dados['descricao'],
                            dados['ingredientes'],
                            dados['origem'], 
                            imagem.filename)
            imagem.save(os.path.join('static/imagens', imagem.filename))
            db.session.add(produto)
            db.session.commit()
        except:
            status = {"type": "erro", "message": f"Houve um problema ao cadastrar o produto {dados['nome']}!"}
        return render_template("cadastrar.html", status = status)
    else:
        return render_template("cadastrar.html")


#Rota para Editar um produto
@app.route("/editar_produto/<int:id>", methods=["GET", "POST"])
@login_required
def editar_produto(id):
    if request.method == "POST":
        dados_editados = request.form
        imagem = request.files['imagem']
        produto = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()

        produto.nome = dados_editados["nome"]
        produto.descricao = dados_editados["descricao"]
        produto.ingredientes = dados_editados["ingredientes"]
        produto.origem = dados_editados["origem"]

        if imagem.filename:
            produto.imagem = imagem.filename
            imagem.save(os.path.join('static/imagens', imagem.filename))

        db.session.commit()

        return redirect("/listar_produtos")
    else:
        produto_editado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
        return render_template("editar.html", produto=produto_editado)



#Rota para deletar produto do banco
@app.route("/deletar_produto/<int:id>")
@login_required
def deletar_produto(id):
    produto_deletado = db.session.execute(db.select(Product).filter(Product.id == id)).scalar()
    db.session.delete(produto_deletado)
    db.session.commit()
    return redirect("/listar_produtos")


if __name__ == '__main__':
    with app.app_context():
        #Criando o banco de dados, SEMPRE TEM DE SER USADO ANTES DO app.run()
        db.create_all()
        app.run()

