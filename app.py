import sqlite3
import csv
import io
import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import html

class LinkManager:
    def __init__(self, db_path='links.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                tags TEXT,
                url TEXT NOT NULL,
                file_group TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_all_links(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM links')
        links = cursor.fetchall()
        conn.close()
        return [{'id': l[0], 'description': l[1], 'tags': l[2], 'url': l[3], 'file_group': l[4]} for l in links]
    
    def get_links_by_group(self, group):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM links WHERE file_group = ?', (group,))
        links = cursor.fetchall()
        conn.close()
        return [{'id': l[0], 'description': l[1], 'tags': l[2], 'url': l[3], 'file_group': l[4]} for l in links]
    
    def search_links(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM links 
            WHERE description LIKE ? OR tags LIKE ? OR url LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        links = cursor.fetchall()
        conn.close()
        return [{'id': l[0], 'description': l[1], 'tags': l[2], 'url': l[3], 'file_group': l[4]} for l in links]
    
    def add_link(self, description, tags, url, file_group):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO links (description, tags, url, file_group)
            VALUES (?, ?, ?, ?)
        ''', (description, tags, url, file_group))
        conn.commit()
        conn.close()
    
    def update_link(self, link_id, description, tags, url, file_group):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE links 
            SET description = ?, tags = ?, url = ?, file_group = ?
            WHERE id = ?
        ''', (description, tags, url, file_group, link_id))
        conn.commit()
        conn.close()
    
    def delete_link(self, link_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM links WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()
    
    def get_link(self, link_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM links WHERE id = ?', (link_id,))
        link = cursor.fetchone()
        conn.close()
        if link:
            return {'id': link[0], 'description': link[1], 'tags': link[2], 'url': link[3], 'file_group': link[4]}
        return None
    
    def get_groups(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT file_group FROM links')
        groups = cursor.fetchall()
        conn.close()
        return [g[0] for g in groups]
    
    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM links')
        total_links = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT file_group) FROM links')
        total_groups = cursor.fetchone()[0]
        cursor.execute('''
            SELECT file_group, COUNT(*) as count 
            FROM links 
            GROUP BY file_group 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        most_group = cursor.fetchone()
        conn.close()
        return {
            'total_links': total_links,
            'total_groups': total_groups,
            'most_group': most_group
        }

class LinkHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.link_manager = LinkManager()
        super().__init__(*args, **kwargs)
    
    def parse_form_data(self):
        """Parse form data from POST request"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = {}
        
        # Check if it's multipart form data
        if 'multipart/form-data' in self.headers.get('Content-Type', ''):
            # Simple multipart parsing for file uploads
            boundary = self.headers.get('Content-Type').split('boundary=')[1]
            parts = post_data.split('--' + boundary)
            
            for part in parts:
                if 'Content-Disposition: form-data' in part:
                    lines = part.split('\r\n')
                    for i, line in enumerate(lines):
                        if 'name=' in line:
                            name = line.split('name="')[1].split('"')[0]
                            if i + 2 < len(lines):
                                value = lines[i + 2]
                                form_data[name] = value
                            break
        else:
            # Regular form data
            pairs = post_data.split('&')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    form_data[urllib.parse.unquote_plus(key)] = urllib.parse.unquote_plus(value)
        
        return form_data
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/':
            group = query_params.get('group', [None])[0]
            if group:
                links = self.link_manager.get_links_by_group(group)
            else:
                links = self.link_manager.get_all_links()
            groups = self.link_manager.get_groups()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.render_index(links, groups).encode('utf-8'))
        
        elif path == '/add':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.render_add_form().encode('utf-8'))
        
        elif path.startswith('/edit/'):
            link_id = int(path.split('/')[-1])
            link = self.link_manager.get_link(link_id)
            if link:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.render_edit_form(link).encode('utf-8'))
            else:
                self.send_error(404)
        
        elif path == '/search':
            query = query_params.get('q', [''])[0]
            links = self.link_manager.search_links(query)
            groups = self.link_manager.get_groups()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.render_index(links, groups, search=query).encode('utf-8'))
        
        elif path == '/stats':
            stats = self.link_manager.get_stats()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.render_stats(stats).encode('utf-8'))
        
        elif path.startswith('/export/'):
            fmt = path.split('/')[-1]
            links = self.link_manager.get_all_links()
            if fmt == 'csv':
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.send_header('Content-Disposition', 'attachment; filename=links.csv')
                self.end_headers()
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['Description', 'Tags', 'URL', 'File Group'])
                for link in links:
                    writer.writerow([link['description'], link['tags'], link['url'], link['file_group']])
                self.wfile.write(output.getvalue().encode('utf-8'))
            elif fmt == 'json':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Disposition', 'attachment; filename=links.json')
                self.end_headers()
                data = [{'description': l['description'], 'tags': l['tags'], 'url': l['url'], 'file_group': l['file_group']} for l in links]
                self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
            else:
                self.send_error(400)
        
        elif path == '/import':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.render_import_form().encode('utf-8'))
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/add':
            form_data = self.parse_form_data()
            description = form_data.get('description', '')
            tags = form_data.get('tags', '')
            url = form_data.get('url', '')
            file_group = form_data.get('file_group', '')
            
            if not url.startswith('http://') and not url.startswith('https://'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.render_add_form(error='URL must start with http:// or https://').encode('utf-8'))
                return
            
            self.link_manager.add_link(description, tags, url, file_group)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        elif path.startswith('/edit/'):
            link_id = int(path.split('/')[-1])
            form_data = self.parse_form_data()
            description = form_data.get('description', '')
            tags = form_data.get('tags', '')
            url = form_data.get('url', '')
            file_group = form_data.get('file_group', '')
            
            self.link_manager.update_link(link_id, description, tags, url, file_group)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        elif path.startswith('/delete/'):
            link_id = int(path.split('/')[-1])
            self.link_manager.delete_link(link_id)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        elif path == '/import':
            # For now, we'll skip file import functionality to keep it simple
            # You can implement it later if needed
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
    
    def render_index(self, links, groups, search=''):
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Web Links Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; }
                .nav { margin-bottom: 20px; text-align: center; }
                .nav a { margin: 0 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .nav a:hover { background: #0056b3; }
                .search-box { margin: 20px 0; text-align: center; }
                .search-box input { padding: 10px; width: 300px; border: 1px solid #ddd; border-radius: 5px; }
                .search-box button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .group-filter { margin: 20px 0; text-align: center; }
                .group-filter select { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; font-weight: bold; }
                .action-buttons a { margin-right: 10px; padding: 5px 10px; text-decoration: none; border-radius: 3px; }
                .edit-btn { background: #ffc107; color: #212529; }
                .delete-btn { background: #dc3545; color: white; }
                .url-cell { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Web Links Manager</h1>
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/add">Add Link</a>
                    <a href="/import">Import</a>
                    <a href="/stats">Stats</a>
                </div>
                
                <div class="search-box">
                    <form action="/search" method="GET">
                        <input type="text" name="q" placeholder="Search links..." value="''' + html.escape(search) + '''">
                        <button type="submit">Search</button>
                    </form>
                </div>
                
                <div class="group-filter">
                    <select onchange="window.location.href=this.value">
                        <option value="/">All Groups</option>
        '''
        
        for group in groups:
            html_content += f'<option value="/?group={urllib.parse.quote(group)}">{html.escape(group)}</option>'
        
        html_content += '''
                    </select>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Tags</th>
                            <th>URL</th>
                            <th>Group</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        '''
        
        for link in links:
            html_content += f'''
                        <tr>
                            <td>{html.escape(link['description'])}</td>
                            <td>{html.escape(link['tags'] or '')}</td>
                            <td class="url-cell"><a href="{html.escape(link['url'])}" target="_blank">{html.escape(link['url'])}</a></td>
                            <td>{html.escape(link['file_group'])}</td>
                            <td>
                                <a href="/edit/{link['id']}" class="action-buttons edit-btn">Edit</a>
                                <form method="POST" action="/delete/{link['id']}" style="display: inline;">
                                    <button type="submit" class="action-buttons delete-btn" onclick="return confirm('Are you sure?')">Delete</button>
                                </form>
                            </td>
                        </tr>
            '''
        
        html_content += '''
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        '''
        return html_content
    
    def render_add_form(self, error=''):
        error_html = f'<div class="error">{html.escape(error)}</div>' if error else ''
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Add Link - Web Links Manager</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background: #0056b3; }}
                .error {{ color: red; margin-bottom: 10px; }}
                .back-link {{ margin-top: 20px; text-align: center; }}
                .back-link a {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Add New Link</h1>
                {error_html}
                <form method="POST">
                    <div class="form-group">
                        <label for="description">Description:</label>
                        <input type="text" id="description" name="description" required>
                    </div>
                    <div class="form-group">
                        <label for="tags">Tags:</label>
                        <input type="text" id="tags" name="tags">
                    </div>
                    <div class="form-group">
                        <label for="url">URL:</label>
                        <input type="url" id="url" name="url" required>
                    </div>
                    <div class="form-group">
                        <label for="file_group">Group:</label>
                        <input type="text" id="file_group" name="file_group" required>
                    </div>
                    <button type="submit">Add Link</button>
                </form>
                <div class="back-link">
                    <a href="/">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        '''
    
    def render_edit_form(self, link):
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Edit Link - Web Links Manager</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background: #0056b3; }}
                .back-link {{ margin-top: 20px; text-align: center; }}
                .back-link a {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Edit Link</h1>
                <form method="POST">
                    <div class="form-group">
                        <label for="description">Description:</label>
                        <input type="text" id="description" name="description" value="{html.escape(link['description'])}" required>
                    </div>
                    <div class="form-group">
                        <label for="tags">Tags:</label>
                        <input type="text" id="tags" name="tags" value="{html.escape(link['tags'] or '')}">
                    </div>
                    <div class="form-group">
                        <label for="url">URL:</label>
                        <input type="url" id="url" name="url" value="{html.escape(link['url'])}" required>
                    </div>
                    <div class="form-group">
                        <label for="file_group">Group:</label>
                        <input type="text" id="file_group" name="file_group" value="{html.escape(link['file_group'])}" required>
                    </div>
                    <button type="submit">Update Link</button>
                </form>
                <div class="back-link">
                    <a href="/">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        '''
    
    def render_import_form(self):
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Import Links - Web Links Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .back-link { margin-top: 20px; text-align: center; }
                .back-link a { color: #007bff; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Import Links</h1>
                <p style="text-align: center; color: #666;">File import functionality is currently disabled.</p>
                <div class="back-link">
                    <a href="/">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        '''
    
    def render_stats(self, stats):
        most_group_text = f"{stats['most_group'][0]} ({stats['most_group'][1]} links)" if stats['most_group'] else "None"
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Statistics - Web Links Manager</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; }}
                .stat-item {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
                .stat-label {{ font-weight: bold; color: #495057; }}
                .stat-value {{ font-size: 1.2em; color: #007bff; margin-top: 5px; }}
                .back-link {{ margin-top: 20px; text-align: center; }}
                .back-link a {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Statistics</h1>
                <div class="stat-item">
                    <div class="stat-label">Total Links:</div>
                    <div class="stat-value">{stats['total_links']}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Groups:</div>
                    <div class="stat-value">{stats['total_groups']}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Most Popular Group:</div>
                    <div class="stat-value">{html.escape(most_group_text)}</div>
                </div>
                <div class="back-link">
                    <a href="/">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        '''

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, LinkHandler)
    print(f"Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    run_server() 