tags:: ideas, xref, import

- ## Ignore always unsupported entities in [[DICTIONARY]] entities
  id:: 6568ce8a-7ffb-432f-8522-a72a586e5239
	- The current behavior of a failing copy process doesn't help anyone.
	- Output and log a message about possible [[AutoCAD]] incompatibility.
	- This change was added to ((6568dc88-ce84-4f46-b490-43768c491a2b))
	- If this change causes too much trouble, there is an option to implement it as an optional feature.
	-
- ## Special Copy-Mode for [[DICTIONARY]] entites
	- The [[ezdxf.xref]] module cannot import unsupported entities
	- This is often related to undocumented entities and objects used by [[AutoCAD]] to implement extended features.
	- These undocumented entities are linked to regular entities by the [[Extension Dictionary]].
	- The import may work if the [[Extension Dictionary]] is deleted.
		- This is cumbersome and error-prone when done manually.
	- The idea is to add a copy-mode setting to the [[DICTIONARY]] entity as a class variable.
	- This must happen in the [[DICTIONARY]] entity, because the copy process is recursive without control from the outside.
		- Existing behavior is the _Regular_  mode, which raises an exception for unsupported entities
		- New mode: _Ignore Unsupported Entities_
			- This mode would ignore unsupported entities and replace the handle by a null-reference or remove the key at all
			- **WARNING** This may remove important data and make DXF documents unreadable for [[AutoCAD]]
	- The copy-mode of the [[DICTIONARY]] entity is controlled by the [[ezdxf.xref]] module
		- New policy `CopyPolicy`
			- _REGULAR_
			- _IGNORE_UNSUPPORTED_ENTITIES_
		- passed to the `Loader.execute()` method
		-
- ### This does not conflict with: ((6568c568-6aed-4de2-83f0-7807a04d230b))
	- If copying of unsupported entities works the problem is solved and this feature would just be dead code.