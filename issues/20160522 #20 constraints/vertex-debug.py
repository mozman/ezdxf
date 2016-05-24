import ezdxf 
import sys


def main():

	print 'Python version is: '+(sys.version)
	print 'ezdxf version is: ' + ezdxf.__version__
	
	print '\nCoordinate for layer 0'
	find_coordinates(filename='test.dxf',layer_name='0')
	
	print '\nCoordinate for layer 1'
	find_coordinates(filename='test.dxf',layer_name='Layer 1')
	
	print '\nCoordinate for layer 2'
	find_coordinates(filename='test.dxf',layer_name='Layer 2')



def find_coordinates(filename='test.dxf', layer_name='0'):


	dwg_dxf = ezdxf.readfile(filename)

	for e in dwg_dxf.entities:
		if layer_name in e.get_dxf_attrib(key='layer') and e.dxftype() == 'LWPOLYLINE':
			
			polygon_points = []
			for i in e.get_rstrip_points(): 
				polygon_points.append(i)
			print polygon_points
			

if __name__ == '__main__':
	main()