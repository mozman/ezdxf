# Load DXF Documents from Reliable Sources
id:: 655fa1b8-2647-41bc-b7b1-9dbb29689907
	- tags:: howto, readfile
	- This works well with DXF files from trusted sources like [[AutoCAD]] or [[BricsCAD]], for loading [[DXF]] files with minor or major flaws look at the [[ezdxf.recover]] module.
	- ```Python
	  import sys
	  import ezdxf
	  
	  try:
	      doc = ezdxf.readfile("your.dxf")
	  except IOError:
	      print(f"Not a DXF file or a generic I/O error.")
	      sys.exit(1)
	  except ezdxf.DXFStructureError:
	      print(f"Invalid or corrupted DXF file.")
	      sys.exit(2)
	  msp = doc.modelspace()
	  ```
	- see also: applications that do fit my criteria of a [[Reliable CAD Application]]
	-
- # Load DXF Documents from Unreliable Sources
  id:: 655f9217-535e-4f2e-8502-387a23853929
	- tags:: howto, readfile, ezdxf.recover
	- If you know the files you will process have most likely minor or major flaws, use the [[ezdxf.recover]] module:
	- ```Python
	  import sys
	  from ezdxf import recover
	  
	  name = "your.dxf"
	  try:  # low level structure repair:
	      doc, auditor = recover.readfile(name)
	  except IOError:
	      print(f"Not a DXF file or a generic I/O error.")
	      sys.exit(1)
	  except ezdxf.DXFStructureError:
	      print(f"Invalid or corrupted DXF file: {name}")
	      sys.exit(2)
	  
	  # DXF file can still have unrecoverable errors, but this is maybe
	  # just a problem when saving the recovered DXF file.
	  if auditor.has_errors:
	      print(f"Found unrecoverable errors in DXF file: {name}.")
	      auditor.print_error_report()
	  ```
	- For more loading scenarios read the docs of the [[ezdxf.recover]] module.
	-
- # Load DWG Documents
  id:: 655f9dec-1dd2-4cd0-91b8-fba13b828a73
	- tags:: howto, readfile, DWG, odafc-addon
	- [[ezdxf]] does not support the [[DWG]] format, but you can use the [[odafc-addon]] to load [[DWG]] files via the [[ODA File Converter]]
	- ```Python
	  import ezdxf
	  from ezdxf.addons import odafc
	  
	  try:
	  	doc = odafc.readfile("your.dwg")
	  except IOError:
	      print(f"Generic I/O error.")
	      sys.exit(1)
	  except odafc.ODAFCError as e:
	      print(f"Invalid or corrupted DWG file.")
	      sys.exit(2)
	  
	  ```