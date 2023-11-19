tags:: FAQ

- # Imported ezdxf package has no content.
- AttributeError: partially initialized module 'ezdxf' has no attribute 'readfile' (most likely due to a circular import)
  logseq.order-list-type:: number
	- Did you name your file/script "ezdxf.py"?
	- This causes problems with circular imports.
	- Renaming your file/script should solve this issue.
- AttributeError: module 'ezdxf' has no attribute 'readfile'
  logseq.order-list-type:: number
	- This could be a hidden permission error, for more information about this issue read Petr Zemeks article:
		- <https://blog.petrzemek.net/2020/11/17/when-you-import-a-python-package-and-it-is-empty/>