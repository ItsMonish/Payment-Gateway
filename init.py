from flask import Flask,render_template

service = Flask(__name__)

@service.route("/")
def display_doc():
    return render_template('index.html')



if __name__ == "__main__":
    service.run(debug=True)