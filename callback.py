from flask import Flask, request
from werkzeug.serving import make_server, BaseWSGIServer
import threading

'''
The callback server that listens for the callback code.
Once loaded it can be started by calling Callback.start(),
and stopped with Callback.stop()
'''

class Callback:
    def __init__(self, host='localhost', port=9999) -> None:
        self.host: str = host
        self.port: int = port
        self.key: str = None
        self.server: BaseWSGIServer = None
        self.flask_thread : threading = None
        self.app: Flask = None
        self.new_server(host, port)
    
    def new_server(self, host='localhost', port=9999):
        if self.flask_thread != None or self.server != None:
            self.stop()
        
        app = Flask(__name__)

        @app.route('/callback')
        def callback():
            if request.args.get('code'):
                self.key = request.args.get('code')
            elif request.args.get('token'):
                self.key = request.args.get('token')
            else:
                self.stop()
                raise ValueError("Code was not recieved from auth server")
            return self.html_wrap(self.key)

        self.host = host
        self.port = port
        self.key = None
        self.app = app
    
    def start(self):
        if self.server != None or self.flask_thread != None:
            print('There is a server running already')
            return

        self.server = make_server(self.host, self.port, self.app)
        self.flask_thread = threading.Thread(target=lambda: self.server.serve_forever())
        self.flask_thread.start()
    
    def stop(self):
        self.server.shutdown()
        self.flask_thread.join()
        self.server = None
        self.flask_thread = None

    def get_key(self):
        return self.key
    
    def html_wrap(self, key):
        return f'<textarea type=text name="key-box" readonly>{key}</textarea>'