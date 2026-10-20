# Keep the notices and the README-linked evidence available in installed ZIPs.
# Do not rewrite document bytes or filter any model/example files here.
SET( _localized_documentation_root "${CMAKE_CURRENT_LIST_DIR}/../.." )
INSTALL( FILES "${_localized_documentation_root}/THIRD_PARTY_NOTICES.md" DESTINATION . )
INSTALL( DIRECTORY "${_localized_documentation_root}/docs/" DESTINATION docs )
UNSET( _localized_documentation_root )
