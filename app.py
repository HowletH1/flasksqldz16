from flask import Flask, request
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy

import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(10))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
        }


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id,
        }


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,
        }


with app.app_context():
    db.create_all()

    for usr_data in data.Users:
        db.session.add(User(**usr_data))
        db.session.commit()

    for ord_data in data.Orders:
        ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%m/%d/%Y').date()
        ord_data['end_date'] = datetime.strptime(ord_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**ord_data))
        db.session.commit()

    for ofr_data in data.Offers:
        db.session.add(Offer(**ofr_data))
        db.session.commit()


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        user_a = User.query.all()
        res = [usr.to_dict() for usr in user_a]
        return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return '', 201


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    if request.method == 'GET':
        user_r = User.query.get(uid).to_dict()
        return json.dumps(user_r), 200, {'Content-Type': 'application/json; charset=utf-8'}
    if request.method == 'DELETE':
        user_r = User.query.get(uid)
        db.session.delete(user_r)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        user_d = json.loads(request.data)
        user_r = User.query.get(uid)
        user_r.first_name = user_d['first_name']
        user_r.last_name = user_d['last_name']
        user_r.role = user_d['role']
        user_r.phone = user_d['phone']
        user_r.email = user_d['email']
        user_r.age = user_d['age']
        db.session.add(user_r)
        db.session.commit()
        return '', 204


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        order_s = Order.query.all()
        res = []
        for order in order_s:
            ord_d = order.to_dict()
            ord_d['start_date'] = str(ord_d['start_date'])
            ord_d['end_date'] = str(ord_d['end_date'])
            res.append(ord_d)
        return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        order_data = json.loads(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()
        return '', 201


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid: int):
    if request.method == 'GET':
        return json.dumps(Order.query.get(oid).to_dict()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        order_r = Order.query.get(oid)
        db.session.delete(order_r)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        order_r = Order.query.get(oid)
        order_d = json.loads(request.data)
        order_d['start_date'] = datetime.strptime(order_d['start_date'], '%Y-%m-%d').date()
        order_d['end_date'] = datetime.strptime(order_d['end_date'], '%Y-%m-%d').date()

        order_r.name = order_d['name']
        order_r.description = order_d['description']
        order_r.start_date = order_d['start_date']
        order_r.end_date = order_d['end_date']
        order_r.price = order_d['price']
        order_r.customer_id = order_d['customer_id']
        order_r.executor_id = order_d['executor_id']
        db.session.add(order_r)
        db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        offers_s = Offer.query.all()
        res = [ofr.to_dict() for ofr in offers_s]
        return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return '', 201


@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid: int):
    if request.method == 'GET':
        return json.dumps(Offer.query.get(oid).to_dict()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        offer_r = Offer.query.get(oid)
        db.session.delete(offer_r)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        offer_d = json.loads(request.data)
        offer_r = Offer.query.get(oid)
        offer_r.offer_id = offer_d['order_id']
        offer_r.executor_id = offer_d['executor_id']
        db.session.add(offer_r)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
