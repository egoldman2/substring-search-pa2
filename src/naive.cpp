#include "search.hpp"

namespace {
template<bool Count>
std::size_t search(std::string_view text, std::string_view pattern, SearchCounts& counts) {
    if (pattern.size() > text.size()) return std::string_view::npos;

    for (std::size_t start = 0; start <= text.size() - pattern.size(); ++start) {
        std::size_t matched = 0;
        while (matched < pattern.size()) {
            if constexpr (Count) ++counts.search;
            if (text[start + matched] != pattern[matched]) break;
            ++matched;
        }
        if (matched == pattern.size()) return start;
    }
    return std::string_view::npos;
}
}

std::size_t naive_search(std::string_view text, std::string_view pattern) {
    SearchCounts unused;
    return search<false>(text, pattern, unused);
}

std::size_t counted_naive_search(std::string_view text, std::string_view pattern, SearchCounts& counts) {
    counts = {};
    return search<true>(text, pattern, counts);
}
