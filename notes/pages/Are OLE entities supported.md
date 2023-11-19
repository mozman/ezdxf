tags:: FAQ

- **TLDR; NO!**
- The Wikipedia definition of [OLE](https://en.wikipedia.org/wiki/Object_Linking_and_Embedding):
	- Object Linking & Embedding (OLE) is a proprietary technology developed by Microsoft that allows embedding and linking to documents and other objects. For developers, it brought OLE Control Extension (OCX), a way to develop and use custom user interface elements. On a technical level, an OLE object is any object that implements the ``OleObject`` interface, possibly along with a wide range of other interfaces, depending on the object's needs.
- Therefore [[ezdxf]] does not support this entities in any way, this only work on Windows and with the required editing application installed.
- The binary data stored in the OLE objects cannot be used without the editing application.
- In my opinion, using OLE objects in a CAD drawing is a very bad design decision that can and will cause problems opening these files in the future, even in AutoCAD on Windows when the required editing application is no longer available or the underlying technology is no longer supported.
- All of this is unacceptable for a data storage format that should be accessed for many years or decades (e.g. construction drawings for buildings or bridges).