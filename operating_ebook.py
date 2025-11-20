# operating_ebook.py

import Env
import ebooklib
from ebooklib import epub
from ebooklib.epub import EpubHtml

# 操作函数
def get_chapter_data(chapter_index=0):
    """
    读取EPUB文件中指定章节的数据
    
    Args:
        chapter_index (int): 章节索引，默认为0（第一个章节）
    
    Returns:
        dict: 包含章节信息的字典，包括标题、内容、ID等
    """
    try:
        # 读取EPUB文件
        book = epub.read_epub(Env.DATA_PATH)
        
        # 获取所有文档项（HTML文件）
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        
        if not items:
            print("未找到任何章节内容")
            return None
            
        if chapter_index >= len(items):
            print(f"章节索引超出范围，总章节数: {len(items)}")
            return None
           
        # 获取指定章节
        chapter = items[chapter_index]
        
        # 提取章节信息
        chapter_info = {
            'id': chapter.id,
            'title': getattr(chapter, 'title', f'Chapter {chapter_index + 1}'),
            'content': chapter.get_content().decode('utf-8') if isinstance(chapter.get_content(), bytes) else chapter.get_content(),
            'file_name': chapter.file_name if hasattr(chapter, 'file_name') else None,
            'index': chapter_index
        }
        
        return chapter_info
        
    except Exception as e:
        print(f"读取章节数据时发生错误: {e}")
        return None

def get_all_chapters():
    """
    获取EPUB文件中所有章节的信息
    
    Returns:
        list: 包含所有章节信息的列表
    """
    try:
        book = epub.read_epub(Env.DATA_PATH)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        chapters = []
        
        for i, item in enumerate(items):
            chapter_info = {
                'id': item.id,
                'title': getattr(item, 'title', f'Chapter {i + 1}'),
                'content': item.get_content().decode('utf-8') if isinstance(item.get_content(), bytes) else item.get_content(),
                'file_name': item.file_name if hasattr(item, 'file_name') else None,
                'index': i
            }
            chapters.append(chapter_info)
            
        return chapters
        
    except Exception as e:
        print(f"获取所有章节时发生错误: {e}")
        return []
    
def update_chapter_content(chapter_index, new_content, replace=False):
    """
    更新指定章节的内容并保存回EPUB文件
    
    Args:
        chapter_index (int): 要更新的章节索引
        new_content (str): 新的章节内容（HTML格式）
    
    Returns:
        bool: 更新是否成功
    """
    try:
        # 读取原始EPUB文件
        book = epub.read_epub(Env.DATA_PATH)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        
        if chapter_index >= len(items):
            print(f"章节索引超出范围，总章节数: {len(items)}")
            return False
            
        # 更新章节内容
        original_chapter = items[chapter_index]
        if isinstance(original_chapter, EpubHtml):
            original_chapter.set_content(new_content.encode('utf-8'))
        else:
            # 如果不是EpubHtml类型，创建新的EpubHtml对象
            new_chapter = EpubHtml(
                uid=original_chapter.id,
                file_name=getattr(original_chapter, 'file_name', f'chapter_{chapter_index}.xhtml'),
                content=new_content.encode('utf-8')
            )
            # 替换原章节
            book.items.remove(original_chapter)
            book.items.append(new_chapter)
            
        # 保存修改后的EPUB文件
        if replace:
            output_path = Env.DATA_PATH
            epub.write_epub(output_path, book)
            print(f"修改后的文件已保存至: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"更新章节内容时发生错误: {e}")
        return False

# 示例使用
if __name__ == "__main__":
    # 获取第一个章节的数据
    chapter_data = get_chapter_data(0)
    if chapter_data:
        print(f"章节标题: {chapter_data['title']}")
        # print(f"章节内容预览: {chapter_data['content'][:200]}...")
    
    # 获取所有章节
    # all_chapters = get_all_chapters()
    # print(f"总章节数: {len(all_chapters)}")
    
    # 更新章节内容示例
    # new_content = "<h1>修改后的标题</h1><p>这是修改后的内容。</p>"

    # update_chapter_content(0, new_content)

