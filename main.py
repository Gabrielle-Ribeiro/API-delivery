from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json

app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello World!'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD = 'mysql+mysqlconnector',
        usuario = 'root',
        senha = 'root',
        servidor = 'localhost',
        database = 'delivery'
    )
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente = db.Column(db.String(100), nullable=False)
    produto = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)

class PedidoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pedido
        load_instance = True
        sqla_session = db.session

@app.route('/')
def lista_pedidos():
    pedidos = Pedido.query.all()
    pedidos_schema = PedidoSchema(many=True)
    return pedidos_schema.dump(pedidos)

@app.route('/criapedido', methods=['POST'])
def cria_pedido():
    cliente = request.json['cliente']
    produto = request.json['produto']
    valor = request.json['valor']

    novo_pedido = Pedido(cliente=cliente, produto=produto, valor=valor)
    db.session.add(novo_pedido)
    db.session.commit()

    pedido_schema = PedidoSchema()
    return pedido_schema.dump(novo_pedido)


@app.route('/pedido/<int:id>', methods=['GET'])
def le_pedido(id):
    pedido = Pedido.query.filter(Pedido.id == id).one_or_none()

    if pedido is not None:
        pedido_schema = PedidoSchema()
        return pedido_schema.dump(pedido)
    else:
        return Response(json.dumps({'Erro': 'Nao encontramos um pedido!'}), status=404)

@app.route('/atualizapedido/<int:id>', methods=['PUT'])
def atualiza_pedido(id):
    pedido = Pedido.query.filter(Pedido.id == id).one_or_none()

    if pedido is not None:
        pedido.cliente = request.json['cliente']
        pedido.produto = request.json['produto']
        pedido.valor = request.json['valor']

        db.session.merge(pedido)
        db.session.commit()

        pedido_schema = PedidoSchema()
        return pedido_schema.dump(pedido), 201
    else:
        return Response(json.dumps({'Erro': 'Nao encontramos um pedido!'}), status=404)

@app.route('/apagapedido/<int:id>', methods=['DELETE'])
def apaga_padido(id):
    pedido = Pedido.query.filter(Pedido.id == id).one_or_none()

    if pedido is not None:
        db.session.delete(pedido)
        db.session.commit()
        pedido_schema = PedidoSchema()
        return pedido_schema.dump(pedido)
    else:
        return Response(json.dumps({'Erro': 'Nao encontramos um pedido!'}), status=404)


app.config['DEBUG'] = True
app.run()