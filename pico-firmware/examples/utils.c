#include "utils.h"
#include <stdio.h>
#include <string.h>

bool is_str_end_with(const char *str, const char *suffix) {

    int len = strlen(str);
    int suffix_len = strlen(suffix);

    // Check if the filename is long enough to potentially end with ".bmp"
    if (len >= suffix_len &&
        strcmp(str + len - suffix_len, suffix) == 0) {
        return true;
    }

    return false;
}