---
name: Pull Request Template
about: Create a pull request to merge your contribution.

---

Describe your changes. Please, keep the description short and simple.

__Important:__ choose `base: master` as the target branch

_Optional_ things you can do before requesting a review:

- Type check the code: `mypy --ignore-missing-imports -p ezdxf`, `ezdxf` has to be installed in dev-mode for that.
- Run the core tests: `pytest tests`
- Format the code by `black` with the default settings.
- Write tests.
- Write a documentation, when adding new features. Doesn't have to be `RestructuredText`, 
  `Markdown` or simple text is OK, just enough to save me time.
