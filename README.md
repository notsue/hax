# HaX

**HaX** is the name of a markup language. 
Read the [HaX Guide](https://notsue.github.io/haxguide.html).

Comming soon: a working `hax.py`,  converting HaX to XML, HTML5 or XHTML.


## Objective

Edit XML- or HTML5-files with less energy. HaX-tags are syntactic sugar for XML-tags. HaX means 'Half XML'. XML-markup is reduced by half. 

For example:

XML: `<p class="alert" title="I should pop up">An example</p>`

HaX: `<p.alert@T="I should pop up" An example>`

So:
  - endtag is nameless;
  - attribunames can be reduced to symbol ('.' in example) or short name ('T' in example).

These symbols and short names are defined in a JSON-file, which can be changed to everybody's preferences.

So: *nothing is fixed in hax*.

HaX is a generic markup language, and does not focus on a specific type of documents. Markdown is used to edit articles,
but with HaX you can edit anything. 

## Last but not least

HaX can be mixed with regular XML or (X)HTML. In fact: XML or HTML is also HaX.
   
