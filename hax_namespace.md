# hax namespace (draft)

THIS PAGE IS UNDER CONSTRUCTION

The namespace url of 'hax' is: http://purl.org/hax/ns

This persistent URL redirects you to this file, which has no role to play.

But we can sum up the elements used so far in this namespace. But first: why a
namespace?

Well, the hax-parser first translates hax-code in XML/HTML. The resulting XML is then 
parsed with an Expat-parser who does all services, like autonumbering, creation of a table of
contents, collection URL's (links) to show them when a document is printed, managing endnotes, 
metadata ... etcetera. 

Yes: etcetera. Ambitious users can change/extend the services with other Expat-parsers, or 
sax- or dom-pasers. Or with XSLT.

The fact that we send the full content through Expat proves that we are creating well-formed XML. 
Expat, does not validate, but can handle namespaces. This provides a standard tool to prevent conflicts 
between extensions. 

The scheme for the hax-namespace is not yet fully defined. Ambitious users must use their own 
'private' namespace. Read the code in parsehax.py, especially the definition of the HaxExpat classes. 

It should be noted, that none of the elements of de hax-namespace appear in the final XML- or HTML-output.
This namespace must not be mentioned as an xmlns-value in in templates.


## Files

- hax:root - used by the parser, should not be used by authors of hax-files

- hax:inc - include-command to build one xml/html file from several hax-files
  
  usage: [hax:inc sourcefilename.hax ]
  
  We use file-extension 'hax', but any extension will work, as long as the files
  are encoded in utf-8
  
## Tokens commands
  
- hax:tokens,default - needs no

- hax:tokens,use

- hax:tokens,replace 

## Preserve commands

Elememts with CDATA content, are well known in HTML: 'pre', 'script' aand 'style'.
In fact, these are the default elements where the hax-parser preserves the content as is.

Users of hax can define more or other elements, with:

- hax:preserve,add

- hax:reserve,remove

# Service commands

- hax:toc - Create table of contents

- hax:note - endnotes, margin- and sidenotes. Footnotes are used in printing. hax can handle 'endnotes'
  which are collected at the end of a document, or at the and of certain sections. User defines where the 
  appear with another tag (tax:notes). Numbering is automated, with links from text to footnote and backlinks.
  
  Usage: 
  
  - [hax:note ...hax-content of note... ]   - an endnote
  
  - [hax:note,margin ... content ...]
  
  - [hax,note,side ... content ...]  
  
  The latter two are used in Tufte-layout.
  
- hax:notes (plural) - locates place where notes should be collected and placed

  Usage: [hax:notes ]
  
  This element can appear on multiple places in the document. The notes created before this element
  re flushed, and numbering restarts from one, gor the next coolection of notes.
  

TO BE CONTINUED
