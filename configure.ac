#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.67])
AC_INIT([How_Traffic_Control_Signals_Work],[2024.11.30],
[John_Sauter@systemeyescomputerstore.com],
[How_Traffic_Control_Signals_Work],
["github@github.com:How_Traffic_Control_Signals_Work.git"])
AM_INIT_AUTOMAKE([tar-pax]) 
AC_CONFIG_SRCDIR([traffic_control_signals.py])

# Use maintainer mode because files extracted from a PDF file
# lose their modification dates, and we don't want the end user
# to need all the Autoconfigure software.
AM_MAINTAINER_MODE

# On the other hand, building the PDF requires LaTeX and lots of
# its packages.  Build it only if --enable-pdf is specified at
# configure time, or if building the distribution kit.
# This won't be a problem if the sources have been extracted from the PDF,
# since the PDF will already be present.
#
AC_ARG_ENABLE([pdf],
  [AS_HELP_STRING([--enable-pdf],
    [Create the PDF file, with embedded sources])],
  [enable_pdf=yes],
  [enable_pdf=no])

AM_CONDITIONAL([ENABLE_PDF], [test "$enable_pdf" = "yes"])

# Checks for programs.
AM_PATH_PYTHON([3])

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

# Checks for system services.

AC_CONFIG_FILES([Makefile])
AC_OUTPUT

# End of file configure.ac
