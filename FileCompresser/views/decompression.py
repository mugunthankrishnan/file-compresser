import os
import zlib
from zipfile import ZipFile
from helpers.preProcessOps import *
from flask import Blueprint, render_template, request, send_file

decompress = Blueprint('decompressfile', __name__)

# Global Variables
filestreams = []
filenames = []
keys = []
contents=[]

@decompress.route('/decompress', methods=['GET','POST'])
def decompressPage():
    enabledwnld = False
    if request.method == "GET":
        empty_tmp_folder()
        filestreams.clear()
        filenames.clear()
    
    if request.method == "POST":
        # Run pre processing steps for database.
        fs = preProcessOps()
        # Upload a file and its metadata.
        if request.form.get("upload"):
            input_file = request.files['file']
            if input_file.filename and input_file.filename not in filenames:
                data = input_file.stream.read()
                filestreams.append(data)
                filenames.append(input_file.filename)

        # Decompress the uploaded files when decompress button is clicked.
        if request.form.get("decompress"):
            for f in range(len(filestreams)):
                decompressed_data = zlib.decompress(filestreams[f])
                key = fs.put(decompressed_data, filename=filenames[f])
                keys.append(key)
                contents.append(fs.get(key).read())
            
            # Create the files in the tmp directory in Heroku Ephemeral Filesystem
            for i in range(len(filenames)):
                file_path = '/tmp/' + filenames[i]
                with open(file_path, 'wb') as f:
                    f.write(contents[i])
            enabledwnld = True

        # Download the decompressed files as a zip file when download file button is clicked.
        if request.form.get("download"):
            enabledwnld = False
            zipfilePath = '/tmp/decompressed.zip'
            with ZipFile(zipfilePath, 'w') as zipObj:
                # Add multiple files to the zip
                for f in filenames:
                    toBeZippedFileName = '/tmp/' + f
                    zipObj.write(toBeZippedFileName, os.path.basename(toBeZippedFileName))
            filenames.clear()
            filestreams.clear()
            return send_file(zipfilePath, as_attachment=True, download_name='decompressed.zip')
    
    return render_template('decompress.html', enabledwnld=enabledwnld, filenames=filenames)