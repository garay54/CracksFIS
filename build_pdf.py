import markdown

md_path = r'C:\Users\Garay\OneDrive\Desktop\grietas\FIS\comentarios_consenso_natural.md'
html_path = r'C:\Users\Garay\OneDrive\Desktop\grietas\FIS\_temp.html'

with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

html_body = markdown.markdown(md_content, extensions=['extra', 'nl2br'])

css = '''
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px; background: #282c34; color: #abb2bf; line-height: 1.7; }
  h1 { color: #e06c75; border-bottom: 2px solid #e06c75; padding-bottom: 10px; }
  h2 { color: #e5c07b; margin-top: 30px; }
  h3 { color: #61afef; margin-top: 25px; }
  h4 { color: #c678dd; }
  strong { color: #e5c07b; }
  blockquote { background: #21252b; border-left: 3px solid #61afef; padding: 12px 18px; margin: 10px 0; color: #98c379; }
  table { border-collapse: collapse; width: 100%; margin: 20px 0; }
  td, th { padding: 8px 14px; border: 1px solid #4b5263; }
  th { background: #21252b; color: #e5c07b; }
  code { background: #21252b; color: #e06c75; padding: 2px 6px; border-radius: 3px; }
  hr { border: 0; border-top: 1px solid #4b5263; margin: 25px 0; }
  a { color: #61afef; }
</style>
'''

full_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
{css}
</head>
<body>
{html_body}
</body>
</html>'''

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print('HTML OK')
