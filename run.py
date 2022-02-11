from flask import Flask
app = Flask(__name__)


if __name__=="__main__":
	

	from canon_lenses.routes import routes
	app.register_blueprint(routes)
	app.run(debug=False)
	