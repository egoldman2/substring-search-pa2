#pragma once

#include <string_view>
#include <cstdint>

// return the first match, or std::string_view::npos if there is no match
// an empty pattern matches at index 0
std::size_t naive_search(std::string_view text, std::string_view pattern);
std::size_t kmp_search(std::string_view text, std::string_view pattern);

struct SearchCounts {
    std::uint64_t preprocessing = 0;
    std::uint64_t search = 0;
};

// separate entry points leave counting out of normal timing
std::size_t counted_naive_search(std::string_view text, std::string_view pattern, SearchCounts& counts);
std::size_t counted_kmp_search(std::string_view text, std::string_view pattern, SearchCounts& counts);
