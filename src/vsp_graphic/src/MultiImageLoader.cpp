#include <MultiImageLoader.h>
#include "OpenGLHeaders.h"

#include "stb_image.h"
#include <cstring>
#include <limits>
#include <memory>

namespace VSPGraphic
{
MultiImageLoader::MultiImageLoader() : ImageLoader()
{
}
MultiImageLoader::~MultiImageLoader()
{
}

ImageData MultiImageLoader::load( std::string fileName )
{
    ImageData iData;

    int w = 0, h = 0, bpp = 0;
    std::unique_ptr<unsigned char, decltype( &stbi_image_free )>
        data( stbi_load( fileName.c_str(), &w, &h, &bpp, 0 ), &stbi_image_free );

    if ( !data || w <= 0 || h <= 0 || bpp < 1 || bpp > 4 )
    {
        return iData;
    }

    // Image consumers use an RGB or RGBA stride, including when reversing rows.
    const size_t out_bpp = ( bpp == 2 || bpp == 4 ) ? 4 : 3;
    const size_t width = static_cast<size_t>( w );
    const size_t height = static_cast<size_t>( h );
    if ( width > std::numeric_limits<unsigned int>::max() / height / out_bpp )
    {
        return iData;
    }

    const size_t pixels = width * height;
    std::unique_ptr<unsigned char[]> normalized( new unsigned char[ pixels * out_bpp ] );
    if ( bpp >= 3 )
    {
        std::memcpy( normalized.get(), data.get(), pixels * out_bpp );
    }
    else
    {
        for ( size_t i = 0; i < pixels; ++i )
        {
            const size_t src = i * bpp;
            const size_t dst = i * out_bpp;
            normalized[ dst ] = normalized[ dst + 1 ] = normalized[ dst + 2 ] = data.get()[ src ];
            if ( bpp == 2 )
            {
                normalized[ dst + 3 ] = data.get()[ src + 1 ];
            }
        }
    }

    iData.valid = true;
    iData.width = w;
    iData.height = h;
    iData.type = out_bpp == 4 ? GL_RGBA : GL_RGB;
    iData.data = normalized.release();

    return iData;
}

bool MultiImageLoader::acceptExt( std::string e )
{
    return ( e == ".jpg" ) ||
           ( e == ".png" ) ||
           ( e == ".tga" ) ||
           ( e == ".bmp" ) ||
           ( e == ".gif" );
}
}
