import uuid

from flask import Flask, render_template
from square.client import Client
from flask_sqlalchemy import SQLAlchemy

from tokens import SQUARE_ACCESS_TOKEN


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
db = SQLAlchemy(app)
cart = []
url = "http://127.0.0.1:4000"


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)

    def __init__(self, status):
        self.status = status

    def save(self):
        db.session.add(self)
        db.session.commit()

    def find_by_id(self, id):
        return Image.query.filter_by(id=id).first()


db.create_all()
db.session.commit()
for i in range(1,11):
    try:
        image = Image(False)
        db.session.add(image)
    except:
        print("table insertion failure")
db.session.commit()

@app.route('/')
def home():
    return render_template('home.html', url=url)


@app.route('/<int:id>')
def image(id):
    return render_template('image.html', url=url)


@app.route('/buy/<int:id>')
def purchase(id):
    current_image = Image.find_by_id(self=Image, id=id)
    if current_image.status:
        return render_template('purchase_failed.html', url=url)
    client = Client(
        access_token=SQUARE_ACCESS_TOKEN,
        environment='sandbox')

    result = client.payments.create_payment(
        body={
            "amount_money": {
                "amount": 100,
                "currency": "USD"
            },
            "idempotency_key": str(uuid.uuid4()),
            "source_id": "cnon:card-nonce-ok"
        }
    )
    current_image.status = True
    current_image.save()
    cart.append(id)
    return render_template('purchase_successful.html', url=url)


@app.route('/cart')
def show_cart():
    stringified = [f"{item}" for item in cart]
    return render_template('cart.html', cart=stringified, url=url)


if __name__ == "__main__":
    from waitress import serve
    # app.run(port=4000)
    print("App has started.")
    serve(app, host="0.0.0.0", port=4000)
    purge = 'DROP TABLE IF EXISTS images;'
    result = db.engine.execute(purge)