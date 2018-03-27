all:
	echo "Nothing to compile!"

#%.%Tests:
%Tests:
	@echo -e "\t\e[1mRUN TESTS FOR $@\e[0m"
	python3 -m unittest $@

tests: arsc.arsc.ResTableTests
tests: arsc.types.ResourceTypeTests
tests: arsc.chunk.ResChunk_headerTests
tests: arsc.table.ResTable_headerTests
tests: arsc.package.ResTable_package_headerTests
tests: arsc.package.ResTable_packageTests
tests: arsc.config.ResTable_configTests
tests: arsc.stringpool.ResStringPool_headerTests
tests: arsc.stringpool.ResStringPoolTests
tests: arsc.tabletype.ResTable_typeSpec_headerTests
tests: arsc.tabletype.ResTable_typeSpecTests
tests: arsc.tabletype.ResTable_type_headerTests
tests: arsc.tabletype.ResTable_typeTests
tests: arsc.type.uint8.uint8Tests
tests: arsc.type.uint16.uint16Tests
tests: arsc.type.uint32.uint32Tests
tests: arsc.type.uint64.uint64Tests

doc:
	doxygen

.PHONY: tests doc
