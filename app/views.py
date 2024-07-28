import os
from flask import render_template, send_from_directory, request, current_app as app

FILE_ICONS = {
    '.txt': 'icons/text.png',
    '.pdf': 'icons/pdf.png',
    '.jpg': 'icons/jpg.png',
    '.jpeg': 'icons/jpeg.png',
    '.png': 'icons/png.png',
    '.gif': 'icons/gif.png',
    '.doc': 'icons/word.png',
    '.docx': 'icons/word.png',
    '.xls': 'icons/excel.png',
    '.xlsx': 'icons/excel.png',
    '.ppt': 'icons/ppt.png',
    '.pptx': 'icons/ppt.png',
    '.zip': 'icons/zip.png',
    '.rar': 'icons/rar.png',
    '.7z': 'icons/7z.png',
    '.tar.gz': 'icons/zip.png',
    '.tar': 'icons/zip.png',
    '.tar.xz': 'icons/zip.png',
    '.csv': 'icons/excel.png',
    '.iso': 'icons/iso.png',
    '.img': 'icons/floppy.png',
}

DEFAULT_ICON = 'icons/unknown.png'

@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    base_path = os.path.join(app.root_path, 'files')
    current_path = os.path.join(base_path, subpath)

    if not os.path.exists(current_path):
        return "Directory does not exist", 404

    files = []
    directories = []
    for root, dirs, filenames in os.walk(current_path):
        for dirname in dirs:
            dir_path = os.path.join(root, dirname)
            relative_path = os.path.relpath(dir_path, base_path)
            directories.append(relative_path)

        for filename in filenames:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            ext = os.path.splitext(filename)[1].lower()
            icon = FILE_ICONS.get(ext, DEFAULT_ICON)
            files.append({
                'path': os.path.relpath(file_path, base_path),
                'name': filename,
                'size': file_size,
                'icon': icon
            })
        break

    empty_message = None
    if not directories and not files:
        empty_message = "Empty directory"

    if subpath:
        parent_path = os.path.dirname(subpath)
        if parent_path == '':
            parent_path = None
    else:
        parent_path = None 

    return render_template('index.html', files=files, directories=directories, parent_path=parent_path, empty_message=empty_message)

@app.route('/download/<path:filename>')
def download(filename):
    base_path = os.path.join(app.root_path, 'files')
    filename = filename.replace('\\', '/')
    safe_path = os.path.abspath(os.path.join(base_path, filename))

    if not safe_path.startswith(base_path) or not os.path.exists(safe_path):
        abort(404, description="File not found")

    return send_from_directory(base_path, filename, as_attachment=True)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    base_path = os.path.join(app.root_path, 'files')
    results = []

    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            if query.lower() in filename.lower():
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                ext = os.path.splitext(filename)[1].lower()
                icon = FILE_ICONS.get(ext, DEFAULT_ICON)
                results.append({
                    'path': os.path.relpath(file_path, base_path),
                    'name': filename,
                    'size': file_size,
                    'icon': icon
                })

    empty_message = None
    if not results:
        empty_message = "No results found"

    return render_template('search_results.html', results=results, query=query, empty_message=empty_message)
