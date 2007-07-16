/*
 * Modified for use within matplotlib
 * 5 July 2007
 * Michael Droettboom
 */

/* Very simple interface to the ppr TT routines */
/* (c) Frank Siegert 1996 */

#include "global_defines.h"
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include "pprdrv.h"

#if DEBUG_TRUETYPE
void debug(const char *format, ... )
{
  va_list arg_list;
  va_start(arg_list, format);

  printf(format, arg_list);

  va_end(arg_list);
}
#endif

#define PRINTF_BUFFER_SIZE 512
void TTStreamWriter::printf(const char* format, ...)
{
  va_list arg_list;
  va_start(arg_list, format);
  char buffer[PRINTF_BUFFER_SIZE];

  int size = vsnprintf(buffer, PRINTF_BUFFER_SIZE, format, arg_list);
  if (size >= PRINTF_BUFFER_SIZE) {
    char* buffer2 = (char*)malloc(size);
    vsnprintf(buffer2, size, format, arg_list);
    free(buffer2);
  } else {
    this->write(buffer);
  }

  va_end(arg_list);
}

void TTStreamWriter::putchar(int val)
{
  char c[2];
  c[0] = (char)val;
  c[1] = 0;
  this->write(c);
}

void TTStreamWriter::puts(const char *a)
{
  this->write(a);
}

void TTStreamWriter::putline(const char *a)
{
  this->write(a);
  this->write("\n");
}

void replace_newlines_with_spaces(char *a) {
  char* i = a;
  while (*i != 0) {
    if (*i == '\n')
      *i = ' ';
    i++;
  }
}
