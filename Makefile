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
tests: type.uint8.uint8Tests
tests: type.uint16.uint16Tests
tests: type.uint32.uint32Tests
tests: type.uint64.uint64Tests

doc:
	doxygen

.PHONY: tests doc
