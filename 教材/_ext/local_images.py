"""让Markdown中的中文、空格等本地图片路径正确进入HTML教材。"""
from urllib.parse import unquote, urlsplit

from docutils import nodes


def decode_local_images(app, doctree):
    for image in doctree.findall(nodes.image):
        uri = image.get("uri", "")
        parsed = urlsplit(uri)
        if uri and not parsed.scheme and not parsed.netloc:
            image["uri"] = unquote(uri)


def setup(app):
    # 在Sphinx收集、复制图片前，还原Markdown解析器编码过的本地路径。
    app.connect("doctree-read", decode_local_images, priority=100)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
