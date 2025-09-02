import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pathlib

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Cm
import requests
from io import BytesIO


def set_slide_background_picture(slide, prs, image_path: str):
    fill = slide.background.fill
    if hasattr(fill, "user_picture"):
        fill.user_picture(image_path)
        return
    # Fallback for older python-pptx versions without user_picture on FillFormat
    pic = slide.shapes.add_picture(
        image_path,
        left=0,
        top=0,
        width=prs.slide_width,
        height=prs.slide_height,
    )
    # SAFELY send picture to back: spTree must keep nvGrpSpPr and grpSpPr first.
    spTree = slide.shapes._spTree
    pic_el = pic._element
    # Remove current node
    spTree.remove(pic_el)
    # Find the insertion index AFTER the header nodes (usually first two)
    insert_idx = 0
    for i, child in enumerate(list(spTree)):
        tag = child.tag.rsplit('}', 1)[-1]
        if tag in ("nvGrpSpPr", "grpSpPr"):
            insert_idx = i + 1
            continue
        # After we’ve passed the header nodes, stop at the first real shape
        if insert_idx:
            break
    # Insert at the computed index (as the first actual shape)
    spTree.insert(insert_idx, pic_el)


def add_logo(slide, prs, logo_path: str, width_cm: float = 2.5):
    """Add a logo image to the lower-right corner of the slide."""
    from pptx.util import Cm
    if not os.path.exists(logo_path):
        print(f"Warning: logo file not found: {logo_path}")
        return
    logo_width = Cm(width_cm)
    logo_height = None  # auto-scale
    left = prs.slide_width - logo_width
    top = prs.slide_height - Cm(2.5)  # 2.5 cm up from bottom
    slide.shapes.add_picture(logo_path, left, top, width=logo_width, height=logo_height)


def create_title_slide(prs, title, subtitle,logo_path):

    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title_shape = slide.shapes.title
    subtitle_shape = slide.placeholders[1]
    #print(f"DEBUG: Checking file exists: assets/backgrounds/title_background_pro.jpg: {os.path.exists('assets/backgrounds/title_background_pro.jpg')}")
    #print(f"DEBUG: WHere am I: {os.getcwd()}")

    IMG = pathlib.Path(__file__).parents[1] / "assets" / "backgrounds" / "title_background_pro.png"
    set_slide_background_picture(slide, prs, str(IMG))
    #set_slide_background_picture(slide, prs, "assets/backgrounds/title_background_pro.png")

    title_shape.text = title
    title_shape.text_frame.paragraphs[0].font.size = Pt(40)
    title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    subtitle_shape.text = subtitle
    subtitle_shape.text_frame.paragraphs[0].font.size = Pt(24)
    subtitle_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    add_logo(slide, prs, logo_path )
    
def create_content_side(prs, slide_data,logo_path):
    content_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(content_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = slide_data.get('title', 'Slide')
    
    tf = body_shape.text_frame
    tf.clear()  # Clear any existing content
    for block in slide_data.get('content_blocks', []):
        if block['type'] == 'Text':
            p = tf.add_paragraph()
            p.text = block['body']
            p.font.size = Pt(18)
            p.space_after = Pt(10)
        elif block['type'] == 'Code':
            p = tf.add_paragraph()
            p.text = block['body']
            p.font.size = Pt(14)
            p.font.name = 'Courier New'
            p.font.color.rgb = RGBColor(0, 0, 255)
            p.space_after = Pt(10)
        elif block['type'] == 'Image':
            print(f"TODO TODO TODO: Not doing anything for image block yet. query: {block['query']}")
    add_logo(slide, prs, logo_path)
    
    
def create_one_presentation(slide_json, theme, output_path):
    prs = Presentation()
    print(f"DEBUG DE:\n\n{slide_json=}\n\n")
    logo_path = str(pathlib.Path(__file__).parents[1] / "assets" / "logos" / "logoPro.png")
    
    create_title_slide(prs, slide_json['title'], slide_json.get('subtitle', ''),logo_path)
    for slide_data in slide_json['slides']:
        create_content_side(prs, slide_data,logo_path)
    prs.save(output_path)