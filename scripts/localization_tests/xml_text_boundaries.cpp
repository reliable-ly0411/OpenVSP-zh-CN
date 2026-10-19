#include "XmlUtil.h"
#include <iostream>
#include <vector>

int main()
{
    const std::vector<std::string> values = {
        "Wing", "主翼", "Wing&Body_1", "Wing &amp; Body", "<Wing> / \"Left\"",
        "用户模型_7 / Export_100%", "C:\\Users\\Example\\A&B.vsp3", ""
    };
    for (const std::string &value : values)
    {
        xmlDocPtr doc = xmlNewDoc(BAD_CAST "1.0");
        xmlNodePtr root = xmlNewNode(nullptr, BAD_CAST "Model");
        xmlDocSetRootElement(doc, root);
        XmlUtil::AddStringNode(root, "Name", value);
        xmlChar *serialized = nullptr;
        int size = 0;
        xmlDocDumpMemoryEnc(doc, &serialized, &size, "UTF-8");
        xmlDocPtr readback = xmlReadMemory(reinterpret_cast<const char *>(serialized), size,
                                          "model.vsp3", nullptr, XML_PARSE_NONET);
        const bool same = readback && XmlUtil::FindString(xmlDocGetRootElement(readback), "Name", "") == value;
        if (readback) xmlFreeDoc(readback);
        xmlFree(serialized);
        xmlFreeDoc(doc);
        if (!same)
        {
            std::cerr << "XML text changed during serialization\n";
            return 1;
        }
    }
    std::cout << "XML user text roundtrip passed\n";
}
