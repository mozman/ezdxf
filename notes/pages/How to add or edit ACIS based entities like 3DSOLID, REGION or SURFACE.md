tags:: FAQ

- The [[BODY]], [[3DSOLID]], [[SURFACE]], [[REGION]] and so on, are stored as [[ACIS]] data embedded in the [[DXF]] file.
- The [[ACIS]] data is stored as [[SAT]] (text) format in the entity itself for DXF R2000-R2010 and as [[SAB]] (binary) format in the [[ACDSDATA]] section for DXF R2013+.
- [[ezdxf]] can read [[SAT]] and [[SAB]] data, but only write [[SAT]] data.
- The [[ACIS]] data is a proprietary format from [[Spatial Inc]], and there exist no free available documentation or open source libraries to create or edit [[SAT]] or [[SAB]] data, and also [[ezdxf]] provides no functionality for creating or editing [[ACIS]] data.
- The [[ACIS]] support provided by [[ezdxf]] is only useful for users which have access to the [[ACIS]] SDK from [[Spatial Inc]].