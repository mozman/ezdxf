.. _knowledge_graph:

Knowledge Graph
===============

I have started managing notes and documents that are not included in the `ezdxf` 
documentation in `Logseq`_ in late 2023.  It works like a wiki but does not require a 
backend server. The Information is edited as Markdown files, which is much more intuitive 
than reStructured Text, and the content is stored in local files.  

The notes are included in the source code repository on Github in the `notes folder`_.

A published edition of this Knowledge Graph is included on the `ezdxf` website and is 
accessible by the link https://ezdxf.mozman.at/notes.


The Knowledge Graph includes:

- `Release Notes`_ of future releases and some versions back
- `CHANGELOG`_
- `IDEAS`_ for future releases
- `FAQ`_ and the `HOWTO`_ sections from this documentation
- all my notes to `ezdxf`
- In the future the `DXF Internals` section from this documentation may also move to the 
  Knowledge Graph.

Logseq's outline structure is not ideal for all the documents I want to include, but I 
chose `Logseq`_ over `Obsidian.md`_ because it is open source and can publish the 
knowledge graph as a static website, static in the sense of no server-side code execution. 

This feature is important to me for hosting the content of the Knowledge Graph on the 
`ezdxf`` website  and cannot be achieved for free with `Obsidian.md`_. 

`Logseq`_ is an `Electron`_ application that runs on all platforms, with the 
disadvantage: it's an `Electron`_ application.

.. _Logseq: https://www.logseq.com/
.. _Obsidian.md: https://obsidian.md/
.. _Release Notes: https://ezdxf.mozman.at/notes/#/page/release%20notes
.. _CHANGELOG: https://ezdxf.mozman.at/notes/#/page/changelog
.. _IDEAS: https://ezdxf.mozman.at/notes/#/page/ideas
.. _FAQ: https://ezdxf.mozman.at/notes/#/page/faq
.. _HOWTO: https://ezdxf.mozman.at/notes/#/page/howto
.. _Electron: https://electronjs.org/
.. _notes folder: https://github.com/mozman/ezdxf/tree/master/notes
