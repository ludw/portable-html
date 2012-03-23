Portable HTML
===============

Portable-HTML is a tool for creating portable self-contained HTML documents.
The goal is to make it really easy to create a html file that contains text, style and images. Images will be included as base64 encoded data in the same file.

Documents can be generated from a source file and a template. The source file contains some configuration and Textile markup.

The template contains style and basic HTML structure.

To generate a portable html document from a source, just run:

	$ ptm.py source.txl out.html


Requirements
-------------------
The following python packages must be installed:

	textile
	jinja2
