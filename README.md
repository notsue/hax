# hax

Generic Markup Language 'hax', with parser 'parsehax.py' and editor 'edithax.py'. Creates wellformed XM or (X)HTML. 

## Objective

Producing wellformed/valid XML-files with less energy. Hax-tags are shortcuts for XML-tags. 

For example:

XML: <h1,id="section1",property="dc.title">An example</h1>

HAX: \[h1,section1,p=dc.title An example\]

So:
  - closing hax-tag is nameless;
  - attributes, sepereted by a comma, can be nameless also, or replaced by a short name 

A hax-parser should convert from HAX-markup to the XML-format.

- each element gives a specified meaning to one nameless attributes
- some attributes can have a short name as identifier
- There are namelless opening tags as well. It suffices to write \[ and the parent-elements defines its meaning.

However: nothing is fixed in hax.

  - user can define nameless tags, nameless attributes and short attributes
  - even the tokens '\[', '\]' ',' , '=' can be changed
 
These re-settings are not stored special config-files, but invoked with specific \[hax:commands ... \] in the
source file. A parse should adapt immediatly to these changes,  and return to default on command.

## Last but not least

- hax can be mixes with regular XML or (X)HTML;
- nothings stops integration in larger XML-, HTML-frameworks;
- the output of a parser MUST deliver wellformed XML, ready for use with SAX or DOM-parsers;
- a hax-file can be presented as wellformed XML

## Issues

Hax assumes some basic knowledge of xml en/or html
Bigger hax-documents are not always easy to debug without support of an editor 
that provides some hints with highlighting. Bugs? Well: a missing closing tag, or bad 
nesting of elements,..
There are trick to use in better editors, but notsue will povide an editor that should asure the use of less energy.



## Comming soon

- *hax.md*: description of the generic markup language 'hax';
- *parsehax.py*: a parser for hax, written in Python (no special dependancies). Usage: command line interface.
  Transforms hax-souce into wellformed xml or (x)html is user prefers this specific xml. But 'hax' is generic.
  A user may prefer other XML-schemes;
- *edithax.py*: an editor fully adapted for 'hax', using the parser parsehax.py


   
