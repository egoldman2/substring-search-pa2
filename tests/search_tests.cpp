#include "search.hpp"

#include <cstdlib>
#include <random>
#include <iostream>
#include <string>
#include <vector>

std::size_t checks = 0;

void check(std::string_view text, std::string_view pattern, std::size_t expected) {
    SearchCounts naive, kmp;
    const std::size_t answers[] = {naive_search(text, pattern), kmp_search(text, pattern),
        counted_naive_search(text, pattern, naive), counted_kmp_search(text, pattern, kmp)};
    for (auto answer : answers) {
        ++checks;
        if (answer != expected) {
            std::cerr << "wrong answer: text length " << text.size() << ", pattern length "
                      << pattern.size() << ", expected " << expected << ", got " << answer << '\n';
            std::exit(1);
        }
    }
}

int main() {
    using namespace std::string_view_literals;
    const auto missing = std::string_view::npos;
    struct Case { std::string_view text, pattern; std::size_t expected; };
    const std::vector<Case> cases = {
        {"ABABABAC", "ABABAC", 2}, {"banana", "ban", 0},
        {"banana", "ana", 1}, {"banana", "nana", 2},
        {"banana", "apple", missing}, {"abc", "abcd", missing},
        {"", "", 0}, {"abc", "", 0}, {"", "a", missing},
        {"abc", "abc", 0}, {"abc", "c", 2}, {"aaaaa", "aaa", 0},
        {"abababab", "abab", 0}, {"abababab", "abac", missing},
        {"abababacababaca", "ababaca", 2},
        {"aaaaaaaaab", "aaaab", 5}, {"x", "x", 0}, {"x", "y", missing},
        {"\xff\x80\0\x7f"sv, "\x80\0"sv, 1},
        {"AAAAAAAB", "AAAAB", 3}, {"abc\0def"sv, "\0d"sv, 3}
    };
    for (const auto& test : cases) {
        check(test.text, test.pattern, test.expected);
    }

    // check every short binary string against the standard library
    std::vector<std::string> strings = {""};
    for (std::size_t i = 0; i < strings.size(); ++i) {
        if (strings[i].size() < 6) {
            const auto value = strings[i];
            strings.push_back(value + 'a');
            strings.push_back(value + 'b');
        }
    }
    for (const auto& text : strings) {
        for (const auto& pattern : strings) {
            const auto expected = text.find(pattern);
            check(text, pattern, expected);
        }
    }
    std::mt19937 random(41052);
    for (int trial = 0; trial < 10000; ++trial) {
        std::string text(random() % 513, '\0'), pattern(random() % 130, '\0');
        const unsigned alphabet = trial % 2 == 0 ? 256 : 4;
        for (char& byte : text) byte = static_cast<char>(random() % alphabet);
        for (char& byte : pattern) byte = static_cast<char>(random() % alphabet);
        if (trial % 3 == 0 && pattern.size() <= text.size()) {
            const auto position = random() % (text.size() - pattern.size() + 1);
            text.replace(position, pattern.size(), pattern);
        }
        check(text, pattern, text.find(pattern));
    }
    SearchCounts naive, kmp;
    counted_naive_search("aaaaaa", "aaab", naive);
    counted_kmp_search("aaaaaa", "aaab", kmp);
    if (naive.search != 12 || naive.preprocessing != 0 || kmp.search != 9 || kmp.preprocessing != 5) {
        std::cerr << "comparison-count regression failed\n";
        return 1;
    }
    std::cout << checks << " answer checks passed, plus exact comparison counts.\n";
}
