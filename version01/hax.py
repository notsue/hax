import argparse, os, sys, json, copy


__VERSION__ = '0.1'
__DATE__ = '2024-06-20'

DEFAULT_CODE = {
    "elementName": {"Q": "quotation",
                    "F": "figure",
                    "CH": ["code", {"class":"language-hax"}]},
    "attributeName": {"P": "property",
                      "T": "title",
                      "AR": "role",
                      "AL": "aria-label",
                      "ALB": "aria-labeledby"},
    "value": {"HAX": "https://github.com/notsue/hax",
              "XML": "https://www.w3.org/TR/xml11/",
              "XMLID": "https://www.w3.org/TR/xml-id/",
              "RDFA": "https://en.wikipedia.org/wiki/RDFa",
              "DC": "https://www.dublincore.org/specifications/dublin-core/dcq-html/"},
    "hax": {".":"class",
            "#": "id",
            "!": "property"},
    "comma": {"a": "href",
              "img": "src",
              "script": "src",
              "style": "src",
              "-": "class"},
    "semicolon": {"a": "target",
                  "img": "alt",
                  "-": "lang"},
    "parent": {"ul": "li",
               "ol": "li",
               "menu": "li",
               "table": "caption",
               "tr": "td",
               "figure": "figcaption",
               "dl": ["dt", "dd"],
                "-": "p"},
    "skip": ["script", "style"],
    "entities": ['code'],
    "metadata": "property"
    
}

class Haxparser():
    
    def __init__(self, config):
        
        self.config = config
        self.void = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']
        
                    
        self.config['basename'] = os.path.basename(self.config['haxfile'])
        self.config['dirname'] = os.path.dirname(self.config['haxfile'])
                
        if self.config['verbose']:
            self.printConfig()
            
        if self.config['code'] == 'default':
            self.code = DEFAULT_CODE
        else:
            self.loadCode()
            
        self.readSource()
        
        self.parse()
        if self.config['format'] in ['html', 'xhtml']:
            self.collectMetadata()
        
        if self.config['verbose']:
            for n in self.nodes:
                if n['type'] in ['starttag', 'empty']:
                    print(n['type'], n['name'], n['attributes'])
                elif n['type'] == 'endtag':
                    print(n['type'], n['name'])
                else:
                    print(n['type'])
        
        self.createXML()
        if not self.config['wait']:
            if self.config['format'] == 'html':
                self.output = html5(self.xml, self.metadata)
            elif self.config['format'] == 'xhtml':
                self.output = xhtml5(self.xml, self.metadata)
            else:
                self.output = xml(self.xml)
            self.writeOutput()
        
    def printConfig(self):
        
        print('\nCONFIG:')
        
        for k in self.config.keys():
            print ('\t%s: %s' % (k, self.config[k]))
            
    def loadCode(self):
        
        p = self.config['code']
        if not os.path.exists(p):
            error("Code file '%s' does not exist" % p, fatal=True)
        try:
            with open(p) as code:
                self.code = json.load(code)
        except json.JSONDecodeError:
            error("Invalid JSON-file (syntax error)",filepath=p, fatal=True)
            
    def readSource(self):
        
        p = self.config['haxfile']
        if not os.path.exists(p):
            error("File does not exist", filepath=p, fatal=True)
        if os.path.isdir(p):
            error("Not a file, but a directory.", filepath=p, fatal=True)
        
        try:
            with open(p) as source:
                self.source = source.read()
        except:
            error("Could not read existing haxfile", filepath=p, fatal=True)
            
    def collectMetadata(self):
        
        self.metadata = {}
        
        select = self.code["metadata"]
        
        i = 0
        while i < len(self.nodes):
            N = self.nodes[i]
            if N['type'] == 'starttag' and select in N['attributes']:
                tagstack = []
                name = N['attributes'][select]
                content = ""
                tagstack.append(N)
                i += 1
                while len(tagstack) > 0:
                    N2 = self.nodes[i]
                    if N2['type'] == 'starttag':
                        tagstack.append(N)
                    elif N2['type'] == 'endtag':
                        tagstack.pop()
                    elif N2['type'] == 'text':
                        content += N2['content']
                    else:
                        pass
                    i += 1
                content = content.replace('\n', ' ')
                content = content.replace('\t', ' ')
                content = content.replace('  ', ' ')
                self.metadata[name] = content   
            i += 1      
                
    def writeOutput(self):
        
        with open(self.config['output'], 'w', encoding="utf-8") as out:
            out.write(self.output)
            
    def xmlx2node(self, tagnode):
        
        tag = tagnode[1].strip()
        
        NODE = {'type': tagnode[0], 'ns': None, 'name': None, 'position': tagnode[2]}
        if tagnode[0] != 'endtag':
            NODE['attributes'] = {}
        
        LIST = ['']
        QUOTE = False
        DONE = True
        
        j = 0 # counter
        
        while j < len(tag):
            char = tag[j]
            if QUOTE == False and "hax" in self.code.keys() and char in self.code['hax'].keys():
                LIST.extend([self.code['hax'][char], "=", ''])
                DONE = True
            elif QUOTE == False and char == ',' and "comma" in self.code.keys():
                if LIST[0] in self.code['comma']:
                    LIST.extend([self.code['comma'][LIST[0]], '=', ''])
                else:
                    LIST.extend([self.code['comma']['-'], '=', ''])
                DONE = True
            elif QUOTE == False and char == ';' and "semicolon" in self.code.keys():
                if LIST[0] in self.code['semicolon']:
                    LIST.extend([self.code['semicolon'][LIST[0]], '=', ''])
                else:
                    LIST.extend([self.code['semicolon']['-'], '=', ''])
                DONE = True
            elif char in ['"', "'"]:
                if QUOTE == False:
                    QUOTE = char
                elif QUOTE == char:
                    QUOTE = False
                else:
                    LIST[-1] += char
                DONE = False
            elif char in ['=', ' ', '\t', '\n']:
                if QUOTE == False:
                    if not DONE:
                        if char == '=':
                            LIST.append('=')
                        LIST.append('')
                        DONE = True
                else:
                    if char in [' ', '\t', '\n']:
                        LIST[-1] += ' '
                    else:
                        LIST[-1] += char
                    DONE = False
            else:
                LIST[-1] += char
                DONE = False
            j += 1
            
        # parsing LIST
        name = LIST[0]
        if ':' in name:
            NODE['ns'], name = name.split(':', 1)
        if name == name.upper():
            if name.startswith("\\"):
                NODE['name'] = name[1:]
            else:
                try:
                    EL =  self.code['elementName'][name]
                except KeyError:
                    error('%s is not listed in HaXcode as a short name for an element' % name, filepath=self.config['basename'], position=tagnode[2], fatal=True)
                
                if isinstance(EL, list):
                    NODE['name'] = EL[0]
                    if NODE['type'] != 'endtag':
                        NODE['attributes'].update(EL[1])
                else:
                    NODE['name'] = EL
        else:
            NODE['name'] = name
            
        j = 1
        while j < len(LIST):
            att = LIST[j]
            if att == att.upper():
                if att.startswith("\\"):
                    att = att[1:]
                else:
                    try:
                        att = self.code["attributeName"][att]
                    except KeyError:
                        error('%s is not a short name for attribute' % att, filepath=self.config['basename'], position=tagnode[2], fatal=True)
            if j < len(LIST) - 2 and LIST[j+1] == '=':
                val = LIST[j+2]
                if val == val.upper(): 
                    if val.strip() == "": # boolean
                        val = ""
                    elif val.startswith("\\"):
                        val = val[1:]
                    elif val[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                        val = val
                    else:
                        try:
                            val = self.code["value"][val]
                        except KeyError:
                            error('%s is not known as attribute-value' % val, filepath=self.config['basename'], position=tagnode[2], fatal=True)
                        
                if att in NODE['attributes'].keys(): # same att as before
                    NODE['attributes'][att] += ' %s' % val
                else:
                    NODE['attributes'][att] = val
                j += 2
            else:
                NODE['attributes'][att] = "" # boolean
            j += 1
        
        if self.config['void'] and NODE['name'] in self.void:
            NODE['type'] = 'empty'  
        return NODE 
    
    def parse(self):
        '''
         elements tagstack are list like ['p': 0]
         the integer serves as a counter, used in hax2xmlx(): 0 = first child, 1 = second child ...
        '''

        self.source += '  '
        entities = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
        line = 1
        col = 0
        state = 'text'
        modus = 'hax'
        quote = None
        fragment = ''
        position = []
        self.nodes = []
        tagstack = []
        i = 0
        
        def hax2xmlx(haxtag):
            '''convert haxtag to xmlx-starttag'''
            xmlx = ''
            markers = [',', ';', '@']
            markers.extend(self.code['hax'].keys())
            quote = False
            if len(tagstack) == 0:
                parent = '-'
            else:
                if ':' in tagstack[-1][0]:
                    ns,parent = tagstack[-1][0].split(':')
                else:
                    parent = tagstack[-1][0]
                if parent not in self.code['parent'].keys():
                    parent = '-'
            
            j = 0   
            while j < len(haxtag):
                char = haxtag[j]
                if char in markers and xmlx == '': # no name
                    child = self.code['parent'][parent]
                    if isinstance(child, str):
                        xmlx += child
                    else:
                        xmlx += child[tagstack[-1][1]]
                        tagstack[-1][1] += 1
                        tagstack[-1][1] = tagstack[-1][1] % len(child) # alternating counter
                    
                if char in ['"', "'"]:
                    if quote == False:
                        quote = char
                    elif quote == char:
                        quote = False
                    xmlx += char
                elif char in [' ', '\n', '\t']:
                    if quote == False:
                        if xmlx == '':
                            child = self.code['parent'][parent] # no name
                            if isinstance(child, str):
                                xmlx += child
                            else:
                                xmlx += child[tagstack[-1][1]]
                                tagstack[-1][1] += 1
                                tagstack[-1][1] = tagstack[-1][1] % len(child) # alternating counter
                        return xmlx
                    else:
                        xmlx += char
                elif char == '@':
                    if quote == False:
                        xmlx += ' '
                    else:
                        xmlx += char
                else:
                    xmlx += char
                j += 1
            
        while i < len(self.source) - 2:
            char = self.source[i]
            nxt = self.source[i+1]
            nxt2 = self.source[i+2]
                        
            if state=='comment':
                if  char == '-' and nxt == '-' and nxt2 == '>':
                    fragment += '-->'
                    i += 2; col +=2
                    position.extend([line,col+1])
                    self.nodes.append({'type': state,'content': fragment, 'position': position})
                    state = 'text'; fragment = ''
                else:
                    fragment += char
            elif state=='cdata':
                if char == ']' and nxt == ']' and nxt2 == '>':
                    fragment += ']]>'
                    i += 2; col +=2
                    position.extend([line,col+1])
                    self.nodes.append({'type': state,'content': fragment, 'position': position})
                    state = 'text'; fragment = ''
                else:
                    fragment += char
            elif state == 'pi':
                if char == '?' and nxt == '>':
                    fragment += '?>'
                    i += 1; col += 1
                    position.extend([line,col+1])
                    self.nodes.append({'type': state,'content': fragment, 'position': position})
                    state = 'text'; fragment = ''
                else:
                    fragment += char
            elif state == 'declaration':
                if char == '>':
                    fragment += '>'
                    position.extend([line,col+1])
                    self.nodes.append({'type': state,'content': fragment, 'position': position})
                    state = 'text'; fragment = ''
                else:
                    fragment += char
            elif state in ['skip', 'entities']:
                if char == '<' and nxt== '/' and nxt2 == '/':
                    position.extend([line,col])
                    self.nodes.append({'type': state,'content': fragment, 'position': position})
                    fragment = ''
                    try:
                        tag = tagstack.pop()
                    except:
                        error('Endtag "<//" misses corresponding starttag', filepath=self.config['basename'], position=position, fatal=True)
                    
                    if ':' in tag[0]:
                        ns, name = tag[0].split(':')
                    else:
                        name = tag[0]; ns = None
                    self.nodes.append({'type': 'endtag', 'ns': ns, 'name': name, 'position': [line, col, line, col+3]})
                    i += 2; col += 2
                    state = 'text'
                else:
                    if state == 'entities' and char in ['<', '>', '&']:
                        fragment += entities[char]
                    else:
                        fragment += char
            elif state == 'text':
                if char == '\\' and nxt in ['<', '>', '&']:
                    fragment += entities(nxt)
                    i += 1; col += 1
                elif char == '<':
                    position = [line, col]
                    if fragment != '':
                        self.nodes.append({'type': 'text', 'content': fragment})
                        fragment = ''
                    if nxt == '/':
                        state = 'endtag'
                        i += 1; col += 1
                    elif nxt == '!':
                        fragment += '<!'
                        if nxt2 == '-':
                            fragment += '--'
                            i += 3; col += 3
                            state = 'comment'
                        elif nxt2 == 'D':
                            fragment += 'DOCTYPE'
                            i += 8; col += 8
                            state = 'declaration'
                        else:
                            fragment += '[CDATA['
                            i += 8; col += 8
                            state = 'cdata'
                    elif nxt == '?':
                        fragment += '<?'
                        state = 'pi'
                        i += 1; col += 1        
                    else:
                        state = 'starttag'
                elif char == '>':
                    if fragment != '':
                        self.nodes.append({'type': 'text', 'content':fragment})
                        fragment = ''
                    pos = [line, col, line, col + 1]
                    try:
                        tag = tagstack.pop()
                    except:
                        error('Endtag misses corresponding starttag', filepath=self.config['basename'], position=pos, fatal=True)
                    self.nodes.append(self.xmlx2node(['endtag', tag[0], pos]))
                else:
                    fragment += char
            elif state == 'endtag': # OK
                if char == '>':
                    position.extend([line,col+1])
                    try:
                        start = tagstack.pop()
                    except:
                        error('Endtag misses corresponding starttag', filepath=self.config['basename'], position=position, fatal=True)
                    starttag = start[0]
                    N = self.xmlx2node(['endtag', fragment, position])
                    if N['ns'] == None:
                        tag = N['name']
                    else:
                        tag = '%s:%s' % (N['ns'], N['name'])
                    if tag != starttag:
                        error('Endtag "%s" does not match corresponding starttag ("%s")' % (tag, starttag), filepath=self.config['basename'], position=position, fatal=True)
                    
                    self.nodes.append(N)
                    fragment = ''; state = 'text'
                else:
                    fragment += char
            elif state == 'starttag':
                if char == '<':
                    if modus == 'hax':
                        modus = 'xml'
                    else:
                        modus = 'hax'
                elif char == '/' and nxt=='>':
                    state = 'text'
                    i += 1; col += 1
                    position.extend([line,col+1])
                    self.nodes.append(self.xmlx2node(['empty', fragment, position]))
                    fragment = ''
                elif char == '>':
                    position.extend([line,col+1])
                    if modus == 'xml':
                        N = self.xmlx2node(['starttag', fragment, position])
                        if N['type'] == 'starttag': # not void
                            if N['ns'] == None:
                                tagstack.append([N['name'], 0])
                            else:
                                tagstack.append(['%s:%s' % (N['ns'], N['name']), 0])
                        self.nodes.append(N)
                    else:
                        tag = hax2xmlx(fragment + ' ')
                        N = self.xmlx2node(['empty', tag, position])
                        self.nodes.append(N)
                        
                    fragment = ''
                    if N['name'] in self.code['skip']:
                        state = 'skip'
                    elif N['name'] in self.code['entities']:
                        state = 'entities'
                    else:
                        state = 'text'
                    
                elif char in [' ', '\t', '\n'] and modus == 'hax' and quote == None:
                    position.extend([line,col])
                    tag = hax2xmlx(fragment + ' ')
                    N = self.xmlx2node(['starttag', tag, position])
                    self.nodes.append(N)
                    if char == '\n': # for tidy output
                        self.nodes.append({'type': 'text', 'content': '\n'})
                    if N['ns'] == None:
                        tagstack.append([N['name'], 0])
                    else:
                        tagstack.append(['%s:%s' % (N['ns'], N['name']), 0])
                    
                    fragment = ''
                    if N['name'] in self.code['skip']:
                        state = 'skip'
                    elif N['name'] in self.code['entities']:
                        state = 'entities'
                    else:
                        state = 'text'
                elif char in ["'", '"'] and modus == 'hax':
                    if quote == char:
                        quote = None
                    else:
                        quote = char
                    fragment += char
                else:
                    fragment += char
            else:
                fragment += char
            
            if char == '\n':
                line += 1; col = 0
            else:
                col += 1
            i += 1
            
        if fragment != '':
            self.nodes.append({'type': 'text', 'content': fragment})
            
        if len(tagstack) != 0:
            error('A starttag (%s) misses corresponding endtag' % tagstack[-1][0], filepath=self.config['basename'], fatal=True)
            
    def createXML(self):
        '''
        when config['format'] == 'html'
            - html5 output
            - for browser compatibility, processing instructions are placed inside comment-delimeters <!-- and --> 
              see: https://developer.mozilla.org/en-US/docs/Web/API/ProcessingInstruction
              
            - cdata: kept if embedded in svg- or math-element
                     otherwise placed inside comment-delimeters
                     see: https://html.spec.whatwg.org/multipage/syntax.html#cdata-sections
                          https://w3c.github.io/html-reference/syntax.html#cdata-sections
        '''
        
        self.xml = ''
        foreign = False
        for N in self.nodes:
            if N['type'] in ['text', 'entities', 'skip', 'declaration']:
                self.xml += N['content']
            elif N['type'] == 'pi':
                if self.config['format'] == 'html':
                    self.xml += '<!-- %s -->' % N['content']
                else:
                    self.xml += N['content']
            elif N['type'] == 'cdata':
                if self.config['format'] == 'html':
                    if foreign:
                        self.xml += N['content']
                    else:
                        self.xml += '<!-- %s -->' % N['content']
                else:
                    self.xml += N['content']
            
            elif N['type'] == 'comment':
                if self.config['nocomment'] == False:
                    self.xml += N['content']
            elif N['type'] == 'endtag':
                if N['name'] in ['math', 'svg']:
                    foreign = False 
                if N['ns'] == None:
                    self.xml += '</%s>' % N['name']
                else:
                    self.xml += '</%s:%s>' % (N['ns'], N['name'])
            else: # 'starttag' and 'empty
                if N['name'] in ['math', 'svg']:
                    foreign = True 
                if N['ns'] == None:
                    tag = '<%s' % N['name']
                else:
                    tag = '<%s:%s' % (N['ns'], N['name'])
                for att in N['attributes']:
                    if N['attributes'][att] == '': # boolean
                        if self.config['format'] == 'html':
                            tag += ' %s' % att
                        else:
                            tag += ' %s=""' % att
                            
                    else:
                        if '"' in N['attributes'][att]:
                            tag += " %s='%s'" % (att, N['attributes'][att])
                        else:
                            tag += ' %s="%s"' % (att, N['attributes'][att])
                if N['type'] == 'empty':
                    if self.config['format'] == 'html':
                        tag += '>'
                    else:
                        tag += ' />'
                else:
                    tag += '>'
                self.xml += tag
                
def html5(body, metadata):
    
    doc = '<!DOCTYPE html>\n'
    doc += '<html lang="%s">\n<head>\n' % metadata['dc:language']
    doc += '<title>%s</title>\n' % metadata['dc:title']
    doc += '<meta charset="utf-8">\n'
    for m in metadata.keys():
        doc += '<meta name="%s" content="%s">\n' % (m, metadata[m])
    doc += '</head>\n<body>\n'
    doc += body
    doc += '</body>\n</html>\n'
    return doc
    
def xhtml5(body,metadata):
    
    doc = '<?xml version="1.0" encoding="utf-8"?>\n'
    doc += '<!DOCTYPE html>\n'
    doc += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="%s">\n<head>\n' % metadata['dc:language']
    doc += '<title>%s</title>\n' % metadata['dc:title']
    #doc += '<meta charset="utf-8" />\n'
    for m in metadata.keys():
        doc += '<meta name="%s" content="%s" />\n' % (m, metadata[m])
    doc += '</head>\n<body>\n'
    doc += body
    doc += '</body>\n</html>\n'
    return doc
    
def xml(body):
    doc = '<?xml version="1.0" encoding="utf-8"?>\n'
    doc += body
    return doc
    
def error(message, filepath=None, position=None, fatal=False, warning=False):
    
    if warning:
        s = '\n\tWARNING: '
    else:
        s = '\n\tERROR: '
    if filepath:
        s += 'in %s ' % filepath
    if position:
        s += 'at %d.%d' % (position[0], position[1])
    s += '\n\t%s' % message
    print(s, file=sys.stderr)    
    if fatal:
        sys.exit()    

def parseCommandLine():
    '''parsing arguments from command line
       converting args to dict
       get absolute paths for haxfile, code, template, output
    '''
    
    desc = "hax.py . version %s/%s . Licence: MIT \u00a9 notSue (http://purl.org/hax/info)" %  (__VERSION__, __DATE__)
    
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("haxfile", help="path hax-sourceFile", nargs='?', default=None)
    parser.add_argument("-o", "--output", help="output file (path). Optional (may be used to store backups)")
    parser.add_argument("-f", "--format", help="Format of  output: 'xml', 'xhtml' or 'html'. Default: 'html'", default='html')
    parser.add_argument("-c", "--code", help="JSON-file with hax codes. If missing, default html is used.", default='default')
    parser.add_argument("-n", "--nocomment", help="remove comments from XML/XHTML output", action='store_true')
    parser.add_argument("-v", "--verbose", help="Switch verbosity on", action='store_true')
    parser.add_argument("--void", help="Detect void elements of  html5", action='store_true')
    parser.add_argument('-w', "--wait", help="Do not create output-file. Parse, detect metadata and stop.", action='store_true')
    args = parser.parse_args()
    config = vars(args)
    config['haxfile'] = os.path.abspath(os.path.join('.', config['haxfile']))
    if config['code'] != 'default':
        config['code'] = os.path.abspath(os.path.join('.', config['code']))
    if config['output']:
        config['output'] = os.path.abspath(os.path.join('.', config['output']))
    else:
        ext = os.path.splitext(config['haxfile'])
        config['output'] = '%s.%s' % (ext[0], config['format'])
        
    HD = Haxparser(config)

if __name__ == '__main__':
    
    parseCommandLine()
    
