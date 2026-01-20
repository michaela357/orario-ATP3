from flask import Flask, render_template, url_for, redirect, request
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/create_task', methods=["GET", "POST"])
def create_task():
    return render_template('create_task.html')

@app.route('/delete_task')
def delete_task():
	return render_template('delete_task.html')

@app.route('/update_task')
def update_task():
	return render_template('update_task.html')


if __name__ == '__main__':
	app.run()
