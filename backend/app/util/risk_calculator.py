import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/send-test', methods=['GET'])
def send_test():
    try:
        response = requests.post("http://172.26.21.246:5001/test", json={"msg": "hello GPU"})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
