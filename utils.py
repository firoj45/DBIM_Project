"""Utility functions for the DBIM Toolkit."""
import re
import requests
from typing import Dict, List, Optional, Any, Tuple
import colorsys
import logging
from datetime import datetime
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Government color groups with their hex codes

GOVERNMENT_COLOR_GROUPS = {
    "group1": ["#410B26", "#6C1340", "#A32966", "#DB70A6", "#EBADCC", "#FAEBF2"],
    "group2": ["#380B41", "#5E136C", "#8F29A3", "#C970DB", "#E0ADEB", "#F7EBFA"],
    "group3": ["#190B41", "#29136C", "#4729A3", "#8B70DB", "#BDADEB", "#EEEBFA"],
    "group4": ["#0B1941", "#13296C", "#2947A3", "#708BBD", "#ADDBEB", "#D6DEFS"],
    "group5": ["#0B2641", "#13406C", "#2966A3", "#6B99C7", "#ADCCEB", "#D6E5F5"],
    "group6": ["#0B4141", "#0F5757", "#2D8686", "#75BDBD", "#A6D9D9", "#D9F2F2"],
    "group7": ["#1E3F0D", "#285412", "#407326", "#9AC982", "#C5E0B8", "#F1F7ED"],
    "group8": ["#412B0B", "#6C4713", "#A37A29", "#DBA57F", "#E8D5B0", "#F7F4ED"],
    "group9": ["#3E170E", "#8C2F26", "#C25038", "#D87A52", "#F3CEBD", "#F7EFED"]
}
DARKEST_TONE_LIST = [
    "#410B26",
    "#380B41",
    "#190B41",
    "#0B1941",
    "#0B2641",
    "#0B4141",
    "#1E3F0D",
    "#412B0B",
    "#3E170E"
]


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate the relative luminance of an RGB color."""
    r, g, b = [x / 255.0 for x in rgb]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def get_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate the contrast ratio between two colors."""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    l1 = get_luminance(rgb1)
    l2 = get_luminance(rgb2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def find_color_group(color: str) -> Optional[str]:
    """Find which color group the given color belongs to."""
    # Normalize the input color
    color = color.upper()
    
    # Check each color group
    for group_name, colors in GOVERNMENT_COLOR_GROUPS.items():
        if color in [c.upper() for c in colors]:
            return group_name
    return None

def is_darkest_in_group(color: str, group_name: str) -> bool:
    """Check if the given color is the darkest in its group."""
    if group_name not in GOVERNMENT_COLOR_GROUPS:
        return False
        
    group_colors = GOVERNMENT_COLOR_GROUPS[group_name]
    # The colors are ordered from lightest to darkest in each group
    return group_colors[-1].upper() == color.upper()

def get_button_elements(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Find all button-like elements in the page.
    Returns a list of button elements with their details.
    """
    button_selectors = [
        'button',
        'input[type="button"]',
        'input[type="submit"]',
        'a[role="button"]',
        '.btn',
        '.button',
        'a[class*="btn"]',
        'a[class*="button"]'
    ]
    
    buttons = []
    for selector in button_selectors:
        for element in soup.select(selector):
            # Skip hidden elements
            if element.get('style', '').lower().find('display: none') != -1:
                continue
                
            # Get button text
            text = ''
            if element.name == 'input' and element.get('type') in ['button', 'submit']:
                text = element.get('value', '')
            else:
                text = element.get_text(strip=True)
            
            # Skip empty or non-interactive buttons
            if not text or len(text) < 2:
                continue
                
            buttons.append({
                'element': str(element.name),
                'text': text[:100],  # Limit text length
                'classes': element.get('class', []),
                'id': element.get('id', ''),
                'html': str(element)[:200] + ('...' if len(str(element)) > 200 else '')
            })
    
    return buttons

def get_button_background_color(element: Dict[str, Any], soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract the background color of a button element.
    Returns a dictionary with color information.
    
    Tries multiple methods to detect background color:
    1. Inline styles
    2. Direct CSS selectors
    3. Parent element styles
    4. CSS class-based selectors
    """
    def get_element_selectors(el):
        """Generate all possible CSS selectors for an element."""
        selectors = []
        
        # Element name
        if el.name:
            selectors.append(el.name)
            
        # ID selector
        if el.get('id'):
            selectors.append(f'#{el["id"]}')
            
        # Class selectors
        for cls in el.get('class', []):
            selectors.append(f'.{cls}')
            
        # Combined selectors
        combined = []
        if el.name:
            if el.get('id'):
                combined.append(f'{el.name}#{el["id"]}')
            if el.get('class'):
                combined.append(f"{el.name}.{'.'.join(el['class'])}")
        
        return selectors + combined

    def find_background_in_styles(style_text, selectors):
        """Search for background color in style text using multiple selectors."""
        for sel in selectors:
            # Look for direct background-color rules
            bg_pattern = rf'{re.escape(sel)}\s*{{[^}}]*background(?:-color)?\s*:\s*([^;}}]+)'
            bg_match = re.search(bg_pattern, style_text, re.IGNORECASE | re.DOTALL)
            if bg_match:
                return bg_match.group(1).strip()
                
            # Look for background shorthand
            bg_shorthand = rf'{re.escape(sel)}\s*{{[^}}]*background\s*:\s*([^;}}]+)'
            bg_match = re.search(bg_shorthand, style_text, re.IGNORECASE | re.DOTALL)
            if bg_match:
                return bg_match.group(1).split()[0].strip()  # Take first value from shorthand
        return None

    try:
        # Try to find the element in the soup
        element_obj = None
        if element.get('id'):
            element_obj = soup.select_one(f'#{element["id"]}')
        elif element.get('classes'):
            # Try different combinations of classes
            for cls in element['classes']:
                element_obj = soup.select_one(f'.{cls}')
                if element_obj:
                    break
        
        if not element_obj:
            return {
                'status': 'element_not_found',
                'suggestion': 'Could not locate the button in the HTML structure',
                'note': 'Try checking if the element has dynamic classes or IDs'
            }
        
        # 1. Check inline style first (highest priority)
        style = element_obj.get('style', '')
        bg_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|\w+)', style, re.IGNORECASE)
        if bg_match:
            return {
                'status': 'success',
                'color': bg_match.group(1).strip(),
                'source': 'inline_style'
            }
        
        # 2. Check parent elements for inherited styles
        parent = element_obj.parent
        while parent and parent.name:
            parent_style = parent.get('style', '')
            bg_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|\w+)', 
                               parent_style, re.IGNORECASE)
            if bg_match:
                return {
                    'status': 'success',
                    'color': bg_match.group(1).strip(),
                    'source': 'parent_inline_style',
                    'parent_tag': parent.name
                }
            parent = parent.parent
            
        # 3. Check all style tags for matching selectors
        element_selectors = get_element_selectors(element_obj)
        
        for style_tag in soup.find_all('style'):
            style_text = style_tag.get_text()
            bg_color = find_background_in_styles(style_text, element_selectors)
            if bg_color:
                return {
                    'status': 'success',
                    'color': bg_color,
                    'source': 'stylesheet',
                    'selector': next((s for s in element_selectors if s in style_text), '')
                }
        
        # 4. Check for common button classes
        common_button_classes = ['btn', 'button', 'primary', 'secondary', 'cta']
        for cls in element_obj.get('class', []):
            if cls in common_button_classes:
                # Look for common button styles
                for style_tag in soup.find_all('style'):
                    style_text = style_tag.get_text()
                    for btn_class in common_button_classes:
                        bg_color = find_background_in_styles(style_text, [f'.{btn_class}'])
                        if bg_color:
                            return {
                                'status': 'success',
                                'color': bg_color,
                                'source': 'common_button_style',
                                'class': btn_class
                            }
        
        return {
            'status': 'no_background_found',
            'suggestion': 'Could not determine button background color',
            'note': ('The button might be using a default browser style, the color is set via JavaScript, '
                    'or the styles are in an external stylesheet not processed here')
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'suggestion': 'An error occurred while processing the button'
        }

def is_color_in_palette(color: str) -> bool:
    """
    Check if a color is in any of the government color palette groups.
    """
    # Normalize the color to uppercase for comparison
    color = color.upper()
    
    # Check all colors in all groups
    for group_name, colors in GOVERNMENT_COLOR_GROUPS.items():
        if color in [c.upper() for c in colors]:
            return True
    return False

def get_footer_background_color(url: str) -> Dict[str, Any]:
    """
    Extract the background color of the footer element from a given URL.
    
    Args:
        url: The URL of the website to check
        
    Returns:
        Dict containing status, color, and element information
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make sure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different ways to find the footer
        footer = None
        footer_selectors = [
            'footer',
            'div.footer',
            'div#footer',
            'div[class*="footer"]',
            'div[class*="Footer"]',
            'div[role="contentinfo"]',
            'div[class*="site-footer"]',
            'div[class*="siteFooter"]'
        ]
        
        for selector in footer_selectors:
            footer = soup.select_one(selector)
            if footer:
                break
        
        if not footer:
            return {
                'status': 'footer_not_found',
                'suggestion': 'No <footer> element or common footer class names found on the page',
                'tried_selectors': footer_selectors
            }
        
        # Check inline styles
        if footer.has_attr('style'):
            style = footer['style']
            bg_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|\w+)', style, re.IGNORECASE)
            if bg_match:
                return {
                    'status': 'success',
                    'color': bg_match.group(1).strip(),
                    'element': str(footer.name),
                    'source': 'inline_style'
                }
        
        # Check style attribute
        style = footer.get('style', '')
        if style:
            bg_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|\w+)', style, re.IGNORECASE)
            if bg_match:
                return {
                    'status': 'success',
                    'color': bg_match.group(1).strip(),
                    'element': str(footer.name),
                    'source': 'style_attribute'
                }
        
        # Check computed styles from stylesheets (basic implementation)
        for style_tag in soup.find_all('style'):
            # Look for footer-related styles
            style_text = style_tag.get_text()
            if any(selector in style_text for selector in ['.footer', '#footer', 'footer[', 'footer ', 'footer.']):
                # Try to find specific background color definitions
                bg_match = re.search(r'(?:footer[^{}]*|\.[^{}]*footer[^{}]*|#[^{}]*footer[^{}]*)\s*{[^}]*background(?:-color)?\s*:\s*([^;\n}]+)', style_text, re.IGNORECASE)
                if bg_match:
                    color = bg_match.group(1).strip()
                    return {
                        'status': 'success',
                        'color': color,
                        'element': str(footer.name),
                        'source': 'stylesheet_parsed',
                        'note': 'Color extracted from stylesheet'
                    }
        
        # Check parent elements for background color
        parent = footer.parent
        for _ in range(3):  # Check up to 3 levels up
            if parent and hasattr(parent, 'get'):
                parent_style = parent.get('style', '')
                bg_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|\w+)', parent_style, re.IGNORECASE)
                if bg_match:
                    return {
                        'status': 'success',
                        'color': bg_match.group(1).strip(),
                        'element': f"{parent.name} (parent of footer)",
                        'source': 'parent_element_style',
                        'note': 'Color found on a parent element of the footer'
                    }
                parent = getattr(parent, 'parent', None)
            else:
                break
        
        # Check child elements for background color (common in modern designs)
        for child in footer.find_all(recursive=False, limit=5):  # Check first 5 direct children
            child_style = child.get('style', '')
            bg_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|\w+)', child_style, re.IGNORECASE)
            if bg_match:
                return {
                    'status': 'success',
                    'color': bg_match.group(1).strip(),
                    'element': f"{child.name} (child of footer)",
                    'source': 'child_element_style',
                    'note': 'Color found on a child element of the footer'
                }

        # Check for background images that might be used for color
        for elem in [footer] + footer.find_all(recursive=False, limit=3):
            style = elem.get('style', '')
            bg_image = re.search(r'background(?:-image)?\s*:\s*url\(([^)]+)\)', style, re.IGNORECASE)
            if bg_image:
                return {
                    'status': 'background_image_found',
                    'image_url': bg_image.group(1).strip("'\""),
                    'element': elem.name,
                    'source': 'background_image',
                    'note': 'Background image found instead of solid color',
                    'suggestion': 'The footer uses a background image. Consider checking the image for the dominant color.'
                }

        # Provide detailed suggestions based on what we found
        suggestions = [
            "The footer's background might be set in an external CSS file.",
            "Check for background colors on child elements or background images.",
            "The color might be set using CSS variables or gradients.",
            "Try inspecting the page in a browser's developer tools for more details."
        ]
        
        # Get class and ID information from the footer and its children
        child_elements = [
            {
                'tag': child.name,
                'classes': child.get('class', []),
                'id': child.get('id', '')
            }
            for child in footer.find_all(recursive=False, limit=3)  # First 3 children
        ]
        
        return {
            'status': 'no_background_found',
            'suggestion': 'Footer element found but no background color could be determined. ' + ' '.join(suggestions),
            'element': str(footer.name),
            'element_html': str(footer)[:200] + ('...' if len(str(footer)) > 200 else ''),
            'element_classes': footer.get('class', []),
            'element_id': footer.get('id', ''),
            'parent_element': str(getattr(footer.parent, 'name', '') if hasattr(footer, 'parent') else ''),
            'child_elements': child_elements,
            'note': 'Consider checking the computed styles in browser developer tools for more accurate results.'
        }
        
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return {
            'status': 'request_error',
            'error': str(e),
            'suggestion': 'Could not fetch the URL. Please check the URL and try again.'
        }
    except Exception as e:
        logger.error(f"Error getting footer color: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'suggestion': 'An unexpected error occurred while processing the page.'
        }
