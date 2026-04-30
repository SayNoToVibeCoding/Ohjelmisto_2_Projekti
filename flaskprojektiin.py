from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(username, password)

        return "Toimii!"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)