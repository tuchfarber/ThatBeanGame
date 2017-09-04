class API:
    '''API endpoint'''
    def __init__(self, route, method):
        self.route = route
        self.method = method
        self.name = ''
        self.params = []
    
    def __str__(self):
        return str(vars(self))

all_apis = []
with open("app/TBG.py", 'r') as source:
    api = None
    doc_string = False
    for line in source:
        if '@app.route' in line:
            if api:
                all_apis.append(api)
            split_api = line.split('\'')
            api = API(split_api[1], split_api[3])
        elif 'def ' in line and api:
            name = line[4:line.index('(')]
            api.name = name
        elif "'''" in line:

            doc_string 
            docstring = ''
        elif 'post_data[' in line:
            param = {}
            param['type'] = line[line.index(': ')+1:line.index('=')].strip()
            param['value'] = line[line.index("post_data['")+11:line.index("']")]
            api.params.append(param)
    for api in all_apis:
        print(api)

with open('docs/api.rst', 'w') as doc:
    lines = []
    lines.append('===\nAPI\n===')
    for api in all_apis:
        lines.append('{}\n------'.format(api.name.replace('_',' ')))
        lines.append('Route: {}'.format(api.route))
        lines.append('Method: {}'.format(api.method))
        lines.append('Params:')
        for param in api.params:
            lines.append('* {} ({})'.format(param['value'],param['type']))
    doc.write('\n\n'.join(lines))

