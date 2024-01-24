tags:: DXF-Internals

- By Gopinath Taget
- Source: <http://adndevblog.typepad.com/autocad/2013/01/hatch-pattern-and-dxf-codes.html>
- You might wonder what the correlation is between the definition file of a hatch pattern("acad.pat", "cadiso.pat") and the DXF codes of [[HATCH]] entity.
- The following is dxf code for pattern data:
	- ```
	  53 Pattern line angle
	  43 Pattern line base point, X component
	  44 Pattern line base point, Y component
	  45 Pattern line offset, X component
	  46 Pattern line offset, Y component
	  79 Number of dash length items
	  49 Dash length (multiple entries)
	  ```
- But you might observe that the values of the pattern in the DXF is not always the same as they are defined in the PAT file.
- This is because the pattern values like base point and offset are transformed by parameters like pattern angle.
- For instance:
	- Pattern line offset, X and Y component :
	- Take the values from the pattern file and rotate them around the z-axis with the pattern angle and you will be able to figure out the value written in the DXF file.
	- For example, from AR-CONC in acadiso.pat, the x and y offset is 104.896, -149.807.
	- Draw a line from 0,0, to 104.896,-149.807 and rotate it about 50 degrees. List its values and you will see that the line is located at 182.185,-15.9391,0.
	- The base point for rotation is 0,0. If you use the offset value from DXF file 7.172601826007534,-0.6275213498259511 to draw a line starting at 0,0, you will see this line laps over the line starting at 0,0 and ending at 182.185,-15.9391.