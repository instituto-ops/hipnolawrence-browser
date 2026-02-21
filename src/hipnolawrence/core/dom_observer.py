import json

class DOMObserver:
    """
    Injeta um radar JavaScript na página para extrair elementos interativos.
    """
    async def observe_page(self, page):
        js_code = """
        () => {
            const elements = [];
            const interactives = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])');
            let id_counter = 0;

            function getXPath(el) {
                if (el.id) return `//*[@id="${el.id}"]`;
                const parts = [];
                while (el && el.nodeType === Node.ELEMENT_NODE) {
                    let sibling = el;
                    let count = 1;
                    while ((sibling = sibling.previousElementSibling) != null) {
                        if (sibling.nodeName === el.nodeName) count++;
                    }
                    parts.unshift(`${el.nodeName.toLowerCase()}[${count}]`);
                    el = el.parentNode;
                }
                return parts.length ? '/' + parts.join('/') : null;
            }

            for (let el of interactives) {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                if (rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.opacity !== '0') {
                    let text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || el.title || '').trim().replace(/\\n/g, ' ').substring(0, 60);
                    if (!text && el.tagName !== 'INPUT') continue;

                    elements.push({
                        id: id_counter++,
                        tag: el.tagName.toLowerCase(),
                        text: text,
                        x: rect.left + (rect.width / 2),
                        y: rect.top + (rect.height / 2),
                        xpath: getXPath(el)
                    });
                }
            }
            return elements;
        }
        """
        try:
            if not page: return []
            elements = await page.evaluate(js_code)
            return elements
        except Exception as e:
            print(f"Erro no DOM Observer: {e}")
            return []
