tags:: FAQ, fonts, font-cache

- ## [[Font Cache]]
	- [[ezdxf]] creates a new [[font cache]] if none exist, most likely at the first lauch of `ezdxf`
	- The [[font cache]] will never be updated automatically!
	- [[ezdxf]] searches recursively these default directories on your system for TrueType fonts #TTF
		- <https://ezdxf.mozman.at/docs/tools/fonts.html#font-locations>
	- [[ezdxf]] searches  recursively the support directories defined in your [[config file]] for shape fonts files #SHX #SHP #LFF
	-
- ## New Installed Fonts
  id:: 6559cc2f-a94c-477f-b092-cf848b093be6
	- ((6559cccd-b1da-4490-b909-a5cc18d23db7))
		- ((6559ccf9-2a1c-4efe-9875-f9a0f5e02b26))
		- ((6559cd2e-0bf8-4d2d-885b-3c97ae22f381))
	-
- ## New Added Support Directories
	- When you add new folders to the support direcories of your [[config file]] e.g. the fonts folder of your Autodesk [[TrueView]] or [[BricsCAD]] installation:
		- ```ini
		  [core]
		  support_dirs =
		    "C:\Program Files\Bricsys\BricsCAD V23 en_US\Fonts",	
		    "C:\Program Files\Autodesk\DWG TrueView 2024 - English\Fonts",
		  
		  ```
	- None of the #SHX, #SHP or #LFF font files in these support directories is included in the current [[font cache]] until you rebuild the [[font cache]], see ((6559cc2f-a94c-477f-b092-cf848b093be6))
	-
- ## Related Links
	- documentation about [[config files]]
	- documentation about fonts: <https://ezdxf.mozman.at/docs/tools/fonts.html>