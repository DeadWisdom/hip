import clevercss, os
static = os.path.abspath(os.path.join(__file__, '..', 'static'))
css = os.path.join(static, 'css')

def compile():
    print " * Compiling CSS"
    total = []
    for filename in os.listdir(css):
        path = os.path.join(css, filename)
        with open(path) as file:
            if path.endswith('.clever'):
                total.append("\n/* %s */" % filename)
                total.append(clevercss.convert(file.read()))
            else:
                total.append("\n/* %s */" % filename)
                total.append(file.read())
    with open(os.path.join(static, 'style.css'), 'w') as file:
        file.write("\n".join(total).strip())