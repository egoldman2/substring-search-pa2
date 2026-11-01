#include "search.hpp"

#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>

std::string read_bytes(const char* path) {
    std::ifstream file(path, std::ios::binary);
    if (!file) throw std::runtime_error(std::string("cannot open: ") + path);
    std::string bytes((std::istreambuf_iterator<char>(file)), {});
    if (file.bad()) throw std::runtime_error(std::string("cannot read: ") + path);
    return bytes;
}

int main(int argc, char** argv) {
    try {
        if (argc != 4 || (std::string(argv[1]) != "naive" && std::string(argv[1]) != "kmp")) {
            std::cerr << "usage: search naive|kmp TEXT_FILE PATTERN_FILE\n";
            return 2;
        }
        const auto text = read_bytes(argv[2]);
        const auto pattern = read_bytes(argv[3]);
        const auto result = std::string(argv[1]) == "naive" ? naive_search(text, pattern) : kmp_search(text, pattern);
        if (result == std::string_view::npos) std::cout << "npos\n";
        else std::cout << result << '\n';
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
