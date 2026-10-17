# This file is selected only for macOS backfill builds via CMAKE_TOOLCHAIN_FILE.
# CMake >= 3.21 passes that environment default to fresh ExternalProject children.
# Scope the setting to the bundled libxml2 build; leave every other project alone.
# Its static catalog implementation otherwise embeds the CI install prefix in
# XML_SYSCONFDIR. /etc is a runtime lookup default, not an installation action.
if(CMAKE_SOURCE_DIR MATCHES "/LIBXML2-prefix/src/LIBXML2$")
  set(CMAKE_INSTALL_SYSCONFDIR "/etc" CACHE PATH "Portable libxml2 catalog lookup directory" FORCE)
endif()
