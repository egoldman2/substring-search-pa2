CXX = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Wpedantic -O2

.PHONY: all test sanitize clean

all: build/search build/search_tests build/benchmark

test: build/search_tests
	./build/search_tests

build/search_tests: tests/search_tests.cpp src/naive.cpp src/kmp.cpp src/search.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -Isrc tests/search_tests.cpp src/naive.cpp src/kmp.cpp -o $@

build/search: src/main.cpp src/naive.cpp src/kmp.cpp src/search.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -Isrc src/main.cpp src/naive.cpp src/kmp.cpp -o $@

build/benchmark: bench/driver.cpp src/naive.cpp src/kmp.cpp src/search.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -Isrc bench/driver.cpp src/naive.cpp src/kmp.cpp -o $@

sanitize:
	mkdir -p build
	$(CXX) -std=c++17 -Wall -Wextra -Wpedantic -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -Isrc tests/search_tests.cpp src/naive.cpp src/kmp.cpp -o build/search_tests_sanitize
	./build/search_tests_sanitize

clean:
	rm -rf build
