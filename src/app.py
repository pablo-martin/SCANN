import sys
import logging
from flask import Flask, request, jsonify, render_template
from model import inference

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    contract = request.form["contract"]
    ranked_NN = inference(contract)    
    
    app.logger.info(ranked_NN)
    return render_template('index.html', **ranked_NN)

@app.route('/view_contracts', methods=['POST'])
def view_contracts():
    if request.method == 'POST':
        if request.form.get('action1') == 'view1':
            app.logger.info("action1")
        elif  request.form.get('action2') == 'view2':
            app.logger.info("action2")
        else:
            app.logger.info(request.form.get('a1'))
            app.logger.info(request.form.get('a2'))
    return render_template("user_session.html")

if __name__ == "__main__":
    app.run(debug=True)
    
    
    