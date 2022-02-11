from flask import Flask
import os
app = Flask(__name__)


if __name__ == "__main__":

	from canon_lenses.routes import routes
	app.register_blueprint(routes)
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
	