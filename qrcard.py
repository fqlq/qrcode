import flask
from flask import request, send_file, jsonify
from MyQR import myqr
from PIL import Image
import requests
from io import BytesIO
from re import compile, match, IGNORECASE
import tempfile
import os

app = flask.Flask(__name__)


@app.route('/python/generate', methods=['POST'])
def generate():
    data = request.get_json()

    # Error if data.type doesn't match available code types
    # ONLY FOR QRCARD.BIZ
    if 'type' not in data.keys():
        type = 0
    else:
        if data['type'] not in ('covered', 'framed'):
            response = {
                'status': 'error',
                'cause': 'Code type should be \'covered\' or \'framed\''
            }
            return jsonify(response), 400
        else:
            if data['type'] == 'covered':
                type = 0
            if data['type'] == 'framed':
                type = 1

    print('Code type:', type)

    # Error if data.scale is not integer in available range
    if 'scale' not in data.keys():
        scale = 1
    else:
        try:
            if int(data['scale']) not in range(1, 16):
                response = {
                    'status': 'error',
                    'cause': 'Scale must be in range from 1 to 10'
                }
                return jsonify(response), 400
            else:
                scale = int(data['scale'])
        except ValueError:
            response = {
                'status': 'error',
                'cause': 'Scale must be an integer'
            }
            return jsonify(response), 400

    print('Scale:', scale)

    # Error if data.scale is not integer in available range
    if 'version' not in data.keys():
        version = 1
    else:
        try:
            if int(data['version']) not in range(1, 21):
                response = {
                    'status': 'error',
                    'cause': 'Version must be in range from 1 to 20'
                }
                return jsonify(response), 400
            else:
                version = int(data['version'])
        except ValueError:
            response = {
                'status': 'error',
                'cause': 'Version must be an integer'
            }
            return jsonify(response), 400

    print('Version:', version)

    # Error if data.text doesn't exists
    if 'text' not in data.keys():
        response = {
            'status': 'error',
            'cause': 'Encoding text required'
        }
        return jsonify(response), 400

    # Error if data.text is empty
    if not str(data['text']).strip():
        response = {
            'status': 'error',
            'cause': 'Text shouldn\'t be is empty'
        }
        return jsonify(response), 400

    print('Text:', str(data['text']).strip())

    # Error if image url is not valid if exists
    url_regexp = compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', IGNORECASE)
    if 'image' in data.keys():
        if match(url_regexp, data['image']) is None:
            response = {
                'status': 'error',
                'cause': 'Invalid image url'
            }
            return jsonify(response), 400
        else:
            print('Image downloading from', data['image'], 'started...')
            response = requests.get(data['image'])
            print('Image downloaded successfully', str(response))
            img = Image.open(BytesIO(response.content))
    else:
        img = None

    print('Image:', img)

    # Error if color is not a valid HEX
    if 'color' in data.keys():
        if len(data['color'].lstrip('#')) != 6:
            response = {
                'status': 'error',
                'cause': 'Color must be a valid HEX color'
            }
            return jsonify(response), 400
        else:
            try:
                color = tuple(int(data['color'].lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                response = {
                    'status': 'error',
                    'cause': 'Color must be a valid HEX color'
                }
                return jsonify(response), 400
    else:
        color = (0, 0, 0)

    print('Color:', color)

    if 'gold' in data.keys():
        gold = data['gold']
    else:
        gold = None

    if type == 0:
        print('QR code generation started')
        qr = myqr.run(
            str(data['text']).strip(),
            scale=scale,
            version=version,
            level='H',
            color=color,
            image=img
        )

    if type == 1:
        import framed

        qr = framed.generate(
            str(data['text']).strip(),
            scale=scale,
            version=version,
            level='H',
            color=color,
            image=img,
            imagesize=(4 * 27 * scale, 4 * 27 * scale),
            gold=gold
        )

    print('QR code successfully generated')

    tempdir = tempfile.mkdtemp(prefix='myqr_')

    try:
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        print('Saving to', os.path.join(tempdir, 'qrcode.png'))

        qr.save(os.path.join(tempdir, 'qrcode.png'), format='PNG')

        print('Sending file to request maker')

        return send_file(os.path.join(tempdir, 'qrcode.png'), mimetype='image/png', as_attachment=True), 200
    except:
        response = {
            'status': 'error',
            'cause': 'Service unavailable'
        }
        return jsonify(response), 500
    finally:
        import shutil
        if os.path.exists(tempdir):
            print('Removing temporary files')
            shutil.rmtree(tempdir)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
